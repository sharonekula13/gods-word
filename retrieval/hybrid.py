"""
Hybrid retrieval: BM25 + ChromaDB dense search fused with Reciprocal Rank Fusion (RRF),
then re-ranked with a cross-encoder.

Usage:
    from retrieval.hybrid import HybridRetriever
    retriever = HybridRetriever(collection, corpus_texts, corpus_ids)
    results = retriever.search(query, top_k=5)
"""

import time
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder


class HybridRetriever:
    def __init__(self, collection, corpus_texts: list, corpus_ids: list):
        """
        Args:
            collection: ChromaDB collection
            corpus_texts: list of all document texts (same order as corpus_ids)
            corpus_ids: list of ChromaDB document IDs
        """
        self.collection = collection
        self.corpus_texts = corpus_texts
        self.corpus_ids = corpus_ids
        self.id_to_text = dict(zip(corpus_ids, corpus_texts))

        # Build BM25 index
        tokenized = [doc.lower().split() for doc in corpus_texts]
        self.bm25 = BM25Okapi(tokenized)

        # Cross-encoder reranker
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def _bm25_search(self, query: str, top_k: int = 20) -> list[tuple[str, float]]:
        """Returns list of (doc_id, bm25_score)"""
        tokens = query.lower().split()
        scores = self.bm25.get_scores(tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [(self.corpus_ids[i], scores[i]) for i in top_indices]

    def _dense_search(self, query: str, top_k: int = 20) -> list[tuple[str, float]]:
        """Returns list of (doc_id, distance_score)"""
        results = self.collection.query(query_texts=[query], n_results=top_k)
        ids = results["ids"][0]
        # ChromaDB returns distances — lower is better, so invert for scoring
        distances = results["distances"][0]
        max_dist = max(distances) if distances else 1
        scores = [(id_, 1 - (d / max_dist)) for id_, d in zip(ids, distances)]
        return scores

    def _reciprocal_rank_fusion(
        self,
        bm25_results: list[tuple[str, float]],
        dense_results: list[tuple[str, float]],
        k: int = 60,
    ) -> list[tuple[str, float]]:
        """Merge two ranked lists using RRF. Higher score = better."""
        rrf_scores: dict[str, float] = {}

        for rank, (doc_id, _) in enumerate(bm25_results):
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1 / (k + rank + 1)

        for rank, (doc_id, _) in enumerate(dense_results):
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1 / (k + rank + 1)

        return sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

    def _rerank(self, query: str, candidates: list[tuple[str, float]], top_k: int = 5) -> list[dict]:
        """Re-rank top candidates using cross-encoder."""
        texts = [self.id_to_text.get(doc_id, "") for doc_id, _ in candidates]
        pairs = [[query, text] for text in texts]
        scores = self.reranker.predict(pairs)

        ranked = sorted(
            zip([doc_id for doc_id, _ in candidates], texts, scores),
            key=lambda x: x[2],
            reverse=True,
        )
        return [{"id": doc_id, "text": text, "score": float(score)} for doc_id, text, score in ranked[:top_k]]

    def search(self, query: str, top_k: int = 5, candidate_pool: int = 20) -> dict:
        """
        Full hybrid search pipeline with timing.

        Returns:
            {
                "results": [{"id": ..., "text": ..., "score": ...}],
                "timing": {"bm25_ms": ..., "dense_ms": ..., "rerank_ms": ..., "total_ms": ...}
            }
        """
        t_start = time.perf_counter()

        t0 = time.perf_counter()
        bm25_results = self._bm25_search(query, top_k=candidate_pool)
        bm25_ms = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        dense_results = self._dense_search(query, top_k=candidate_pool)
        dense_ms = (time.perf_counter() - t0) * 1000

        fused = self._reciprocal_rank_fusion(bm25_results, dense_results)
        top_candidates = fused[:candidate_pool]

        t0 = time.perf_counter()
        results = self._rerank(query, top_candidates, top_k=top_k)
        rerank_ms = (time.perf_counter() - t0) * 1000

        total_ms = (time.perf_counter() - t_start) * 1000

        return {
            "results": results,
            "timing": {
                "bm25_ms": round(bm25_ms, 1),
                "dense_ms": round(dense_ms, 1),
                "rerank_ms": round(rerank_ms, 1),
                "total_ms": round(total_ms, 1),
            },
        }
