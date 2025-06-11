import instaloader
import time

def test_instaloader():
    try:
        # Initialize Instaloader
        loader = instaloader.Instaloader()
        
        # Get profile
        profile = instaloader.Profile.from_username(loader.context, 'instagram')
        
        print(f'Profile name: {profile.full_name}')
        print(f'Biography: {profile.biography}')
        print(f'Followers: {profile.followers}')
        
        print('\nFirst 3 posts:')
        for i, post in enumerate(profile.get_posts()):
            print(f'Post {i+1}: https://www.instagram.com/p/{post.shortcode}/')
            print(f'  Date: {post.date_local}')
            print(f'  Likes: {post.likes}')
            print(f'  Comments: {post.comments}')
            print(f'  Caption: {post.caption[:100]}...' if post.caption and len(post.caption) > 100 else f'  Caption: {post.caption}')
            print('---')
            
            # Limit to 3 posts
            if i >= 2:
                break
                
            # Add a small delay to avoid rate limiting
            time.sleep(1)
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_instaloader()