"""
google_drive_tool.py
────────────────────
Google Drive ke saath baat karne ka tool.
LangChain is tool ko call karta hai jab user files search karna chahta hai.

Kaise kaam karta hai:
1. User: "find financial report from last week"
2. LLM ye tool call karta hai with proper query
3. Tool Drive API se files dhundta hai
4. Results wapas LLM ko jaate hain
5. LLM human-friendly response deta hai
"""

import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

# ── Setup Google Drive client ─────────────────────────────────────────────────
def get_drive_service():
    """
    Service Account se Drive API client banao.
    Service Account = ek 'robot user' jo Drive access kar sakta hai bina
    kisi actual Google account ke.
    """
    creds = service_account.Credentials.from_service_account_file(
        os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json"),
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    return build("drive", "v3", credentials=creds)


# ── File type mapping (human → MIME type) ─────────────────────────────────────
MIME_TYPES = {
    "pdf":        "application/pdf",
    "doc":        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "docx":       "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "google doc": "application/vnd.google-apps.document",
    "sheet":      "application/vnd.google-apps.spreadsheet",
    "sheets":     "application/vnd.google-apps.spreadsheet",
    "excel":      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "xlsx":       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "slide":      "application/vnd.google-apps.presentation",
    "slides":     "application/vnd.google-apps.presentation",
    "ppt":        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "image":      "image/",
    "jpg":        "image/jpeg",
    "png":        "image/png",
    "video":      "video/",
    "txt":        "text/plain",
    "text":       "text/plain",
    "folder":     "application/vnd.google-apps.folder",
}


@tool
def search_google_drive(query: str) -> str:
    """
    Google Drive mein files search karo.

    Query format examples:
    - name contains 'financial'
    - name contains 'report' and mimeType = 'application/pdf'
    - fullText contains 'invoice' and modifiedTime > '2024-01-01T00:00:00'
    - name contains 'meeting' and mimeType = 'application/vnd.google-apps.document'

    Returns formatted list of matching files with names, types, and links.
    """
    try:
        service = get_drive_service()
        folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

        # Folder constraint add karo — sirf us folder mein search karo
        folder_query = f"'{folder_id}' in parents and trashed = false"

        # User ki query ke saath combine karo
        if query.strip():
            full_query = f"({query}) and {folder_query}"
        else:
            full_query = folder_query

        # Drive API call
        results = service.files().list(
            q=full_query,
            pageSize=15,
            fields="files(id, name, mimeType, modifiedTime, size, webViewLink)",
            orderBy="modifiedTime desc"
        ).execute()

        files = results.get("files", [])

        if not files:
            return "No files found matching your search criteria."

        # Human-readable response format karo
        response_lines = [f"Found {len(files)} file(s):\n"]

        for i, f in enumerate(files, 1):
            name        = f.get("name", "Unknown")
            mime        = f.get("mimeType", "")
            modified    = f.get("modifiedTime", "")[:10]  # YYYY-MM-DD
            link        = f.get("webViewLink", "No link")
            file_type   = _mime_to_readable(mime)

            response_lines.append(
                f"{i}. 📄 {name}\n"
                f"   Type: {file_type}\n"
                f"   Modified: {modified}\n"
                f"   Link: {link}\n"
            )

        return "\n".join(response_lines)

    except Exception as e:
        return f"Error searching Drive: {str(e)}"


@tool
def list_all_files(dummy: str = "") -> str:
    """
    Google Drive folder ke saare files list karo.
    Use this when user asks 'show all files' or 'what files do you have'.
    dummy parameter is required by LangChain tool format but not used.
    """
    try:
        service = get_drive_service()
        folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            pageSize=30,
            fields="files(id, name, mimeType, modifiedTime, webViewLink)",
            orderBy="name"
        ).execute()

        files = results.get("files", [])

        if not files:
            return "The Drive folder appears to be empty."

        # Group by file type
        grouped = {}
        for f in files:
            ft = _mime_to_readable(f.get("mimeType", ""))
            grouped.setdefault(ft, []).append(f["name"])

        lines = [f"Total {len(files)} files in the Drive folder:\n"]
        for ftype, names in sorted(grouped.items()):
            lines.append(f"📁 {ftype} ({len(names)}):")
            for n in names:
                lines.append(f"   • {n}")
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        return f"Error listing files: {str(e)}"


def _mime_to_readable(mime: str) -> str:
    """MIME type ko human-readable string mein convert karo."""
    mapping = {
        "application/pdf":                                                     "PDF",
        "application/vnd.google-apps.document":                                "Google Doc",
        "application/vnd.google-apps.spreadsheet":                             "Google Sheet",
        "application/vnd.google-apps.presentation":                            "Google Slides",
        "application/vnd.google-apps.folder":                                  "Folder",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "Word Doc",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":   "Excel",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": "PowerPoint",
        "text/plain":                                                           "Text File",
        "image/jpeg":                                                           "Image (JPG)",
        "image/png":                                                            "Image (PNG)",
    }
    if mime in mapping:
        return mapping[mime]
    if mime.startswith("image/"):
        return "Image"
    if mime.startswith("video/"):
        return "Video"
    return mime.split("/")[-1].capitalize()
