import os
import sys
import re
import json
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone, timedelta
import requests
from bs4 import BeautifulSoup
import feedparser
from dotenv import load_dotenv
from openai import OpenAI

# Force UTF-8 stdout encoding on Windows to prevent print crashes
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# 1. Load Environment Variables from possible locations
env_paths = [
    os.path.join(os.path.dirname(__file__), ".env"),
    os.path.join(os.path.dirname(__file__), "..", ".env"),
    os.path.join(os.path.dirname(__file__), "..", "scmp_newsletter_agent", ".env")
]
for path in env_paths:
    if os.path.exists(path):
        load_dotenv(path)
        print(f"Loaded configuration from: {path}")
        break

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# SMTP Configurations
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT_RAW = os.getenv("SMTP_PORT", "587")
try:
    SMTP_PORT = int(SMTP_PORT_RAW) if SMTP_PORT_RAW.strip() else 587
except ValueError:
    SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").strip()
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "aagarwal1802@gmail.com")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "") or SMTP_USER or "aagarwal1802@gmail.com"

# Safety valves for failed auth/credits to prevent script slowdowns
openai_disabled = False
smtp_disabled = False

# Feeds Configuration
TECH_FEEDS = {
    "OpenAI": "https://openai.com/news/rss.xml",
    "Google AI": "https://blog.google/technology/ai/rss/",
    "Microsoft": "https://blogs.microsoft.com/feed/",
    "NVIDIA": "https://blogs.nvidia.com/feed/",
    "Apple": "https://www.apple.com/newsroom/rss-feed.rss",
    "Clore AI": "https://blog.clore.ai/rss/"
}

SCMP_FEEDS = {
    "SCMP Tech": "https://www.scmp.com/rss/36/feed",
    "SCMP China Tech": "https://www.scmp.com/rss/519735/feed",
    "SCMP Science & Research": "https://www.scmp.com/rss/318224/feed",
    "This Week in Asia": "https://www.scmp.com/rss/323045/feed",
    "Diplomacy & Defence": "https://www.scmp.com/rss/318199/feed",
    "Diplomacy": "https://www.scmp.com/rss/318213/feed",
    "China News": "https://www.scmp.com/rss/4/feed"
}

AEON_FEEDS = {
    "Aeon Essays": "https://aeon.co/feed.rss",
    "Psyche": "https://psyche.co/feed"
}

# Time window for active display (Strictly last 24 hours)
TIME_WINDOW_HOURS = 24

def send_alert_email(error_message):
    """Sends an email alert to the user if the OpenAI API or scheduler fails."""
    global smtp_disabled
    if smtp_disabled:
        return False
        
    if not SMTP_USER or not SMTP_PASSWORD:
        print("[Warning] SMTP credentials not set. Could not send error notification email.")
        smtp_disabled = True
        return False
        
    print(f"Sending error alert email to {RECEIVER_EMAIL}...")
    subject = "⚠️ News Aggregator Alert: API Failure / Model Problem"
    
    body = f"""
    <h2>Aggregator API Alert</h2>
    <p>The News Aggregator encountered an error during its daily run at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}.</p>
    <p><b>Error Details:</b></p>
    <pre style="background: #f4f4f4; padding: 15px; border-left: 4px solid #d9534f; font-family: monospace;">{error_message}</pre>
    <p>The pipeline has fallen back to default RSS content to avoid crashing. Summarization and filtering are temporarily bypassed.</p>
    <hr>
    <p style="color: #888; font-size: 11px;">This is an automated notification from your News Aggregator Agent.</p>
    """
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.ehlo()
        if SMTP_PORT == 587:
            server.starttls()
            server.ehlo()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("Alert email dispatched successfully.")
        return True
    except Exception as e:
        print(f"[Error] Failed to send alert email: {e}")
        # If credentials fail once, disable SMTP to prevent subsequent slow attempts
        if "535" in str(e) or "authentication" in str(e).lower() or "credentials" in str(e).lower():
            print("  Disabling SMTP notifications for this run due to auth failure.")
            smtp_disabled = True
        return False

