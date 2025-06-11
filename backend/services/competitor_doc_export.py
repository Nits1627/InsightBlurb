import streamlit as st
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive"
]

def export_competitor_analysis_to_doc(data, brand_name="Brand", make_public=True):
    """
    Export competitor analysis data to a Google Doc (Streamlit Cloud safe).
    """
    # Credentials from Streamlit secrets (dict, not file)
    service_account_info = st.secrets["GOOGLE_SERVICE_ACCOUNT_FILE"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    YOUR_EMAIL = st.secrets.get("YOUR_EMAIL")

    docs_service = build("docs", "v1", credentials=creds)
    drive_service = build("drive", "v3", credentials=creds)

    today = datetime.now().strftime("%Y-%m-%d")
    doc_title = f"Competitor Analysis - {brand_name} - {today}"

    # Step 1: Create the new Google Doc
    doc_metadata = {"title": doc_title}
    doc = docs_service.documents().create(body=doc_metadata).execute()
    doc_id = doc.get("documentId")

    # Step 2: Prepare the content
    requests = []

    # Add title
    main_title = f"Competitor Analysis: {brand_name}\n\n"
    requests.append({
        "insertText": {
            "location": {"index": 1},
            "text": main_title
        }
    })
    requests.append({
        "updateParagraphStyle": {
            "range": {"startIndex": 1, "endIndex": len(main_title) + 1},
            "paragraphStyle": {"namedStyleType": "TITLE"},
            "fields": "namedStyleType"
        }
    })

    current_index = len(main_title) + 1

    # Add each section
    for item in data:
        section = item.get("section", "")
        name = item.get("name", "")
        website = item.get("website", "")
        details = item.get("details", "")
        item_type = item.get("type", "")

        # Section header
        section_text = f"{section}\n"
        requests.append({
            "insertText": {
                "location": {"index": current_index},
                "text": section_text
            }
        })
        header_style = "HEADING_1"
        requests.append({
            "updateParagraphStyle": {
                "range": {"startIndex": current_index, "endIndex": current_index + len(section_text)},
                "paragraphStyle": {"namedStyleType": header_style},
                "fields": "namedStyleType"
            }
        })
        current_index += len(section_text)

        # Name and website
        if name or website:
            name_website_text = ""
            if name:
                name_website_text += f"Name: {name}\n"
            if website:
                name_website_text += f"Website: {website}\n"
            requests.append({
                "insertText": {
                    "location": {"index": current_index},
                    "text": name_website_text
                }
            })
            requests.append({
                "updateTextStyle": {
                    "range": {"startIndex": current_index, "endIndex": current_index + len(name_website_text)},
                    "textStyle": {"bold": True},
                    "fields": "bold"
                }
            })
            current_index += len(name_website_text)

        # Details
        if details:
            details_text = f"{details}\n\n"
            requests.append({
                "insertText": {
                    "location": {"index": current_index},
                    "text": details_text
                }
            })
            current_index += len(details_text)

    # Step 3: Push content to the doc
    docs_service.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": requests}
    ).execute()

    # Step 4: Share document with your email
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

    # Step 5: Make public if requested
    if make_public:
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
