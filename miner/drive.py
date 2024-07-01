import io
from uuid import uuid4

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

import cli.auth.drive as drive


async def write_uuid_file(data: bytes) -> str:
    """Uploads a file to the Volara drive bucket with a random UUID.

    Args:
        data: The data to upload.

    Returns:
        The URL of the uploaded file.
    """
    creds = drive.get_active_account()
    if not creds:
        raise Exception("No active drive account found.")
    service = build("drive", "v3", credentials=creds)

    # Check if the folder already exists
    query = "name='Volara' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = (
        service.files()
        .list(q=query, spaces="drive", fields="files(id, name)")
        .execute()
    )
    items = results.get("files", [])
    if items:
        folder_id = items[0]["id"]
    else:
        # Create volara folder if it did not exist
        folder_metadata = {
            "name": "Volara",
            "mimeType": "application/vnd.google-apps.folder",
        }
        folder = service.files().create(body=folder_metadata).execute()
        folder_id = folder.get("id")

    uuid_path = str(uuid4())
    file_metadata = {"name": uuid_path, "parents": [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(data), mimetype="application/zip")
    resp = service.files().create(body=file_metadata, media_body=media).execute()

    # Make the file publicly shareable
    permission = {"type": "anyone", "role": "reader", "allowFileDiscovery": False}
    service.permissions().create(fileId=resp["id"], body=permission).execute()

    # Get the downloadable link
    file = service.files().get(fileId=resp["id"], fields="webContentLink").execute()
    downloadable_link = file.get("webContentLink")
    return downloadable_link
