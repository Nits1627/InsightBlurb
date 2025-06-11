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

def export_to_sheet(data, brand_name="Brand", make_public=True):
    """
    Export data to a Google Sheet.
    
    Args:
        data: List of dictionaries containing data to export
        brand_name: Name of the brand being analyzed
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
    sheet_title = f"Ad Research - {brand_name} - {today}"

    # Step 1: Create the new Google Sheet
    sheet_metadata = {"properties": {"title": sheet_title}}
    sheet = sheets_service.spreadsheets().create(
        body=sheet_metadata,
        fields="spreadsheetId"
    ).execute()
    sheet_id = sheet["spreadsheetId"]

    # Step 2: Write the data
    header = ["Sr. No.", "Product Name", "YouTube Link", "Release Date", "Language", "Duration", "Insights"]
    rows = []
    for item in data:
        rows.append([
            item.get("sr_no"),
            item.get("title"),
            item.get("url"),
            item.get("published_at"),
            item.get("language", "Unknown"),
            item.get("duration", "Unknown"),
            item.get("insight")
        ])

    body = {"values": [header] + rows}
    sheets_service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range="A1",
        valueInputOption="RAW",
        body=body
    ).execute()

    # Step 3: Share the sheet with your email
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