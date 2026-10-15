# God's Word

God’s Word is a Bible study assistant I built to make it easier to explore Scripture through conversation. Instead of searching across Bible passages and videos separately, users can ask questions and receive answers informed by relevant verses and teaching content. The app draws from the KJV Bible, Billy Graham sermon transcripts, and BibleProject transcripts, with Llama 3 running locally through Ollama.

## How it works

The app stores Bible verses and transcript chunks in ChromaDB. When someone asks a question, it searches these collections for relevant content and includes the retrieved passages in the model’s prompt. Recent conversation history helps it understand follow-up questions.

Bible verses are stored individually with their references. Video transcripts are split into overlapping chunks to preserve context during retrieval. When users ask for a video, the app finds related content and provides YouTube links.

The prompts ask the model to use the supplied passages and acknowledge when there is not enough information. This guides the responses, but it does not guarantee accuracy. Answers and Bible references should still be checked against the original text.

## Using the app

Alongside the chatbot, the app includes a daily verse, topic browsing, favourite verses, and a prayer journal. Users can explore topics such as faith, hope, forgiveness, and prayer, or ask their own questions. The interface supports light and dark themes.

Saved verses, journal entries, and the user’s name are stored in local JSON files. Conversation history is kept within the current Streamlit session. The app currently uses local storage rather than separate user accounts.

## Running it

To run the project locally, install the Python dependencies, start Llama 3 through Ollama, and load the Bible passages and available transcripts into ChromaDB. Then launch the Streamlit app with `streamlit run app.py`. A YouTube API key is needed to fetch video metadata.

The project also includes a script for checking recent videos and loading available transcripts. It can be run manually or through an external scheduler.

## Tech used

Python, Streamlit, ChromaDB, Llama 3 through Ollama, YouTube Data API v3, youtube-transcript-api, and local JSON storage.

## Data sources

- KJV Bible: https://github.com/aruljohn/Bible-kjv
- Billy Graham sermons: https://www.youtube.com/@billygraham
- BibleProject: https://www.youtube.com/@thebibleproject

