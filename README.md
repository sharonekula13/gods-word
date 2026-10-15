# God's Word

God's Word is a Bible study assistant built with Python and Streamlit. It uses retrieval-augmented generation (RAG) to find relevant Bible passages and supporting teaching content, then generate conversational responses using Llama 3 through Ollama.

The application combines Scripture search, related video recommendations, saved verses, and a prayer journal in a single interface. It is a personal project intended to support Bible study and reflection.

## Features

- **Conversational Bible Q&A:** Ask questions using natural language.
- **Context-aware responses:** Recent conversation history helps interpret follow-up questions.
- **Scripture retrieval:** Search Bible verses stored in ChromaDB.
- **Supporting content:** Retrieve passages from Billy Graham sermon transcripts and BibleProject transcripts.
- **Video recommendations:** Find related YouTube videos when requested.
- **Daily verse:** Display a verse selected for the current date.
- **Topic browsing:** Explore subjects such as hope, faith, forgiveness, and prayer.
- **Saved verses:** Save verses for later reference.
- **Prayer journal:** Record personal reflections and prayer entries.
- **Appearance settings:** Switch between light and dark themes.

## How It Works

1. Bible verses and video transcripts are loaded into persistent ChromaDB collections.
2. Transcripts are divided into approximately 500-word chunks with 50-word overlap.
3. The application searches the collections using the user's question and recent conversation context.
4. Retrieved passages are included in the prompt sent to Llama 3 through Ollama.
5. The response is displayed in the Streamlit chat interface. Related video links are shown when requested.

The current implementation uses ChromaDB vector retrieval. It does not implement BM25 search, reciprocal rank fusion, or cross-encoder reranking.

## Technology

| Component | Technology |
| --- | --- |
| Language | Python |
| Interface | Streamlit |
| Language model | Llama 3 |
| Local model runtime | Ollama |
| Vector database | ChromaDB |
| Video metadata | YouTube Data API v3 |
| Transcript retrieval | youtube-transcript-api |
| Environment configuration | python-dotenv |
| Local preferences and journal storage | JSON files |

## Setup

Run the following commands from the project directory unless otherwise specified.

### 1. Clone the repository

```bash
git clone https://github.com/sharonekula13/gods-word.git
cd gods-word
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install streamlit chromadb ollama python-dotenv requests google-api-python-client youtube-transcript-api
```

### 4. Configure YouTube access

Create a `.env` file in the project root:

```dotenv
YOUTUBE_API_KEY=your_youtube_api_key_here
```

The transcript-fetching scripts use this key to access YouTube video metadata. Enable YouTube Data API v3 for the associated Google Cloud project.

### 5. Set up Ollama

Install Ollama from https://ollama.com, then download the model:

```bash
ollama pull llama3
```

Ensure Ollama is running before starting the application. If it is not already running through the desktop application, start it in a separate terminal:

```bash
ollama serve
```

### 6. Prepare the data

Create the working directories and load the Bible:

```bash
mkdir -p transcripts processed
python scripts/load_bible.py
```

Fetch and process sermon transcripts:

```bash
python scripts/fetch_latest.py
python scripts/process_transcript.py
python scripts/load_to_chroma.py
```

Then fetch and load BibleProject transcripts:

```bash
python scripts/fetch_bible_project.py
python scripts/load_bible_project.py
```

This order keeps BibleProject transcripts out of the initial sermon-processing step. The sermon loader reads every JSON file in `processed/`, so check that directory before rerunning it.

Data preparation requires internet access. Transcript availability, API quotas, and model downloads may affect setup time.

### 7. Start the application

```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Content Updates

The project includes a script that checks for recent videos, retrieves available transcripts, and loads new content into ChromaDB:

```bash
python scripts/daily_update.py
```

The script can be run manually or through an external scheduler. Scheduling is separate from the Streamlit application.

## Project Structure

```text
gods-word/
├── app.py
├── requirements.txt
├── scripts/
│   ├── fetch_latest.py
│   ├── fetch_bible_project.py
│   ├── fetch_telugu.py
│   ├── process_transcript.py
│   ├── load_bible.py
│   ├── load_to_chroma.py
│   ├── load_bible_project.py
│   ├── chatbot.py
│   └── daily_update.py
├── transcripts/
├── processed/
└── chroma_db/
```

The data directories are created locally during setup. User preferences, saved verses, and prayer journal entries are also stored locally as JSON files.

## Current Limitations

- Responses are generated by a language model and may contain errors. Prompt instructions encourage source-based answers but do not guarantee accuracy.
- The application does not independently verify generated claims or Bible references.
- No formal evaluation harness or verified performance benchmarks are included in this version.
- Transcript availability and quality vary between videos.
- Preferences and journal entries use shared local files rather than separate authenticated user accounts.
- The application requires local data preparation and a running Ollama instance.

## Planned Improvements

- Validate Bible references and provide clearer links between answers and retrieved sources.
- Build an evaluation dataset covering factual questions, follow-up questions, and insufficient-context cases.
- Improve retrieval for specific books, passages, and topics.
- Separate transcript processing by source and make ingestion safer to rerun.
- Add user-specific storage before supporting a shared deployment.

## Data Sources

- KJV Bible: https://github.com/aruljohn/Bible-kjv
- Billy Graham sermons: https://www.youtube.com/@billygraham
- BibleProject: https://www.youtube.com/@thebibleproject

Third-party content remains subject to its applicable rights and usage terms.

## Configuration and Local Data

Keep API keys and personal journal data out of version control. Review `.gitignore` before committing to ensure it excludes:

```text
.env
.venv/
chroma_db/
transcripts/
processed/
favourites.json
prayer_journal.json
user_name.json
```