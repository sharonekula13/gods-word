import os
import json
import time
import requests
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
from deep_translator import GoogleTranslator

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
TELUGU_CHANNEL_ID = "UCFyCGU7WW2BFPMO9eBKD8XQ"

def get_all_videos():
    playlist_id = "UU" + TELUGU_CHANNEL_ID[2:]
    videos = []
    next_page_token = None

    while True:
        url = (
            f"https://www.googleapis.com/youtube/v3/playlistItems"
            f"?part=snippet&playlistId={playlist_id}"
            f"&maxResults=50&key={API_KEY}"
        )
        if next_page_token:
            url += f"&pageToken={next_page_token}"

        response = requests.get(url)
        data = response.json()

        if "error" in data:
            print(f"❌ API Error: {data['error']['message']}")
            break

        for item in data["items"]:
            title = item["snippet"]["title"]
            video_id = item["snippet"]["resourceId"]["videoId"]
            published = item["snippet"]["publishedAt"]

            videos.append({
                "video_id": video_id,
                "title": title,
                "published": published
            })
            print(f"✅ Found: {title}")

        next_page_token = data.get("nextPageToken")
        if not next_page_token:
            break

        time.sleep(1)

    print(f"\nTotal videos found: {len(videos)}")
    return videos

def translate_text(text):
    try:
        if len(text) <= 4500:
            return GoogleTranslator(source='auto', target='en').translate(text)

        pieces = [text[i:i+4500] for i in range(0, len(text), 4500)]
        translated_pieces = []
        for piece in pieces:
            translated = GoogleTranslator(source='auto', target='en').translate(piece)
            translated_pieces.append(translated)
            time.sleep(0.5)
        return " ".join(translated_pieces)
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def get_transcript(video):
    video_id = video["video_id"]
    title = video["title"]
    published = video["published"]

    filename = f"transcripts/telugu_{video_id}.json"
    if os.path.exists(filename):
        print(f"⏭️  Skipping (already exists): {title}")
        return

    try:
        ytt = YouTubeTranscriptApi()

        try:
            transcript = ytt.fetch(video_id, languages=["te"])
            print(f"📖 Telugu transcript found: {title}")
        except:
            transcript = ytt.fetch(video_id, languages=["en"])
            print(f"📖 English transcript found: {title}")

        raw = transcript.to_raw_data()
        full_text = " ".join([seg["text"] for seg in raw])

        print(f"🔄 Translating: {title}")
        translated_text = translate_text(full_text)
        print(f"✅ Translated: {title}")

        os.makedirs("transcripts", exist_ok=True)
        with open(filename, "w") as f:
            json.dump({
                "video_id": video_id,
                "title": title,
                "published": published,
                "source": "Telugu Sermon",
                "original_language": "Telugu",
                "transcript_text": translated_text
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