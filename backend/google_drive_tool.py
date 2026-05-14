import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()


def get_drive_service():
    """Get authenticated Google Drive service client using service account."""
    creds = service_account.Credentials.from_service_account_file(
        os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json"),
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    return build("drive", "v3", credentials=creds)


def search_google_drive(query: str) -> str:
    """Search for files in Google Drive using a query string."""
    try:
        service = get_drive_service()
        folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
        folder_query = f"'{folder_id}' in parents and trashed = false"

        if query.strip():
            full_query = f"({query}) and {folder_query}"
        else:
            full_query = folder_query

        results = service.files().list(
            q=full_query,
            pageSize=15,
            fields="files(id, name, mimeType, modifiedTime, webViewLink)",
            orderBy="modifiedTime desc"
        ).execute()

        files = results.get("files", [])
        if not files:
            return "No files found matching your search criteria."

        response_lines = [f"Found {len(files)} file(s):\n"]
        for i, f in enumerate(files, 1):
            name     = f.get("name", "Unknown")
            mime     = f.get("mimeType", "")
            modified = f.get("modifiedTime", "")[:10]
            link     = f.get("webViewLink", "No link")
            ftype    = _mime_to_readable(mime)
            response_lines.append(
                f"{i}. {name}\n"
                f"   Type: {ftype} | Modified: {modified}\n"
                f"   Link: {link}\n"
            )
        return "\n".join(response_lines)

    except Exception as e:
        return f"Error searching Drive: {str(e)}"


def list_all_files() -> str:
    """List all files in the configured Google Drive folder."""
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

        grouped = {}
        for f in files:
            ft = _mime_to_readable(f.get("mimeType", ""))
            grouped.setdefault(ft, []).append(f["name"])

        lines = [f"Total {len(files)} files in the Drive folder:\n"]
        for ftype, names in sorted(grouped.items()):
            lines.append(f"{ftype} ({len(names)}):")
            for n in names:
                lines.append(f"  - {n}")
            lines.append("")
        return "\n".join(lines)

    except Exception as e:
        return f"Error listing files: {str(e)}"


def _mime_to_readable(mime: str) -> str:
    """Convert MIME type string to human readable file type name."""
    mapping = {
        "application/pdf": "PDF",
        "application/vnd.google-apps.document": "Google Doc",
        "application/vnd.google-apps.spreadsheet": "Google Sheet",
        "application/vnd.google-apps.presentation": "Google Slides",
        "application/vnd.google-apps.folder": "Folder",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "Word Doc",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "Excel",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": "PowerPoint",
        "text/plain": "Text File",
        "image/jpeg": "Image (JPG)",
        "image/png": "Image (PNG)",
    }
    if mime in mapping:
        return mapping[mime]
    if mime.startswith("image/"):
        return "Image"
    if mime.startswith("video/"):
        return "Video"
    return mime.split("/")[-1].capitalize()