import os
import json
from dotenv import load_dotenv
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = "UC29BKw2DaNMQe2B90QRVCNw"  # Billy Graham channel

def get_latest_video():
    youtube = build("youtube", "v3", developerKey=API_KEY)

    response = youtube.search().list(
        part="snippet",
        channelId=CHANNEL_ID,
        order="date",
        maxResults=1,
        type="video"
    ).execute()

    video = response["items"][0]
    video_id = video["id"]["videoId"]
    title = video["snippet"]["title"]
    published = video["snippet"]["publishedAt"]

    print(f"Latest video: {title}")
    print(f"Video ID: {video_id}")
    print(f"Published: {published}")

    return video_id, title, published

def get_transcript(video_id, title, published):
    ytt = YouTubeTranscriptApi()
    transcript = ytt.fetch(video_id, languages=["en"])
    raw = transcript.to_raw_data()

    os.makedirs("transcripts", exist_ok=True)
    filename = f"transcripts/{video_id}.json"

    with open(filename, "w") as f:
        json.dump({
            "video_id": video_id,
            "title": title,
            "published": published,
            "transcript": raw
        }, f, indent=2)

    print(f"Transcript saved → {filename}")
    return raw

if __name__ == "__main__":
    video_id, title, published = get_latest_video()
    get_transcript(video_id, title, published)