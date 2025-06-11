import os
import json
import streamlit as st

def load_env():
    # Load API keys
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
    os.environ["YOUTUBE_API_KEY"] = st.secrets["YOUTUBE_API_KEY"]
    os.environ["YOUR_EMAIL"] = st.secrets["YOUR_EMAIL"]

    # Write service account JSON to a temporary file
    with open("credentials.json", "w") as f:
        json.dump(st.secrets["GOOGLE_SERVICE_ACCOUNT_FILE"], f)

    os.environ["GOOGLE_SERVICE_ACCOUNT_FILE"] = "credentials.json"
