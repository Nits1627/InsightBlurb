import os
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

# Get service account file path
SERVICE_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
YOUR_EMAIL = os.getenv("YOUR_EMAIL")

print(f"SERVICE_FILE: {SERVICE_FILE}")
print(f"File exists: {os.path.exists(SERVICE_FILE if SERVICE_FILE else '')}")

try:
    # Define scopes
    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Create credentials
    creds = Credentials.from_service_account_file(SERVICE_FILE, scopes=SCOPES)
    
    # Build Sheets and Drive services
    sheets_service = build("sheets", "v4", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)
    
    print("Successfully created sheets service")
    
    # Try to create a test sheet
    sheet_metadata = {"properties": {"title": "Test Sheet"}}
    sheet = sheets_service.spreadsheets().create(
        body=sheet_metadata,
        fields="spreadsheetId"
    ).execute()
    sheet_id = sheet["spreadsheetId"]
    
    print(f"Successfully created test sheet with ID: {sheet_id}")
    print(f"Sheet URL: https://docs.google.com/spreadsheets/d/{sheet_id}")
    
    # Share the sheet with your email
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
        print(f"Shared sheet with {YOUR_EMAIL}")
    
except Exception as e:
    print(f"Error: {e}")