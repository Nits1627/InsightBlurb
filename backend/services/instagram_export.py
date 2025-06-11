import streamlit as st
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def export_instagram_analysis_to_sheet(data, account_name="Instagram Account", make_public=True):
    """
    Export Instagram analysis data to a Google Sheet.
    Args:
        data: Dictionary containing Instagram analysis data
        account_name: Name of the Instagram account being analyzed
        make_public: Whether to make the sheet publicly accessible (default: True)
    Returns:
        URL of the created Google Sheet
    """
    # Credentials from Streamlit secrets (not from local file)
    service_account_info = st.secrets["GOOGLE_SERVICE_ACCOUNT_FILE"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    
    sheets_service = build("sheets", "v4", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    today = datetime.now().strftime("%Y-%m-%d")
    sheet_title = f"Instagram Analysis - {account_name} - {today}"

    # Create Google Sheet
    sheet_metadata = {"properties": {"title": sheet_title}}
    sheet = sheets_service.spreadsheets().create(
        body=sheet_metadata,
        fields="spreadsheetId"
    ).execute()
    sheet_id = sheet["spreadsheetId"]

    # Prepare the data
    rows = []
    rows.append(["PROFILE ANALYSIS", ""])
    rows.append(["", ""])
    profile_analysis_lines = data["profile_analysis"].split("\n")
    for line in profile_analysis_lines:
        rows.append([line, ""])
    rows.append(["", ""])
    rows.append(["CONTENT ANALYSIS", ""])
    rows.append(["", ""])
    content_analysis_lines = data["content_analysis"].split("\n")
    for line in content_analysis_lines:
        rows.append([line, ""])
    rows.append(["", ""])
    rows.append(["AUDIENCE ANALYSIS", ""])
    rows.append(["", ""])
    audience_analysis_lines = data["audience_analysis"].split("\n")
    for line in audience_analysis_lines:
        rows.append([line, ""])
    rows.append(["", ""])
    rows.append(["RECOMMENDATIONS", ""])
    rows.append(["", ""])
    recommendations_lines = data["recommendations"].split("\n")
    for line in recommendations_lines:
        rows.append([line, ""])

    # Write to the sheet
    body = {"values": rows}
    sheets_service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range="A1",
        valueInputOption="RAW",
        body=body
    ).execute()
    
    # Optional formatting (batchUpdate)
    requests = [
        # Example: Bold the first row (Profile Analysis header)
        {
            "repeatCell": {
                "range": {
                    "sheetId": 0,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 1
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 0.8,
                            "green": 0.8,
                            "blue": 0.8
                        },
                        "horizontalAlignment": "LEFT",
                        "textFormat": {
                            "bold": True,
                            "fontSize": 12
                        }
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
            }
        },
        # Set column width for better readability
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": 0,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": 1
                },
                "properties": {
                    "pixelSize": 800
                },
                "fields": "pixelSize"
            }
        }
    ]
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={"requests": requests}
    ).execute()

    # Share sheet with your email if present
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

    # Make public if requested
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
