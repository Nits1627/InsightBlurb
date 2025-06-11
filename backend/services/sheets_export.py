import streamlit as st
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def export_to_sheet(data, brand_name="Brand", make_public=True):
    """
    Export data to a Google Sheet (Streamlit Cloud compatible).
    
    Args:
        data: List of dictionaries to export
        brand_name: Name of the brand
        make_public: Whether to make the sheet public (default: True)
        
    Returns:
        URL of the created Google Sheet
    """
    # --- Credentials from st.secrets, NOT local file ---
    service_account_info = st.secrets["GOOGLE_SERVICE_ACCOUNT_FILE"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    
    sheets_service = build("sheets", "v4", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    # Dynamic sheet title
    today = datetime.now().strftime("%Y-%m-%d")
    sheet_title = f"Ad Research - {brand_name} - {today}"

    # 1. Create Google Sheet
    sheet_metadata = {"properties": {"title": sheet_title}}
    sheet = sheets_service.spreadsheets().create(
        body=sheet_metadata,
        fields="spreadsheetId"
    ).execute()
    sheet_id = sheet["spreadsheetId"]

    # 2. Prepare and write data
    header = ["Sr. No.", "Product Name", "YouTube Link", "Release Date", "Language", "Duration", "Insights"]
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

    # 3. Share sheet with YOUR_EMAIL if set
    YOUR_EMAIL = st.secrets.get("YOUR_EMAIL", None)
    if YOUR_EMAIL:
        permission = {
            "type": "user",
            "role": "writer",
            "emailAddress": YOUR_EMAIL
        }
        drive_service.permissions().create(
            fileId=sheet_id,
            body=permission,
            fields="id",
            sendNotificationEmail=False
        ).execute()
    
    # 4. Make sheet public if requested
    if make_public:
        public_permission = {
            "type": "anyone",
            "role": "reader"
        }
        drive_service.permissions().create(
            fileId=sheet_id,
            body=public_permission,
            fields="id"
        ).execute()

    return f"https://docs.google.com/spreadsheets/d/{sheet_id}"
