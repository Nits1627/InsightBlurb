import os
import instaloader
import time
import random
import google.generativeai as genai
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API with the latest model
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use the latest Gemini 1.5 Pro model for best performance
# This can be updated to Gemini 2.0 or 2.5 when available
model = genai.GenerativeModel("models/gemini-1.5-pro")

def fetch_instagram_posts(instagram_handle, max_posts=20, years_back=1):
    """
    Fetch Instagram posts using instaloader without authentication.
    
    Args:
        instagram_handle: Instagram handle (username)
        max_posts: Maximum number of posts to fetch
        years_back: Number of years to look back
        
    Returns:
        List of post data dictionaries with link, date, caption, likes, comments
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * years_back)
        
        print(f"Fetching posts for {instagram_handle} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        # Initialize Instaloader
        loader = instaloader.Instaloader()
        
        # Get profile
        print(f"Getting profile for {instagram_handle}...")
        profile = instaloader.Profile.from_username(loader.context, instagram_handle)
        
        print(f"Profile: {profile.full_name}")
        print(f"Followers: {profile.followers}")
        print(f"Following: {profile.followees}")
        print(f"Biography: {profile.biography}")
        
        # Get posts
        posts = []
        post_count = 0
        
        print(f"Fetching posts...")
        # Iterate through profile posts
        for post in profile.get_posts():
            # Check if post is within date range
            post_date = post.date_local
            if post_date >= start_date:
                # Get post details
                post_data = {
                    "link": f"https://www.instagram.com/p/{post.shortcode}/",
                    "date": post_date.strftime("%Y-%m-%d"),
                    "caption": post.caption if post.caption else "",
                    "likes": post.likes,
                    "comments": post.comments
                }
                posts.append(post_data)
                post_count += 1
                
                print(f"Post {post_count}: {post_data['link']} - {post_data['date']}")
                
                # Add a small delay to avoid rate limiting
                time.sleep(random.uniform(1, 2))
                
                # Limit the number of posts
                if post_count >= max_posts:
                    break
            elif post_date < start_date:
                # Posts are in chronological order, so we can stop once we reach posts older than start_date
                break
        
        print(f"Successfully fetched {len(posts)} posts for {instagram_handle}")
        return posts
    except Exception as e:
        print(f"Error in fetch_instagram_posts: {e}")
        return []

def analyze_instagram_posts(instagram_handle, posts_data):
    """
    Analyze Instagram posts using the latest Gemini AI model.
    
    Args:
        instagram_handle: Instagram handle (username)
        posts_data: List of post data dictionaries
        
    Returns:
        List of dictionaries with post data and insights
    """
    analyzed_posts = []
    
    for post in posts_data:
        # Create prompt for Gemini
        prompt = f"""
        You are a social media marketing expert specializing in Instagram campaign analysis.
        
        Analyze the following Instagram post from @{instagram_handle}:
        
        Post URL: {post['link']}
        Date: {post['date']}
        Caption: {post['caption']}
        Likes: {post['like_count'] if 'like_count' in post else post['likes']}
        Comments: {post['comment_count'] if 'comment_count' in post else post['comments']}
        
        Provide a brief but insightful analysis of this post, including:
        1. The likely campaign or marketing objective
        2. Target audience
        3. Key messaging and strategy
        4. Effectiveness based on engagement metrics
        5. How this fits into the brand's overall Instagram strategy
        
        Keep your analysis concise (3-5 sentences) but insightful.
        """
        
        try:
            # Get insight from Gemini
            response = model.generate_content(prompt)
            insight = response.text.strip()
            print(f"Generated insight for post: {post['link']}")
        except Exception as e:
            insight = f"Analysis not available: {e}"
            print(f"Error generating insight: {e}")
        
        # Add insight to post data
        analyzed_post = {
            "post_link": post['link'],
            "date": post['date'],
            "insight": insight
        }
        analyzed_posts.append(analyzed_post)
        
        # Add a small delay between API calls
        time.sleep(1)
    
    return analyzed_posts

def generate_hypothetical_campaigns(instagram_handle, years_back=1):
    """
    Generate hypothetical campaign data using Gemini when instaloader fails.
    
    Args:
        instagram_handle: Instagram handle (username)
        years_back: Number of years to look back
        
    Returns:
        List of dictionaries with hypothetical post data
    """
    current_year = datetime.now().year
    start_year = current_year - years_back
    
    prompt = f"""
    You are a social media analyst specializing in Instagram marketing campaigns.
    
    For the Instagram account @{instagram_handle}, create a list of 10-15 hypothetical major posts or campaigns 
    they might have shared on Instagram from {start_year} to {current_year} (past {years_back} years).
    
    For each post, provide:
    1. A realistic Instagram post link (using the format https://www.instagram.com/p/[10-character code]/).
    2. A realistic date between {start_year} and {current_year} (format: YYYY-MM-DD).
    3. A brief but insightful analysis of what this post likely contained and its marketing significance.
    
    Format your response as a JSON-like structure with these exact fields for each post:
    {{"post_link": "https://www.instagram.com/p/AbCdEfGhIj/", "date": "YYYY-MM-DD", "insight": "Analysis text here"}}
    
    Make the posts diverse in terms of content types, campaign objectives, and dates throughout the year(s).
    """
    
    try:
        print(f"Generating hypothetical campaigns for {instagram_handle}...")
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Parse the response to extract posts
        posts = []
        current_post = {}
        in_post = False
        
        for line in response_text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check for start of a post entry
            if '{"post_link":' in line or '{"post_link" :' in line or line.startswith('{'):
                in_post = True
                current_post = {}
                
                # Extract post link if present in this line
                if 'post_link' in line and 'instagram.com/p/' in line:
                    start_idx = line.find('https://')
                    end_idx = line.find('"', start_idx + 8)
                    if start_idx != -1 and end_idx != -1:
                        current_post['post_link'] = line[start_idx:end_idx]
            
            # Extract date if present
            if 'date' in line and in_post:
                parts = line.split('"date":')
                if len(parts) > 1:
                    date_part = parts[1].strip()
                    if '"' in date_part:
                        date_str = date_part.split('"')[1]
                        if '-' in date_str and len(date_str.split('-')) == 3:
                            current_post['date'] = date_str
            
            # Extract insight if present
            if 'insight' in line and in_post:
                parts = line.split('"insight":')
                if len(parts) > 1:
                    insight_part = parts[1].strip()
                    if '"' in insight_part:
                        insight_str = insight_part.split('"')[1]
                        current_post['insight'] = insight_str
            
            # Check for end of a post entry
            if line.endswith('},') or line.endswith('}'):
                in_post = False
                if 'post_link' in current_post and 'date' in current_post and 'insight' in current_post:
                    posts.append(current_post)
                    current_post = {}
        
        # If parsing failed or no posts found, create basic fallback data
        if not posts:
            print("Parsing failed, creating fallback data...")
            posts = create_fallback_posts(instagram_handle, years_back)
        
        print(f"Generated {len(posts)} hypothetical posts")
        return posts
    except Exception as e:
        print(f"Error generating hypothetical campaigns: {e}")
        return create_fallback_posts(instagram_handle, years_back)

def create_fallback_posts(instagram_handle, years_back):
    """
    Create basic fallback posts when all else fails.
    
    Args:
        instagram_handle: Instagram handle (username)
        years_back: Number of years to look back
        
    Returns:
        List of dictionaries with basic post data
    """
    current_year = datetime.now().year
    start_year = current_year - years_back
    
    fallback_posts = []
    for i in range(10):
        month = (i % 12) + 1
        day = (i % 28) + 1
        year = start_year + (i // 12)
        date = f"{year}-{month:02d}-{day:02d}"
        
        code = ''.join([chr(ord('A') + (i * 3 + j) % 26) for j in range(10)])
        post_link = f"https://www.instagram.com/p/{code}/"
        
        insight = f"This appears to be a promotional post for {instagram_handle}'s products or services. It likely featured engaging visuals and targeted their core audience with seasonal messaging appropriate for {month:02d}/{year}."
        
        fallback_posts.append({
            "post_link": post_link,
            "date": date,
            "insight": insight
        })
    
    return fallback_posts

def main():
    # Example usage
    username = "instagram"  # Example username
    
    # Fetch posts
    posts = fetch_instagram_posts(username, max_posts=5)
    
    if posts:
        print("\nAnalyzing posts with Gemini...")
        analyzed_posts = analyze_instagram_posts(username, posts)
        
        print("\nAnalyzed posts:")
        for i, post in enumerate(analyzed_posts, 1):
            print(f"\nPost {i}:")
            print(f"Link: {post['post_link']}")
            print(f"Date: {post['date']}")
            print(f"Insight: {post['insight']}")
    else:
        print("No posts were fetched. Generating hypothetical data...")
        hypothetical_posts = generate_hypothetical_campaigns(username)
        
        print("\nHypothetical posts:")
        for i, post in enumerate(hypothetical_posts, 1):
            print(f"\nPost {i}:")
            print(f"Link: {post['post_link']}")
            print(f"Date: {post['date']}")
            print(f"Insight: {post['insight']}")

if __name__ == "__main__":
    main()