"""
Evaluation harness for Gods Word RAG pipeline.

Measures:
- recall@5: Was the expected verse in the top 5 retrieved results?
- MRR: Mean Reciprocal Rank of the expected verse
- keyword_hit_rate: Did retrieved text contain expected keywords?

Run BEFORE and AFTER adding hybrid retrieval to get your before/after numbers.

Usage:
    python eval/run_eval.py --mode baseline    # pure ChromaDB
    python eval/run_eval.py --mode hybrid      # BM25 + dense + reranker
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb

# ── Args ──────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--mode", choices=["baseline", "hybrid"], default="baseline")
parser.add_argument("--eval-set", default="eval/eval_set.json")
parser.add_argument("--output-dir", default="eval/results")
args = parser.parse_args()

os.makedirs(args.output_dir, exist_ok=True)

# ── Load eval set ─────────────────────────────────────────────────────────────
with open(args.eval_set) as f:
    eval_set = json.load(f)

print(f"\n{'='*60}")
print(f"Gods Word Eval — Mode: {args.mode.upper()}")
print(f"Questions: {len(eval_set)}")
print(f"{'='*60}\n")

# ── Load ChromaDB ─────────────────────────────────────────────────────────────
client = chromadb.PersistentClient(path="chroma_db")
bible_col = client.get_or_create_collection(name="bible_verses")
sermon_col = client.get_or_create_collection(name="sermons")
bp_col = client.get_or_create_collection(name="bible_project")

# ── Baseline retrieval (pure vector) ──────────────────────────────────────────
def baseline_search(query: str, n_results: int = 5):
    results = bible_col.query(query_texts=[query], n_results=n_results)
    return {
        "ids": results["ids"][0],
        "documents": results["documents"][0],
    }

# ── Hybrid retrieval (BM25 + dense + reranker) ────────────────────────────────
hybrid_retriever = None
if args.mode == "hybrid":
    print("Loading hybrid retriever (this takes ~30s first run)...")
    # Build corpus from ChromaDB
    all_results = bible_col.get(limit=40000)
    corpus_texts = all_results["documents"]
    corpus_ids = all_results["ids"]
    from retrieval.hybrid import HybridRetriever
    hybrid_retriever = HybridRetriever(bible_col, corpus_texts, corpus_ids)
    print(f"Hybrid retriever ready. Corpus size: {len(corpus_texts):,} verses\n")

# ── Run eval ──────────────────────────────────────────────────────────────────
results_log = []
recall_hits = 0
mrr_total = 0.0
keyword_hits = 0
total_retrieve_ms = []

for i, item in enumerate(eval_set, 1):
    question = item["question"]
    expected_id = item["expected_reference"]
    expected_keywords = item.get("expected_keywords", [])

    t0 = time.perf_counter()

    if args.mode == "baseline":
        search_result = baseline_search(question, n_results=5)
        retrieved_ids = search_result["ids"]
        retrieved_docs = search_result["documents"]
    else:
        search_result = hybrid_retriever.search(question, top_k=5)
        retrieved_ids = [r["id"] for r in search_result["results"]]
        retrieved_docs = [r["text"] for r in search_result["results"]]

    retrieve_ms = (time.perf_counter() - t0) * 1000
    total_retrieve_ms.append(retrieve_ms)

    # Recall@5
    hit = expected_id in retrieved_ids
    if hit:
        recall_hits += 1

    # MRR
    rank = None
    for j, rid in enumerate(retrieved_ids):
        if rid == expected_id:
            rank = j + 1
            break
    mrr_total += (1 / rank) if rank else 0

    # Keyword hit rate
    combined_text = " ".join(retrieved_docs).lower()
    kw_hit = all(kw.lower() in combined_text for kw in expected_keywords) if expected_keywords else True
    if kw_hit:
        keyword_hits += 1

    result = {
        "question": question,
        "expected_id": expected_id,
        "retrieved_ids": retrieved_ids,
        "recall_hit": hit,
        "rank": rank,
        "keyword_hit": kw_hit,
        "retrieve_ms": round(retrieve_ms, 1),
    }
    results_log.append(result)

    status = "✅" if hit else "❌"
    print(f"[{i:03}/{len(eval_set)}] {status} {question[:60]}")
    if not hit:
        print(f"         Expected: {expected_id}")
        print(f"         Got:      {retrieved_ids[:3]}")

# ── Summary ───────────────────────────────────────────────────────────────────
n = len(eval_set)
recall_at_5 = recall_hits / n * 100
mrr = mrr_total / n
keyword_hit_rate = keyword_hits / n * 100

latencies = sorted(total_retrieve_ms)
p50 = latencies[int(len(latencies) * 0.50)]
p95 = latencies[int(len(latencies) * 0.95)]

print(f"\n{'='*60}")
print(f"RESULTS — {args.mode.upper()} — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"{'='*60}")
print(f"Recall@5:         {recall_at_5:.1f}%  ({recall_hits}/{n})")
print(f"MRR:              {mrr:.3f}")
print(f"Keyword Hit Rate: {keyword_hit_rate:.1f}%")
print(f"Latency p50:      {p50:.0f}ms")
print(f"Latency p95:      {p95:.0f}ms")
print(f"{'='*60}\n")

# ── Save results ──────────────────────────────────────────────────────────────
output = {
    "mode": args.mode,
    "timestamp": datetime.now().isoformat(),
    "n_questions": n,
    "metrics": {
        "recall_at_5": round(recall_at_5, 1),
        "mrr": round(mrr, 3),
        "keyword_hit_rate": round(keyword_hit_rate, 1),
        "latency_p50_ms": round(p50, 1),
        "latency_p95_ms": round(p95, 1),
    },
    "per_question": results_log,
}

out_path = os.path.join(args.output_dir, f"{args.mode}.json")
with open(out_path, "w") as f:
    json.dump(output, f, indent=2)

print(f"Results saved to {out_path}")
