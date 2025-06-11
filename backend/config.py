import os
from dotenv import load_dotenv

def load_env():
    load_dotenv()

    # Ensure critical environment variables are set
    # Gemini
    if not os.environ.get("GEMINI_API_KEY"):
        print("Warning: GEMINI_API_KEY not set")
    
    # YouTube
    if not os.environ.get("YOUTUBE_API_KEY"):
        print("Warning: YOUTUBE_API_KEY not set")
    
    # Google Sheets
    if not os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE"):
        print("Warning: GOOGLE_SERVICE_ACCOUNT_FILE not set")
        
    if not os.environ.get("YOUR_EMAIL"):
        print("Warning: YOUR_EMAIL not set")
    os.environ.get("GOOGLE_SHEET_ID")