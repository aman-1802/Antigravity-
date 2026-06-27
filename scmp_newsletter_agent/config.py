import os
from dotenv import load_dotenv

# Load local environment variables from .env file
load_dotenv()

# Gemini Config
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Email SMTP Config
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# Receiver & Sender
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "aagarwal1802@gmail.com")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "") or SMTP_USER or "aagarwal1802@gmail.com"

# Target SCMP RSS Feeds (Prioritizing User's Specific Channels)
SCMP_FEEDS = {
    "SCMP Tech": "https://www.scmp.com/rss/36/feed",
    "China Future Tech": "https://www.scmp.com/rss/519735/feed",
    "China Science & Research": "https://www.scmp.com/rss/318224/feed",
    "This Week in Asia": "https://www.scmp.com/rss/323045/feed",
    "Diplomacy & Defence": "https://www.scmp.com/rss/318199/feed",
    "Diplomacy": "https://www.scmp.com/rss/318213/feed",
    "China News": "https://www.scmp.com/rss/4/feed"
}

# Number of hours of news to cover
TIME_WINDOW_HOURS = 24
