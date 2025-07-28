# File: services/sheets_exporter.py

import streamlit as st
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# 1) Define the scopes your service‐account needs:
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def export_to_sheet(data, brand_name="Brand", make_public=True):
    """
    Export a list of dicts `data` into a new Google Sheet.
    Reads the service account info from st.secrets["google_service_account"].
    Returns the URL of the created sheet.
    """

    # 2) Load the service account info from Streamlit Secrets (as a TOML table)
    svc_info = st.secrets["google_service_account"]

    # 3) Build Credentials directly from that dict:
    creds = Credentials.from_service_account_info(svc_info, scopes=SCOPES)

    # 4) Build Drive & Sheets clients:
    drive_service  = build("drive",  "v3", credentials=creds)
    sheets_service = build("sheets", "v4", credentials=creds)

    # 5) Create the spreadsheet via Drive API so we can set parents if needed:
    today = datetime.now().strftime("%Y-%m-%d")
    title = f"Ad Research - {brand_name} - {today}"
    file_metadata = {
        "name": title,
        "mimeType": "application/vnd.google-apps.spreadsheet",
        # Optionally, specify a shared folder ID:
        # "parents": ["<YOUR_SHARED_FOLDER_ID>"]
    }
    created_file = drive_service.files().create(
        body=file_metadata,
        fields="id"
    ).execute()
    sheet_id = created_file["id"]

    # 6) Prepare header and rows:
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

    # 7) Grant your own email edit access (optional)
    your_email = st.secrets.get("YOUR_EMAIL")
    if your_email:
        drive_service.permissions().create(
            fileId=sheet_id,
            body={"type": "user", "role": "writer", "emailAddress": your_email},
            fields="id"
        ).execute()

    # 8) Make it publicly viewable if requested
    if make_public:
        drive_service.permissions().create(
            fileId=sheet_id,
            body={"type": "anyone", "role": "reader"},
            fields="id"
        ).execute()

    # 9) Return the URL to the new sheet
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