def get_openai_client():
    """Initializes and returns the OpenAI client if key is present."""
    global openai_disabled
    if openai_disabled:
        return None
        
    if not OPENAI_API_KEY or "your-openai-api-key" in OPENAI_API_KEY:
        print("[Warning] Valid OPENAI_API_KEY environment variable is not set. Bypassing OpenAI API calls.")
        openai_disabled = True
        return None
    try:
        return OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print(f"[Error] Failed to initialize OpenAI client: {e}")
        send_alert_email(f"Initialization Failure: {e}")
        openai_disabled = True
        return None

def parse_date(date_str):
    """Parses date string into datetime object with timezone. Defaults to now if parsing fails."""
    if not date_str:
        return datetime.now(timezone.utc)
    
    formats = [
        "%a, %d %b %Y %H:%M:%S %Z",  # "Wed, 03 Jun 2026 18:00:00 GMT" or "Mon, 01 Jun 2026 10:06:33 +0000"
        "%a, %d %b %Y %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%S%z",      # ISO 8601
        "%Y-%m-%dT%H:%M:%SZ",
        "%b %d, %Y",                # "May 28, 2026"
        "%B %d, %Y",                # "August 28, 2026"
        "%Y-%m-%d %H:%M:%S",
    ]
    
    date_str = date_str.strip()
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            pass
            
    # Try Regex fallback for structural dates
    try:
        match = re.search(r'\d{1,2}\s+[A-Za-z]{3}\s+\d{4}', date_str)
        if match:
            parsed = datetime.strptime(match.group(0), "%d %b %Y")
            return parsed.replace(tzinfo=timezone.utc)
    except Exception:
        pass
        
    return datetime.now(timezone.utc)

def clean_html(html_text):
    """Cleans HTML tags and returns plain text."""
    if not html_text:
        return ""
    soup = BeautifulSoup(html_text, "html.parser")
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    return soup.get_text(separator=" ").strip()

def scrape_anthropic():
    """Scrapes Anthropic Newsroom for articles published in the last 24 hours."""
    print("Scraping Anthropic Newsroom: https://www.anthropic.com/news")
    articles = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        r = requests.get("https://www.anthropic.com/news", headers=headers, timeout=12)
        if r.status_code != 200:
            print(f"  [Warning] Anthropic scrape returned status code {r.status_code}")
            return articles
            
        soup = BeautifulSoup(r.text, 'html.parser')
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('/news/'):
                link = f"https://www.anthropic.com{href}"
                
                # De-duplicate locally in this fetch run
                if any(art["link"] == link for art in articles):
                    continue
                    
                h_tag = a.find(['h2', 'h3', 'h4', 'h5', 'h6', 'div'])
                title = h_tag.get_text().strip() if h_tag else a.get_text().strip()
                if not title or len(title) < 5:
                    continue
                    
                time_tag = a.find('time')
                date_str = time_tag.get_text().strip() if time_tag else ""
                dt = parse_date(date_str)
                
                p_tag = a.find('p')
                summary = p_tag.get_text().strip() if p_tag else ""
                
                articles.append({
                    "title": title,
                    "link": link,
                    "published_date": dt.isoformat(),
                    "summary": summary,
                    "source": "Anthropic",
                    "category": "AI"
                })
    except Exception as e:
        print(f"  [Error] Failed to scrape Anthropic: {e}")
        
    print(f"  Loaded {len(articles)} articles from Anthropic.")
    return articles

