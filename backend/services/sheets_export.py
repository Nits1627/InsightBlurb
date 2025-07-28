import os
import csv
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

def export_to_csv(data, brand_name="Brand", output_dir=None):
    """
    Export data to a CSV file.
    
    Args:
        data: List of dictionaries containing data to export
        brand_name: Name of the brand being analyzed
        output_dir: Directory to save the CSV file (default: current directory)
        
    Returns:
        Path to the created CSV file
        
    Raises:
        Exception: If there's an error writing to the CSV file
    """
    try:
        # Generate dynamic file name
        today = datetime.now().strftime("%Y-%m-%d")
        file_name = f"Ad_Research_{brand_name}_{today}.csv"
        
        # Set output directory
        if output_dir is None:
            output_dir = os.getcwd()
        
        # Create full file path
        file_path = os.path.join(output_dir, file_name)
        
        # Prepare header and rows
        header = ["Sr. No.", "Product Name", "YouTube Link", "Release Date", "Language", "Duration", "Insights"]
        
        # Write to CSV file
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            
            for item in data:
                writer.writerow([
                    item.get("sr_no"),
                    item.get("title"),
                    item.get("url"),
                    item.get("published_at"),
                    item.get("language", "Unknown"),
                    item.get("duration", "Unknown"),
                    item.get("insight")
                ])
        
        return file_path
    except Exception as e:
        raise Exception(f"Error exporting to CSV: {str(e)}")

def export_to_sheet(data, brand_name="Brand", make_public=True, fallback_to_csv=True):
    """
    Export data to a Google Sheet with optional fallback to CSV if Google Sheets export fails.
    
    Args:
        data: List of dictionaries containing data to export
        brand_name: Name of the brand being analyzed
        make_public: Whether to make the sheet publicly accessible (default: True)
        fallback_to_csv: Whether to fall back to CSV export if Google Sheets export fails (default: True)
        
    Returns:
        Dictionary containing:
            - 'url': URL of the created Google Sheet or path to CSV file
            - 'export_type': 'google_sheet' or 'csv' indicating which export method was used
        
    Raises:
        ValueError: If the Google service account file is not set
        Exception: For other errors when both Google Sheets and CSV export fail
    """
    # Check if SERVICE_FILE is None and raise a more descriptive error
    if not SERVICE_FILE:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_FILE environment variable is not set or is empty")
    
    try:
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

        return {
            'url': f"https://docs.google.com/spreadsheets/d/{sheet_id}",
            'export_type': 'google_sheet'
        }
    except Exception as e:
        # Check for storage quota exceeded error
        error_message = str(e)
        if "storage quota has been exceeded" in error_message:
            if fallback_to_csv:
                try:
                    # Attempt to export to CSV as fallback
                    csv_path = export_to_csv(data, brand_name)
                    return {
                        'url': csv_path,
                        'export_type': 'csv',
                        'message': "Google Drive storage quota exceeded. Data has been exported to CSV instead."
                    }
                except Exception as csv_error:
                    # Both Google Sheets and CSV export failed
                    raise Exception(
                        f"Failed to export to Google Sheets due to storage quota exceeded, and CSV fallback also failed: {str(csv_error)}"
                    )
            else:
                # No fallback requested, raise the original error with suggestions
                raise Exception(
                    "Google Drive storage quota has been exceeded. Please try one of the following solutions:\n"
                    "1. Delete unnecessary files from your Google Drive to free up space\n"
                    "2. Upgrade your Google Drive storage plan\n"
                    "3. Use a different Google account with more available storage\n"
                    "4. Set fallback_to_csv=True to automatically export to CSV when Google Sheets export fails"
                )
        # Re-raise other exceptions
        raise
