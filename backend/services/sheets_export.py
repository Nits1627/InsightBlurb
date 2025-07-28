# File: services/sheets_exporter.py

import os
import json
import streamlit as st
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# 1) Define your scopes here
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def export_to_sheet(data, brand_name="Brand", make_public=True):
    """
    Export data to a Google Sheet using a service account stored in st.secrets.
    Returns the public URL of the created sheet.
    """
    # 2) Load & parse the full JSON blob from your Streamlit Secrets
    #    Make sure in Secrets you have a key GOOGLE_SERVICE_ACCOUNT_JSON
    svc_json = st.secrets["GOOGLE_SERVICE_ACCOUNT_JSON"]
    if isinstance(svc_json, str):
        svc_info = json.loads(svc_json)
    else:
        svc_info = svc_json  # already a dict

    # 3) Build credentials + services
    creds = Credentials.from_service_account_info(svc_info, scopes=SCOPES)
    drive = build("drive", "v3", credentials=creds)
    sheets = build("sheets", "v4", credentials=creds)

    # 4) Create the sheet via Drive API (so you can specify folder-parents if you want)
    today = datetime.now().strftime("%Y-%m-%d")
    title = f"Ad Research - {brand_name} - {today}"
    file_metadata = {
        "name": title,
        "mimeType": "application/vnd.google-apps.spreadsheet",
        # Optionally, put it in a shared folder:
        # "parents": ["<YOUR_SHARED_FOLDER_ID>"]
    }
    created = drive.files().create(body=file_metadata, fields="id").execute()
    sheet_id = created["id"]

    # 5) Populate it via Sheets API
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
    sheets.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range="A1",
        valueInputOption="RAW",
        body=body
    ).execute()

    # 6) Grant permissions
    #    a) Invite your email if you want edit access
    your_email = st.secrets.get("YOUR_EMAIL")
    if your_email:
        drive.permissions().create(
            fileId=sheet_id,
            body={"type": "user", "role": "writer", "emailAddress": your_email},
            fields="id"
        ).execute()

    #    b) Make it public for read if requested
    if make_public:
        drive.permissions().create(
            fileId=sheet_id,
            body={"type": "anyone", "role": "reader"},
            fields="id"
        ).execute()

    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
