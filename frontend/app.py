"""
app.py — Streamlit Frontend
────────────────────────────
Ye chat UI hai jo user dekhta hai.

Features:
- Chat interface (WhatsApp jaisi feel)
- Conversation history display
- Session management
- Reset button
- File type quick filters

Kaise run karo:
    streamlit run app.py
"""

import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
SESSION_ID  = "streamlit_session"

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TailorTalk — Drive Search",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #f0f2f6; }

    /* Chat message bubbles */
    .user-bubble {
        background: #0A1931;
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0 8px 60px;
        font-size: 14px;
        line-height: 1.5;
    }
    .bot-bubble {
        background: white;
        color: #222;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 60px 8px 0;
        font-size: 14px;
        line-height: 1.5;
        border: 1px solid #e0e0e0;
        white-space: pre-wrap;
    }
    .bubble-label {
        font-size: 11px;
        color: #888;
        margin-bottom: 2px;
    }

    /* Title styling */
    h1 { color: #0A1931 !important; }

    /* Input box */
    .stTextInput > div > div > input {
        border-radius: 24px;
        border: 2px solid #1565C0;
        padding: 10px 16px;
    }

    /* Quick filter buttons */
    .stButton > button {
        border-radius: 20px;
        font-size: 12px;
        padding: 4px 12px;
        background: white;
        border: 1px solid #1565C0;
        color: #1565C0;
    }
    .stButton > button:hover {
        background: #1565C0;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# ── Session State Init ────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "👋 Hi! I'm **TailorTalk** — your Google Drive search assistant.\n\n"
            "I can help you find files by:\n"
            "• 📝 **Name** — *'find the Q1 report'*\n"
            "• 📂 **File type** — *'show me all PDFs'*\n"
            "• 📅 **Date** — *'files from last week'*\n"
            "• 🔍 **Content** — *'documents about invoice'*\n\n"
            "What are you looking for?"
        )
    })


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/0A1931/FFFFFF?text=TailorTalk", width=150)
    st.markdown("---")

    st.markdown("### 🔍 Quick Searches")
    st.caption("Click to search instantly")

    quick_searches = [
        ("📄 All PDFs",           "show me all PDF files"),
        ("📊 Spreadsheets",        "find all spreadsheets and Excel files"),
        ("📝 Documents",           "find all Google Docs and Word documents"),
        ("🖼️ Images",              "find all image files"),
        ("🕐 Recent Files",        "show files modified recently"),
        ("📁 All Files",           "list all files in the drive"),
    ]

    for label, query in quick_searches:
        if st.button(label, use_container_width=True):
            st.session_state.pending_message = query

    st.markdown("---")

    # Backend health check
    st.markdown("### ⚙️ System Status")
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=3)
        if r.status_code == 200:
            data = r.json()
            st.success("✅ Backend Connected")
            st.caption(f"LLM: {data.get('llm_provider', 'unknown').upper()}")
        else:
            st.error("❌ Backend Error")
    except:
        st.error("❌ Backend Offline")
        st.caption(f"Make sure backend is running at {BACKEND_URL}")

    st.markdown("---")
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        # Reset backend session
        try:
            requests.post(f"{BACKEND_URL}/reset", json={"session_id": SESSION_ID})
        except:
            pass
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Conversation cleared! How can I help you find files?"
        }]
        st.rerun()


# ── Main Chat Area ────────────────────────────────────────────────────────────
st.title("🔍 TailorTalk")
st.caption("Conversational Google Drive Search Agent")
st.markdown("---")

# Display chat history
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f'<p class="bubble-label" style="text-align:right">You</p>'
                f'<div class="user-bubble">{msg["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<p class="bubble-label">TailorTalk 🤖</p>'
                f'<div class="bot-bubble">{msg["content"]}</div>',
                unsafe_allow_html=True
            )

st.markdown("---")

# ── Input Area ────────────────────────────────────────────────────────────────
col1, col2 = st.columns([5, 1])

with col1:
    user_input = st.text_input(
        "Message",
        placeholder="Find financial report from last week...",
        label_visibility="collapsed",
        key="chat_input"
    )

with col2:
    send_clicked = st.button("Send 🚀", use_container_width=True)


# ── Handle Quick Search or Send ───────────────────────────────────────────────
def send_message(message: str):
    """Message backend ko bhejo aur response lo."""
    if not message.strip():
        return

    # User message add karo
    st.session_state.messages.append({"role": "user", "content": message})

    # Backend call karo
    with st.spinner("🔍 Searching Drive..."):
        try:
            response = requests.post(
                f"{BACKEND_URL}/chat",
                json={"message": message, "session_id": SESSION_ID},
                timeout=60
            )

            if response.status_code == 200:
                bot_reply = response.json()["response"]
            else:
                bot_reply = f"Error: {response.status_code} — {response.text}"

        except requests.exceptions.ConnectionError:
            bot_reply = (
                "❌ Cannot connect to backend.\n\n"
                f"Make sure the FastAPI server is running at {BACKEND_URL}\n"
                "Run: `uvicorn main:app --reload --port 8000`"
            )
        except requests.exceptions.Timeout:
            bot_reply = "⏱️ Request timed out. Please try again."
        except Exception as e:
            bot_reply = f"❌ Unexpected error: {str(e)}"

    # Bot response add karo
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    st.rerun()


# Quick search pending hai?
if hasattr(st.session_state, "pending_message") and st.session_state.pending_message:
    msg = st.session_state.pending_message
    st.session_state.pending_message = None
    send_message(msg)

# Send button ya Enter
if send_clicked and user_input:
    send_message(user_input)
elif user_input and user_input != st.session_state.get("last_input", ""):
    st.session_state.last_input = user_input


# ── Sample queries at bottom ──────────────────────────────────────────────────
with st.expander("💡 Example queries you can try"):
    examples = [
        "Find all PDF files",
        "Show me documents about finance",
        "Find files modified this week",
        "Search for any file with 'report' in the name",
        "Show me all images",
        "Find spreadsheets related to budget",
        "What files were added recently?",
        "Find the meeting notes document",
    ]
    cols = st.columns(2)
    for i, ex in enumerate(examples):
        with cols[i % 2]:
            if st.button(f"→ {ex}", key=f"ex_{i}"):
                send_message(ex)