def fetch_duckduckgo_news():
    """Performs daily web searches on DuckDuckGo and fetches the direct article permalinks."""
    today_str = datetime.now().strftime("%B %d, %Y")
    queries = [
        f"AI model release {today_str}",
        f"AI announcement {today_str}",
        f"LLM update {today_str}"
    ]
    
    print(f"Performing DuckDuckGo daily search runs for {today_str}...")
    articles = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    
    for query in queries:
        time.sleep(1.0)  # Rate limiting safety
        print(f"  Searching DuckDuckGo for: '{query}'")
        search_url = f"https://lite.duckduckgo.com/lite/"
        try:
            r = requests.post(search_url, data={"q": query}, headers=headers, timeout=15)
            if r.status_code != 200:
                print(f"    [Warning] Search returned status code {r.status_code}")
                continue
                
            soup = BeautifulSoup(r.text, 'html.parser')
            rows = soup.find_all('td', class_='result-link')
            
            count = 0
            for row in rows:
                if count >= 3: # Keep top 3 results per query
                    break
                a_tag = row.find('a', class_='result-link')
                if not a_tag or not a_tag.get('href'):
                    continue
                    
                raw_href = a_tag['href']
                match = re.search(r'uddg=(https?%3A%2F%2F[^\s&]+)', raw_href)
                if match:
                    import urllib.parse
                    link = urllib.parse.unquote(match.group(1))
                else:
                    link = raw_href
                
                title = a_tag.get_text().strip()
                
                parsed_url = link.replace("https://", "").replace("http://", "").split('/')
                if len(parsed_url) <= 1 or not parsed_url[1]:
                    continue
                
                if any(art["link"] == link for art in articles):
                    continue
                
                snippet_td = row.parent.find_next_sibling('tr')
                snippet = ""
                if snippet_td:
                    snippet_text_td = snippet_td.find('td', class_='result-snippet')
                    if snippet_text_td:
                        snippet = snippet_text_td.get_text().strip()
                
                articles.append({
                    "title": title,
                    "link": link,
                    "published_date": datetime.now(timezone.utc).isoformat(),
                    "summary": snippet,
                    "source": "Web Search",
                    "category": "AI"
                })
                count += 1
        except Exception as e:
            print(f"    [Error] DuckDuckGo query '{query}' failed: {e}")
            
    print(f"  Discovered {len(articles)} articles from daily search queries.")
    return articles

def fetch_rss_feed(feed_name, url, category):
    """Fetches and parses a standard RSS feed."""
    print(f"Fetching RSS feed '{feed_name}' from: {url}")
    articles = []
    try:
        feed = feedparser.parse(url)
        if feed.bozo:
            print(f"  [Warning] Parsing issues with feed '{feed_name}': {feed.bozo_exception}")
            
        for entry in feed.entries:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            if not title or not link:
                continue
                
            raw_date = entry.get("published") or entry.get("updated") or entry.get("created")
            struct_time = entry.get("published_parsed") or entry.get("updated_parsed")
            if struct_time:
                dt = datetime(*struct_time[:6], tzinfo=timezone.utc)
            else:
                dt = parse_date(raw_date)
                
            summary_raw = entry.get("summary") or entry.get("description") or ""
            summary_clean = clean_html(summary_raw)
            
            content_list = entry.get("content", [])
            content_text = ""
            if isinstance(content_list, list) and len(content_list) > 0:
                content_text = clean_html(content_list[0].get("value", ""))
            
            articles.append({
                "title": title,
                "link": link,
                "published_date": dt.isoformat(),
                "summary": content_text if content_text and category == "Aeon" else summary_clean,
                "source": feed_name,
                "category": category
            })
    except Exception as e:
        print(f"  [Error] Failed to fetch feed '{feed_name}': {e}")
        
    print(f"  Loaded {len(articles)} articles.")
    return articles

