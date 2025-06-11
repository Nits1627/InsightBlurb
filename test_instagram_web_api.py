import json
from instagram_web_api import Client, ClientCompatPatch, ClientError

def get_instagram_posts(username, count=10):
    """Fetch public Instagram posts for a given username without authentication"""
    try:
        # Initialize web API client without authentication
        web_api = Client(auto_patch=True, drop_incompat_keys=False)
        
        # First get the user ID from username
        user_info = web_api.user_info2(username)
        user_id = user_info.get('id')
        
        if not user_id:
            print(f"Could not find user ID for username: {username}")
            return []
        
        # Fetch user feed using the user ID
        user_feed = web_api.user_feed(user_id, count=count)
        
        # Process the posts to extract relevant information
        posts = []
        for post in user_feed:
            # Apply compatibility patch to make the data structure more consistent
            ClientCompatPatch.media(post)
            
            # Extract the data we need
            post_data = {
                'link': post.get('link', ''),
                'date': post.get('taken_at', ''),
                'caption': post.get('caption', {}).get('text', '') if post.get('caption') else '',
                'likes': post.get('like_count', 0),
                'comments': post.get('comment_count', 0),
                'media_type': post.get('media_type', ''),
                'id': post.get('code', '')
            }
            posts.append(post_data)
        
        return posts
    
    except ClientError as e:
        print(f"Instagram API error: {e}")
        return []
    except Exception as e:
        print(f"Error fetching Instagram posts: {e}")
        return []

# Test the function with a public Instagram account
if __name__ == "__main__":
    # Try with a popular public Instagram account
    username = "instagram"
    posts = get_instagram_posts(username, count=5)
    
    if posts:
        print(f"Successfully fetched {len(posts)} posts from {username}")
        for i, post in enumerate(posts, 1):
            print(f"\nPost {i}:")
            print(f"Link: {post['link']}")
            print(f"Date: {post['date']}")
            print(f"Likes: {post['likes']}")
            print(f"Comments: {post['comments']}")
            print(f"Caption: {post['caption'][:100]}..." if len(post['caption']) > 100 else f"Caption: {post['caption']}")
    else:
        print(f"No posts fetched from {username}")