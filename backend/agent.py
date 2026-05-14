"""
agent.py — Simple Direct Approach
LangGraph bypass karke directly Groq + Drive call karo
"""

import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain_groq import ChatGroq
from google_drive_tool import get_drive_service

load_dotenv()


def get_llm():
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="llama-3.1-8b-instant",
        temperature=0,
        max_tokens=1024
    )


def search_drive_directly(user_query: str) -> str:
    """Directly Drive API call karo — no LangGraph needed."""
    try:
        service = get_drive_service()
        folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
        query_lower = user_query.lower()

        if any(w in query_lower for w in ["pdf"]):
            drive_query = f"mimeType = 'application/pdf' and '{folder_id}' in parents and trashed = false"
        elif any(w in query_lower for w in ["sheet", "excel", "spreadsheet"]):
            drive_query = f"(mimeType = 'application/vnd.google-apps.spreadsheet' or mimeType contains 'excel') and '{folder_id}' in parents and trashed = false"
        elif any(w in query_lower for w in ["doc", "document", "word"]):
            drive_query = f"(mimeType = 'application/vnd.google-apps.document' or mimeType contains 'word') and '{folder_id}' in parents and trashed = false"
        elif any(w in query_lower for w in ["image", "photo", "jpg", "png"]):
            drive_query = f"mimeType contains 'image' and '{folder_id}' in parents and trashed = false"
        elif any(w in query_lower for w in ["slide", "presentation", "ppt"]):
            drive_query = f"(mimeType = 'application/vnd.google-apps.presentation' or mimeType contains 'presentation') and '{folder_id}' in parents and trashed = false"
        elif any(w in query_lower for w in ["all", "list", "show", "everything"]):
            drive_query = f"'{folder_id}' in parents and trashed = false"
        else:
            words = [w for w in user_query.split() if len(w) > 2]
            search_term = words[0] if words else "file"
            drive_query = f"name contains '{search_term}' and '{folder_id}' in parents and trashed = false"

        results = service.files().list(
            q=drive_query,
            pageSize=15,
            fields="files(id, name, mimeType, modifiedTime, webViewLink)",
            orderBy="modifiedTime desc"
        ).execute()

        files = results.get("files", [])
        if not files:
            return "No files found. Try different keywords."

        lines = [f"Found {len(files)} file(s):\n"]
        for i, f in enumerate(files, 1):
            name     = f.get("name", "Unknown")
            modified = f.get("modifiedTime", "")[:10]
            link     = f.get("webViewLink", "No link")
            mime     = f.get("mimeType", "")
            ftype    = _readable(mime)
            lines.append(f"{i}. {name}\n   Type: {ftype} | Modified: {modified}\n   Link: {link}\n")

        return "\n".join(lines)

    except Exception as e:
        return f"Drive search error: {str(e)}"


def _readable(mime: str) -> str:
    m = {
        "application/pdf": "PDF",
        "application/vnd.google-apps.document": "Google Doc",
        "application/vnd.google-apps.spreadsheet": "Google Sheet",
        "application/vnd.google-apps.presentation": "Google Slides",
        "application/vnd.google-apps.folder": "Folder",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "Word",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "Excel",
        "text/plain": "Text",
    }
    if mime in m:
        return m[mime]
    if mime.startswith("image/"):
        return "Image"
    return mime.split("/")[-1]


class TailorTalkAgent:
    def __init__(self):
        self.llm = get_llm()
        self.chat_history = []

    def chat(self, user_message: str) -> str:
        try:
            drive_results = search_drive_directly(user_message)

            prompt = f"""You are TailorTalk, a helpful Google Drive search assistant.

User asked: "{user_message}"

Drive search results:
{drive_results}

Present these results in a clear, friendly way with file names and links.
If no files found, suggest alternatives."""

            response = self.llm.invoke([HumanMessage(content=prompt)])
            reply = response.content

            self.chat_history.append(HumanMessage(content=user_message))
            self.chat_history.append(AIMessage(content=reply))
            if len(self.chat_history) > 20:
                self.chat_history = self.chat_history[-20:]

            return reply

        except Exception as e:
            return f"Error: {str(e)}"

    def reset(self):
        self.chat_history = []
        return "Conversation reset! How can I help you find files?"