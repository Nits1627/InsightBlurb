# File: app2.py
import os
import streamlit as st
import pandas as pd
from datetime import datetime
from backend.services.youtube_ads import get_channel_ads
from backend.services.gemini_insights import get_video_insights
from backend.services.sheets_export import export_to_sheet
from backend.services.competitor_analysis import get_competitor_analysis
from backend.services.competitor_doc_export import export_competitor_analysis_to_doc
from backend.services.competitor_export import export_competitor_analysis
from backend.services.instagram_analysis import get_instagram_analysis
from backend.services.instagram_export import export_instagram_analysis_to_sheet
from backend.services.instagram_campaign_analysis import get_instagram_campaigns
from backend.services.instagram_campaign_export import export_instagram_campaigns_to_sheet
from backend.config import load_env

load_env()

# Initialize session state
for key in ['youtube_data', 'competitor_data', 'instagram_data', 'instagram_campaign_data', 'channel_input_value', 'brand_name_value', 'instagram_handle_value', 'campaign_handle_value']:
    if key not in st.session_state:
        st.session_state[key] = None
if 'years_back_value' not in st.session_state:
    st.session_state.years_back_value = 7

# Page config
st.set_page_config(page_title="InsightBlurb", page_icon="📊", layout="wide")

# Sidebar
with st.sidebar:
    st.title("InsightBlurb")
    st.write("AI-powered marketing research tool")
    st.subheader("Theme")
    theme = st.selectbox("Select theme", ["Light", "Dark"])
    st.subheader("Sharing Options")
    make_public = st.checkbox("Make exported documents public", value=True)
    st.success("Exported documents will be publicly accessible") if make_public else st.info("Exported documents will be shared with your email only")

# Tabs
tab1, tab2, tab3 = st.tabs(["Ad Analysis", "Competitor Analysis", "Instagram Analysis"])

# === Ad Analysis Tab ===
with tab1:
    st.header("YouTube Ad Research")
    col1, col2 = st.columns(2)
    with col1:
        channel_input = st.text_input("Enter YouTube Channel Name, URL, or ID")
    with col2:
        search_terms = st.text_input("Enter search terms (comma separated)", value="ad,commercial,official,campaign")
        years_back = st.selectbox("Years to look back", options=list(range(1, 11)), index=6)

    if st.button("Analyze Ads", key="analyze_ads"):
        if channel_input:
            with st.spinner("Fetching YouTube ads..."):
                videos = get_channel_ads(channel_input, years_back=years_back)
            if videos:
                with st.spinner("Generating insights with Gemini..."):
                    videos_with_insights = get_video_insights(videos)
                st.session_state.youtube_data = videos_with_insights
                st.session_state.channel_input_value = channel_input
                st.session_state.years_back_value = years_back
                st.subheader(f"Found {len(videos_with_insights)} potential ads")
                for i, video in enumerate(videos_with_insights):
                    with st.expander(f"{i+1}. {video['title']} ({video['published_at']})"):
                        st.write(f"**URL:** {video['url']}")
                        st.write(f"**Published:** {video['published_at']}")
                        st.write(f"**Language:** {video.get('language', 'Unknown')}")
                        st.write(f"**Duration:** {video.get('duration', 'Unknown')}")
                        st.write(f"**Insight:** {video.get('insight', 'No insight available')}")
            else:
                st.error("No ads found for this channel.")
        else:
            st.error("Please enter a YouTube channel name, URL, or ID.")

    # Export options
    if st.session_state.youtube_data:
        colA, colB = st.columns(2)
        with colA:
            if st.button("Export to Google Sheets", key="export_ads"):
                try:
                    with st.spinner("Exporting to Google Sheets..."):
                        sheet_url = export_to_sheet(
                            st.session_state.youtube_data,
                            brand_name=f"{st.session_state.channel_input_value} ({st.session_state.years_back_value}yrs)",
                            make_public=make_public
                        )
                    msg = f"Exported to Google Sheets. [{'Public' if make_public else 'Private'}] [Open Sheet]({sheet_url})"
                    st.success(msg)
                except Exception as e:
                    st.error(f"Error exporting to Google Sheets: {e}")
        with colB:
            csv_df = pd.DataFrame(st.session_state.youtube_data)
            csv_bytes = csv_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Ads CSV",
                data=csv_bytes,
                file_name=f"{st.session_state.channel_input_value}_{st.session_state.years_back_value}yrs_ads.csv",
                mime="text/csv"
            )

