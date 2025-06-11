import os
import google.generativeai as genai
from datetime import datetime

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use Pro variant for more comprehensive analysis
model = genai.GenerativeModel("models/gemini-1.5-pro")

def get_instagram_analysis(account_name, account_url, years_back):
    """
    Analyze Instagram posts and campaigns for a brand using Gemini AI.
    
    Args:
        account_name: Instagram account name
        account_url: URL of the Instagram account
        years_back: Number of years to look back (1-10)
        
    Returns:
        List of dictionaries containing post analysis data
    """
    # Get posts data
    posts_data = identify_instagram_posts(account_name, account_url, years_back)
    
    # Analyze posts
    analyzed_posts = analyze_instagram_posts(account_name, posts_data)
    
    # Format for export
    return format_for_export(analyzed_posts)

def identify_instagram_posts(account_name, account_url, years_back):
    """
    Identify major Instagram posts and campaigns using Gemini AI.
    
    Args:
        account_name: Instagram account name
        account_url: URL of the Instagram account
        years_back: Number of years to look back (1-10)
        
    Returns:
        Text containing identified posts
    """
    current_year = datetime.now().year
    start_year = current_year - years_back
    
    prompt = f"""
    You are a social media analyst specializing in Instagram marketing campaigns.
    
    For the Instagram account @{account_name} ({account_url}), identify the major posts, campaigns, and events 
    they have shared on Instagram from {start_year} to {current_year} (past {years_back} years).
    
    For each major post or campaign, provide:
    1. Post name or campaign title
    2. Approximate date (month and year)
    3. A direct link to the post (if you can reasonably guess it based on Instagram URL patterns, otherwise state "Link unavailable")
    4. Brief description of what the post or campaign was about
    
    Focus on:
    - Product launches
    - Major marketing campaigns
    - Viral posts
    - Special events or announcements
    - Collaborations with influencers or other brands
    - Seasonal campaigns
    
    Format your response as a structured list with clear sections for each post/campaign.
    Include at least 10-15 major posts/campaigns if possible.
    
    If you don't have specific information about this account's posts, make educated guesses based on:
    1. Typical posting patterns for brands in their industry
    2. Standard seasonal campaigns
    3. Likely product launches or events based on the brand's profile
    
    Clearly indicate when you are making an educated guess versus providing known information.
    """
    
    try:
        response = model.generate_content(prompt)
        posts_data = response.text.strip()
    except Exception as e:
        posts_data = f"Could not identify Instagram posts: {e}"
    
    return posts_data

def analyze_instagram_posts(account_name, posts_data):
    """
    Analyze identified Instagram posts using Gemini AI.
    
    Args:
        account_name: Instagram account name
        posts_data: Text containing identified posts
        
    Returns:
        Text containing post analysis
    """
    prompt = f"""
    Based on the following list of Instagram posts and campaigns for @{account_name}:
    
    {posts_data}
    
    Provide a detailed analysis of each post/campaign. For each one, include:
    
    1. Why this post/campaign was likely successful
    2. The key marketing strategies employed
    3. The target audience it was likely aimed at
    4. How it contributed to the brand's overall social media presence
    5. Lessons other brands could learn from this post/campaign
    
    Format your response as a structured analysis with clear sections for each post/campaign.
    """
    
    try:
        response = model.generate_content(prompt)
        analysis = response.text.strip()
    except Exception as e:
        analysis = f"Analysis not available: {e}"
    
    return {
        "posts": posts_data,
        "analysis": analysis
    }

