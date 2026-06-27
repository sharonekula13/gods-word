import os
import json
import chromadb
import requests
import time

# All 66 books of the Bible
BOOKS = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
    "Joshua", "Judges", "Ruth", "1Samuel", "2Samuel",
    "1Kings", "2Kings", "1Chronicles", "2Chronicles", "Ezra",
    "Nehemiah", "Esther", "Job", "Psalms", "Proverbs",
    "Ecclesiastes", "SongofSolomon", "Isaiah", "Jeremiah", "Lamentations",
    "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
    "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk",
    "Zephaniah", "Haggai", "Zechariah", "Malachi", "Matthew",
    "Mark", "Luke", "John", "Acts", "Romans",
    "1Corinthians", "2Corinthians", "Galatians", "Ephesians", "Philippians",
    "Colossians", "1Thessalonians", "2Thessalonians", "1Timothy", "2Timothy",
    "Titus", "Philemon", "Hebrews", "James", "1Peter",
    "2Peter", "1John", "2John", "3John", "Jude", "Revelation"
]

# Set up Chroma
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="bible_verses")

print("Loading Bible into Chroma...")

for book_name in BOOKS:
    url = f"https://raw.githubusercontent.com/aruljohn/Bible-kjv/master/{book_name}.json"
    response = requests.get(url)
    book = response.json()

    for chapter in book["chapters"]:
        chapter_num = chapter["chapter"]
        for verse in chapter["verses"]:
            verse_num = verse["verse"]
            verse_text = verse["text"]
            verse_id = f"{book_name}_{chapter_num}_{verse_num}"
            reference = f"{book_name} {chapter_num}:{verse_num}"

            collection.add(
                documents=[verse_text],
                metadatas=[{
                    "book": book_name,
                    "chapter": int(chapter_num),
                    "verse": int(verse_num),
                    "reference": reference,
                    "source": "KJV Bible"
                }],
                ids=[verse_id]
            )

    print(f"✅ Loaded: {book_name}")
    time.sleep(0.5)

print(f"\nTotal verses in Chroma: {collection.count()}")