# === Competitor Analysis Tab ===
with tab2:
    st.header("Competitor Analysis")
    brand_name = st.text_input("Enter Brand Name", key="brand_name_input")
    website_url = st.text_input("Enter Website URL (optional)", key="website_url")
    st.subheader("Competitor Types to Include")
    c1, c2, c3 = st.columns(3)
    include_national = c1.checkbox("National Competitors", value=True)
    include_regional = c2.checkbox("Regional Competitors", value=True)
    include_upcoming = c3.checkbox("Upcoming Competitors", value=True)
    if 'reprompt_text' not in st.session_state:
        st.session_state.reprompt_text = ""
    if st.button("Analyze Competitors", key="analyze_competitors"):
        if brand_name:
            with st.spinner("Analyzing competitors with Gemini..."):
                competitor_data = get_competitor_analysis(
                    brand_name, website_url,
                    include_national=include_national,
                    include_regional=include_regional,
                    include_upcoming=include_upcoming,
                    reprompt=st.session_state.reprompt_text
                )
            if competitor_data:
                st.session_state.competitor_data = competitor_data
                st.session_state.brand_name_value = brand_name
                st.subheader("Competitor Analysis Results")
                with st.expander("Brand Analysis", expanded=True):
                    st.write(competitor_data["brand"]["analysis"])
                with st.expander("Brand Recommendations & Strategies", expanded=True):
                    st.write(competitor_data["brand"].get("recommendations", "No recommendations."))
                st.subheader("Identified Competitors")
                with st.expander("Competitor Identification", expanded=True):
                    st.write(competitor_data["competitors"]["identification"])
                with st.expander("Competitor Analysis", expanded=True):
                    st.write(competitor_data["competitors"]["analysis"])
            else:
                st.error("Failed to analyze competitors.")
        else:
            st.error("Please enter a brand name.")
    if st.session_state.competitor_data:
        st.subheader("Need Changes? Provide Reprompt")
        st.session_state.reprompt_text = st.text_area(
            "Enter requests for changes/additions", height=100
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Export to Google Docs", key="export_competitor_docs"):
                try:
                    from backend.services.competitor_analysis import format_for_export
                    formatted = format_for_export(st.session_state.competitor_data)
                    doc_url = export_competitor_analysis_to_doc(
                        formatted, st.session_state.brand_name_value, make_public=make_public
                    )
                    st.success(f"Exported to Google Docs. [Open Document]({doc_url})")
                except Exception as e:
                    st.error(f"Error exporting to Google Docs: {e}")
        with c2:
            if st.button("Export to Google Sheets", key="export_competitor_sheets"):
                try:
                    sheet_url = export_competitor_analysis(
                        st.session_state.competitor_data,
                        st.session_state.brand_name_value,
                        make_public=make_public
                    )
                    st.success(f"Exported to Google Sheets. [Open Sheet]({sheet_url})")
                except Exception as e:
                    st.error(f"Error exporting to Google Sheets: {e}")
            comp_list = st.session_state.competitor_data["competitors"]["analysis"]
            comp_df   = pd.DataFrame(comp_list)
            csv_bytes = comp_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Competitors CSV",
                data=csv_bytes,
                file_name=f"{st.session_state.brand_name_value}_competitors.csv",
                mime="text/csv"
            )

# === Instagram Analysis Tab ===
with tab3:
    st.header("Instagram Analysis")
    profile_tab, campaigns_tab = st.tabs(["Profile Analysis","Campaign Analysis"])
    with profile_tab:
        instagram_handle = st.text_input("Enter Instagram Handle", key="instagram_handle_input")
        if st.button("Analyze Instagram Profile", key="analyze_instagram"):
            if instagram_handle:
                with st.spinner("Analyzing Instagram with Gemini..."):
                    instagram_data = get_instagram_analysis(instagram_handle)
                if instagram_data:
                    st.session_state.instagram_data = instagram_data
                    st.session_state.instagram_handle_value = instagram_handle
                    st.subheader("Instagram Analysis Results")
                    with st.expander("Profile Analysis", expanded=True):
                        st.write(instagram_data["profile_analysis"])
                    with st.expander("Content Analysis", expanded=True):
                        st.write(instagram_data["content_analysis"])
                    with st.expander("Audience Analysis", expanded=True):
                        st.write(instagram_data["audience_analysis"])
                    with st.expander("Recommendations", expanded=True):
                        st.write(instagram_data["recommendations"])
                else:
                    st.error("Failed to analyze Instagram.")
            else:
                st.error("Please enter an Instagram handle.")
        if st.session_state.instagram_data:
            if st.button("Export to Google Sheets", key="export_instagram_sheets"):
                try:
                    sheet_url = export_instagram_analysis_to_sheet(
                        st.session_state.instagram_data,
                        st.session_state.instagram_handle_value,
                        make_public=make_public
                    )
                    st.success(f"Exported to Google Sheets. [Open Sheet]({sheet_url})")
                except Exception as e:
                    st.error(f"Error exporting to Google Sheets: {e}")
    with campaigns_tab:
        campaign_handle = st.text_input("Enter Instagram Handle", key="campaign_handle_input")
        years_back = st.selectbox("Years back", options=list(range(1,11)), index=0, key="campaign_years_back")
        if st.button("Analyze Campaigns", key="analyze_campaigns"):
            if campaign_handle:
                with st.spinner("Fetching and analyzing Instagram campaigns..."):
                    campaign_data = get_instagram_campaigns(campaign_handle, years_back)
                if campaign_data:
                    st.session_state.instagram_campaign_data = campaign_data
                    st.session_state.campaign_handle_value = campaign_handle
                    st.session_state.campaign_years_back_value = years_back
                    st.subheader("Instagram Campaign Analysis Results")
                    table = [{
                        "Post Link": p.get("post_link",""),
                        "Date": p.get("date",""),
                        "Insight": p.get("insight","")
                    } for p in campaign_data]
                    st.table(table)
                else:
                    st.error("Failed to analyze Instagram campaigns.")
            else:
                st.error("Please enter an Instagram handle.")
        if st.session_state.instagram_campaign_data:
            if st.button("Export Campaigns to Google Sheets", key="export_campaigns_sheets"):
                try:
                    sheet_url = export_instagram_campaigns_to_sheet(
                        st.session_state.instagram_campaign_data,
                        st.session_state.campaign_handle_value,
                        st.session_state.campaign_years_back_value,
                        make_public=make_public
                    )
                    st.success(f"Exported to Google Sheets. [Open Sheet]({sheet_url})")
                except Exception as e:
                    st.error(f"Error exporting to Google Sheets: {e}")
            camp_df   = pd.DataFrame(st.session_state.instagram_campaign_data)
            csv_bytes = camp_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Campaigns CSV",
                data=csv_bytes,
                file_name=f"{st.session_state.campaign_handle_value}_campaigns.csv",
                mime="text/csv"
            )
