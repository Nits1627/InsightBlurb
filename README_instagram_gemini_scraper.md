# Instagram Gemini Scraper

This tool fetches Instagram posts and analyzes them using Google's Gemini AI model to provide marketing insights.

## Features

- Fetches Instagram profile information and posts without requiring login
- Uses the latest Gemini 1.5 Pro model for AI-powered analysis
- Provides marketing insights for each post including campaign objectives, target audience, and effectiveness
- Generates hypothetical campaign data when real posts can't be fetched
- Handles rate limiting and errors gracefully

## Requirements

- Python 3.6+
- instaloader
- google-generativeai
- python-dotenv

## Setup

1. Install required packages:
   ```
   pip install instaloader google-generativeai python-dotenv
   ```

2. Create a `.env` file in the project directory with your Gemini API key:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Usage

### Basic Usage

Run the script with a default Instagram handle:

```bash
python instagram_gemini_scraper.py
```

### Customizing the Script

To use a different Instagram handle or modify the number of posts fetched, edit the `main()` function in the script:

```python
def main():
    # Change the username here
    username = "your_target_instagram_handle"  
    
    # Change the number of posts to fetch
    posts = fetch_instagram_posts(username, max_posts=10)
    
    # Rest of the function...
```

## Functions

### `fetch_instagram_posts(instagram_handle, max_posts=20, years_back=1)`

Fetches Instagram posts for a given handle within a specified time range.

- `instagram_handle`: Instagram username to fetch posts from
- `max_posts`: Maximum number of posts to fetch (default: 20)
- `years_back`: Number of years to look back for posts (default: 1)

### `analyze_instagram_posts(instagram_handle, posts_data)`

Analyzes fetched posts using the Gemini AI model.

- `instagram_handle`: Instagram username the posts belong to
- `posts_data`: List of post data dictionaries from `fetch_instagram_posts`

### `generate_hypothetical_campaigns(instagram_handle, years_back=1)`

Generates hypothetical campaign data when real posts can't be fetched.

- `instagram_handle`: Instagram username to generate hypothetical posts for
- `years_back`: Number of years to look back (default: 1)

## Error Handling

The script includes robust error handling:

1. If Instagram posts can't be fetched (due to rate limiting or other issues), it falls back to generating hypothetical data
2. If the Gemini API encounters errors, it provides a fallback insight message
3. If parsing of Gemini's response fails, it creates basic fallback post data

## Notes

- Instagram's API policies may change, affecting the ability to fetch posts without authentication
- The script includes delays between requests to avoid rate limiting
- For production use, consider implementing proper session management with browser cookies

## Updating the Gemini Model

To use a newer version of the Gemini model when available, update the model initialization line:

```python
# Update this line to use newer models when available
model = genai.GenerativeModel("models/gemini-2.0-pro")  # or newer version
```