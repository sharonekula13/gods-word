# Gods Word 🕊️
### Where Scripture Meets the Heart — A Gospel Chatbot Powered by AI

Gods Word is a RAG-based (Retrieval Augmented Generation) Bible chatbot that answers your questions about Scripture, faith, and daily life — drawing from Billy Graham's sermons, the KJV Bible, and Bible Project transcripts. It speaks like a warm, caring friend who knows the Bible deeply.

---

## ✨ Features

- 🕊️ **Gospel Chatbot** — Ask anything about the Bible and get warm, pastoral answers
- 📖 **Daily Verse of the Day** — A new Bible verse every morning to start your day
- 🔍 **Browse by Topic** — Explore verses on Hope, Fear, Love, Forgiveness, and more
- ⭐ **Favourite Verses** — Save verses that speak to your heart
- 📝 **Prayer Journal** — Write and save your personal prayers
- 🌙 **Dark & Light Mode** — Choose the theme that suits you
- 📺 **YouTube Links** — Get relevant sermon and Bible Project video links
- 💬 **Conversation Memory** — The chatbot remembers context across your conversation

---

## 🛠️ Tech Stack

| Layer | Tool |
|---|---|
| Language | Python |
| UI | Streamlit |
| LLM | Ollama (Llama3 — runs locally) |
| Vector Database | ChromaDB |
| Bible Text | KJV Bible (public domain) |
| Sermon Transcripts | Billy Graham YouTube Channel |
| Bible Explanations | Bible Project YouTube Channel |
| Transcript Fetching | youtube-transcript-api |
| YouTube Metadata | YouTube Data API v3 |

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/gods-word.git
cd gods-word
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up your `.env` file
Create a `.env` file in the root folder:
```
YOUTUBE_API_KEY=your_youtube_api_key_here
```

Get your YouTube API key from [Google Cloud Console](https://console.cloud.google.com).

### 4. Install and start Ollama
Download Ollama from [ollama.com](https://ollama.com) then run:
```bash
ollama pull llama3
ollama serve
```

### 5. Fetch Billy Graham sermon transcripts
```bash
python3 scripts/fetch_latest.py
```

### 6. Fetch Bible Project transcripts
```bash
python3 scripts/fetch_bible_project.py
```

### 7. Process transcripts
```bash
python3 scripts/process_transcript.py
```

### 8. Load KJV Bible into ChromaDB
```bash
python3 scripts/load_bible.py
```

### 9. Load sermons into ChromaDB
```bash
python3 scripts/load_to_chroma.py
```

### 10. Load Bible Project into ChromaDB
```bash
python3 scripts/load_bible_project.py
```

### 11. Run the app
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501` 🎉

---

## 📁 Project Structure

```
gods-word/
├── app.py                      # Main Streamlit app
├── scripts/
│   ├── fetch_latest.py         # Fetch Billy Graham transcripts
│   ├── fetch_bible_project.py  # Fetch Bible Project transcripts
│   ├── process_transcript.py   # Clean and chunk transcripts
│   ├── load_bible.py           # Load KJV Bible into ChromaDB
│   ├── load_to_chroma.py       # Load sermons into ChromaDB
│   └── load_bible_project.py   # Load Bible Project into ChromaDB
├── chroma_db/                  # Vector database (auto-generated)
├── transcripts/                # Raw transcripts (auto-generated)
├── processed/                  # Processed transcripts (auto-generated)
├── favourites.json             # Saved favourite verses
├── prayer_journal.json         # Saved prayers
├── requirements.txt
└── .env                        # API keys (never commit this!)
```

---

## 🔒 Important Notes

- Never share or commit your `.env` file — it contains your API key
- The `transcripts/`, `processed/`, and `chroma_db/` folders are excluded from GitHub — regenerate them locally using the setup steps above
- Ollama must be running (`ollama serve`) before starting the app

---

## 🙏 Data Sources

- **KJV Bible** — Public domain
- **Billy Graham sermons** — [Billy Graham YouTube Channel](https://www.youtube.com/@billygraham)
- **Bible Project** — [The Bible Project YouTube Channel](https://www.youtube.com/@thebibleproject)

---

## 📜 License

This project is for educational and personal use. Bible content is from the public domain KJV translation. Sermon transcripts are sourced from publicly available YouTube videos.

---

*"Thy word is a lamp unto my feet, and a light unto my path." — Psalm 119:105* 🕊️
