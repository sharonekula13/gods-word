import os
import json
import re

def clean_transcript(raw):
    # Join all text segments together
    full_text = " ".join([seg["text"] for seg in raw])
    
    # Remove HTML tags like <i>, <b> etc
    full_text = re.sub(r"<[^>]+>", "", full_text)
    
    # Remove noise like [Music], [Applause]
    full_text = re.sub(r"\[.*?\]", "", full_text)
    
    # Fix special characters
    full_text = full_text.replace("&amp;", "&")
    full_text = full_text.replace("&#39;", "'")
    
    # Remove extra spaces
    full_text = re.sub(r"\s+", " ", full_text).strip()
    
    return full_text

def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

# Process all transcripts
for fname in os.listdir("transcripts"):
    if fname.endswith(".json"):
        with open(f"transcripts/{fname}") as f:
            data = json.load(f)

        clean = clean_transcript(data["transcript"])
        chunks = chunk_text(clean)

        os.makedirs("processed", exist_ok=True)
        out = {
            "video_id": data["video_id"],
            "title": data["title"],
            "published": data["published"],
            "full_text": clean,
            "chunks": chunks
        }

        with open(f"processed/{data['video_id']}.json", "w") as f:
            json.dump(out, f, indent=2)

        print(f"✅ Processed: {data['title']}")
        print(f"   Total chunks: {len(chunks)}")