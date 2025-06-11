import os
from datetime import datetime, timedelta
from googleapiclient.discovery import build
import isodate

def get_youtube_service():
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
    if not YOUTUBE_API_KEY:
        raise ValueError("YOUTUBE_API_KEY is not set in environment variables.")
    return build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def get_channel_id(channel_input):
    youtube = get_youtube_service()
    if "youtube.com/channel/" in channel_input:
        return channel_input.split("/channel/")[1].split("/")[0]
    elif "youtube.com/@" in channel_input:
        handle = channel_input.split("@")[1].split("/")[0]
        response = youtube.search().list(
            q=handle,
            type="channel",
            part="id",
            maxResults=1
        ).execute()
        if response["items"]:
            return response["items"][0]["id"]["channelId"]
    else:
        response = youtube.search().list(
            q=channel_input,
            type="channel",
            part="id",
            maxResults=1
        ).execute()
        if response["items"]:
            return response["items"][0]["id"]["channelId"]
    raise ValueError("Could not resolve YouTube channel ID.")

def is_ad_video(title, description):
    ad_keywords = ["ad", "advertisement", "tvc", "commercial", "campaign", "promo", "promotion"]
    text = f"{title} {description}".lower()
    return any(kw in text for kw in ad_keywords)

def get_channel_ads(channel_input, years_back=7):
    youtube = get_youtube_service()
    channel_id = get_channel_id(channel_input)
    years_ago = (datetime.utcnow() - timedelta(days=int(years_back) * 365)).isoformat("T") + "Z"

    videos = []
    next_page_token = None

    while True:
        search_response = youtube.search().list(
            channelId=channel_id,
            part="id,snippet",
            order="date",
            publishedAfter=years_ago,
            maxResults=50,
            type="video",
            pageToken=next_page_token
        ).execute()

        video_ids = [item["id"]["videoId"] for item in search_response["items"]]
        if not video_ids:
            break

        video_details = youtube.videos().list(
            part="snippet,contentDetails",
            id=",".join(video_ids)
        ).execute()

        for item in video_details["items"]:
            title = item["snippet"]["title"]
            description = item["snippet"].get("description", "")
            if not is_ad_video(title, description):
                continue

            duration_iso = item["contentDetails"].get("duration", "PT0S")
            duration = str(isodate.parse_duration(duration_iso))
            language = item["snippet"].get("defaultAudioLanguage") or item["snippet"].get("defaultLanguage") or "Unknown"

            videos.append({
                "sr_no": len(videos) + 1,
                "title": title,
                "url": f"https://www.youtube.com/watch?v={item['id']}",
                "published_at": item["snippet"]["publishedAt"],
                "language": language,
                "duration": duration,
                "description": description
            })

        next_page_token = search_response.get("nextPageToken")
        if not next_page_token:
            break

    return videos
