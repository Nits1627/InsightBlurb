import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

try:
    model = genai.GenerativeModel('models/gemini-1.5-pro')
    response = model.generate_content("hi how are you")
    print("✅ Response:", response.text)
except Exception as e:
    print("❌ Gemini Error:", e)