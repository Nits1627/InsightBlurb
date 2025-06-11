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

def export_instagram_campaigns_to_sheet(data, account_name="Instagram Account", years_back=1, make_public=True):
    """
    Export Instagram campaign data to a Google Sheet.
    
    Args:
        data: List of dictionaries containing post data with links, dates, and insights
        account_name: Name of the Instagram account being analyzed
        years_back: Number of years of data included
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
    sheet_title = f"Instagram Campaigns - {account_name} - {years_back} Year{'s' if years_back > 1 else ''} - {today}"

    # Step 1: Create the new Google Sheet
    sheet_metadata = {"properties": {"title": sheet_title}}
    sheet = sheets_service.spreadsheets().create(
        body=sheet_metadata,
        fields="spreadsheetId"
    ).execute()
    sheet_id = sheet["spreadsheetId"]

    # Step 2: Prepare the data
    rows = []
    
    # Add header row
    rows.append(["Post Link", "Date", "Insight"])
    
    # Add campaign data
    for post in data:
        rows.append([
            post.get("post_link", ""),
            post.get("date", ""),
            post.get("insight", "")
        ])

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
        # Format header row
        {
            "repeatCell": {
                "range": {
                    "sheetId": 0,
                    "startRowIndex": 0,
                    "endRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 3
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": {
                            "red": 0.8,
                            "green": 0.8,
                            "blue": 0.8
                        },
                        "horizontalAlignment": "CENTER",
                        "textFormat": {
                            "bold": True,
                            "fontSize": 12
                        }
                    }
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
            }
        },
        # Set column widths
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": 0,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": 1
                },
                "properties": {
                    "pixelSize": 300  # Post Link column
                },
                "fields": "pixelSize"
            }
        },
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": 0,
                    "dimension": "COLUMNS",
                    "startIndex": 1,
                    "endIndex": 2
                },
                "properties": {
                    "pixelSize": 100  # Date column
                },
                "fields": "pixelSize"
            }
        },
        {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": 0,
                    "dimension": "COLUMNS",
                    "startIndex": 2,
                    "endIndex": 3
                },
                "properties": {
                    "pixelSize": 600  # Insight column
                },
                "fields": "pixelSize"
            }
        },
        # Enable text wrapping for all cells
        {
            "repeatCell": {
                "range": {
                    "sheetId": 0,
                    "startRowIndex": 0,
                    "startColumnIndex": 0
                },
                "cell": {
                    "userEnteredFormat": {
                        "wrapStrategy": "WRAP"
                    }
                },
                "fields": "userEnteredFormat.wrapStrategy"
            }
        },
        # Make post links clickable
        {
            "repeatCell": {
                "range": {
                    "sheetId": 0,
                    "startRowIndex": 1,
                    "startColumnIndex": 0,
                    "endColumnIndex": 1
                },
                "cell": {
                    "userEnteredFormat": {
                        "textFormat": {
                            "foregroundColor": {
                                "red": 0.0,
                                "green": 0.0,
                                "blue": 0.8
                            },
                            "underline": True
                        }
                    }
                },
                "fields": "userEnteredFormat.textFormat"
            }
        },
        # Alternate row colors for better readability
        {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [{
                        "sheetId": 0,
                        "startRowIndex": 1
                    }],
                    "booleanRule": {
                        "condition": {
                            "type": "CUSTOM_FORMULA",
                            "values": [{
                                "userEnteredValue": "=MOD(ROW(),2)=0"
                            }]
                        },
                        "format": {
                            "backgroundColor": {
                                "red": 0.95,
                                "green": 0.95,
                                "blue": 0.95
                            }
                        }
                    }
                },
                "index": 0
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