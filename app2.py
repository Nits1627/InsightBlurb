import os
import streamlit as st
from backend.services.youtube_ads import get_channel_ads
from backend.services.gemini_insights import get_video_insights
from backend.services.sheets_export import export_to_sheet
from backend.services.competitor_analysis import get_competitor_analysis
from backend.services.competitor_doc_export import export_competitor_analysis_to_doc
from backend.services.competitor_export import export_competitor_analysis
from backend.services.instagram_analysis import get_instagram_analysis
from backend.services.instagram_export import export_instagram_analysis_to_sheet
from backend.config import load_env

load_env()

# Initialize session state for storing analysis results
if 'youtube_data' not in st.session_state:
    st.session_state.youtube_data = None
if 'competitor_data' not in st.session_state:
    st.session_state.competitor_data = None
if 'instagram_data' not in st.session_state:
    st.session_state.instagram_data = None
if 'channel_input_value' not in st.session_state:
    st.session_state.channel_input_value = None
if 'years_back_value' not in st.session_state:
    st.session_state.years_back_value = 7

# Set page config
st.set_page_config(page_title="InsightBlurb", page_icon="📊", layout="wide")

# Sidebar
with st.sidebar:
    st.title("InsightBlurb")
    st.write("AI-powered marketing research tool")
    
    # Theme selection
    st.subheader("Theme")
    theme = st.selectbox("Select theme", ["Light", "Dark"])
    
    # Public sharing option
    st.subheader("Sharing Options")
    make_public = st.checkbox("Make exported documents public", value=True)
    if make_public:
        st.success("Exported documents will be publicly accessible")
    else:
        st.info("Exported documents will be shared with your email only")

# Main content
tab1, tab2, tab3 = st.tabs(["Ad Analysis", "Competitor Analysis", "Instagram Analysis"])

# Ad Analysis Tab
with tab1:
    st.header("YouTube Ad Research")
    
    col1, col2 = st.columns(2)
    
    with col1:
        channel_input = st.text_input("Enter YouTube Channel Name, URL, or ID")
        
    with col2:
        col2a, col2b = st.columns(2)
        with col2a:
            search_terms = st.text_input("Enter search terms (comma separated)", 
                                        value="ad,commercial,official,campaign")
        with col2b:
            years_back = st.selectbox("Years to look back", options=list(range(1, 11)), index=6)
    
    if st.button("Analyze Ads", key="analyze_ads"):
        if channel_input:
            with st.spinner("Fetching YouTube ads..."):
                # Get YouTube ads
                videos = get_channel_ads(channel_input, years_back=years_back)
                
                if videos:
                    # Get insights for each video
                    with st.spinner("Generating insights with Gemini..."):
                        videos_with_insights = get_video_insights(videos)
                        
                    # Store in session state
                    st.session_state.youtube_data = videos_with_insights
                    st.session_state.channel_input_value = channel_input
                    st.session_state.years_back_value = years_back
                    
                    # Display results
                    st.subheader(f"Found {len(videos_with_insights)} potential ads")
                    
                    for i, video in enumerate(videos_with_insights):
                        with st.expander(f"{i+1}. {video['title']} ({video['published_at']})"): 
                            st.write(f"**URL:** {video['url']}")
                            st.write(f"**Published:** {video['published_at']}")
                            st.write(f"**Language:** {video.get('language', 'Unknown')}")
                            st.write(f"**Duration:** {video.get('duration', 'Unknown')}")
                            st.write(f"**Insight:** {video.get('insight', 'No insight available')}")
                else:
                    st.error("No ads found for this channel. Try different search terms or check the channel name/URL.")
        else:
            st.error("Please enter a YouTube channel name, URL, or ID.")
    
    # Show export button if data is available
    if st.session_state.youtube_data:
        if st.button("Export to Google Sheets", key="export_ads"):
            try:
                with st.spinner("Exporting to Google Sheets..."):
                    sheet_url = export_to_sheet(st.session_state.youtube_data, brand_name=f"{st.session_state.channel_input_value} ({st.session_state.years_back_value} years)", make_public=make_public)
                    
                    if make_public:
                        st.success(f"Exported to Google Sheets. The sheet is publicly accessible. [Open Sheet]({sheet_url})")
                    else:
                        st.success(f"Exported to Google Sheets. The sheet is shared with your email only. [Open Sheet]({sheet_url})")
            except Exception as e:
                st.error(f"Error exporting to Google Sheets: {e}")

