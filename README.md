# Gods Word 🕊️

### Where Scripture Meets the Heart — A Production RAG Bible Chatbot

Gods Word is a production-grade RAG (Retrieval Augmented Generation) Bible chatbot built without LangChain. It answers questions about Scripture drawing from the KJV Bible, Billy Graham sermons, and Bible Project transcripts — using hybrid retrieval, cross-encoder reranking, and a versioned evaluation harness.

---

## 🏗️ Architecture

```
Query
  │
  ├── BM25 (keyword search over corpus)
  ├── ChromaDB (dense vector search)
  │
  └── Reciprocal Rank Fusion (merge results)
        │
        └── Cross-Encoder Reranker (bge-reranker / ms-marco)
              │
              └── Llama 3 (local via Ollama) → Answer
```

**Three data sources:**
| Source | Documents | Type |
|---|---|---|
| KJV Bible | 31,102 verses | Verse-level chunks |
| Billy Graham Sermons | ~80 videos | 500-word chunks with overlap |
| Bible Project | ~19 videos | 500-word chunks with overlap |

---

## ✨ Features

- 🔍 **Hybrid Retrieval** — BM25 + dense vector search fused with Reciprocal Rank Fusion
- 🎯 **Cross-Encoder Reranking** — Re-ranks top candidates for precision
- 📊 **Versioned Eval Harness** — 50-question labeled set measuring recall@5, MRR, keyword hit rate
- 🚦 **CI Eval Gate** — GitHub Actions fails any PR that drops retrieval quality below threshold
- 🕊️ **Gospel Chatbot** — Warm, pastoral answers grounded in Scripture
- 📖 **Daily Verse of the Day**
- 🔍 **Browse by Topic** — Hope, Fear, Love, Forgiveness, and more
- ⭐ **Favourite Verses**
- 📝 **Prayer Journal**
- 🌙 **Dark & Light Mode**
- 📺 **YouTube Video Links** — Relevant sermons retrieved semantically
- 💬 **Multi-turn Conversation Memory**

---

## 📊 Eval Results

| Metric | Baseline (pure vector) | Hybrid + Rerank |
|---|---|---|
| Recall@5 | — | — |
| MRR | — | — |
| Keyword Hit Rate | — | — |
| Latency p95 | — | — |

*Run `python eval/run_eval.py --mode baseline` then `--mode hybrid` to fill in your numbers.*

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| Language | Python |
| UI | Streamlit |
| LLM | Ollama (Llama 3 — runs locally) |
| Vector Database | ChromaDB |
| Keyword Search | rank-bm25 |
| Reranker | sentence-transformers (cross-encoder/ms-marco-MiniLM-L-6-v2) |
| Transcript Fetching | youtube-transcript-api |
| YouTube Metadata | YouTube Data API v3 |
| CI | GitHub Actions |

---

## ⚙️ Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/sharonekula13/gods-word.git
cd gods-word
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up `.env`

```bash
YOUTUBE_API_KEY=your_youtube_api_key_here
```

Get your key from [Google Cloud Console](https://console.cloud.google.com).

### 4. Install and start Ollama

```bash
# Download from https://ollama.com then:
ollama pull llama3
ollama serve
```

### 5. Build the ChromaDB (run in order)

```bash
python scripts/fetch_latest.py          # Fetch Billy Graham transcripts
python scripts/fetch_bible_project.py   # Fetch Bible Project transcripts
python scripts/process_transcript.py    # Clean and chunk transcripts
python scripts/load_bible.py            # Load KJV Bible (31k verses)
python scripts/load_to_chroma.py        # Load sermons
python scripts/load_bible_project.py    # Load Bible Project
```

### 6. Run the app

```bash
streamlit run app.py
```

Open `http://localhost:8501` 🎉

---

## 📊 Running Evaluations

```bash
# Get your baseline numbers FIRST before any changes
python eval/run_eval.py --mode baseline

# After adding hybrid retrieval:
python eval/run_eval.py --mode hybrid

# Results saved to eval/results/baseline.json and eval/results/hybrid.json
```

---

## 📁 Project Structure

```
gods-word/
├── app.py                          # Main Streamlit app
├── retrieval/
│   ├── __init__.py
│   └── hybrid.py                   # BM25 + dense + RRF + cross-encoder reranker
├── eval/
│   ├── eval_set.json               # 50 labeled Q&A pairs (versioned)
│   ├── run_eval.py                 # Measures recall@5, MRR, keyword hit rate
│   └── results/                    # Saved eval runs (baseline.json, hybrid.json)
├── scripts/
│   ├── fetch_latest.py             # Fetch Billy Graham transcripts
│   ├── fetch_bible_project.py      # Fetch Bible Project transcripts
│   ├── process_transcript.py       # Clean and chunk transcripts
│   ├── load_bible.py               # Load KJV Bible into ChromaDB
│   ├── load_to_chroma.py           # Load sermons into ChromaDB
│   └── load_bible_project.py       # Load Bible Project into ChromaDB
├── .github/
│   └── workflows/
│       └── eval.yml                # CI eval gate — fails PR if recall drops
├── requirements.txt
└── .env                            # API keys (never commit)
```

---

## 🔒 Notes

- Never commit `.env` — it contains your API key
- `transcripts/`, `processed/`, `chroma_db/` are gitignored — regenerate locally
- Ollama must be running before starting the app
- CI runs Bible-only eval (no Ollama needed) — sermon evals run locally

---

## 🙏 Data Sources

- **KJV Bible** — Public domain
- **Billy Graham Sermons** — [YouTube Channel](https://www.youtube.com/@billygraham)
- **Bible Project** — [YouTube Channel](https://www.youtube.com/@thebibleproject)

---

*"Thy word is a lamp unto my feet, and a light unto my path." — Psalm 119:105* 🕊️
