import os
import json
import chromadb

# Set up Chroma
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="bible_project")

# Load all Bible Project transcripts
for fname in os.listdir("transcripts"):
    if fname.startswith("bibleproject_") and fname.endswith(".json"):
        with open(f"transcripts/{fname}") as f:
            data = json.load(f)

        video_id = data["video_id"]
        title = data["title"]

        # Clean and chunk
        full_text = " ".join([seg["text"] for seg in data["transcript"]])
        words = full_text.split()
        chunks = []
        for i in range(0, len(words), 450):
            chunk = " ".join(words[i:i + 500])
            chunks.append(chunk)

        collection.add(
            documents=chunks,
            metadatas=[{"video_id": video_id, "title": title, "source": "Bible Project"} for _ in chunks],
            ids=[f"bp_{video_id}_chunk_{i}" for i in range(len(chunks))]
        )

        print(f"✅ Loaded: {title} ({len(chunks)} chunks)")

print(f"\nTotal Bible Project chunks in Chroma: {collection.count()}")