def format_for_export(analysis_data):
    """
    Format the Instagram analysis data for export to Google Sheets.
    
    Args:
        analysis_data: Dictionary containing posts and analysis data
        
    Returns:
        List of dictionaries formatted for export
    """
    export_data = []
    
    # Parse the posts data to extract individual posts
    posts_text = analysis_data["posts"]
    analysis_text = analysis_data["analysis"]
    
    # Split the text into lines
    lines = posts_text.split('\n')
    
    # Variables to track current post
    current_post = {}
    post_count = 0
    
    # Process each line to extract post information
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Check if this line starts a new post (usually numbered or with a clear title pattern)
        if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.', '11.', '12.', '13.', '14.', '15.')) or \
           (line.startswith('Post') and ':' in line) or \
           (line.startswith('Campaign') and ':' in line):
            
            # If we have a current post with data, add it to export_data
            if current_post and 'title' in current_post:
                export_data.append(current_post)
            
            # Start a new post
            post_count += 1
            current_post = {
                "sr_no": post_count,
                "title": "",
                "date": "",
                "url": "",
                "description": "",
                "insight": ""
            }
            
            # Extract title if possible
            if ':' in line:
                parts = line.split(':', 1)
                current_post["title"] = parts[1].strip()
            else:
                # Remove numbering
                for prefix in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.', '11.', '12.', '13.', '14.', '15.']:
                    if line.startswith(prefix):
                        current_post["title"] = line[len(prefix):].strip()
                        break
        
        # Extract date if this line contains date information
        elif 'date' in line.lower() or any(month in line.lower() for month in ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']):
            if 'date' not in current_post or not current_post["date"]:
                if ':' in line:
                    current_post["date"] = line.split(':', 1)[1].strip()
                else:
                    current_post["date"] = line
        
        # Extract URL if this line contains URL information
        elif 'link' in line.lower() or 'url' in line.lower() or 'instagram.com' in line.lower():
            if 'url' not in current_post or not current_post["url"]:
                if ':' in line:
                    url_part = line.split(':', 1)[1].strip()
                    if 'unavailable' not in url_part.lower() and 'instagram.com' in url_part:
                        current_post["url"] = url_part
                    elif 'instagram.com' in line:
                        # Try to extract URL from the line
                        words = line.split()
                        for word in words:
                            if 'instagram.com' in word:
                                current_post["url"] = word
                                break
        
        # Add to description for all other lines
        elif current_post and 'title' in current_post:
            if 'description' not in current_post:
                current_post["description"] = line
            else:
                current_post["description"] += "\n" + line
    
    # Add the last post if it exists
    if current_post and 'title' in current_post:
        export_data.append(current_post)
    
    # Try to match insights from analysis to posts
    # This is a simplified approach - in a real implementation, you'd want more sophisticated matching
    analysis_sections = analysis_text.split('\n\n')
    
    for i, post in enumerate(export_data):
        # Find a matching section in the analysis
        for section in analysis_sections:
            if post["title"] in section:
                post["insight"] = section
                break
        
        # If no match found, use a generic insight or the first available section
        if not post["insight"] and i < len(analysis_sections):
            post["insight"] = analysis_sections[i]
    
    return export_data

def get_instagram_analysis(instagram_handle):
    """
    Analyze Instagram account using Gemini AI.
    
    Args:
        instagram_handle: Instagram handle (username)
        
    Returns:
        Dictionary containing profile analysis, content analysis, audience analysis, and recommendations
    """
    # Generate Instagram profile URL
    account_url = f"https://www.instagram.com/{instagram_handle}/"
    
    # Analyze Instagram profile
    analysis = analyze_instagram_profile(instagram_handle, account_url)
    
    return analysis

def analyze_instagram_profile(instagram_handle, account_url):
    """
    Analyze Instagram profile using Gemini AI.
    
    Args:
        instagram_handle: Instagram handle (username)
        account_url: URL of the Instagram account
        
    Returns:
        Dictionary containing profile analysis, content analysis, audience analysis, and recommendations
    """
    prompt = f"""
    You are a social media marketing expert specializing in Instagram analytics.
    
    Provide a comprehensive analysis of the Instagram account @{instagram_handle} ({account_url}).
    
    Your analysis should include:
    
    1. Profile Analysis:
       - Overall brand identity and positioning on Instagram
       - Profile optimization (bio, highlights, link usage)
       - Visual consistency and branding elements
    
    2. Content Analysis:
       - Content themes and categories
       - Post frequency and timing patterns
       - Content formats (feed posts, Stories, Reels, IGTV)
       - Visual aesthetics and quality
       - Caption strategy and voice
       - Hashtag strategy
    
    3. Audience Analysis:
       - Estimated target demographic
       - Engagement patterns
       - Community building efforts
       - Audience growth strategies
    
    4. Recommendations:
       - Specific actionable improvements for their Instagram strategy
       - Content opportunities they're missing
       - Engagement tactics they should implement
       - Growth strategies tailored to their niche
    
    Format your response with clear section headers and concise, actionable insights.
    If you don't have specific information about this account, make educated guesses based on industry standards and best practices, but clearly indicate when you are making assumptions.
    """
    
    try:
        response = model.generate_content(prompt)
        analysis_text = response.text.strip()
        
        # Parse the analysis into sections
        sections = parse_analysis_sections(analysis_text)
        
        return sections
    except Exception as e:
        return {
            "profile_analysis": f"Analysis not available: {e}",
            "content_analysis": "Not available",
            "audience_analysis": "Not available",
            "recommendations": "Not available"
        }

def parse_analysis_sections(analysis_text):
    """
    Parse the analysis text into sections.
    
    Args:
        analysis_text: Full analysis text from Gemini
        
    Returns:
        Dictionary with sections as keys
    """
    sections = {
        "profile_analysis": "",
        "content_analysis": "",
        "audience_analysis": "",
        "recommendations": ""
    }
    
    current_section = None
    lines = analysis_text.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Identify section headers
        lower_line = line.lower()
        if "profile analysis" in lower_line or "1. profile" in lower_line:
            current_section = "profile_analysis"
        elif "content analysis" in lower_line or "2. content" in lower_line:
            current_section = "content_analysis"
        elif "audience analysis" in lower_line or "3. audience" in lower_line:
            current_section = "audience_analysis"
        elif "recommendations" in lower_line or "4. recommend" in lower_line:
            current_section = "recommendations"
        
        # Add content to current section
        if current_section and line:
            if sections[current_section]:
                sections[current_section] += "\n" + line
            else:
                sections[current_section] = line
    
    return sections