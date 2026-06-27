import os
import chromadb
import ollama
from dotenv import load_dotenv

load_dotenv()

# Set up Chroma
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="sermons")

def search_sermons(query, n_results=5):
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    return results["documents"][0], results["metadatas"][0]

def ask_billy_graham(question):
    # Search for relevant sermon chunks
    chunks, metadatas = search_sermons(question)

    # Build context from chunks
    context = "\n\n".join([
        f"From sermon '{meta['title']}':\n{chunk}"
        for chunk, meta in zip(chunks, metadatas)
    ])

    # Build prompt
    prompt = f"""You are a helpful assistant that answers questions based on 
Billy Graham's sermons. Use ONLY the sermon excerpts below to answer the question.
If the answer is not in the excerpts, say "I couldn't find that in Billy Graham's sermons."

Sermon excerpts:
{context}

Question: {question}

Answer:"""

    response = ollama.chat(
        model="llama3",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]

if __name__ == "__main__":
    print("🕊️  Gods Word Chatbot — Ask anything about Billy Graham's sermons!")
    print("Type 'quit' to exit\n")

    while True:
        question = input("You: ")
        if question.lower() == "quit":
            break
        answer = ask_billy_graham(question)
        print(f"\nGods Word: {answer}\n")