#app/services/google_drive.py
import io
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
from app.core.config import get_settings

SERVICE_ACCOUNT_FILE = "app/keys/drive_service_account.json"
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds)


def download_drive_folder(folder_id: str, output_path: Path):
    drive = get_drive_service()
    archivos = []

    output_path.mkdir(parents=True, exist_ok=True)

    query = f"'{folder_id}' in parents and trashed = false"
    results = drive.files().list(
        q=query,
        fields="files(id, name, mimeType)"
    ).execute()

    for item in results.get("files", []):
        file_id = item["id"]
        name = item["name"]
        mime = item["mimeType"]

        # Recursivo si es carpeta
        if mime == "application/vnd.google-apps.folder":
            subdir = output_path / name
            archivos += download_drive_folder(file_id, subdir)
            continue

        # Google Docs export
        if mime.startswith("application/vnd.google-apps"):
            if mime == "application/vnd.google-apps.document":
                export_mime = "application/pdf"
                ext = ".pdf"
            elif mime == "application/vnd.google-apps.spreadsheet":
                export_mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ext = ".xlsx"
            elif mime == "application/vnd.google-apps.presentation":
                export_mime = "application/pdf"
                ext = ".pdf"
            else:
                continue

            out_path = output_path / f"{name}{ext}"
            request = drive.files().export_media(fileId=file_id, mimeType=export_mime)

        else:
            # archivo binario normal
            out_path = output_path / name
            request = drive.files().get_media(fileId=file_id)

        fh = io.FileIO(out_path, "wb")
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()

        archivos.append(str(out_path))

    return archivos


def download_drive_file(file_id: str, output_path: Path):
    drive = get_drive_service()

    file = drive.files().get(fileId=file_id, fields="id, name, mimeType").execute()
    name = file["name"]
    mime = file["mimeType"]

    # Google Docs export
    if mime == "application/vnd.google-apps.document":
        out_path = output_path / f"{name}.pdf"
        request = drive.files().export_media(fileId=file_id, mimeType="application/pdf")

    elif mime == "application/vnd.google-apps.spreadsheet":
        out_path = output_path / f"{name}.xlsx"
        request = drive.files().export_media(
            fileId=file_id,
            mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    elif mime.startswith("application/vnd.google-apps"):
        raise Exception(f"Tipo Google no soportado: {mime}")

    else:
        # binario normal
        out_path = output_path / name
        request = drive.files().get_media(fileId=file_id)

    fh = io.FileIO(out_path, "wb")
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    return str(out_path)
