import os
import json
import random
import streamlit as st
import chromadb
import ollama
from dotenv import load_dotenv
from datetime import date, datetime

load_dotenv()

THEMES = {
    "dark": {
        "bg": "#0d1321",
        "bg2": "#101828",
        "sidebar": "#0f1626",
        "card": "#161f33",
        "card2": "#1a2438",
        "border": "#232f47",
        "text": "#eef0f3",
        "subtext": "#8b93a7",
        "muted": "#4a5568",
        "accent": "#c4974a",
        "accent_soft": "rgba(196,151,74,0.10)",
        "accent_glow": "rgba(196,151,74,0.07)",
        "bot_bubble": "#161f33",
        "user_bubble": "#1c2942",
        "shadow": "rgba(0,0,0,0.4)",
    },
    "light": {
        "bg": "#faf6ee",
        "bg2": "#f5ede0",
        "sidebar": "#f3ead8",
        "card": "#fffdf8",
        "card2": "#f6efe0",
        "border": "#e3d5bc",
        "text": "#1e1a14",
        "subtext": "#6b5f4a",
        "muted": "#a89880",
        "accent": "#9c7230",
        "accent_soft": "rgba(156,114,48,0.10)",
        "accent_glow": "rgba(156,114,48,0.05)",
        "bot_bubble": "#fffdf8",
        "user_bubble": "#ede5d0",
        "shadow": "rgba(120,90,40,0.12)",
    }
}

st.set_page_config(page_title="Gods Word", page_icon="🕊️", layout="wide")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_journal" not in st.session_state:
    st.session_state.show_journal = False
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

FAVOURITES_FILE = "favourites.json"
JOURNAL_FILE = "prayer_journal.json"
USER_NAME_FILE = "user_name.json"

def load_json(path):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return []

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f)

if "favourites" not in st.session_state:
    st.session_state.favourites = load_json(FAVOURITES_FILE)
if "journal" not in st.session_state:
    st.session_state.journal = load_json(JOURNAL_FILE)
if "user_name" not in st.session_state:
    name_data = load_json(USER_NAME_FILE)
    st.session_state.user_name = name_data.get("name", "") if isinstance(name_data, dict) else ""

