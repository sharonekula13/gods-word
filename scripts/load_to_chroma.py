import os
import json
import chromadb

# Set up Chroma client — saves locally in a chroma_db folder
client = chromadb.PersistentClient(path="chroma_db")

# Create a collection called "sermons"
collection = client.get_or_create_collection(name="sermons")

# Load all processed transcripts
for fname in os.listdir("processed"):
    if fname.endswith(".json"):
        with open(f"processed/{fname}") as f:
            data = json.load(f)

        video_id = data["video_id"]
        title = data["title"]
        chunks = data["chunks"]

        # Add each chunk to Chroma
        collection.add(
            documents=chunks,
            metadatas=[{"video_id": video_id, "title": title} for _ in chunks],
            ids=[f"{video_id}_chunk_{i}" for i in range(len(chunks))]
        )

        print(f"✅ Loaded: {title}")
        print(f"   Chunks added: {len(chunks)}")

print(f"\nTotal documents in Chroma: {collection.count()}")