# Competitor Analysis Tab
with tab2:
    st.header("Competitor Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        brand_name = st.text_input("Enter Brand Name", key="brand_name_input")
        
    with col2:
        website_url = st.text_input("Enter Website URL (optional)", key="website_url")
    
    # Add competitor type selection
    st.subheader("Competitor Types to Include")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        include_national = st.checkbox("National Competitors", value=True, key="include_national")
    
    with col2:
        include_regional = st.checkbox("Regional Competitors", value=True, key="include_regional")
    
    with col3:
        include_upcoming = st.checkbox("Upcoming Competitors", value=True, key="include_upcoming")
    
    # Initialize reprompt in session state if not exists
    if 'reprompt_text' not in st.session_state:
        st.session_state.reprompt_text = ""
    
    if st.button("Analyze Competitors", key="analyze_competitors"):
        if brand_name:
            with st.spinner("Analyzing competitors with Gemini..."):
                # Get competitor analysis with competitor type preferences
                competitor_data = get_competitor_analysis(
                    brand_name, 
                    website_url,
                    include_national=include_national,
                    include_regional=include_regional,
                    include_upcoming=include_upcoming,
                    reprompt=st.session_state.reprompt_text
                )
                
                if competitor_data:
                    # Store in session state
                    st.session_state.competitor_data = competitor_data
                    st.session_state.brand_name_value = brand_name
                    
                    # Display results
                    st.subheader("Competitor Analysis Results")
                    
                    # Display brand analysis
                    with st.expander("Brand Analysis", expanded=True):
                        st.write(competitor_data["brand"]["analysis"])
                    
                    # Display recommendations
                    with st.expander("Brand Recommendations & Strategies", expanded=True):
                        if "recommendations" in competitor_data["brand"]:
                            st.write(competitor_data["brand"]["recommendations"])
                        else:
                            st.write("No recommendations available.")
                    
                    # Display competitors
                    st.subheader("Identified Competitors")
                    
                    # Display competitor identification
                    with st.expander("Competitor Identification", expanded=True):
                        st.write(competitor_data["competitors"]["identification"])
                    
                    # Display competitor analysis
                    with st.expander("Competitor Analysis", expanded=True):
                        st.write(competitor_data["competitors"]["analysis"])
                else:
                    st.error("Failed to analyze competitors. Please try again.")
        else:
            st.error("Please enter a brand name.")
    
    # Add reprompting box if data is available
    if st.session_state.competitor_data:
        st.subheader("Need Changes or More Details?")
        st.session_state.reprompt_text = st.text_area(
            "Enter your specific requests for changes or additional information",
            height=100,
            key="reprompt_input",
            help="For example: 'Focus more on digital marketing strategies' or 'Add more details about pricing strategies'"
        )
    
    # Show export buttons if data is available
    if st.session_state.competitor_data:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Export to Google Docs", key="export_competitor_docs"):
                try:
                    with st.spinner("Exporting to Google Docs..."):
                        # Import the format_for_export function
                        from backend.services.competitor_analysis import format_for_export
                        
                        # Format the data before passing it to the export function
                        formatted_data = format_for_export(st.session_state.competitor_data)
                        
                        # Pass the formatted data to the export function
                        doc_url = export_competitor_analysis_to_doc(formatted_data, st.session_state.brand_name_value, make_public=make_public)
                        
                        if make_public:
                            st.success(f"Exported to Google Docs. The document is publicly accessible. [Open Document]({doc_url})")
                        else:
                            st.success(f"Exported to Google Docs. The document is shared with your email only. [Open Document]({doc_url})")
                except Exception as e:
                    st.error(f"Error exporting to Google Docs: {e}")
        
        with col2:
            if st.button("Export to Google Sheets", key="export_competitor_sheets"):
                try:
                    with st.spinner("Exporting to Google Sheets..."):
                        sheet_url = export_competitor_analysis(st.session_state.competitor_data, st.session_state.brand_name_value, make_public=make_public)
                        
                        if make_public:
                            st.success(f"Exported to Google Sheets. The sheet is publicly accessible. [Open Sheet]({sheet_url})")
                        else:
                            st.success(f"Exported to Google Sheets. The sheet is shared with your email only. [Open Sheet]({sheet_url})")
                except Exception as e:
                    st.error(f"Error exporting to Google Sheets: {e}")

# Instagram Analysis Tab
with tab3:
    st.header("Instagram Analysis")
    
    # Create two tabs for different Instagram analysis types
    profile_tab, campaigns_tab = st.tabs(["Profile Analysis", "Campaign Analysis"])
    
    with profile_tab:
        instagram_handle = st.text_input("Enter Instagram Handle", key="instagram_handle_input")
        
        if st.button("Analyze Instagram Profile", key="analyze_instagram"):
            if instagram_handle:
                with st.spinner("Analyzing Instagram with Gemini..."):
                    # Get Instagram analysis
                    instagram_data = get_instagram_analysis(instagram_handle)
                    
                    if instagram_data:
                        # Store in session state
                        st.session_state.instagram_data = instagram_data
                        st.session_state.instagram_handle_value = instagram_handle
                        
                        # Display results
                        st.subheader("Instagram Analysis Results")
                        
                        # Display profile analysis
                        with st.expander("Profile Analysis", expanded=True):
                            st.write(instagram_data["profile_analysis"])
                        
                        # Display content analysis
                        with st.expander("Content Analysis", expanded=True):
                            st.write(instagram_data["content_analysis"])
                        
                        # Display audience analysis
                        with st.expander("Audience Analysis", expanded=True):
                            st.write(instagram_data["audience_analysis"])
                        
                        # Display recommendations
                        with st.expander("Recommendations", expanded=True):
                            st.write(instagram_data["recommendations"])
                    else:
                        st.error("Failed to analyze Instagram. Please try again.")
            else:
                st.error("Please enter an Instagram handle.")
        
        # Show export button if data is available
        if 'instagram_data' in st.session_state and st.session_state.instagram_data:
            if st.button("Export to Google Sheets", key="export_instagram_sheets"):
                try:
                    with st.spinner("Exporting to Google Sheets..."):
                        sheet_url = export_instagram_analysis_to_sheet(st.session_state.instagram_data, st.session_state.instagram_handle_value, make_public=make_public)
                        
                        if make_public:
                            st.success(f"Exported to Google Sheets. The sheet is publicly accessible. [Open Sheet]({sheet_url})")
                        else:
                            st.success(f"Exported to Google Sheets. The sheet is shared with your email only. [Open Sheet]({sheet_url})")
                except Exception as e:
                    st.error(f"Error exporting to Google Sheets: {e}")
    
    with campaigns_tab:
        # Import the campaign analysis functions
        from backend.services.instagram_campaign_analysis import get_instagram_campaigns
        from backend.services.instagram_campaign_export import export_instagram_campaigns_to_sheet
        
        # Initialize session state for campaign data
        if 'instagram_campaign_data' not in st.session_state:
            st.session_state.instagram_campaign_data = None
        
        # Input fields
        campaign_handle = st.text_input("Enter Instagram Handle", key="campaign_handle_input")
        
        # Years back dropdown
        years_back = st.selectbox(
            "Select number of years to analyze",
            options=list(range(1, 11)),
            index=0,
            key="campaign_years_back",
            help="Select how many years back you want to analyze posts"
        )
        
        # Analyze button
        if st.button("Analyze Campaigns", key="analyze_campaigns"):
            if campaign_handle:
                with st.spinner("Fetching and analyzing Instagram campaigns..."):
                    # Get campaign data
                    campaign_data = get_instagram_campaigns(campaign_handle, years_back)
                    
                    if campaign_data:
                        # Store in session state
                        st.session_state.instagram_campaign_data = campaign_data
                        st.session_state.campaign_handle_value = campaign_handle
                        st.session_state.campaign_years_back_value = years_back
                        
                        # Display results
                        st.subheader("Instagram Campaign Analysis Results")
                        
                        # Create a table to display the campaign data
                        campaign_table = []
                        for post in campaign_data:
                            campaign_table.append({
                                "Post Link": post.get("post_link", ""),
                                "Date": post.get("date", ""),
                                "Insight": post.get("insight", "")
                            })
                        
                        st.table(campaign_table)
                    else:
                        st.error("Failed to analyze Instagram campaigns. Please try again.")
            else:
                st.error("Please enter an Instagram handle.")
        
        # Show export button if campaign data is available
        if 'instagram_campaign_data' in st.session_state and st.session_state.instagram_campaign_data:
            if st.button("Export Campaigns to Google Sheets", key="export_campaigns_sheets"):
                try:
                    with st.spinner("Exporting campaigns to Google Sheets..."):
                        sheet_url = export_instagram_campaigns_to_sheet(
                            st.session_state.instagram_campaign_data,
                            st.session_state.campaign_handle_value,
                            st.session_state.campaign_years_back_value,
                            make_public=make_public
                        )
                        
                        if make_public:
                            st.success(f"Exported to Google Sheets. The sheet is publicly accessible. [Open Sheet]({sheet_url})")
                        else:
                            st.success(f"Exported to Google Sheets. The sheet is shared with your email only. [Open Sheet]({sheet_url})")
                except Exception as e:
                    st.error(f"Error exporting to Google Sheets: {e}")