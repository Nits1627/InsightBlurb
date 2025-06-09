import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key")
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"

    # API Keys
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    CRUNCHBASE_API_KEY = os.getenv("CRUNCHBASE_API_KEY", "")

    # Cache
    CACHE_TTL_HOURS = int(os.getenv("CACHE_TTL_HOURS", "24"))

    # Selenium
    CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH", "/usr/bin/chromedriver")
    SELENIUM_HEADLESS = os.getenv("SELENIUM_HEADLESS", "True").lower() == "true"