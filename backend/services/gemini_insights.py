import os
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use Flash variant for quota efficiency
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

def get_video_insights(videos):
    enriched = []

    for video in videos:
        title = video.get("title", "")
        published = video.get("published_at", "Unknown date")

        prompt = f"""
You're a creative strategist at a top ad agency.

Based on the product name or video title provided below, write a concise and meaningful 2–3 line description explaining what this ad is likely showcasing.

Title: "{title}"
Published On: {published}

Avoid repeating the title verbatim. Think like you're briefing a client about the ad's purpose and positioning.
"""

        try:
            response = model.generate_content(prompt)
            insight = response.text.strip()
        except Exception as e:
            insight = f"Insight not available: {e}"

        enriched.append({
            **video,
            "insight": insight
        })

    return enriched