def filter_scmp_articles(openai_client, articles):
    """Uses OpenAI to filter SCMP articles to keep only tech/science/geopolitical topics."""
    global openai_disabled
    if openai_disabled or not openai_client or not articles:
        # Fallback filter by keywords
        return fallback_filter(articles)
        
    print(f"Filtering {len(articles)} SCMP articles via OpenAI (gpt-4o-mini)...")
    
    payload = []
    for idx, art in enumerate(articles):
        payload.append({
            "id": idx,
            "title": art["title"],
            "summary": art["summary"][:120] if art.get("summary") else ""
        })
        
    prompt = f"""
    You are an editor sorting South China Morning Post (SCMP) news.
    Analyze the following articles and return a JSON array containing the IDs of only the articles that are highly relevant to these preferences:
    1. Geopolitical updates (US-China relations, regional security, tech-related diplomacy/defense).
    2. China technology breakthroughs, AI, Space development, Humanoid robots, or Semiconductor chip wars.
    Exclude: Local social updates, court cases, municipal affairs, standard crime stories, unless they carry major geopolitical or semiconductor significance.
    
    Articles:
    {json.dumps(payload, indent=2)}
    
    Response format: Return ONLY a raw JSON array of indices. No markdown styling, no backticks, no text. Example: [0, 2, 5]
    """
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=150
        )
        text = response.choices[0].message.content.strip()
        text = re.sub(r"^```json|```$", "", text, flags=re.MULTILINE).strip()
        selected_ids = json.loads(text)
        
        filtered = [articles[idx] for idx in selected_ids if 0 <= idx < len(articles)]
        print(f"  OpenAI selected {len(filtered)} relevant SCMP articles.")
        return filtered
    except Exception as e:
        print(f"  [Warning] OpenAI SCMP filtering failed: {e}")
        send_alert_email(f"SCMP Filtering Failure:\n{e}")
        
        # Trigger safety valve if it's an API Key or Auth problem
        if "401" in str(e) or "invalid_api_key" in str(e) or "Authentication" in type(e).__name__:
            print("  Disabling OpenAI API calls for this run due to authentication error.")
            openai_disabled = True
            
        return fallback_filter(articles)

def fallback_filter(articles):
    """Filters articles using simple keywords as fallback."""
    keywords = ["tech", "ai", "artificial intelligence", "robot", "space", "satellite", "chip", "semiconductor", 
                "geopolitics", "defense", "military", "diplomacy", "us-china", "china-us", "tariff", "nuclear", "asml", "huawei", "byd"]
    filtered = []
    for art in articles:
        text_check = (art["title"] + " " + art.get("summary", "")).lower()
        if any(kw in text_check for kw in keywords):
            filtered.append(art)
    print(f"  Fallback keyword filtering selected {len(filtered)} articles.")
    return filtered

def summarize_article(openai_client, title, content, category, source):
    """Uses OpenAI (gpt-4o-mini) to summarize articles depending on their category."""
    global openai_disabled
    if openai_disabled or not openai_client:
        return content or "No content available."
        
    if category == "Aeon":
        prompt = f"""
        You are a sharp essay summarizer. Read the essay below and return ONLY 4-5 bullet points (each starting with •).
        Be extremely concise — exactly one sentence per bullet point. Keep it highly engaging and philosophical/insightful.
        Do not add any preamble, intro, conclusion, or extra formatting. Just start with the first bullet point.
        
        Source: {source}
        Title: {title}
        
        Content:
        {content[:6000]}
        """
    else:
        prompt = f"""
        You are a premium tech news editor. Analyze the article title and details below, and write a high-value, jaw-dropping executive summary in exactly 1 or 2 sentences. 
        Focus on what the breakthrough is and why it matters. Keep it clean and readable.
        Do not use any markdown bolding, prefixes, or list formats. Just return the raw sentence(s).
        
        Source: {source}
        Title: {title}
        Details: {content[:1000]}
        """
        
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=250
        )
        summary = response.choices[0].message.content.strip()
        if summary:
            return summary
    except Exception as e:
        print(f"  [Warning] OpenAI summarization failed for '{title}': {e}")
        send_alert_email(f"Summarization Failure on '{title}':\n{e}")
        
        # Trigger safety valve if it's an API Key or Auth problem
        if "401" in str(e) or "invalid_api_key" in str(e) or "Authentication" in type(e).__name__:
            print("  Disabling OpenAI API calls for this run due to authentication error.")
            openai_disabled = True
            
    return content or "No description available."

