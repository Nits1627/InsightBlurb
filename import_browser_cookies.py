import browser_cookie3
import instaloader
import argparse
import sys

def import_cookies_from_browser(browser_name, username=None):
    """
    Import Instagram cookies from a browser and create an Instaloader session.
    
    Args:
        browser_name: Name of the browser ('chrome', 'firefox', 'edge', 'opera', 'safari')
        username: Instagram username to associate with the session
        
    Returns:
        Instaloader instance with cookies loaded
    """
    print(f"Importing cookies from {browser_name}...")
    
    try:
        # Get cookies from the specified browser
        if browser_name.lower() == 'chrome':
            cookies = browser_cookie3.chrome(domain_name='instagram.com')
        elif browser_name.lower() == 'firefox':
            cookies = browser_cookie3.firefox(domain_name='instagram.com')
        elif browser_name.lower() == 'edge':
            cookies = browser_cookie3.edge(domain_name='instagram.com')
        elif browser_name.lower() == 'opera':
            cookies = browser_cookie3.opera(domain_name='instagram.com')
        elif browser_name.lower() == 'safari':
            cookies = browser_cookie3.safari(domain_name='instagram.com')
        else:
            raise ValueError(f"Unsupported browser: {browser_name}")
        
        # Create Instaloader instance
        loader = instaloader.Instaloader(max_connection_attempts=3)
        
        # Update session cookies
        loader.context._session.cookies.update(cookies)
        
        # Test login
        detected_username = loader.test_login()
        if not detected_username:
            print("Warning: Not logged in. Make sure you are logged into Instagram in your browser.")
            return None
        
        print(f"Successfully imported session for user: {detected_username}")
        
        # Save username to context
        loader.context.username = detected_username
        
        # Save session to file if username is provided
        if username:
            session_filename = f"{username}" if username else f"{detected_username}"
            loader.save_session_to_file(session_filename)
            print(f"Session saved to file: {session_filename}")
        
        return loader
    
    except Exception as e:
        print(f"Error importing cookies: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Import Instagram cookies from browser')
    parser.add_argument('browser', choices=['chrome', 'firefox', 'edge', 'opera', 'safari'],
                        help='Browser to import cookies from')
    parser.add_argument('-u', '--username', help='Instagram username to save session for')
    parser.add_argument('-t', '--test', action='store_true', help='Test fetching a profile after importing cookies')
    parser.add_argument('-p', '--profile', default='instagram', help='Profile to test fetching (default: instagram)')
    
    args = parser.parse_args()
    
    # Import cookies
    loader = import_cookies_from_browser(args.browser, args.username)
    if not loader:
        sys.exit(1)
    
    # Test fetching a profile if requested
    if args.test:
        try:
            print(f"\nTesting by fetching profile: {args.profile}")
            profile = instaloader.Profile.from_username(loader.context, args.profile)
            
            print(f"Profile name: {profile.full_name}")
            print(f"Biography: {profile.biography}")
            print(f"Followers: {profile.followers}")
            
            print("\nFetching first post...")
            for post in profile.get_posts():
                print(f"Post: https://www.instagram.com/p/{post.shortcode}/")
                print(f"Date: {post.date_local}")
                print(f"Likes: {post.likes}")
                print(f"Comments: {post.comments}")
                break
                
            print("\nTest successful!")
        except Exception as e:
            print(f"Test failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()