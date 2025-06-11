import os
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Use os.environ.get instead of os.getenv for consistency with config.py
SERVICE_FILE = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE")
YOUR_EMAIL = os.environ.get("YOUR_EMAIL")

def export_competitor_analysis(data, brand_name="Brand", make_public=True):
    """
    Export competitor analysis data to a Google Sheet.
    
    Args:
        data: List of dictionaries containing competitor analysis data
        brand_name: Name of the brand being analyzed
        make_public: Whether to make the sheet publicly accessible (default: True)
        
    Returns:
        URL of the created Google Sheet
    """
    # Check if SERVICE_FILE is None and raise a more descriptive error
    if not SERVICE_FILE:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_FILE environment variable is not set or is empty")
        
    creds = Credentials.from_service_account_file(SERVICE_FILE, scopes=SCOPES)
    
    # Build Sheets and Drive services
    sheets_service = build("sheets", "v4", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    # Generate dynamic sheet title
    today = datetime.now().strftime("%Y-%m-%d")
    sheet_title = f"Competitor Analysis - {brand_name} - {today}"

    # Step 1: Create the new Google Sheet
    sheet_metadata = {"properties": {"title": sheet_title}}
    sheet = sheets_service.spreadsheets().create(
        body=sheet_metadata,
        fields="spreadsheetId"
    ).execute()
    sheet_id = sheet["spreadsheetId"]

    # Step 2: Write the data
    header = ["Section", "Name", "Website", "Type", "Details"]
    rows = []
    for item in data:
        rows.append([
            item.get("section", ""),
            item.get("name", ""),
            item.get("website", ""),
            item.get("type", ""),
            item.get("details", "")
        ])

    body = {"values": [header] + rows}
    sheets_service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range="A1",
        valueInputOption="RAW",
        body=body
    ).execute()
    
    # Step 3: Format the sheet
    requests = [
        # Format header row
        {
            "repeatCell": {
                "range": {
                    "sheetId": 0,
                    "startRowIndex": 0,
                    "endRowIndex": 1
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {"red": 0.2, "green": 0.2, "blue": 0.2},
                        "textFormat": {"bold": True, "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}}
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat)"
            }
        },
        # Auto-resize columns
        {
            "autoResizeDimensions": {
                "dimensions": {
                    "sheetId": 0,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": 5
                }
            }
        },
        # Wrap text in details column
        {
            "repeatCell": {
                "range": {
                    "sheetId": 0,
                    "startColumnIndex": 4,
                    "endColumnIndex": 5
                },
                "cell": {
                    "userEnteredFormat": {
                        "wrapStrategy": "WRAP"
                    }
                },
                "fields": "userEnteredFormat.wrapStrategy"
            }
        }
    ]
    
    # Find recommendations row and format it specially
    recommendation_rows = []
    for i, row in enumerate(rows):
        if "Recommendations" in row[0] or "Strategies" in row[0]:
            recommendation_rows.append(i + 1)  # +1 because of header row
    
    # Add special formatting for recommendation rows
    if recommendation_rows:
        for row_index in recommendation_rows:
            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": row_index,
                        "endRowIndex": row_index + 1
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": {"red": 0.9, "green": 1.0, "blue": 0.9},
                            "textFormat": {"bold": True}
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor,textFormat)"
                }
            })
            
            # Format the details cell for recommendations
            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": 0,
                        "startRowIndex": row_index,
                        "endRowIndex": row_index + 1,
                        "startColumnIndex": 4,
                        "endColumnIndex": 5
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {"foregroundColor": {"red": 0.0, "green": 0.5, "blue": 0.3}}
                        }
                    },
                    "fields": "userEnteredFormat.textFormat.foregroundColor"
                }
            })
    
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
