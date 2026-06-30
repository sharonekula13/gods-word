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
    verse_chunks, verse_metas = search_collection(collections["bible_verses"], question, n_results=5)
    bp_chunks, bp_metas = search_collection(collections["bible_project"], question)
    sermon_chunks, sermon_metas = search_collection(collections["sermons"], question)

    verse_context = "\n".join([
        meta['reference'] + ": " + chunk[:300]
        for chunk, meta in zip(verse_chunks, verse_metas)
    ])
    bp_context = "\n".join([chunk[:300] for chunk in bp_chunks])
    sermon_context = "\n".join([chunk[:300] for chunk in sermon_chunks])

    if is_factual_question(question):
        system_prompt = (
            "You are Gods Word, a warm and caring Bible assistant.\n\n"
            "The person is asking a factual Bible question. Answer it accurately and completely first, "
            "then add a short warm encouraging note at the end.\n\n"
            "- Give the complete accurate answer\n"
            "- Use simple easy to understand language\n"
            "- After the answer add 1-2 sentences of warm encouragement\n"
            "- NEVER mention Billy Graham by name\n\n"
            "BIBLE PASSAGES:\n" + verse_context
        )
    else:
        system_prompt = (
            "You are Gods Word, a warm and caring Bible assistant that speaks like a compassionate pastor and friend.\n\n"
            "IMPORTANT RULES:\n"
            "- If the person is just greeting you, respond with a short warm friendly greeting only.\n"
            "- Talk like a warm, caring FRIEND who happens to know the Bible deeply\n"
            "- Never sound preachy, formal or like a sermon\n"
            "- Answer ONLY what was asked — use the conversation history for context\n"
            "- Keep the answer to 3-4 sentences maximum\n"
            "- Weave in 1-2 Bible verses naturally like a friend quoting something they love\n"
            "- If you are not sure of the answer, say so honestly rather than guessing\n"
            "- Give the specific name, place or fact asked — be precise\n"
            "- ONLY use the Bible passages provided below for your answer — do not add information from your own knowledge\n"
            "- If the Bible passages don't contain enough information, say so honestly\n"
            "- Do NOT use headers, bullet points, or sections\n"
            "- NEVER offer to pray with the person, call them, or do anything an AI cannot do\n"
            "- If asked about praying together, kindly explain you are an AI but encourage them to pray on their own\n"
            "- If someone asks for a video, just say 'Here are some relevant videos for you' and nothing else\n\n"
            "BIBLE PASSAGES:\n" + verse_context + "\n\n"
            "BIBLE PROJECT CONTENT:\n" + bp_context + "\n\n"
            "SERMON CONTENT:\n" + sermon_context
        )

    # Build messages with full conversation history
    messages = [{"role": "system", "content": system_prompt}]

    # Add last 6 messages for context
    for msg in st.session_state.messages[-6:]:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # Add current question
    messages.append({"role": "user", "content": question})

    response = ollama.chat(
        model="llama3",
        messages=messages
    )
    content = response.message.content
    if not content or content.strip() == "":
        return "I'm here for you! How can I help you today? 🕊️"
    return content