def aggregate_pipeline():
    """Coordinates the scraping, processing, caching, and database updates."""
    print("=" * 60)
    print(f"  UNIFIED NEWS AGGREGATOR PIPELINE STARTED: {datetime.now(timezone.utc)}")
    print("=" * 60)
    
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, "news_data.json")
    
    # 1. Load active display cache
    cached_articles = {}
    if os.path.exists(db_path):
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                articles_list = cached_data.get("articles", [])
                cached_articles = {art["link"]: art for art in articles_list if "link" in art}
            print(f"Loaded {len(cached_articles)} articles from local database cache.")
        except Exception as e:
            print(f"[Warning] Failed to read database: {e}")

    # 2. Fetch and aggregate all feeds
    raw_articles = []
    
    # Category: AI
    for source, url in TECH_FEEDS.items():
        raw_articles.extend(fetch_rss_feed(source, url, "AI"))
    raw_articles.extend(scrape_anthropic())
    raw_articles.extend(fetch_duckduckgo_news())
    
    # Category: SCMP
    scmp_raw = []
    for source, url in SCMP_FEEDS.items():
        scmp_raw.extend(fetch_rss_feed(source, url, "SCMP"))
        
    # Category: Aeon
    for source, url in AEON_FEEDS.items():
        raw_articles.extend(fetch_rss_feed(source, url, "Aeon"))

    # 3. Initialize OpenAI Client
    openai_client = get_openai_client()

    # 4. Filter SCMP Articles
    scmp_filtered = filter_scmp_articles(openai_client, scmp_raw)
    raw_articles.extend(scmp_filtered)

    # 5. Process and Summarize (with Cache Checking)
    print("\nProcessing and summarizing new articles...")
    processed_articles = []
    
    now_utc = datetime.now(timezone.utc)
    cutoff_time = now_utc - timedelta(hours=TIME_WINDOW_HOURS)
    
    for art in raw_articles:
        link = art["link"]
        pub_dt = parse_date(art["published_date"])
        
        # Enforce strict 24-hour limit
        if pub_dt < cutoff_time:
            continue
            
        # Check cache
        if link in cached_articles:
            # Re-insert existing item to keep summary/details intact
            processed_articles.append(cached_articles[link])
            continue
            
        # Summarize new article
        print(f"New article found [{art['source']}]: '{art['title']}'")
        if not openai_disabled and openai_client:
            time.sleep(0.1) # Rate limit safety
            summary = summarize_article(
                openai_client, 
                art["title"], 
                art["summary"], 
                art["category"], 
                art["source"]
            )
            art["summary"] = summary
            
        processed_articles.append(art)

    # 6. Final Deduplication and Sorting (Strictly within last 24h)
    unique_articles = {}
    for art in processed_articles:
        link = art["link"]
        pub_dt = parse_date(art["published_date"])
        # Final safety check for 24 hours
        if pub_dt >= cutoff_time:
            if link not in unique_articles or parse_date(unique_articles[link]["published_date"]) < pub_dt:
                unique_articles[link] = art
                
    final_list = list(unique_articles.values())
    # Sort by published date descending
    final_list.sort(key=lambda x: parse_date(x.get("published_date", "")), reverse=True)

    # 7. Write to news_data.json
    output_data = {
        "last_updated": now_utc.isoformat(),
        "articles": final_list
    }
    
    try:
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"\nAggregated database successfully updated at: {db_path}")
        print(f"Total active display articles (last 24h): {len(final_list)}")
        
        # Categorical counts for verification
        ai_count = sum(1 for a in final_list if a["category"] == "AI")
        scmp_count = sum(1 for a in final_list if a["category"] == "SCMP")
        aeon_count = sum(1 for a in final_list if a["category"] == "Aeon")
        print(f"  AI Stories:   {ai_count}")
        print(f"  SCMP Stories: {scmp_count}")
        print(f"  Aeon Stories: {aeon_count}")
    except Exception as e:
        print(f"[Error] Failed to write database JSON: {e}")
        
    print("=" * 60)

if __name__ == "__main__":
    aggregate_pipeline()
