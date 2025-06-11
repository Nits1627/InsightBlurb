import os
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SERVICE_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
YOUR_EMAIL = os.getenv("YOUR_EMAIL")

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
    creds = Credentials.from_service_account_file(SERVICE_FILE, scopes=SCOPES)
    
    # Build Sheets and Drive services
    sheets_service = build("sheets", "v4", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    # Generate dynamic sheet title
    today = datetime.now().strftime("%Y-%m-%d")
    sheet_title = f"Instagram Analysis - {account_name} - {today}"

    # Step 1: Create the new Google Sheet
    sheet_metadata = {"properties": {"title": sheet_title}}
    sheet = sheets_service.spreadsheets().create(
        body=sheet_metadata,
        fields="spreadsheetId"
    ).execute()
    sheet_id = sheet["spreadsheetId"]

    # Step 2: Prepare the data
    rows = []
    
    # Add profile analysis
    rows.append(["PROFILE ANALYSIS", ""])
    rows.append(["", ""])
    profile_analysis_lines = data["profile_analysis"].split("\n")
    for line in profile_analysis_lines:
        rows.append([line, ""])
    rows.append(["", ""])
    
    # Add content analysis
    rows.append(["CONTENT ANALYSIS", ""])
    rows.append(["", ""])
    content_analysis_lines = data["content_analysis"].split("\n")
    for line in content_analysis_lines:
        rows.append([line, ""])
    rows.append(["", ""])
    
    # Add audience analysis
    rows.append(["AUDIENCE ANALYSIS", ""])
    rows.append(["", ""])
    audience_analysis_lines = data["audience_analysis"].split("\n")
    for line in audience_analysis_lines:
        rows.append([line, ""])
    rows.append(["", ""])
    
    # Add recommendations
    rows.append(["RECOMMENDATIONS", ""])
    rows.append(["", ""])
    recommendations_lines = data["recommendations"].split("\n")
    for line in recommendations_lines:
        rows.append([line, ""])

    # Write the data to the sheet
    body = {"values": rows}
    sheets_service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range="A1",
        valueInputOption="RAW",
        body=body
    ).execute()
    
    # Step 3: Format the sheet for better readability
    requests = [
        # Format section headers
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
        # Format content analysis header
        {
            "repeatCell": {
                "range": {
                    "sheetId": 0,
                    "startRowIndex": len(profile_analysis_lines) + 3,
                    "endRowIndex": len(profile_analysis_lines) + 4,
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
        # Set column width
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

    # Step 4: Share the sheet with your email
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
    
    # Make the sheet public if requested
    if make_public:
        # Create a permission for anyone to access the sheet
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