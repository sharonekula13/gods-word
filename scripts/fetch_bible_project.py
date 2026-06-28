import os
import json
import time
from dotenv import load_dotenv
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = "UCVfwlh9XpX2Y_tQfjeln9QA"  # Bible Project channel

def get_all_videos():
    youtube = build("youtube", "v3", developerKey=API_KEY)
    uploads_playlist_id = "UU" + CHANNEL_ID[2:]
    
    videos = []
    next_page_token = None

    while True:
        response = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        for item in response["items"]:
            title = item["snippet"]["title"]
            video_id = item["snippet"]["resourceId"]["videoId"]
            published = item["snippet"]["publishedAt"]

            videos.append({
                "video_id": video_id,
                "title": title,
                "published": published
            })
            print(f"✅ Found: {title}")

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

        time.sleep(1)

    print(f"\nTotal videos found: {len(videos)}")
    return videos

def get_transcript(video):
    video_id = video["video_id"]
    title = video["title"]
    published = video["published"]

    filename = f"transcripts/bibleproject_{video_id}.json"
    if os.path.exists(filename):
        print(f"⏭️  Skipping (already exists): {title}")
        return

    try:
        ytt = YouTubeTranscriptApi()
        transcript = ytt.fetch(video_id, languages=["en"])
        raw = transcript.to_raw_data()

        os.makedirs("transcripts", exist_ok=True)
        with open(filename, "w") as f:
            json.dump({
                "video_id": video_id,
                "title": title,
                "published": published,
                "source": "Bible Project",
                "transcript": raw
            }, f, indent=2)

        print(f"✅ Saved: {title}")

    except (TranscriptsDisabled, NoTranscriptFound):
        print(f"⚠️  No transcript: {title}")
    except Exception as e:
        print(f"❌ Error on {title}: {e}")

    time.sleep(5)

if __name__ == "__main__":
    videos = get_all_videos()
    for video in videos:
        get_transcript(video)