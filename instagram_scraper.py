import instaloader
import time
from datetime import datetime, timedelta
import random

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

def main():
    # Example usage
    username = "instagram"  # Example username
    posts = fetch_instagram_posts(username, max_posts=5)
    
    if posts:
        print("\nFetched posts:")
        for i, post in enumerate(posts, 1):
            print(f"\nPost {i}:")
            print(f"Link: {post['link']}")
            print(f"Date: {post['date']}")
            print(f"Likes: {post['likes']}")
            print(f"Comments: {post['comments']}")
            print(f"Caption: {post['caption'][:100]}..." if len(post['caption']) > 100 else f"Caption: {post['caption']}")
    else:
        print("No posts were fetched.")

if __name__ == "__main__":
    main()