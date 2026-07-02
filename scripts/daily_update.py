import os
import json
import time
import chromadb
from dotenv import load_dotenv
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from datetime import datetime, timedelta

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = "UC29BKw2DaNMQe2B90QRVCNw"
BP_CHANNEL_ID = "UCVfwlh9XpX2Y_tQfjeln9QA"
SERMON_KEYWORDS = ["billy graham", "classic sermon", "crusade"]
LOG_FILE = "scheduler_log.json"

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
    logs.append({"time": timestamp, "message": message})
    with open(LOG_FILE, "w") as f:
        json.dump(logs[-50:], f, indent=2)  # keep last 50 logs

def is_sermon(title):
    return any(k in title.lower() for k in SERMON_KEYWORDS)

def get_recent_videos(channel_id, days=1):
    youtube = build("youtube", "v3", developerKey=API_KEY)
    uploads_playlist_id = "UU" + channel_id[2:]
    since_date = (datetime.now() - timedelta(days=days)).isoformat() + "Z"

    videos = []
    response = youtube.playlistItems().list(
        part="snippet",
        playlistId=uploads_playlist_id,
        maxResults=10
    ).execute()

    for item in response["items"]:
        published = item["snippet"]["publishedAt"]
        if published >= since_date:
            videos.append({
                "video_id": item["snippet"]["resourceId"]["videoId"],
                "title": item["snippet"]["title"],
                "published": published
            })

    return videos

def fetch_transcript(video):
    video_id = video["video_id"]
    filename = f"transcripts/{video_id}.json"

    if os.path.exists(filename):
        log(f"Already exists: {video['title']}")
        return None

    try:
        ytt = YouTubeTranscriptApi()
        transcript = ytt.fetch(video_id, languages=["en"])
        raw = transcript.to_raw_data()

        os.makedirs("transcripts", exist_ok=True)
        with open(filename, "w") as f:
            json.dump({
                "video_id": video_id,
                "title": video["title"],
                "published": video["published"],
                "transcript": raw
            }, f, indent=2)

        log(f"Fetched: {video['title']}")
        time.sleep(5)
        return raw

    except (TranscriptsDisabled, NoTranscriptFound):
        log(f"No transcript: {video['title']}")
        return None
    except Exception as e:
        log(f"Error: {video['title']} — {e}")
        return None

def process_and_load(video_id, title, published, collection_name):
    import re
    filename = f"transcripts/{video_id}.json"

    if not os.path.exists(filename):
        return

    with open(filename) as f:
        data = json.load(f)

    # Clean transcript
    full_text = " ".join([seg["text"] for seg in data["transcript"]])
    full_text = re.sub(r"<[^>]+>", "", full_text)
    full_text = re.sub(r"\[.*?\]", "", full_text)
    full_text = full_text.replace("&amp;", "&").replace("&#39;", "'")
    full_text = re.sub(r"\s+", " ", full_text).strip()

    # Chunk
    words = full_text.split()
    chunks = []
    for i in range(0, len(words), 450):
        chunk = " ".join(words[i:i + 500])
        chunks.append(chunk)

    if not chunks:
        return

    # Load into Chroma
    client = chromadb.PersistentClient(path="chroma_db")
    collection = client.get_or_create_collection(name=collection_name)

    collection.add(
        documents=chunks,
        metadatas=[{"video_id": video_id, "title": title} for _ in chunks],
        ids=[f"{video_id}_chunk_{i}" for i in range(len(chunks))]
    )

    log(f"Loaded into Chroma: {title} ({len(chunks)} chunks)")

def run_daily_update():
    log("=== Daily Update Started ===")

    # Check Billy Graham channel
    log("Checking Billy Graham channel...")
    bg_videos = get_recent_videos(CHANNEL_ID, days=1)
    for video in bg_videos:
        if is_sermon(video["title"]):
            raw = fetch_transcript(video)
            if raw:
                process_and_load(video["video_id"], video["title"], video["published"], "sermons")
        else:
            log(f"Skipping (not a sermon): {video['title']}")

    # Check Bible Project channel
    log("Checking Bible Project channel...")
    bp_videos = get_recent_videos(BP_CHANNEL_ID, days=1)
    for video in bp_videos:
        raw = fetch_transcript(video)
        if raw:
            process_and_load(video["video_id"], video["title"], video["published"], "bible_project")

    log("=== Daily Update Complete ===")

if __name__ == "__main__":
    run_daily_update()