# File: services/sheets_exporter.py

import streamlit as st
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# 1) Scopes for Sheets & Drive
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def export_to_sheet(data, brand_name="Brand", make_public=True):
    """
    Export `data` (list of dicts) into a new Google Sheet placed
    in your Shared Drive. Returns the edit URL of the sheet.
    """

    # 2) Load service-account info from the table you defined
    svc_info = st.secrets["GOOGLE_SERVICE_ACCOUNT_FILE"]

    # 3) Build credentials and API clients
    creds = Credentials.from_service_account_info(svc_info, scopes=SCOPES)
    drive_service  = build("drive",  "v3", credentials=creds)
    sheets_service = build("sheets", "v4", credentials=creds)

    # 4) Define Shared Drive ID and file metadata
    SHARED_DRIVE_ID = "1KexGWs6evki7WWkA9naipMHvjd8Y49EG"
    today = datetime.now().strftime("%Y-%m-%d")
    title = f"Ad Research — {brand_name} — {today}"

    file_metadata = {
        "name": title,
        "mimeType": "application/vnd.google-apps.spreadsheet",
        "parents": [SHARED_DRIVE_ID]
    }

    # 5) Create the spreadsheet in the Shared Drive
    created = drive_service.files().create(
        body=file_metadata,
        fields="id",
        supportsAllDrives=True
    ).execute()
    sheet_id = created["id"]

    # 6) Populate header + rows
    header = ["Sr. No.", "Product Name", "YouTube Link",
              "Release Date", "Language", "Duration", "Insights"]
    rows = [
        [
            item.get("sr_no"),
            item.get("title"),
            item.get("url"),
            item.get("published_at"),
            item.get("language", "Unknown"),
            item.get("duration", "Unknown"),
            item.get("insight"),
        ]
        for item in data
    ]
    body = {"values": [header] + rows}
    sheets_service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range="A1",
        valueInputOption="RAW",
        body=body
    ).execute()

    # 7) Grant your personal email edit access (if YOU set YOUR_EMAIL)
    your_email = st.secrets.get("YOUR_EMAIL")
    if your_email:
        drive_service.permissions().create(
            fileId=sheet_id,
            body={"type": "user", "role": "writer", "emailAddress": your_email},
            fields="id",
            sendNotificationEmail=False,
            supportsAllDrives=True
        ).execute()

    # 8) Make it public for anyone to view (if requested)
    if make_public:
        drive_service.permissions().create(
            fileId=sheet_id,
            body={"type": "anyone", "role": "reader"},
            fields="id",
            supportsAllDrives=True
        ).execute()

    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
