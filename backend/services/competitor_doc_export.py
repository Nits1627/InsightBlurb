import os
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive"
]

# Use os.environ.get instead of os.getenv for consistency with config.py
SERVICE_FILE = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE")
YOUR_EMAIL = os.environ.get("YOUR_EMAIL")

def export_competitor_analysis_to_doc(data, brand_name="Brand", make_public=True):
    """
    Export competitor analysis data to a Google Doc.
    
    Args:
        data: List of dictionaries containing competitor analysis data
        brand_name: Name of the brand being analyzed
        make_public: Whether to make the document publicly accessible (default: True)
        
    Returns:
        URL of the created Google Doc
    """
    # Check if SERVICE_FILE is None and raise a more descriptive error
    if not SERVICE_FILE:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_FILE environment variable is not set or is empty")
        
    creds = Credentials.from_service_account_file(SERVICE_FILE, scopes=SCOPES)
    
    # Build Docs and Drive services
    docs_service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    # Generate dynamic document title
    today = datetime.now().strftime("%Y-%m-%d")
    doc_title = f"Competitor Analysis - {brand_name} - {today}"

    # Step 1: Create the new Google Doc
    doc_metadata = {
        "title": doc_title
    }
    doc = docs_service.documents().create(body=doc_metadata).execute()
    doc_id = doc.get("documentId")

    # Step 2: Prepare the content
    requests = []
    
    # Add title
    requests.append({
        "insertText": {
            "location": {
                "index": 1
            },
            "text": f"Competitor Analysis: {brand_name}\n\n"
        }
    })
    
    # Format title
    requests.append({
        "updateParagraphStyle": {
            "range": {
                "startIndex": 1,
                "endIndex": len(f"Competitor Analysis: {brand_name}\n\n") + 1
            },
            "paragraphStyle": {
                "namedStyleType": "TITLE"
            },
            "fields": "namedStyleType"
        }
    })
    
    # Current index to track position in document
    current_index = len(f"Competitor Analysis: {brand_name}\n\n") + 1
    
    # Add each section
    for item in data:
        section = item.get("section", "")
        name = item.get("name", "")
        website = item.get("website", "")
        details = item.get("details", "")
        item_type = item.get("type", "")
        
        # Add section header
        section_text = f"{section}\n"
        requests.append({
            "insertText": {
                "location": {
                    "index": current_index
                },
                "text": section_text
            }
        })
        
        # Format section header with different styles based on section type
        header_style = "HEADING_1"
        
        # Use a special style for recommendations section
        if "Recommendations" in section or "Strategies" in section:
            header_style = "HEADING_1"
            
            # Add a special color to recommendations header
            requests.append({
                "updateTextStyle": {
                    "range": {
                        "startIndex": current_index,
                        "endIndex": current_index + len(section_text)
                    },
                    "textStyle": {
                        "foregroundColor": {
                            "color": {
                                "rgbColor": {
                                    "red": 0.0,
                                    "green": 0.5,
                                    "blue": 0.3
                                }
                            }
                        },
                        "bold": True
                    },
                    "fields": "foregroundColor,bold"
                }
            })
        
        requests.append({
            "updateParagraphStyle": {
                "range": {
                    "startIndex": current_index,
                    "endIndex": current_index + len(section_text)
                },
                "paragraphStyle": {
                    "namedStyleType": header_style
                },
                "fields": "namedStyleType"
            }
        })
        
        current_index += len(section_text)
        
        # Add name and website if available
        if name or website:
            name_website_text = ""
            if name:
                name_website_text += f"Name: {name}\n"
            if website:
                name_website_text += f"Website: {website}\n"
            
            requests.append({
                "insertText": {
                    "location": {
                        "index": current_index
                    },
                    "text": name_website_text
                }
            })
            
            # Format name and website
            requests.append({
                "updateTextStyle": {
                    "range": {
                        "startIndex": current_index,
                        "endIndex": current_index + len(name_website_text)
                    },
                    "textStyle": {
                        "bold": True
                    },
                    "fields": "bold"
                }
            })
            
            current_index += len(name_website_text)
        
        # Add details
        if details:
            details_text = f"{details}\n\n"
            requests.append({
                "insertText": {
                    "location": {
                        "index": current_index
                    },
                    "text": details_text
                }
            })
            current_index += len(details_text)
    
    # Execute the requests
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": requests}
    ).execute()

    # Share the document with your email
    if YOUR_EMAIL:
        permission = {
            "type": "user",
            "role": "writer",
            "emailAddress": YOUR_EMAIL
        }
        drive_service.permissions().create(
            fileId=doc_id,
            body=permission,
            fields="id",
            sendNotificationEmail=False
        ).execute()
    
    # Make the document public if requested
    if make_public:
        # Create a permission for anyone to access the document
        public_permission = {
            "type": "anyone",
            "role": "reader"
        }
        drive_service.permissions().create(
            fileId=doc_id,
            body=public_permission,
            fields="id"
        ).execute()

    return f"https://docs.google.com/document/d/{doc_id}/edit"
