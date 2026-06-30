import os
import json
import random
import streamlit as st
import chromadb
import ollama
from dotenv import load_dotenv
from datetime import date, datetime

load_dotenv()

# ============================================================
# THEME — single harmonious navy/parchment family, one accent
# ============================================================
THEMES = {
    "dark": {
        "bg": "#0d1321",
        "bg_gradient_end": "#10182a",
        "sidebar": "#0f1626",
        "card": "#161f33",
        "card2": "#1a2438",
        "border": "#26314a",
        "text": "#eef0f3",
        "subtext": "#8b93a7",
        "accent": "#d4af6a",
        "accent_soft": "rgba(212, 175, 106, 0.12)",
        "bot_bubble": "#161f33",
        "user_bubble": "#1c2942",
        "shadow": "rgba(0, 0, 0, 0.35)",
    },
    "light": {
        "bg": "#faf6ee",
        "bg_gradient_end": "#f3ecdd",
        "sidebar": "#f3ecdc",
        "card": "#fffdf8",
        "card2": "#f6efe0",
        "border": "#e3d8bf",
        "text": "#2c2417",
        "subtext": "#7a6f5c",
        "accent": "#9c7a2e",
        "accent_soft": "rgba(156, 122, 46, 0.10)",
        "bot_bubble": "#fffdf8",
        "user_bubble": "#f0e6cd",
        "shadow": "rgba(120, 100, 60, 0.15)",
    }
}

st.set_page_config(page_title="Gods Word", page_icon="🕊️", layout="wide")

# ============================================================
# SESSION STATE
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_journal" not in st.session_state:
    st.session_state.show_journal = False
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

FAVOURITES_FILE = "favourites.json"
JOURNAL_FILE = "prayer_journal.json"

