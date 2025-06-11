import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()  # Make sure this loads your .env file

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

try:
    models = genai.list_models()
    print("✅ Gemini Key Working. Available Models:")
    for model in models:
        print("-", model.name)
except Exception as e:
    print("❌ Gemini Error:\n", e)