t = THEMES[st.session_state.theme]

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,500;0,600;1,400&family=Inter:wght@300;400;500;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background: """ + t["bg"] + """; color: """ + t["text"] + """; }
    header[data-testid="stHeader"] { background: """ + t["bg"] + """ !important; }
    footer { background: """ + t["bg"] + """ !important; }
    .block-container { padding-top: 2rem !important; padding-bottom: 7rem !important; max-width: 860px; padding-left: 2rem !important; padding-right: 2rem !important; }
    section[data-testid="stSidebar"] { background: """ + t["sidebar"] + """ !important; border-right: 0.5px solid """ + t["border"] + """; }

    /* Bottom bar */
    [data-testid="stBottom"] { background: """ + t["bg"] + """ !important; }
    [data-testid="stBottom"] > div { background: """ + t["bg"] + """ !important; }
    [data-testid="stBottomBlockContainer"] { background: """ + t["bg"] + """ !important; }
    .stBottomBlockContainer { background: """ + t["bg"] + """ !important; }
    .stBottomBlockContainer > div { background: """ + t["bg"] + """ !important; }
    .stChatFloatingInputContainer { background: """ + t["bg"] + """ !important; }

    /* Chat input */
    .stChatInput { background: """ + t["bg"] + """ !important; position: fixed; bottom: 1.4rem; left: 50%; transform: translateX(-50%); width: min(660px, 88%) !important; }
    .stChatInput > div { background: """ + t["card"] + """ !important; border: 1px solid """ + t["border"] + """ !important; border-radius: 28px !important; box-shadow: 0 4px 20px """ + t["shadow"] + """ !important; transition: border-color 0.25s !important; }
    .stChatInput > div:focus-within { border-color: """ + t["accent"] + """80 !important; }
    .stChatInput > div > div { background: """ + t["card"] + """ !important; border-radius: 28px !important; }
    [data-baseweb="textarea"] { background: """ + t["card"] + """ !important; border-radius: 28px !important; }
    [data-baseweb="base-input"] { background: """ + t["card"] + """ !important; }
    [data-baseweb="base-input"] > textarea { background: """ + t["card"] + """ !important; color: """ + t["text"] + """ !important; }
    .stChatInput textarea { color: """ + t["text"] + """ !important; font-size: 0.9rem !important; font-family: 'Inter', sans-serif !important; background: """ + t["card"] + """ !important; }
    .stChatInput textarea::placeholder { color:""" + t["muted"] + """ !important; }

    /* Animations */
    @keyframes dove-glow {
        0%,100% { filter: drop-shadow(0 0 6px """ + t["accent_soft"] + """); }
        50% { filter: drop-shadow(0 0 18px """ + t["accent_soft"] + """); }
    }
    @keyframes fade-up { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }
    @keyframes card-in { from { opacity:0; transform:translateY(10px) scale(0.99); } to { opacity:1; transform:translateY(0) scale(1); } }
    @keyframes msg-in { from { opacity:0; transform:translateY(6px); } to { opacity:1; transform:translateY(0); } }
    @keyframes breathe { 0%,100% { transform:scale(1); opacity:0.5; } 50% { transform:scale(1.2); opacity:1; } }

    /* Header */
    .gw-header { text-align:center; animation: fade-up 0.6s ease-out; padding-bottom: 0.5rem; }
    .gw-dove { font-size:2.2rem; animation: dove-glow 4s ease-in-out infinite; display:inline-block; }
    .gw-title { font-family:'Lora',serif; font-weight:600; font-size:2.4rem; color:""" + t["text"] + """; letter-spacing:0.3px; margin:0.25rem 0 0.1rem; }
    .gw-sub { color:""" + t["subtext"] + """; font-size:0.88rem; letter-spacing:0.4px; }
    .gw-rule { width:40px; height:1.5px; margin:0.8rem auto 0; background: linear-gradient(90deg,transparent,""" + t["accent"] + """,transparent); opacity:0.55; }

    /* Welcome screen */
    .welcome-wrap { text-align:center; padding: 5rem 2rem 2rem; animation: fade-up 0.6s ease-out; }
    .welcome-dove { font-size:3rem; animation: dove-glow 4s ease-in-out infinite; display:inline-block; margin-bottom:1rem; }
    .welcome-title { font-family:'Lora',serif; font-size:2.2rem; font-weight:600; color:""" + t["text"] + """; margin-bottom:0.5rem; }
    .welcome-sub { color:""" + t["subtext"] + """; font-size:0.95rem; margin-bottom:2rem; }

    /* Verse card */
    .verse-card { background: """ + t["card"] + """; border: 0.5px solid """ + t["border"] + """; border-radius: 18px; padding: 1.4rem 1.8rem; position: relative; overflow: hidden; animation: card-in 0.7s cubic-bezier(0.22,1,0.36,1); margin-bottom: 0.6rem; }
    .verse-card::before { content:""; position:absolute; top:-50px; right:-30px; width:180px; height:180px; border-radius:50%; background: radial-gradient(circle, """ + t["accent_glow"] + """ 0%, transparent 70%); pointer-events:none; }
    .verse-card::after { content:""; position:absolute; bottom:-40px; left:-20px; width:120px; height:120px; border-radius:50%; background: radial-gradient(circle, """ + t["accent_glow"] + """ 0%, transparent 70%); pointer-events:none; }
    .vc-badge { display:inline-flex; align-items:center; gap:5px; background: """ + t["accent_soft"] + """; border: 0.5px solid """ + t["accent"] + """40; border-radius: 999px; padding: 3px 11px; font-size: 9px; font-weight:600; letter-spacing:1.8px; text-transform:uppercase; color:""" + t["accent"] + """; margin-bottom: 0.75rem; }
    .vc-text { font-family:'Lora',serif; font-style:italic; font-size:1.1rem; line-height:1.7; color:""" + t["text"] + """; margin-bottom: 0.9rem; }
    .vc-footer { display:flex; align-items:center; justify-content:space-between; }
    .vc-ref { font-size:0.82rem; font-weight:500; color:""" + t["accent"] + """; letter-spacing:0.3px; }

    /* Chat bubbles */
    .msg-row { display:flex; gap:10px; margin:6px 0; animation: msg-in 0.3s ease-out; }
    .msg-row.user { flex-direction:row-reverse; }
    .avatar { width:30px; height:30px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:14px; flex-shrink:0; margin-top:2px; }
    .avatar.bot { background:""" + t["accent_soft"] + """; border: 0.5px solid """ + t["accent"] + """40; }
    .avatar.user { background:""" + t["card2"] + """; border: 0.5px solid """ + t["border"] + """; }
    .msg-body { display:flex; flex-direction:column; max-width:72%; }
    .bubble { padding: 11px 16px; font-size: 0.9rem; line-height: 1.6; border-radius: 16px; border: 0.5px solid """ + t["border"] + """; color: """ + t["text"] + """; }
    .bubble.bot { background:""" + t["bot_bubble"] + """; border-left: 2.5px solid """ + t["accent"] + """; border-bottom-left-radius: 4px; }
    .bubble.user { background:""" + t["user_bubble"] + """; border-bottom-right-radius: 4px; text-align: right; }
    .msg-time { font-size: 0.68rem; color: """ + t["muted"] + """; margin-top: 4px; padding: 0 2px; }
    .msg-row.user .msg-time { text-align:right; }

    /* Video cards */
    .video-card { background: """ + t["card"] + """; border: 0.5px solid """ + t["border"] + """; border-radius: 12px; padding: 10px 14px; margin: 5px 0; transition: border-color 0.2s; }
    .video-card:hover { border-color: """ + t["accent"] + """; }
    .video-card a { color:""" + t["accent"] + """ !important; text-decoration:none !important; font-size:0.85rem; }

    /* Loading */
    .dove-loading-wrap { text-align:center; padding:16px 0; }
    .dove-loading { font-size:1.6rem; display:inline-block; animation:breathe 1.4s ease-in-out infinite; }
    .dove-loading-text { color:""" + t["subtext"] + """; font-size:0.82rem; margin-top:6px; letter-spacing:0.3px; }

    /* Sidebar */
    .sb-logo-wrap { display:flex; align-items:center; gap:10px; padding: 0 4px 4px; }
    .sb-title { font-family:'Lora',serif; font-size:1.05rem; font-weight:600; color:""" + t["text"] + """; }
    .sb-tagline { font-size:0.68rem; color:""" + t["muted"] + """; letter-spacing:0.3px; margin-top:1px; }
    .sb-section { font-size:0.65rem; font-weight:600; letter-spacing:2px; text-transform:uppercase; color:""" + t["muted"] + """; padding: 0 2px; margin-bottom: 8px; }
    .sb-hist-item { display:flex; align-items:center; gap:8px; padding:7px 10px; border-radius:10px; cursor:pointer; transition:background 0.15s; }
    .sb-hist-item:hover { background:""" + t["card"] + """; }
    .sb-hist-dot { width:5px; height:5px; border-radius:50%; background:""" + t["accent"] + """; flex-shrink:0; }
    .sb-hist-text { font-size:0.78rem; color:""" + t["subtext"] + """; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
    .sb-fav-item { padding:9px 11px; background:""" + t["card"] + """; border: 0.5px solid """ + t["border"] + """; border-radius:10px; margin:4px 0; cursor:pointer; transition:border-color 0.15s; }
    .sb-fav-item:hover { border-color:""" + t["accent"] + """; }
    .sb-fav-ref { font-size:0.72rem; font-weight:500; color:""" + t["accent"] + """; margin-bottom:2px; }
    .sb-fav-text { font-size:0.72rem; color:""" + t["muted"] + """; font-style:italic; line-height:1.4; }

    /* Buttons */
    .stButton button { background:transparent !important; color:""" + t["subtext"] + """ !important; border: 0.5px solid """ + t["border"] + """ !important; border-radius:8px !important; font-size:0.78rem !important; font-weight:400 !important; padding: 7px 12px !important; transition:all 0.15s !important; letter-spacing:0.2px !important; white-space:nowrap !important; }
    .stButton button:hover { background:""" + t["card"] + """ !important; color:""" + t["text"] + """ !important; border-color:""" + t["accent"] + """50 !important; transform:none !important; }

    /* Save verse button */
    .save-verse-wrap .stButton button { background: """ + t["accent_soft"] + """ !important; color: """ + t["accent"] + """ !important; border: 0.5px solid """ + t["accent"] + """60 !important; border-radius: 8px !important; font-size: 0.78rem !important; font-weight: 500 !important; padding: 6px 16px !important; white-space: nowrap !important; }
    .save-verse-wrap .stButton button:hover { background: """ + t["accent"] + """20 !important; border-color: """ + t["accent"] + """ !important; }

    /* Welcome begin button */
    .begin-btn .stButton button { background: """ + t["accent"] + """ !important; color: """ + t["bg"] + """ !important; border: none !important; border-radius: 10px !important; font-size: 0.9rem !important; font-weight: 600 !important; padding: 10px 20px !important; }
    .begin-btn .stButton button:hover { opacity: 0.9 !important; transform: translateY(-1px) !important; }

    /* Text input */
    .stTextInput input { background: """ + t["card"] + """ !important; color: """ + t["text"] + """ !important; border: 1px solid """ + t["border"] + """ !important; border-radius: 10px !important; font-size: 0.95rem !important; }
    .stTextInput input:focus { border-color: """ + t["accent"] + """80 !important; }

    div[data-baseweb="select"] > div { background:""" + t["card"] + """ !important; border-color:""" + t["border"] + """ !important; color:""" + t["text"] + """ !important; border-radius:10px !important; }
    .stTextArea textarea { background:""" + t["card"] + """ !important; color:""" + t["text"] + """ !important; border: 0.5px solid """ + t["border"] + """ !important; border-radius:12px !important; }
    hr { border-color:""" + t["border"] + """ !important; opacity:0.6; }
    </style>
""", unsafe_allow_html=True)

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
    factual_keywords = ["what are","list","how many","name the","what is the","commandments","beatitudes","fruits of the spirit","apostles","disciples","psalms","proverbs"]
    return any(k in question.lower() for k in factual_keywords)

def get_relevant_video(question):
    sermon_results = collections["sermons"].query(query_texts=[question], n_results=1)
    bp_results = collections["bible_project"].query(query_texts=[question], n_results=1)
    videos = []
    if sermon_results["metadatas"][0]:
        m = sermon_results["metadatas"][0][0]
        vid = m.get("video_id","")
        if vid:
            videos.append({"title": m.get("title",""), "url": "https://www.youtube.com/watch?v=" + vid, "source": "Billy Graham"})
    if bp_results["metadatas"][0]:
        m = bp_results["metadatas"][0][0]
        vid = m.get("video_id","")
        if vid:
            videos.append({"title": m.get("title",""), "url": "https://www.youtube.com/watch?v=" + vid, "source": "Bible Project"})
    return videos

def ask_gods_word(question):
    recent_context = " ".join([m["content"] for m in st.session_state.messages[-4:] if m["role"] == "user"])
    search_query = recent_context + " " + question
    verse_chunks, verse_metas = search_collection(collections["bible_verses"], search_query, n_results=5)
    bp_chunks, _ = search_collection(collections["bible_project"], search_query)
    sermon_chunks, _ = search_collection(collections["sermons"], search_query)
    verse_context  = "\n".join([m['reference'] + ": " + c[:300] for c, m in zip(verse_chunks, verse_metas)])
    bp_context     = "\n".join([c[:300] for c in bp_chunks])
    sermon_context = "\n".join([c[:300] for c in sermon_chunks])

    user_name = st.session_state.user_name

    if is_factual_question(question):
        system_prompt = (
            "You are Gods Word, a warm and caring Bible assistant.\n\n"
            "Answer the factual Bible question accurately and completely, then add a short warm encouraging note.\n\n"
            "- Give the complete accurate answer\n"
            "- Use simple easy to understand language\n"
            "- Add 1-2 sentences of warm encouragement after\n"
            "- ONLY use the Bible passages provided\n"
            "- NEVER mention Billy Graham by name\n"
            "- The user's name is " + user_name + ". Use their name warmly and naturally\n\n"
            "BIBLE PASSAGES:\n" + verse_context
        )
    else:
        system_prompt = (
            "You are Gods Word, a warm and caring Bible assistant that speaks like a compassionate pastor and friend.\n\n"
            "RULES:\n"
            "- Greetings get a short warm friendly reply only\n"
            "- Talk like a warm caring FRIEND who knows the Bible deeply\n"
            "- Never sound preachy or like a sermon\n"
            "- Answer ONLY what was asked — use conversation history for context\n"
            "- Keep the answer to 3-4 sentences maximum\n"
            "- Weave in 1-2 Bible verses naturally\n"
            "- ONLY use the Bible passages provided\n"
            "- If unsure, say so honestly rather than guessing\n"
            "- Be precise about names, places, and facts\n"
            "- No headers, bullet points, or sections\n"
            "- NEVER offer to pray with the person or do anything an AI cannot do\n"
            "- If someone asks for a video, just say Here are some relevant videos for you\n"
            "- The user's name is " + user_name + ". Use their name warmly and naturally — not every sentence, just occasionally\n"
            "- Never call them friend — always use their actual name\n\n"
            "BIBLE PASSAGES:\n" + verse_context + "\n\nBIBLE PROJECT CONTENT:\n" + bp_context + "\n\nSERMON CONTENT:\n" + sermon_context
        )
    messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.messages[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})
    response = ollama.chat(model="llama3", messages=messages)
    content = response.message.content
    return content if content and content.strip() else "I'm here for you! How can I help you today? 🕊️"

@st.cache_data
def get_verse_of_the_day(today_date):
    popular_verses = [
        ("John 3:16","For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life."),
        ("Jeremiah 29:11","For I know the thoughts that I think toward you, saith the LORD, thoughts of peace, and not of evil, to give you an expected end."),
        ("Philippians 4:13","I can do all things through Christ which strengtheneth me."),
        ("Psalm 23:1","The LORD is my shepherd; I shall not want."),
        ("Romans 8:28","And we know that all things work together for good to them that love God."),
        ("Isaiah 40:31","But they that wait upon the LORD shall renew their strength; they shall mount up with wings as eagles."),
        ("Proverbs 3:5","Trust in the LORD with all thine heart; and lean not unto thine own understanding."),
        ("Matthew 11:28","Come unto me, all ye that labour and are heavy laden, and I will give you rest."),
        ("Psalm 46:1","God is our refuge and strength, a very present help in trouble."),
        ("Joshua 1:9","Be strong and courageous. Do not be afraid; do not be discouraged, for the LORD your God will be with you wherever you go."),
        ("Romans 15:13","Now the God of hope fill you with all joy and peace in believing."),
        ("Psalm 119:105","Thy word is a lamp unto my feet, and a light unto my path."),
        ("Philippians 4:6","Be careful for nothing; but in every thing by prayer and supplication with thanksgiving let your requests be made known unto God."),
        ("2 Timothy 1:7","For God hath not given us the spirit of fear; but of power, and of love, and of a sound mind."),
        ("Psalm 34:18","The LORD is nigh unto them that are of a broken heart; and saveth such as be of a contrite spirit."),
        ("Isaiah 41:10","Fear thou not; for I am with thee: be not dismayed; for I am thy God: I will strengthen thee."),
        ("Matthew 6:33","But seek ye first the kingdom of God, and his righteousness; and all these things shall be added unto you."),
        ("Psalm 37:4","Delight thyself also in the LORD: and he shall give thee the desires of thine heart."),
        ("Romans 8:38-39","For I am persuaded, that neither death, nor life, nor angels, nor principalities, nor powers, nor things present, nor things to come, shall be able to separate us from the love of God."),
        ("Lamentations 3:22-23","It is of the LORD's mercies that we are not consumed, because his compassions fail not. They are new every morning: great is thy faithfulness."),
        ("John 14:6","Jesus saith unto him, I am the way, the truth, and the life: no man cometh unto the Father, but by me."),
        ("Psalm 139:14","I will praise thee; for I am fearfully and wonderfully made: marvellous are thy works."),
        ("Romans 12:2","And be not conformed to this world: but be ye transformed by the renewing of your mind."),
        ("Ephesians 2:8","For by grace are ye saved through faith; and that not of yourselves: it is the gift of God."),
        ("Galatians 5:22-23","But the fruit of the Spirit is love, joy, peace, longsuffering, gentleness, goodness, faith, meekness, temperance: against such there is no law."),
        ("Hebrews 11:1","Now faith is the substance of things hoped for, the evidence of things not seen."),
        ("1 John 4:19","We love him, because he first loved us."),
        ("Psalm 51:10","Create in me a clean heart, O God; and renew a right spirit within me."),
        ("John 16:33","These things I have spoken unto you, that in me ye might have peace. In the world ye shall have tribulation: but be of good cheer; I have overcome the world."),
        ("Romans 5:8","But God commendeth his love toward us, in that, while we were yet sinners, Christ died for us."),
        ("Proverbs 16:3","Commit thy works unto the LORD, and thy thoughts shall be established."),
        ("Isaiah 26:3","Thou wilt keep him in perfect peace, whose mind is stayed on thee: because he trusteth in thee."),
        ("Matthew 28:20","Teaching them to observe all things whatsoever I have commanded you: and, lo, I am with you always, even unto the end of the world."),
        ("Psalm 27:1","The LORD is my light and my salvation; whom shall I fear? the LORD is the strength of my life; of whom shall I be afraid?"),
        ("Colossians 3:23","And whatsoever ye do, do it heartily, as to the Lord, and not unto men."),
        ("1 Peter 5:7","Casting all your care upon him; for he careth for you."),
        ("Proverbs 4:23","Keep thy heart with all diligence; for out of it are the issues of life."),
        ("Psalm 91:1","He that dwelleth in the secret place of the most High shall abide under the shadow of the Almighty."),
        ("John 15:5","I am the vine, ye are the branches: He that abideth in me, and I in him, the same bringeth forth much fruit: for without me ye can do nothing."),
        ("Isaiah 43:2","When thou passest through the waters, I will be with thee; and through the rivers, they shall not overflow thee."),
        ("Romans 8:1","There is therefore now no condemnation to them which are in Christ Jesus, who walk not after the flesh, but after the Spirit."),
        ("Ephesians 3:20","Now unto him that is able to do exceeding abundantly above all that we ask or think, according to the power that worketh in us."),
        ("John 10:10","The thief cometh not, but for to steal, and to kill, and to destroy: I am come that they might have life, and that they might have it more abundantly."),
        ("Hebrews 13:5","Let your conversation be without covetousness; and be content with such things as ye have: for he hath said, I will never leave thee, nor forsake thee."),
        ("Zephaniah 3:17","The LORD thy God in the midst of thee is mighty; he will save, he will rejoice over thee with joy; he will rest in his love, he will joy over thee with singing."),
        ("Psalm 32:8","I will instruct thee and teach thee in the way which thou shalt go: I will guide thee with mine eye."),
        ("Matthew 5:16","Let your light so shine before men, that they may see your good works, and glorify your Father which is in heaven."),
        ("James 1:17","Every good gift and every perfect gift is from above, and cometh down from the Father of lights."),
        ("1 Corinthians 13:4","Charity suffereth long, and is kind; charity envieth not; charity vaunteth not itself, is not puffed up."),
        ("Proverbs 31:25","Strength and honour are her clothing; and she shall rejoice in time to come."),
    ]
    random.seed(today_date)
    return random.choice(popular_verses)

# ── WELCOME SCREEN ──
if not st.session_state.user_name:
    st.markdown(
        "<div class='welcome-wrap'>"
        "<div class='welcome-dove'>🕊️</div>"
        "<div class='welcome-title'>Welcome to Gods Word</div>"
        "<div class='welcome-sub'>Where Scripture meets the heart</div>"
        "</div>",
        unsafe_allow_html=True
    )
    col1, col2, col3 = st.columns([2, 3, 2])
    with col2:
        name_input = st.text_input(
            "What's your name?",
            placeholder="Enter your name...",
            label_visibility="visible"
        )
        st.markdown("<div class='begin-btn'>", unsafe_allow_html=True)
        if st.button("Let's Begin 🕊️", use_container_width=True):
            if name_input.strip():
                st.session_state.user_name = name_input.strip()
                save_json(USER_NAME_FILE, {"name": name_input.strip()})
                st.rerun()
            else:
                st.warning("Please enter your name to continue!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ── SIDEBAR ──
with st.sidebar:
    st.markdown(
        "<div class='sb-logo-wrap'><span style='font-size:1.3rem'>🕊️</span>"
        "<div><div class='sb-title'>Gods Word</div>"
        "<div class='sb-tagline'>Where Scripture meets the heart</div></div></div>",
        unsafe_allow_html=True
    )

    # Show user name
    st.markdown(
        f"<p style='color:{t['accent']};font-size:0.82rem;padding:4px 4px 0;'>👤 {st.session_state.user_name}</p>",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.markdown(f"<p style='color:{t['subtext']};font-size:0.78rem;margin-top:8px;'>Theme</p>", unsafe_allow_html=True)
    with col2:
        label = "☀️ Light" if st.session_state.theme == "dark" else "🌙 Dark"
        if st.button(label, use_container_width=True):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()

    st.divider()
    st.markdown("<div class='sb-section'>Recent chats</div>", unsafe_allow_html=True)
    if len(st.session_state.messages) == 0:
        st.markdown(f"<p style='color:{t['muted']};font-size:0.78rem;font-style:italic;padding:0 4px'>No conversations yet.</p>", unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(
                    "<div class='sb-hist-item'><div class='sb-hist-dot'></div>"
                    "<div class='sb-hist-text'>" + msg['content'][:45] + "...</div></div>",
                    unsafe_allow_html=True
                )

    st.divider()
    st.markdown("<div class='sb-section'>Browse by topic</div>", unsafe_allow_html=True)
    topics = {
        "Hope":"hope trust God future","Fear & Anxiety":"fear anxiety worry peace",
        "Love":"love God love others","Forgiveness":"forgiveness sin grace mercy",
        "Strength":"strength courage power weakness","Prayer":"prayer seek God communicate",
        "Faith":"faith believe trust God","Grief & Loss":"grief loss sorrow comfort",
        "Anger":"anger wrath patience kindness","Purpose":"purpose calling destiny meaning",
        "Marriage":"marriage husband wife love","Money":"money wealth greed contentment",
        "Wisdom":"wisdom knowledge understanding","Salvation":"salvation saved eternal life Jesus",
        "Joy":"joy happiness praise thankfulness"
    }
    selected_topic = st.selectbox("Topic", ["Select a topic..."] + list(topics.keys()), label_visibility="collapsed")
    if selected_topic and selected_topic != "Select a topic...":
        results = collections["bible_verses"].query(query_texts=[topics[selected_topic]], n_results=3)
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            st.markdown(
                "<div class='sb-fav-item'><div class='sb-fav-ref'>" + meta['reference'] + "</div>"
                "<div class='sb-fav-text'>\"" + doc[:180] + "\"</div></div>",
                unsafe_allow_html=True
            )

    st.divider()
    st.markdown("<div class='sb-section'>Saved verses</div>", unsafe_allow_html=True)
    if len(st.session_state.favourites) == 0:
        st.markdown(f"<p style='color:{t['muted']};font-size:0.78rem;font-style:italic;padding:0 4px'>No saved verses yet.</p>", unsafe_allow_html=True)
    else:
        for fav in st.session_state.favourites:
            st.markdown(
                "<div class='sb-fav-item'><div class='sb-fav-ref'>" + fav['reference'] + "</div>"
                "<div class='sb-fav-text'>\"" + fav['text'][:150] + "\"</div></div>",
                unsafe_allow_html=True
            )
        if st.button("🗑️ Clear favourites", use_container_width=True):
            st.session_state.favourites = []
            save_json(FAVOURITES_FILE, [])
            st.rerun()

    st.divider()
    st.markdown("<div class='sb-section'>Tools</div>", unsafe_allow_html=True)
    if st.button("✏️  Prayer journal", use_container_width=True):
        st.session_state.show_journal = not st.session_state.show_journal
        st.rerun()
    if st.button("🗑️  Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    if st.button("👤  Change name", use_container_width=True):
        st.session_state.user_name = ""
        save_json(USER_NAME_FILE, {"name": ""})
        st.rerun()

# ── MAIN ──
st.markdown(
    "<div class='gw-header'><span class='gw-dove'>🕊️</span>"
    "<div class='gw-title'>Gods Word</div>"
    "<div class='gw-sub'>Ask anything about the Bible</div>"
    "<div class='gw-rule'></div></div>",
    unsafe_allow_html=True
)

verse_ref, verse_text = get_verse_of_the_day(str(date.today()))
already_saved = any(f["reference"] == verse_ref for f in st.session_state.favourites)

st.markdown(
    "<div class='verse-card'>"
    "<div class='vc-badge'>✦ Verse of the day</div>"
    "<div class='vc-text'>\u201c" + verse_text + "\u201d</div>"
    "<div class='vc-footer'><div class='vc-ref'>— " + verse_ref + "</div></div>"
    "</div>",
    unsafe_allow_html=True
)

st.markdown("<div class='save-verse-wrap'>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([3.5, 2, 3.5])
with col2:
    btn_label = "✦ Saved" if already_saved else "⭐ Save Verse"
    if st.button(btn_label, use_container_width=True, key="save_verse"):
        if not already_saved:
            st.session_state.favourites.append({"reference": verse_ref, "text": verse_text})
            save_json(FAVOURITES_FILE, st.session_state.favourites)
            st.toast("Verse saved ⭐")
st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.show_journal:
    st.markdown(f"<h3 style='color:{t['accent']};font-family:Lora,serif;margin-top:1rem'>📝 Prayer Journal</h3>", unsafe_allow_html=True)
    prayer = st.text_area("Write your prayer...", height=130, placeholder="Dear God...", label_visibility="collapsed")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("💾 Save prayer", use_container_width=True):
            if prayer.strip():
                st.session_state.journal.append({"date": str(date.today()), "prayer": prayer})
                save_json(JOURNAL_FILE, st.session_state.journal)
                st.success("Prayer saved 🙏")
    with c2:
        if st.button("✕ Close", use_container_width=True):
            st.session_state.show_journal = False
            st.rerun()
    if st.session_state.journal:
        st.markdown(f"<p style='color:{t['subtext']};font-size:0.82rem;margin-top:12px'>Past prayers</p>", unsafe_allow_html=True)
        for entry in reversed(st.session_state.journal[-5:]):
            st.markdown(
                "<div class='sb-fav-item' style='margin:6px 0;'>"
                "<div class='sb-fav-ref'>📅 " + entry['date'] + "</div>"
                "<div style='font-size:0.85rem;color:" + t["text"] + ";margin-top:4px'>" + entry['prayer'] + "</div>"
                "</div>",
                unsafe_allow_html=True
            )
    st.divider()

# Chat history
for message in st.session_state.messages:
    role = message["role"]
    icon = "🙏" if role == "user" else "🕊️"
    css  = "user" if role == "user" else "bot"
    st.markdown(
        "<div class='msg-row " + css + "'>"
        "<div class='avatar " + css + "'>" + icon + "</div>"
        "<div class='msg-body'>"
        "<div class='bubble " + css + "'>" + message['content'] + "</div>"
        "<div class='msg-time'>" + message.get('time','') + "</div>"
        "</div></div>",
        unsafe_allow_html=True
    )

question = st.chat_input("Ask anything about the Bible...")

if question:
    now = datetime.now().strftime("%I:%M %p")
    st.session_state.messages.append({"role": "user", "content": question, "time": now})
    st.markdown(
        "<div class='msg-row user'><div class='avatar user'>🙏</div>"
        "<div class='msg-body'><div class='bubble user'>" + question + "</div>"
        "<div class='msg-time' style='text-align:right'>" + now + "</div></div></div>",
        unsafe_allow_html=True
    )

    video_keywords = ["video","watch","youtube","sermon video","show me","can you show","link","where can i watch"]
    wants_video = any(k in question.lower() for k in video_keywords)

    placeholder = st.empty()
    placeholder.markdown(
        "<div class='dove-loading-wrap'><div class='dove-loading'>🕊️</div>"
        "<div class='dove-loading-text'>Searching God's Word...</div></div>",
        unsafe_allow_html=True
    )

    answer = ask_gods_word(question)

    if wants_video:
        prev = [m["content"] for m in st.session_state.messages if m["role"] == "user"]
        sq = " ".join(prev[-2:])
        for w in ["video","watch","youtube","show me","can you show","link","share","where can i watch","relevant"]:
            sq = sq.replace(w,"")
        videos = get_relevant_video(sq.strip())
    else:
        videos = []

    placeholder.empty()
    answer_time = datetime.now().strftime("%I:%M %p")
    st.session_state.messages.append({"role": "assistant", "content": answer, "time": answer_time})
    st.markdown(
        "<div class='msg-row bot'><div class='avatar bot'>🕊️</div>"
        "<div class='msg-body'><div class='bubble bot'>" + answer + "</div>"
        "<div class='msg-time'>" + answer_time + "</div></div></div>",
        unsafe_allow_html=True
    )

    if videos:
        for video in videos:
            st.markdown(
                "<div class='video-card'>▶️ <a href='" + video['url'] + "' target='_blank'>"
                + video['source'] + ": " + video['title'] + "</a></div>",
                unsafe_allow_html=True
            )