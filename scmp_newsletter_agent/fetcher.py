import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
import time
from .config import SCMP_FEEDS, TIME_WINDOW_HOURS

def parse_rss_date(entry):
    """
    Parses feed entry publication date into a timezone-aware datetime object.
    Returns datetime in UTC.
    """
    for date_key in ['published_parsed', 'updated_parsed', 'created_parsed']:
        struct_time = entry.get(date_key)
        if struct_time:
            # Struct time is always parsed in UTC by feedparser
            return datetime(*struct_time[:6], tzinfo=timezone.utc)
    
    # Fallback if parsing failed but date string exists
    for raw_key in ['published', 'updated', 'created']:
        raw_str = entry.get(raw_key)
        if raw_str:
            try:
                # E.g. "Mon, 01 Jun 2026 10:06:33 +0000"
                # Remove timezone offset or GMT for simple parsing if necessary
                return datetime.strptime(raw_str[:25].strip(), "%a, %d %b %Y %H:%M:%S").replace(tzinfo=timezone.utc)
            except Exception:
                pass
                
    # If no date found, default to current time in UTC so it isn't skipped
    return datetime.now(timezone.utc)

def clean_html_summary(html_content):
    """
    Removes HTML tags from RSS summaries and returns clean text.
    """
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    # SCMP summaries often end with '...' or have image tags, clean them up
    text = soup.get_text(separator=" ").strip()
    return text

def fetch_scmp_news():
    """
    Fetches articles from SCMP RSS feeds, filters for those published
    within the last 24 hours, and de-duplicates them.
    """
    print("=" * 60)
    print("  SCMP NEWS FETCHER: INITIATING FEED EXTRACTION")
    print("=" * 60)
    
    now = datetime.now(timezone.utc)
    cutoff_time = now - timedelta(hours=TIME_WINDOW_HOURS)
    
    all_articles = {}
    
    for category, feed_url in SCMP_FEEDS.items():
        print(f"Fetching '{category}' feed from: {feed_url}")
        try:
            feed = feedparser.parse(feed_url)
            
            # Check for parsing errors
            if feed.bozo:
                print(f"  [Warning] Parsing issues encountered with feed {category}: {feed.bozo_exception}")
                
            entries_count = len(feed.entries)
            print(f"  Loaded {entries_count} entries.")
            
            for entry in feed.entries:
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                
                if not title or not link:
                    continue
                    
                pub_date = parse_rss_date(entry)
                
                # Check if within the 24-hour time window
                is_recent = pub_date >= cutoff_time
                
                if is_recent:
                    # De-duplicate by link (keep the first category we found it under)
                    if link not in all_articles:
                        summary_html = entry.get("summary", "") or entry.get("description", "")
                        clean_summary = clean_html_summary(summary_html)
                        
                        all_articles[link] = {
                            "title": title,
                            "link": link,
                            "published_date": pub_date,
                            "raw_date_str": entry.get("published", ""),
                            "summary": clean_summary,
                            "source_feed": category
                        }
        except Exception as e:
            print(f"  [Error] Failed to fetch feed '{category}': {str(e)}")
            
    print(f"\nCompleted fetching. Found {len(all_articles)} unique recent articles in the last {TIME_WINDOW_HOURS} hours.")
    print("=" * 60)
    
    return list(all_articles.values())

if __name__ == "__main__":
    # Test fetcher locally
    results = fetch_scmp_news()
    for idx, item in enumerate(results[:5]):
        print(f"\n{idx+1}. [{item['source_feed']}] {item['title']}")
        print(f"   Date: {item['published_date']}")
        print(f"   Link: {item['link']}")
        print(f"   Summary: {item['summary'][:120]}...")
