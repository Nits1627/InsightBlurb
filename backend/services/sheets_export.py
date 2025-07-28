# File: services/sheets_exporter.py

import streamlit as st
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# 1) Scopes needed for Sheets & Drive
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

def export_to_sheet(data, brand_name="Brand", make_public=True):
    """
    Export `data` (list of dicts) into a new Google Sheet.
    Reads service-account info from st.secrets["GOOGLE_SERVICE_ACCOUNT_FILE"].
    Returns the `https://docs.google.com/spreadsheets/d/...` URL.
    """

    # 2) Grab the table you defined in Secrets → Key: GOOGLE_SERVICE_ACCOUNT_FILE
    svc_info = st.secrets["GOOGLE_SERVICE_ACCOUNT_FILE"]

    # 3) Build Credentials from that dict
    creds = Credentials.from_service_account_info(svc_info, scopes=SCOPES)

    # 4) Build the Drive & Sheets clients
    drive_service  = build("drive",  "v3", credentials=creds)
    sheets_service = build("sheets", "v4", credentials=creds)

    # 5) Create the spreadsheet via Drive API (so we can set parents if desired)
    today = datetime.now().strftime("%Y-%m-%d")
    title = f"Ad Research — {brand_name} — {today}"
    file_metadata = {
        "name": title,
        "mimeType": "application/vnd.google-apps.spreadsheet",
        # Optionally place it in a shared folder:
        # "parents": ["<YOUR_SHARED_FOLDER_ID>"]
    }
    created = drive_service.files().create(body=file_metadata, fields="id").execute()
    sheet_id = created["id"]

    # 6) Prepare and write your rows
    header = ["Sr. No.", "Product Name", "YouTube Link", "Release Date",
              "Language", "Duration", "Insights"]
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

    # 7) Grant your personal email edit access (if set)
    your_email = st.secrets.get("YOUR_EMAIL")
    if your_email:
        drive_service.permissions().create(
            fileId=sheet_id,
            body={"type": "user", "role": "writer", "emailAddress": your_email},
            fields="id",
            sendNotificationEmail=False
        ).execute()

    # 8) Make it public for anyone to view (if requested)
    if make_public:
        drive_service.permissions().create(
            fileId=sheet_id,
            body={"type": "anyone", "role": "reader"},
            fields="id"
        ).execute()

    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
