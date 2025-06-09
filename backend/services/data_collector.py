import aiohttp
import re
from bs4 import BeautifulSoup
import yfinance as yf
from googleapiclient.discovery import build
import os
import logging

logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self):
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        self.youtube = build("youtube", "v3", developerKey=self.youtube_api_key) if self.youtube_api_key else None

    async def scrape_company_website(self, url: str) -> dict:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")
                    title = soup.title.string if soup.title else ""
                    desc_tag = soup.find("meta", attrs={"name": "description"})
                    description = desc_tag["content"] if desc_tag else ""
                    return {
                        "title": title,
                        "description": description,
                        "scraped_url": url
                    }
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return {}

    async def get_company_financial_data(self, company_name: str) -> dict:
        try:
            symbol = self._guess_ticker(company_name)
            if not symbol:
                return {}
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return {
                "ticker": symbol,
                "market_cap": info.get("marketCap"),
                "revenue": info.get("totalRevenue"),
                "employees": info.get("fullTimeEmployees"),
                "industry": info.get("industry"),
                "sector": info.get("sector"),
                "website": info.get("website"),
                "business_summary": info.get("longBusinessSummary")
            }
        except Exception as e:
            logger.error(f"Error getting financials for {company_name}: {e}")
            return {}

    def _guess_ticker(self, name: str) -> str:
        guess_map = {
            "apple": "AAPL",
            "microsoft": "MSFT",
            "google": "GOOGL",
            "amazon": "AMZN",
            "facebook": "META",
            "tesla": "TSLA"
        }
        name = name.lower()
        return guess_map.get(name)

    async def get_youtube_channel_data(self, channel_input: str) -> dict:
        try:
            if "youtube.com" in channel_input:
                channel_id = self._extract_channel_id(channel_input)
            else:
                search = self.youtube.search().list(q=channel_input, part="id,snippet", type="channel", maxResults=1).execute()
                if not search["items"]:
                    return {"error": "Channel not found"}
                channel_id = search["items"][0]["id"]["channelId"]

            channel_data = self.youtube.channels().list(part="snippet,statistics", id=channel_id).execute()
            stats = channel_data["items"][0]["statistics"]
            videos_response = self.youtube.search().list(channelId=channel_id, part="id,snippet", order="date", maxResults=5, type="video").execute()

            videos = []
            for video in videos_response["items"]:
                videos.append({
                    "title": video["snippet"]["title"],
                    "video_id": video["id"]["videoId"],
                    "published_at": video["snippet"]["publishedAt"]
                })

            return {
                "channel_id": channel_id,
                "videos": videos,
                "subscriber_count": stats.get("subscriberCount"),
                "total_views": stats.get("viewCount"),
                "video_count": stats.get("videoCount")
            }
        except Exception as e:
            logger.error(f"YouTube data error: {e}")
            return {"error": str(e)}

    def _extract_channel_id(self, url: str) -> str:
        match = re.search(r"youtube\\.com/(channel|c|user|@)/([^/?]+)", url)
        return match.group(2) if match else url