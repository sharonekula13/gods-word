import os
import chromadb
import ollama
from dotenv import load_dotenv

load_dotenv()

# Set up Chroma collections
client = chromadb.PersistentClient(path="chroma_db")
sermons = client.get_or_create_collection(name="sermons")
bible_verses = client.get_or_create_collection(name="bible_verses")
bible_project = client.get_or_create_collection(name="bible_project")

def search_collection(collection, query, n_results=2):
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results["documents"][0], results["metadatas"][0]

def is_factual_question(question):
    factual_keywords = [
        "what are", "list", "how many", "name the", "what is the",
        "commandments", "beatitudes", "fruits of the spirit",
        "apostles", "disciples", "psalms", "proverbs"
    ]
    question_lower = question.lower()
    return any(keyword in question_lower for keyword in factual_keywords)

def ask_gods_word(question):
    verse_chunks, verse_metas = search_collection(bible_verses, question)
    bp_chunks, bp_metas = search_collection(bible_project, question)
    sermon_chunks, sermon_metas = search_collection(sermons, question)

    verse_context = "\n".join([
        f"{meta['reference']}: {chunk[:300]}"
        for chunk, meta in zip(verse_chunks, verse_metas)
    ])

    bp_context = "\n".join([
        f"{chunk[:300]}"
        for chunk in bp_chunks
    ])

    sermon_context = "\n".join([
        f"{chunk[:300]}"
        for chunk in sermon_chunks
    ])

    if is_factual_question(question):
        prompt = (
            "You are Gods Word, a warm and caring Bible assistant.\n\n"
            "The person is asking a factual Bible question. Answer it accurately and completely first, "
            "then add a short warm encouraging note at the end.\n\n"
            "- Give the complete accurate answer (e.g. list all 10 commandments if asked)\n"
            "- Use simple easy to understand language\n"
            "- After the answer add 1-2 sentences of warm encouragement\n"
            "- NEVER mention Billy Graham by name\n\n"
            "BIBLE PASSAGES:\n" + verse_context + "\n\n"
            "Person asked: " + question + "\n\n"
            "Response:"
        )
    else:
        prompt = (
            "You are Gods Word, a warm and caring Bible assistant that speaks like a compassionate pastor and friend.\n\n"
            "IMPORTANT RULES:\n"
            "- If the person is just greeting you (like 'hey', 'hello', 'hi'), respond with a short warm friendly greeting back. Don't give Bible verses for greetings.\n"
            "- For all other questions, answer in a single flowing paragraph of 6-8 sentences\n"
            "- Naturally weave in 2-3 relevant Bible verses with their references in quotes\n"
            "- Include a simple explanation of what those verses mean\n"
            "- End with practical encouragement for daily life\n"
            "- NEVER mention Billy Graham by name\n"
            "- Sound like a wise, caring friend — warm, personal, encouraging\n"
            "- Do NOT use headers, bullet points, or sections\n\n"
            "BIBLE PASSAGES:\n" + verse_context + "\n\n"
            "BIBLE PROJECT CONTENT:\n" + bp_context + "\n\n"
            "SERMON CONTENT:\n" + sermon_context + "\n\n"
            "Person said: " + question + "\n\n"
            "Response:"
        )

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.message.content
    if not content or content.strip() == "":
        return "I'm here for you! How can I help you today? 🕊️"
    return content

if __name__ == "__main__":
    print("🕊️  Gods Word — Ask anything about the Bible!")
    print("Type 'quit' to exit\n")

    while True:
        question = input("You: ")
        if question.lower() == "quit":
            break
        print("\nSearching God's Word...\n")
        answer = ask_gods_word(question)
        print(f"{answer}\n")
        print("-" * 60 + "\n")