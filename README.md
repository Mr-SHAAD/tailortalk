# TailorTalk — Conversational Google Drive Search Agent

> **An AI-powered assistant that lets you search and discover files in Google Drive through natural conversation.**

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?logo=streamlit)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-0.2-yellow)](https://langchain.com)
[![Google Drive API](https://img.shields.io/badge/Google_Drive_API-v3-blue?logo=google-drive)](https://developers.google.com/drive)

---

## Live Demo

| Service | URL |
|---------|-----|
| 🌐 Frontend (Chat UI) | `[Streamlit URL]` |
| ⚙️ Backend (API) | `[Render URL]` |
| 📂 GitHub Repository | https://github.com/Mr-SHAAD/tailortalk |

---

## What is TailorTalk?

TailorTalk is a **conversational AI agent** that enables users to search, filter, and discover files within a designated Google Drive folder using natural language — no technical queries required.

Instead of manually browsing folders, users can simply ask:

- *"Find the financial report from last week"*
- *"Show me all PDF files"*
- *"Find documents about invoices"*
- *"List all spreadsheets modified this month"*

The agent understands the intent, translates it into a precise Google Drive API query, fetches the results, and presents them in a clean, conversational format.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER (Browser)                        │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Streamlit Frontend (Chat UI)                │
│              frontend/app.py — Port 8501                 │
└─────────────────────┬───────────────────────────────────┘
                      │  HTTP POST /chat
                      ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (REST API)                  │
│              backend/main.py — Port 8000                 │
│              Endpoints: /chat  /reset  /health           │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│           AI Agent (LangChain + Groq LLM)               │
│           backend/agent.py                               │
│           Model: llama-3.1-8b-instant (FREE)            │
└─────────────────────┬───────────────────────────────────┘
                      │  Tool Call
                      ▼
┌─────────────────────────────────────────────────────────┐
│         Google Drive Search Tool                         │
│         backend/google_drive_tool.py                     │
│         Uses: files.list(), q parameter, fullText        │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Google Drive API (v3)                       │
│              Service Account Authentication              │
└─────────────────────────────────────────────────────────┘
```

---

## Key Features

- **Natural Language Search** — Users describe what they need in plain English; the agent handles the query translation
- **Multi-parameter Filtering** — Search by file name, type (PDF, Docs, Sheets, Images), content (`fullText`), and modification date
- **Conversational Memory** — The agent remembers context across messages within a session
- **Real-time Results** — Files returned with direct Google Drive links for instant access
- **Quick Filters** — One-click buttons for common searches (All PDFs, Recent Files, Images, etc.)
- **Session Management** — Each user session is independent; conversation can be reset anytime
- **Health Monitoring** — Live backend status indicator in the UI

---

## Technical Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit | Chat interface |
| **Backend** | FastAPI + Uvicorn | REST API server |
| **AI Agent** | LangChain + Groq | Natural language understanding |
| **LLM** | Llama 3.1 8B (via Groq) | Free, fast inference |
| **Drive Integration** | Google Drive API v3 | File search and retrieval |
| **Auth** | Google Service Account | Secure Drive access |
| **Deployment** | Render (Backend) + Streamlit Cloud (Frontend) | Cloud hosting |

---

## Google Drive Search Capabilities

The agent translates natural language into precise Drive API queries:

| User Says | Drive API Query Generated |
|-----------|--------------------------|
| "find all PDFs" | `mimeType = 'application/pdf'` |
| "show Google Docs" | `mimeType = 'application/vnd.google-apps.document'` |
| "files from last week" | `modifiedTime > '2026-05-07T00:00:00'` |
| "documents about invoice" | `fullText contains 'invoice'` |
| "find report PDF" | `name contains 'report' and mimeType = 'application/pdf'` |

---

## Project Structure

```
tailortalk/
├── backend/
│   ├── main.py                 # FastAPI server — /chat, /reset, /health, /files
│   ├── agent.py                # AI agent — LangChain + Groq LLM
│   ├── google_drive_tool.py    # Google Drive API integration
│   └── service_account.json   # Google credentials (not committed)
├── frontend/
│   ├── app.py                  # Streamlit chat UI
│   └── .streamlit/
│       └── config.toml         # Streamlit theme configuration
├── .env.example                # Environment variables template
├── .gitignore                  # Secrets excluded from version control
├── Procfile                    # Render deployment configuration
├── requirements.txt            # Python dependencies
└── README.md
```

---

## Local Setup

### Prerequisites
- Python 3.11+
- Google Cloud account (free)
- Groq API key (free) — https://console.groq.com

### Step 1 — Clone the repository
```bash
git clone https://github.com/Mr-SHAAD/tailortalk.git
cd tailortalk
```

### Step 2 — Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Configure environment variables
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
GROQ_API_KEY=your_groq_api_key
LLM_PROVIDER=groq
GOOGLE_SERVICE_ACCOUNT_FILE=service_account.json
GOOGLE_DRIVE_FOLDER_ID=your_folder_id
BACKEND_URL=http://localhost:8000
```

### Step 5 — Add Google Service Account
Place your `service_account.json` file inside the `backend/` directory.

> To generate this file: Google Cloud Console → APIs & Services → Credentials → Create Service Account → Download JSON key

### Step 6 — Share Drive folder with Service Account
Share your Google Drive folder with the service account email (found in `service_account.json` → `client_email`), granting **Viewer** access.

### Step 7 — Run the application

**Terminal 1 — Backend:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## API Reference

### `POST /chat`
Send a message and receive a response from the agent.

**Request:**
```json
{
  "message": "find all PDF files",
  "session_id": "user_session_1"
}
```

**Response:**
```json
{
  "response": "I found 3 PDF files in your Drive...",
  "session_id": "user_session_1"
}
```

### `GET /health`
Check backend status and configuration.

### `POST /reset`
Clear conversation history for a session.

### `GET /files`
List all files in the configured Drive folder.

---

## Deployment

### Backend — Render
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables:** Set all values from `.env.example`

### Frontend — Streamlit Cloud
- **Main file:** `frontend/app.py`
- **Secrets:** Add `BACKEND_URL` pointing to your Render backend URL

---

## Security

- All credentials (API keys, service account) are excluded from version control via `.gitignore`
- Google Drive access is read-only (`drive.readonly` scope)
- Service Account follows least-privilege principle — access limited to the shared folder only
- CORS configured on the FastAPI backend

---

## Sample Queries to Try

```
"Show me all files"
"Find all PDF documents"
"Search for files related to finance"
"Show spreadsheets modified this week"
"Find images in the drive"
"Look for any file named report"
"Show me the most recently modified files"
```

---

## Author

**Mohammad Shaad**
Python Backend Developer

- GitHub: [@Mr-SHAAD](https://github.com/Mr-SHAAD)
- LinkedIn: [linkedin.com/in/mohammadshaad](https://linkedin.com/in/mohammadshaad)
- Email: knowmore8126@gmail.com