def load_json_file(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_json_file(path, data):
    with open(path, "w") as f:
        json.dump(data, f)

if "favourites" not in st.session_state:
    st.session_state.favourites = load_json_file(FAVOURITES_FILE)
if "journal" not in st.session_state:
    st.session_state.journal = load_json_file(JOURNAL_FILE)

t = THEMES[st.session_state.theme]

# ============================================================
# STYLES
# ============================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600;1,400&family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp {
        background: linear-gradient(180deg, """ + t["bg"] + """ 0%, """ + t["bg_gradient_end"] + """ 100%);
        color: """ + t["text"] + """;
    }
    header[data-testid="stHeader"] { background-color: transparent !important; }
    [data-testid="stBottomBlockContainer"], .stBottomBlockContainer, .stChatFloatingInputContainer, footer {
        background: transparent !important;
    }

    .block-container { padding-top: 2.5rem !important; padding-bottom: 7rem !important; max-width: 900px; }
    section[data-testid="stSidebar"] {
        background-color: """ + t["sidebar"] + """;
        border-right: 1px solid """ + t["border"] + """;
    }
    section[data-testid="stSidebar"] * { font-family: 'Inter', sans-serif; }

    /* ---------- Header ---------- */
    @keyframes gentle-glow {
        0%, 100% { filter: drop-shadow(0 0 4px """ + t["accent_soft"] + """); }
        50% { filter: drop-shadow(0 0 14px """ + t["accent_soft"] + """); }
    }
    @keyframes fade-up {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .gw-header { text-align: center; animation: fade-up 0.6s ease-out; margin-bottom: 0.25rem; }
    .gw-dove { font-size: 2.4rem; animation: gentle-glow 4s ease-in-out infinite; display: inline-block; }
    .gw-title {
        font-family: 'Lora', serif;
        font-weight: 600;
        font-size: 2.6rem;
        color: """ + t["text"] + """;
        letter-spacing: 0.5px;
        margin: 0.3rem 0 0.1rem 0;
    }
    .gw-subtitle {
        color: """ + t["subtext"] + """;
        font-size: 0.95rem;
        letter-spacing: 0.3px;
        margin-bottom: 1.6rem;
    }
    .gw-rule {
        width: 64px; height: 2px; margin: 0 auto 2rem auto;
        background: linear-gradient(90deg, transparent, """ + t["accent"] + """, transparent);
        opacity: 0.6;
    }

    /* ---------- Verse of the day card ---------- */
    @keyframes card-in {
        from { opacity: 0; transform: translateY(14px) scale(0.99); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }
    .verse-card {
        background: linear-gradient(150deg, """ + t["card"] + """ 0%, """ + t["card2"] + """ 100%);
        border: 1px solid """ + t["border"] + """;
        border-left: 3px solid """ + t["accent"] + """;
        border-radius: 18px;
        padding: 2rem 2.4rem;
        text-align: center;
        box-shadow: 0 8px 30px """ + t["shadow"] + """;
        animation: card-in 0.7s cubic-bezier(0.22, 1, 0.36, 1);
        margin-bottom: 1.4rem;
        position: relative;
        overflow: hidden;
    }
    .verse-card::before {
        content: "";
        position: absolute; top: -40%; right: -10%;
        width: 220px; height: 220px; border-radius: 50%;
        background: radial-gradient(circle, """ + t["accent_soft"] + """ 0%, transparent 70%);
        pointer-events: none;
    }
    .verse-eyebrow {
        color: """ + t["accent"] + """;
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 0.9rem;
        font-weight: 600;
    }
    .verse-text {
        font-family: 'Lora', serif;
        font-style: italic;
        font-size: 1.25rem;
        line-height: 1.65;
        color: """ + t["text"] + """;
        margin: 0 0 1rem 0;
        position: relative;
    }
    .verse-divider {
        width: 36px; height: 1.5px; margin: 0 auto 0.8rem auto;
        background-color: """ + t["accent"] + """; opacity: 0.55;
    }
    .verse-ref { color: """ + t["accent"] + """; font-weight: 600; font-size: 0.92rem; letter-spacing: 0.3px; }

    /* ---------- Buttons ---------- */
    .stButton button {
        background-color: transparent !important;
        color: """ + t["accent"] + """ !important;
        border: 1.5px solid """ + t["accent"] + """ !important;
        border-radius: 999px !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        padding: 0.45rem 1.3rem !important;
        transition: all 0.25s ease !important;
        box-shadow: none !important;
    }
    .stButton button:hover {
        background-color: """ + t["accent"] + """ !important;
        color: """ + t["bg"] + """ !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 14px """ + t["accent_soft"] + """ !important;
    }
    .stButton button:active { transform: translateY(0); }

    /* ---------- Chat bubbles ---------- */
    @keyframes msg-in {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .chat-row { display: flex; margin: 14px 0; animation: msg-in 0.35s ease-out; }
    .chat-row.user { justify-content: flex-end; }
    .chat-row.bot { justify-content: flex-start; }
    .bubble {
        max-width: 72%;
        padding: 14px 18px;
        border-radius: 18px;
        line-height: 1.55;
        font-size: 0.97rem;
        box-shadow: 0 2px 10px """ + t["shadow"] + """;
    }
    .bubble.user {
        background-color: """ + t["user_bubble"] + """;
        border: 1px solid """ + t["border"] + """;
        border-bottom-right-radius: 6px;
        color: """ + t["text"] + """;
    }
    .bubble.bot {
        background-color: """ + t["bot_bubble"] + """;
        border: 1px solid """ + t["border"] + """;
        border-left: 2.5px solid """ + t["accent"] + """;
        border-bottom-left-radius: 6px;
        color: """ + t["text"] + """;
    }
    .bubble-time {
        font-size: 0.68rem;
        color: """ + t["subtext"] + """;
        margin-top: 6px;
        opacity: 0.8;
    }

    /* ---------- Loading (breathing dove) ---------- */
    @keyframes breathe {
        0%, 100% { transform: scale(1); opacity: 0.55; }
        50% { transform: scale(1.18); opacity: 1; }
    }
    .dove-loading-wrap { text-align: center; padding: 18px 0; }
    .dove-loading { font-size: 1.8rem; display: inline-block; animation: breathe 1.4s ease-in-out infinite; }
    .dove-loading-text { color: """ + t["subtext"] + """; font-size: 0.85rem; margin-top: 6px; letter-spacing: 0.3px; }

    /* ---------- Video links ---------- */
    .video-card {
        background-color: """ + t["card"] + """;
        border: 1px solid """ + t["border"] + """;
        border-radius: 12px;
        padding: 12px 16px;
        margin: 6px 0;
        transition: border-color 0.2s ease;
    }
    .video-card:hover { border-color: """ + t["accent"] + """; }
    .video-card a { color: """ + t["accent"] + """ !important; text-decoration: none !important; font-size: 0.9rem; }

    /* ---------- Sidebar cards ---------- */
    .side-card {
        background-color: """ + t["card"] + """;
        border: 1px solid """ + t["border"] + """;
        border-radius: 10px;
        padding: 10px 12px;
        margin: 6px 0;
        font-size: 0.82rem;
    }
    .side-eyebrow {
        color: """ + t["accent"] + """;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin: 0 0 10px 0;
    }
    .side-empty { color: """ + t["subtext"] + """; font-size: 0.82rem; font-style: italic; }

    /* ---------- Chat input ---------- */
    .stChatInput {
        position: fixed;
        bottom: 1.6rem;
        left: 50%;
        transform: translateX(-50%);
        width: min(680px, 90%) !important;
    }
    .stChatInput > div {
        background-color: """ + t["card"] + """ !important;
        border: 1.5px solid """ + t["border"] + """ !important;
        border-radius: 28px !important;
        box-shadow: 0 10px 35px """ + t["shadow"] + """ !important;
        transition: border-color 0.25s ease !important;
    }
    .stChatInput > div:focus-within {
        border-color: """ + t["accent"] + """ !important;
    }
    .stChatInput textarea {
        color: """ + t["text"] + """ !important;
        font-size: 0.95rem !important;
    }
    .stChatInput textarea::placeholder { color: """ + t["subtext"] + """ !important; }

    div[data-baseweb="select"] > div {
        background-color: """ + t["card"] + """ !important;
        border-color: """ + t["border"] + """ !important;
        color: """ + t["text"] + """ !important;
        border-radius: 10px !important;
    }
    .stTextArea textarea {
        background-color: """ + t["card"] + """ !important;
        color: """ + t["text"] + """ !important;
        border: 1px solid """ + t["border"] + """ !important;
        border-radius: 12px !important;
    }
    hr { border-color: """ + t["border"] + """ !important; opacity: 0.6; }
    </style>
""", unsafe_allow_html=True)

# ============================================================
# DATA LAYER
# ============================================================
@st.cache_resource
def load_collections():
    client = chromadb.PersistentClient(path="chroma_db")
    return {
        "sermons": client.get_or_create_collection(name="sermons"),
        "bible_verses": client.get_or_create_collection(name="bible_verses"),
        "bible_project": client.get_or_create_collection(name="bible_project")
    }

collections = load_collections()

def search_collection(collection, query, n_results=2):
    results = collection.query(query_texts=[query], n_results=n_results)
    return results["documents"][0], results["metadatas"][0]

def is_factual_question(question):
    factual_keywords = [
        "what are", "list", "how many", "name the", "what is the",
        "commandments", "beatitudes", "fruits of the spirit",
        "apostles", "disciples", "psalms", "proverbs"
    ]
    return any(k in question.lower() for k in factual_keywords)

def get_relevant_video(question):
    sermon_results = collections["sermons"].query(query_texts=[question], n_results=1)
    bp_results = collections["bible_project"].query(query_texts=[question], n_results=1)
    videos = []
    if sermon_results["metadatas"][0]:
        m = sermon_results["metadatas"][0][0]
        vid = m.get("video_id", "")
        if vid:
            videos.append({"title": m.get("title", ""), "url": "https://www.youtube.com/watch?v=" + vid, "source": "Billy Graham"})
    if bp_results["metadatas"][0]:
        m = bp_results["metadatas"][0][0]
        vid = m.get("video_id", "")
        if vid:
            videos.append({"title": m.get("title", ""), "url": "https://www.youtube.com/watch?v=" + vid, "source": "Bible Project"})
    return videos

def ask_gods_word(question):
    recent_context = " ".join([m["content"] for m in st.session_state.messages[-4:] if m["role"] == "user"])
    search_query = recent_context + " " + question

    verse_chunks, verse_metas = search_collection(collections["bible_verses"], search_query, n_results=5)
    bp_chunks, bp_metas = search_collection(collections["bible_project"], search_query)
    sermon_chunks, sermon_metas = search_collection(collections["sermons"], search_query)

    verse_context = "\n".join([m['reference'] + ": " + c[:300] for c, m in zip(verse_chunks, verse_metas)])
    bp_context = "\n".join([c[:300] for c in bp_chunks])
    sermon_context = "\n".join([c[:300] for c in sermon_chunks])

    if is_factual_question(question):
        system_prompt = (
            "You are Gods Word, a warm and caring Bible assistant.\n\n"
            "The person is asking a factual Bible question. Answer it accurately and completely first, "
            "then add a short warm encouraging note at the end.\n\n"
            "- Give the complete accurate answer\n"
            "- Use simple easy to understand language\n"
            "- After the answer add 1-2 sentences of warm encouragement\n"
            "- ONLY use the Bible passages provided below for your answer — do not add information from your own knowledge\n"
            "- If the Bible passages don't contain enough information, say so honestly\n"
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
            "- ONLY use the Bible passages provided below for your answer — do not add information from your own knowledge\n"
            "- If the Bible passages don't contain enough information, say so honestly rather than guessing\n"
            "- Give the specific name, place or fact asked — be precise\n"
            "- Do NOT use headers, bullet points, or sections\n"
            "- NEVER offer to pray with the person, call them, or do anything an AI cannot do\n"
            "- If asked about praying together, kindly explain you are an AI but encourage them to pray on their own\n"
            "- If someone asks for a video, just say 'Here are some relevant videos for you' and nothing else\n\n"
            "BIBLE PASSAGES:\n" + verse_context + "\n\n"
            "BIBLE PROJECT CONTENT:\n" + bp_context + "\n\n"
            "SERMON CONTENT:\n" + sermon_context
        )

    messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.messages[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})

    response = ollama.chat(model="llama3", messages=messages)
    content = response.message.content
    if not content or content.strip() == "":
        return "I'm here for you! How can I help you today? 🕊️"
    return content

@st.cache_data
def get_verse_of_the_day(today_date):
    popular_verses = [
        ("John 3:16", "For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life."),
        ("Jeremiah 29:11", "For I know the thoughts that I think toward you, saith the LORD, thoughts of peace, and not of evil, to give you an expected end."),
        ("Philippians 4:13", "I can do all things through Christ which strengtheneth me."),
        ("Psalm 23:1", "The LORD is my shepherd; I shall not want."),
        ("Romans 8:28", "And we know that all things work together for good to them that love God."),
        ("Isaiah 40:31", "But they that wait upon the LORD shall renew their strength; they shall mount up with wings as eagles."),
        ("Proverbs 3:5", "Trust in the LORD with all thine heart; and lean not unto thine own understanding."),
        ("Matthew 11:28", "Come unto me, all ye that labour and are heavy laden, and I will give you rest."),
        ("Psalm 46:1", "God is our refuge and strength, a very present help in trouble."),
        ("Joshua 1:9", "Be strong and courageous. Do not be afraid; do not be discouraged, for the LORD your God will be with you wherever you go."),
        ("Romans 15:13", "Now the God of hope fill you with all joy and peace in believing."),
        ("Psalm 119:105", "Thy word is a lamp unto my feet, and a light unto my path."),
        ("Philippians 4:6", "Be careful for nothing; but in every thing by prayer and supplication with thanksgiving let your requests be made known unto God."),
        ("2 Timothy 1:7", "For God hath not given us the spirit of fear; but of power, and of love, and of a sound mind."),
        ("Psalm 34:18", "The LORD is nigh unto them that are of a broken heart; and saveth such as be of a contrite spirit."),
        ("Isaiah 41:10", "Fear thou not; for I am with thee: be not dismayed; for I am thy God: I will strengthen thee."),
        ("Matthew 6:33", "But seek ye first the kingdom of God, and his righteousness; and all these things shall be added unto you."),
        ("Psalm 37:4", "Delight thyself also in the LORD: and he shall give thee the desires of thine heart."),
        ("Romans 8:38-39", "For I am persuaded, that neither death, nor life, nor angels, nor principalities, nor powers, nor things present, nor things to come, shall be able to separate us from the love of God."),
        ("Lamentations 3:22-23", "It is of the LORD's mercies that we are not consumed, because his compassions fail not. They are new every morning: great is thy faithfulness."),
        ("Proverbs 31:25", "Strength and honour are her clothing; and she shall rejoice in time to come."),
        ("John 14:6", "Jesus saith unto him, I am the way, the truth, and the life: no man cometh unto the Father, but by me."),
        ("Psalm 139:14", "I will praise thee; for I am fearfully and wonderfully made: marvellous are thy works."),
        ("Matthew 5:16", "Let your light so shine before men, that they may see your good works, and glorify your Father which is in heaven."),
        ("Romans 12:2", "And be not conformed to this world: but be ye transformed by the renewing of your mind."),
        ("1 Corinthians 13:4", "Charity suffereth long, and is kind; charity envieth not; charity vaunteth not itself, is not puffed up."),
        ("Ephesians 2:8", "For by grace are ye saved through faith; and that not of yourselves: it is the gift of God."),
        ("Galatians 5:22-23", "But the fruit of the Spirit is love, joy, peace, longsuffering, gentleness, goodness, faith, meekness, temperance: against such there is no law."),
        ("Hebrews 11:1", "Now faith is the substance of things hoped for, the evidence of things not seen."),
        ("James 1:17", "Every good gift and every perfect gift is from above, and cometh down from the Father of lights."),
        ("1 John 4:19", "We love him, because he first loved us."),
        ("Psalm 51:10", "Create in me a clean heart, O God; and renew a right spirit within me."),
        ("John 16:33", "These things I have spoken unto you, that in me ye might have peace. In the world ye shall have tribulation: but be of good cheer; I have overcome the world."),
        ("Romans 5:8", "But God commendeth his love toward us, in that, while we were yet sinners, Christ died for us."),
        ("Proverbs 16:3", "Commit thy works unto the LORD, and thy thoughts shall be established."),
        ("Isaiah 26:3", "Thou wilt keep him in perfect peace, whose mind is stayed on thee: because he trusteth in thee."),
        ("Matthew 28:20", "Teaching them to observe all things whatsoever I have commanded you: and, lo, I am with you always, even unto the end of the world."),
        ("Psalm 27:1", "The LORD is my light and my salvation; whom shall I fear? the LORD is the strength of my life; of whom shall I be afraid?"),
        ("Colossians 3:23", "And whatsoever ye do, do it heartily, as to the Lord, and not unto men."),
        ("1 Peter 5:7", "Casting all your care upon him; for he careth for you."),
        ("Proverbs 4:23", "Keep thy heart with all diligence; for out of it are the issues of life."),
        ("Psalm 91:1", "He that dwelleth in the secret place of the most High shall abide under the shadow of the Almighty."),
        ("John 15:5", "I am the vine, ye are the branches: He that abideth in me, and I in him, the same bringeth forth much fruit: for without me ye can do nothing."),
        ("Isaiah 43:2", "When thou passest through the waters, I will be with thee; and through the rivers, they shall not overflow thee."),
        ("Psalm 143:8", "Cause me to hear thy lovingkindness in the morning; for in thee do I trust: cause me to know the way wherein I should walk."),
        ("Romans 8:1", "There is therefore now no condemnation to them which are in Christ Jesus, who walk not after the flesh, but after the Spirit."),
        ("Ephesians 3:20", "Now unto him that is able to do exceeding abundantly above all that we ask or think, according to the power that worketh in us."),
        ("Psalm 32:8", "I will instruct thee and teach thee in the way which thou shalt go: I will guide thee with mine eye."),
        ("John 10:10", "The thief cometh not, but for to steal, and to kill, and to destroy: I am come that they might have life, and that they might have it more abundantly."),
        ("Hebrews 13:5", "Let your conversation be without covetousness; and be content with such things as ye have: for he hath said, I will never leave thee, nor forsake thee."),
        ("Zephaniah 3:17", "The LORD thy God in the midst of thee is mighty; he will save, he will rejoice over thee with joy; he will rest in his love, he will joy over thee with singing.")
    ]
    random.seed(str(date.today()))
    return random.choice(popular_verses)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("<h2 style='color:" + t["accent"] + "; font-family: Lora, serif; font-weight:600;'>🕊️ Gods Word</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("<p style='color:" + t["subtext"] + "; margin-top:10px; font-size:0.85rem;'>Theme</p>", unsafe_allow_html=True)
    with col2:
        if st.session_state.theme == "dark":
            if st.button("☀️ Light", use_container_width=True):
                st.session_state.theme = "light"; st.rerun()
        else:
            if st.button("🌙 Dark", use_container_width=True):
                st.session_state.theme = "dark"; st.rerun()

    st.divider()
    st.markdown("<p class='side-eyebrow'>Chat History</p>", unsafe_allow_html=True)
    if len(st.session_state.messages) == 0:
        st.markdown("<p class='side-empty'>No conversations yet. Ask something!</p>", unsafe_allow_html=True)
    else:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown("<div class='side-card'>🙏 " + message['content'][:50] + "...</div>", unsafe_allow_html=True)

    st.divider()
    st.markdown("<p class='side-eyebrow'>📖 Browse by Topic</p>", unsafe_allow_html=True)
    topics = {
        "Hope": "hope trust God future", "Fear & Anxiety": "fear anxiety worry peace",
        "Love": "love God love others", "Forgiveness": "forgiveness sin grace mercy",
        "Strength": "strength courage power weakness", "Prayer": "prayer seek God communicate",
        "Faith": "faith believe trust God", "Grief & Loss": "grief loss sorrow comfort",
        "Anger": "anger wrath patience kindness", "Purpose": "purpose calling destiny meaning",
        "Marriage": "marriage husband wife love", "Money": "money wealth greed contentment",
        "Wisdom": "wisdom knowledge understanding", "Salvation": "salvation saved eternal life Jesus",
        "Joy": "joy happiness praise thankfulness"
    }
    selected_topic = st.selectbox("Choose a topic", ["Select a topic..."] + list(topics.keys()), label_visibility="collapsed")
    if selected_topic and selected_topic != "Select a topic...":
        results = collections["bible_verses"].query(query_texts=[topics[selected_topic]], n_results=3)
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            st.markdown(
                "<div class='side-card'><span style='color:" + t["accent"] + "; font-weight:600;'>" + meta['reference'] + "</span>"
                "<br><span style='font-style:italic;'>\"" + doc[:200] + "\"</span></div>",
                unsafe_allow_html=True
            )

    st.divider()
    st.markdown("<p class='side-eyebrow'>⭐ Favourite Verses</p>", unsafe_allow_html=True)
    if len(st.session_state.favourites) == 0:
        st.markdown("<p class='side-empty'>No saved verses yet.</p>", unsafe_allow_html=True)
    else:
        for fav in st.session_state.favourites:
            st.markdown(
                "<div class='side-card'><span style='color:" + t["accent"] + "; font-weight:600;'>" + fav['reference'] + "</span>"
                "<br><span style='font-style:italic;'>\"" + fav['text'][:150] + "\"</span></div>",
                unsafe_allow_html=True
            )
        if st.button("🗑️ Clear Favourites", use_container_width=True):
            st.session_state.favourites = []
            save_json_file(FAVOURITES_FILE, [])
            st.rerun()

    st.divider()
    st.markdown("<p class='side-eyebrow'>📝 Prayer Journal</p>", unsafe_allow_html=True)
    if st.button("✏️ Open Journal", use_container_width=True):
        st.session_state.show_journal = not st.session_state.show_journal
        st.rerun()

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ============================================================
# MAIN
# ============================================================
st.markdown(
    "<div class='gw-header'>"
    "<span class='gw-dove'>🕊️</span>"
    "<div class='gw-title'>Gods Word</div>"
    "<div class='gw-subtitle'>Ask anything about the Bible</div>"
    "</div>"
    "<div class='gw-rule'></div>",
    unsafe_allow_html=True
)

verse_ref, verse_text = get_verse_of_the_day(str(date.today()))
st.markdown(
    "<div class='verse-card'>"
    "<div class='verse-eyebrow'>Verse of the Day</div>"
    "<div class='verse-text'>\u201c" + verse_text + "\u201d</div>"
    "<div class='verse-divider'></div>"
    "<div class='verse-ref'>— " + verse_ref + "</div>"
    "</div>",
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns([3, 1, 3])
with col2:
    if st.button("⭐ Save Verse"):
        fav = {"reference": verse_ref, "text": verse_text}
        if fav not in st.session_state.favourites:
            st.session_state.favourites.append(fav)
            save_json_file(FAVOURITES_FILE, st.session_state.favourites)
            st.success("Verse saved ⭐")
        else:
            st.info("Already saved!")

if st.session_state.show_journal:
    st.markdown("<h3 style='color:" + t["accent"] + "; font-family: Lora, serif;'>📝 Prayer Journal</h3>", unsafe_allow_html=True)
    prayer = st.text_area("Write your prayer...", height=150, placeholder="Dear God...", label_visibility="collapsed")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("💾 Save Prayer", use_container_width=True):
            if prayer.strip():
                st.session_state.journal.append({"date": str(date.today()), "prayer": prayer})
                save_json_file(JOURNAL_FILE, st.session_state.journal)
                st.success("Prayer saved 🙏")
    with col2:
        if st.button("❌ Close Journal", use_container_width=True):
            st.session_state.show_journal = False
            st.rerun()

    if len(st.session_state.journal) > 0:
        st.markdown("<p style='color:" + t["subtext"] + "; margin-top:15px;'>Past Prayers</p>", unsafe_allow_html=True)
        for entry in reversed(st.session_state.journal[-5:]):
            st.markdown(
                "<div class='side-card' style='font-size:0.9rem;'>"
                "<span style='color:" + t["accent"] + "; font-size:0.78rem;'>📅 " + entry['date'] + "</span><br>"
                + entry['prayer'] + "</div>",
                unsafe_allow_html=True
            )
    st.divider()

# Chat history
for message in st.session_state.messages:
    role = message["role"]
    icon = "🙏" if role == "user" else "🕊️"
    css_role = "user" if role == "user" else "bot"
    st.markdown(
        "<div class='chat-row " + css_role + "'>"
        "<div class='bubble " + css_role + "'>"
        "<div>" + icon + " " + message['content'] + "</div>"
        "<div class='bubble-time'>" + message.get('time', '') + "</div>"
        "</div></div>",
        unsafe_allow_html=True
    )

question = st.chat_input("Ask anything about the Bible...")

if question:
    now = datetime.now().strftime("%I:%M %p")
    st.session_state.messages.append({"role": "user", "content": question, "time": now})
    st.markdown(
        "<div class='chat-row user'><div class='bubble user'>"
        "<div>🙏 " + question + "</div><div class='bubble-time'>" + now + "</div>"
        "</div></div>",
        unsafe_allow_html=True
    )

    video_keywords = ["video", "watch", "youtube", "sermon video", "show me", "can you show", "link", "where can i watch"]
    wants_video = any(k in question.lower() for k in video_keywords)

    loading_placeholder = st.empty()
    loading_placeholder.markdown(
        "<div class='dove-loading-wrap'>"
        "<div class='dove-loading'>🕊️</div>"
        "<div class='dove-loading-text'>Searching God's Word...</div>"
        "</div>",
        unsafe_allow_html=True
    )

    answer = ask_gods_word(question)

    if wants_video:
        previous_questions = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
        search_query = " ".join(previous_questions[-2:])
        for word in ["video", "watch", "youtube", "show me", "can you show", "link", "share", "where can i watch", "relevant"]:
            search_query = search_query.replace(word, "")
        videos = get_relevant_video(search_query.strip())
    else:
        videos = []

    loading_placeholder.empty()

    answer_time = datetime.now().strftime("%I:%M %p")
    st.session_state.messages.append({"role": "assistant", "content": answer, "time": answer_time})
    st.markdown(
        "<div class='chat-row bot'><div class='bubble bot'>"
        "<div>🕊️ " + answer + "</div><div class='bubble-time'>" + answer_time + "</div>"
        "</div></div>",
        unsafe_allow_html=True
    )

    if videos:
        for video in videos:
            st.markdown(
                "<div class='video-card'>▶️ <a href='" + video['url'] + "' target='_blank'>"
                + video['source'] + ": " + video['title'] + "</a></div>",
                unsafe_allow_html=True
            )