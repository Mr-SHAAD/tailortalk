# TailorTalk — Conversational Google Drive Search Agent

## Architecture

```
User (Browser)
    ↓
Streamlit Frontend (frontend/app.py)  ← Chat UI
    ↓ HTTP POST /chat
FastAPI Backend (backend/main.py)     ← API Server
    ↓
LangChain Agent (backend/agent.py)    ← AI Brain
    ↓ Tool Call
Google Drive Tool (backend/google_drive_tool.py)
    ↓
Google Drive API                      ← Actual files
```

---

## Step 1 — Groq API Key Lo (FREE)

1. https://console.groq.com/ pe jao
2. Sign up karo (Google se bhi ho sakta hai)
3. "API Keys" mein jao → "Create API Key"
4. Key copy karo — `gsk_...` se shuru hogi

---

## Step 2 — Google Drive Service Account Banao

Ye sabse important step hai. Dhyan se karo:

### 2a. Google Cloud Console mein Project banao
1. https://console.cloud.google.com/ pe jao
2. Top pe "Select Project" → "New Project"
3. Name: `TailorTalk` → Create

### 2b. Google Drive API Enable karo
1. Left menu → "APIs & Services" → "Library"
2. Search: "Google Drive API"
3. Click → "Enable"

### 2c. Service Account banao
1. Left menu → "APIs & Services" → "Credentials"
2. "+ Create Credentials" → "Service Account"
3. Name: `tailortalk-service` → Create
4. Role: "Editor" → Continue → Done

### 2d. JSON Key download karo
1. Service accounts list mein apna account click karo
2. "Keys" tab → "Add Key" → "Create New Key"
3. JSON select karo → Create
4. File download hogi — iska naam `service_account.json` rakho
5. Is file ko project ke root mein rakh do

### 2e. Drive Folder share karo Service Account se
1. Sample folder copy karo apne Drive mein:
   https://drive.google.com/drive/folders/1qkx58doSeYrcLjHPDysJyVJ36PsSqqlt
2. Copied folder pe right click → "Share"
3. Service account ki email add karo (service_account.json mein `client_email` field mein hai)
4. Permission: "Viewer" → Share
5. Folder URL se ID copy karo:
   `https://drive.google.com/drive/folders/FOLDER_ID_YE_HAI`

---

## Step 3 — .env File Banao

```bash
cp .env.example .env
```

.env mein fill karo:
```
GROQ_API_KEY=gsk_your_key_here
LLM_PROVIDER=groq
GOOGLE_SERVICE_ACCOUNT_FILE=service_account.json
GOOGLE_DRIVE_FOLDER_ID=1qkx58doSeYrcLjHPDysJyVJ36PsSqqlt
BACKEND_URL=http://localhost:8000
```

---

## Step 4 — Install Dependencies

```bash
# Python virtual environment banao
python -m venv venv

# Activate karo
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Dependencies install karo
pip install -r requirements.txt
```

---

## Step 5 — Locally Run Karo

**Terminal 1 — Backend:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```
→ http://localhost:8000 pe open hoga
→ http://localhost:8000/docs pe API documentation milegi

**Terminal 2 — Frontend:**
```bash
cd frontend
streamlit run app.py
```
→ http://localhost:8501 pe chat UI open hoga

---

## Step 6 — Test Karo

Streamlit mein ye queries try karo:
- "show all files"
- "find PDF files"
- "find documents about finance"
- "show files from last week"

---

## Step 7 — Railway pe Deploy Karo

### Backend Deploy (Railway)
1. https://railway.app/ pe jao → Login with GitHub
2. "New Project" → "Deploy from GitHub repo"
3. Apna repo select karo
4. Environment Variables add karo (same as .env):
   - GROQ_API_KEY
   - LLM_PROVIDER=groq
   - GOOGLE_DRIVE_FOLDER_ID
   - GOOGLE_SERVICE_ACCOUNT_FILE=service_account.json
5. service_account.json ka content bhi env var mein add karo:
   - Variable name: `GOOGLE_SERVICE_ACCOUNT_JSON`
   - Value: poora JSON file ka content paste karo
6. Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
7. Deploy → URL milega like: `https://tailortalk-backend.railway.app`

### Frontend Deploy (Streamlit Cloud) — FREE
1. https://streamlit.io/cloud pe jao → Login with GitHub
2. "New app" → repo select karo
3. Main file path: `frontend/app.py`
4. Secrets mein add karo:
   ```toml
   BACKEND_URL = "https://your-railway-backend-url.railway.app"
   GROQ_API_KEY = "gsk_..."
   GOOGLE_DRIVE_FOLDER_ID = "your_folder_id"
   ```
5. Deploy → URL milega

---

## Common Errors & Fixes

### "No files found" always
- Drive folder ID check karo
- Service account ko folder share kiya kya?
- Folder mein files hain kya?

### "Error: credentials file not found"
- service_account.json sahi jagah hai kya?
- Railway pe — JSON content ko env var mein daalo

### "Groq API error"
- API key check karo
- Free tier limit exceed toh nahi hua?

### Backend connect nahi ho raha
- BACKEND_URL .env mein sahi hai kya?
- Backend wala terminal chal raha hai kya?

---

## Project Structure

```
tailortalk/
├── backend/
│   ├── main.py              # FastAPI server — API endpoints
│   ├── agent.py             # LangChain agent — AI brain
│   └── google_drive_tool.py # Drive API integration
├── frontend/
│   ├── app.py               # Streamlit chat UI
│   └── .streamlit/
│       └── config.toml      # Streamlit config
├── service_account.json     # Google credentials (DO NOT COMMIT)
├── .env                     # Your secrets (DO NOT COMMIT)
├── .env.example             # Template
├── requirements.txt
├── Procfile                 # Railway deployment
└── README.md
```

---

## .gitignore (Important — secrets commit mat karo)

```
.env
service_account.json
venv/
__pycache__/
*.pyc
.DS_Store
```
