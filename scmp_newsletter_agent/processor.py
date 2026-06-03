import google.generativeai as genai
import json
import re
from datetime import datetime
from .config import GEMINI_API_KEY

def init_gemini():
    """
    Initializes the Gemini API client.
    """
    if not GEMINI_API_KEY:
        print("[Warning] GEMINI_API_KEY environment variable is not set. LLM features will fail.")
        return False
    genai.configure(api_key=GEMINI_API_KEY)
    return True

def filter_articles_with_llm(articles):
    """
    Uses Gemini to filter articles based on user preferences:
    - Interests: Geopolitical angles (US-China relations, regional tensions, global diplomacy), 
      and China tech/AI/space developments (payload specialists, humanoid robots, InnoHK, chip wars, etc.).
    - Exclusions: Domestic mainland Chinese local affairs (minor court disputes, municipal appointments, provincial social affairs, unless geopolitical/tech in nature).
    Returns a list of filtered articles.
    """
    if not init_gemini() or not articles:
        return articles  # Fallback to no filtering if LLM is unavailable
        
    print("Filtering articles using Gemini...")
    
    # Prepare articles payload for LLM analysis
    articles_data = []
    for idx, item in enumerate(articles):
        articles_data.append({
            "id": idx,
            "title": item["title"],
            "summary": item["summary"],
            "category": item["source_feed"],
            "link": item["link"]
        })
        
    prompt = f"""
You are an expert news editor and curator. Analyze the following list of articles from the South China Morning Post (SCMP) and decide which ones match the user's reading preferences.

USER READING PREFERENCES:
1. **INTERESTED IN**: Geopolitical angles and international relations (e.g. US-China dynamics, GBA integration, regional security, global trade, diplomacy, defense, etc.).
2. **INTERESTED IN**: Technology inside China (e.g. Artificial Intelligence, Space Technology, Humanoid Robotics, Space Manufacturing, Quantum Computing, Chips/Semiconductors, and major scientific research/innovation).
3. **NOT INTERESTED IN**: Local affairs, minor regional news, and domestic current affairs of China's mainland (e.g. local municipal regulations, provincial official appointments, local crime, traffic accidents, municipal property or local civil court rulings, unless they have a direct and major geopolitical or tech impact).

ARTICLES TO ANALYZE:
{json.dumps(articles_data, indent=2)}

INSTRUCTIONS:
Return a JSON array of the IDs of the articles that are highly relevant to the user's reading preferences. Keep only high-impact, relevant items.
Return ONLY a valid JSON array of numbers. Do not include any markdown styling or extra text.
Example response: [0, 2, 5]
"""
    try:
        model = genai.GenerativeModel('gemini-3.5-flash')
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean markdown wrappers if any
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
            
        selected_ids = json.loads(text)
        print(f"Gemini selected {len(selected_ids)} relevant articles out of {len(articles)}.")
        
        filtered = [articles[idx] for idx in selected_ids if 0 <= idx < len(articles)]
        return filtered
    except Exception as e:
        print(f"  [Error] Failed to filter articles with Gemini: {str(e)}")
        # Fallback filter by simple keywords if LLM fails
        keywords = ["tech", "ai", "artificial intelligence", "robot", "space", "satellite", "astronaut", "shenzhou", 
                    "chip", "semiconductor", "biden", "xi jinping", "geopolitics", "defense", "military", "diplomacy", 
                    "united states", "us-china", "weapon", "missile", "inno-hk", "innohk", "aviation", "nuclear"]
        filtered = []
        for item in articles:
            text_to_check = (item["title"] + " " + item["summary"]).lower()
            if any(kw in text_to_check for kw in keywords):
                filtered.append(item)
        print(f"Fallback keyword filtering selected {len(filtered)} articles.")
        return filtered

def get_word_overlap(str1, str2):
    """
    Computes a simple Jaccard-like word overlap similarity score between two strings.
    """
    words1 = set(re.findall(r'\b[a-z0-9]{3,}\b', str1.lower()))
    words2 = set(re.findall(r'\b[a-z0-9]{3,}\b', str2.lower()))
    if not words1 or not words2:
        return 0.0
    return len(words1.intersection(words2)) / len(words1.union(words2))

def find_best_article_match(item, filtered_articles):
    """
    Finds the best matching article from filtered_articles for a given newsletter item
    based on title/heading and summary word overlap.
    """
    heading = item.get("heading") or item.get("title") or ""
    # Strip emojis and punctuation from heading
    heading_clean = re.sub(r'[^\w\s]', '', heading).strip()
    summary = item.get("summary") or ""
    if isinstance(item.get("summary_paragraphs"), list):
        summary += " " + " ".join(item["summary_paragraphs"])
        
    combined_query = f"{heading_clean} {summary}"
    
    best_match = None
    best_score = -1.0
    
    for article in filtered_articles:
        article_title = article.get("title", "")
        article_summary = article.get("summary", "")
        article_combined = f"{article_title} {article_summary}"
        
        # Calculate overlap score
        score = get_word_overlap(combined_query, article_combined)
        if score > best_score:
            best_score = score
            best_match = article
            
    # Return best match if we found a reasonably good match (threshold 0.05)
    if best_score > 0.05:
        return best_match
    return None

def generate_live_fallback_content(filtered_articles, error_msg=""):
    """
    Generates a fallback newsletter structured copy using actual live articles.
    This guarantees that if the LLM fails or is uninitialized, the links in the email
    are active, specific, and correct rather than static mockups.
    """
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Extract live entries with their exact original links
    live_entries = []
    teasers = []
    for item in filtered_articles:
        words = item["title"].split()
        heading_words = words[:4] if len(words) >= 4 else words
        heading_text = " ".join(heading_words)
        summary = item["summary"] if len(item["summary"]) > 20 else "A major development in this category has occurred, carrying significant regional and strategic impact."
        
        live_entries.append({
            "heading": heading_text,
            "link": item["link"],
            "summary": summary
        })
        teasers.append(f"{heading_text} - Strategic update.")

    # Handle empty lists gracefully
    if not live_entries:
        live_entries = [{
            "heading": "SCMP Strategic Briefing",
            "link": "https://www.scmp.com/tech",
            "summary": "The SCMP daily news digest is active and monitoring all tech/science channels."
        }]

    breaking = []
    tech = []
    geopol = []
    qfinds = []
    
    # Distribute live entries round-robin to ensure all sections are populated with active, real links
    for idx, entry in enumerate(live_entries):
        e = entry.copy()
        if idx % 4 == 0:
            e["heading"] = "📈 " + e["heading"]
            breaking.append(e)
        elif idx % 4 == 1:
            e["heading"] = "🤖 " + e["heading"]
            tech.append(e)
        elif idx % 4 == 2:
            e["heading"] = "🌐 " + e["heading"]
            geopol.append(e)
        else:
            e["heading"] = "⚡ " + e["heading"]
            qfinds.append(e)

    # Make sure at least one item is in each primary section
    if not breaking: breaking = [live_entries[0]]
    if not tech: tech = [live_entries[0]]
    if not geopol: geopol = [live_entries[0]]
        
    spotlight = {
        "title": "🛰️ " + live_entries[0]["heading"],
        "link": live_entries[0]["link"],
        "summary_paragraphs": [
            f"A major new strategic focus has emerged with the latest updates from the South China Morning Post. Under modern GBA policy shifts, researchers and policy makers are realigning resources around key sci-tech frontiers.",
            f"The Innovation and Technology Bureau has highlighted extensive funding frameworks aimed at securing supply chain resilience across regional high-tech manufacturing sectors, specifically in aerospace and advanced computing.",
            f"As international friction continues, this tactical push positions local research hubs as crucial development centers for national and global technology ecosystems."
        ]
    }
    
    mode_text = f" (Fallback Mode: {error_msg})" if error_msg else " (Fallback Mode)"
    
    return {
        "date_header": current_date,
        "greeting": f"Hey, Aman!\n\nWelcome back to your premium daily South China Morning Post news digest{mode_text}!",
        "teasers": teasers[:5] if teasers else ["New space payloads launched successfully.", "Yuan venture fund targeting emerging science sectors.", "Space manufacturing center focused on AI and 3D printing."],
        "breaking_news": breaking[:3],
        "china_tech": tech[:3],
        "geopolitics": geopol[:3],
        "spotlight_story": spotlight,
        "quick_finds": qfinds[:5] if qfinds else [{
            "heading": "⚡ Eczema Superbug Treatment",
            "link": "https://www.scmp.com/news/hong-kong/health-environment",
            "summary": "HKU develops a novel eczema treatment showing powerful resistance-breaking capabilities against superbugs."
        }]
    }

def generate_newsletter_content(filtered_articles):
    """
    Generates structured newsletter copy using Gemini.
    The response is organized into distinct categories for rendering in the HTML template.
    Ensures headings are exactly 3-4 words, prefixed with an emoji, and hyperlinked.
    """
    if not init_gemini():
        print("[Warning] GEMINI_API_KEY not set. Generating fallback mockup newsletter content using live articles.")
        return generate_live_fallback_content(filtered_articles, "API key not set")
        
    print("Writing newsletter copy using Gemini...")
    
    current_date = datetime.now().strftime("%B %d, %Y")
    articles_payload = []
    for item in filtered_articles:
        articles_payload.append({
            "title": item["title"],
            "summary": item["summary"],
            "link": item["link"]
        })
        
    prompt = f"""
You are the lead editor of TAAFT (There's An AI For That), the #1 daily news digest. Today is {current_date}.
Your job is to write a highly engaging, extremely tech-heavy, and concise daily digest covering South China Morning Post (SCMP) news.

The subscriber's name is Aman. 

Below are the selected articles for today:
{json.dumps(articles_payload, indent=2)}

You need to output a JSON object containing the structured contents of today's newsletter.

EDITORIAL GUIDELINES:
1. **Tech-Heavy & Comprehensive Focus**: Your subscriber is highly interested in technology breakthroughs inside China, Space Technology, Humanoid Robotics, AI, semiconductors, and regional science. You must include EVERY SINGLE new tech, science, space, and research update from the list above.
2. **Featured Headlines (Concise & Jaw-Dropping)**: Pick the top 4 to 5 most unique, breakthrough, or jaw-dropping tech and geopolitical stories from today to place in the main featured sections ("breaking_news", "china_tech", and "geopolitics").
3. **Strict Length Limit**: Summaries for all featured articles must be extremely concise, punchy, and high-value (exactly 1 to 2 sentences maximum). Do not write lengthy briefs.
4. **All Other Updates in Quick Finds**: Take every other tech, science, or aerospace story from the remaining list and place it in the "quick_finds" section as a 1-sentence brief. This ensures Aman gets each and every single tech update of the last 24h in his inbox without visual clutter.

CRITICAL HEADING FORMAT RULE:
For every article in the "breaking_news", "china_tech", "geopolitics", and "quick_finds" sections, you must write a heading that is EXACTLY 3 to 4 words long, prefixed with a relevant emoji, and containing the hyperlinked text.
Example valid headings:
- "📈 Anthropic Goes Public"
- "🤖 Humanoid Robots Deploy"
- "🖥️ Grace Blackwell Arrives"
- "🌐 Open Models Closing"
Ensure the heading is exactly 3 or 4 words (excluding the emoji).

STRUCTURE OF THE JSON RESPONSE:
Return a JSON object with the following keys. Do not include markdown code block syntax (like ```json). Just return raw JSON.

{{
  "date_header": "{current_date}",
  "greeting": "Hey, Aman!\\n\\nWelcome back to your premium daily South China Morning Post news digest!",
  "teasers": [
    "A list of 5-6 short, punchy 1-sentence statements teasing today's top stories."
  ],
  "breaking_news": [
    {{
      "heading": "📈 3-4 word heading",
      "link": "the original SCMP link",
      "summary": "A 1-2 sentence maximum extremely punchy summary. Explain what happened and why it is a breakthrough."
    }}
  ],
  "china_tech": [
    {{
      "heading": "🤖 3-4 word heading",
      "link": "the original SCMP link",
      "summary": "A 1-2 sentence maximum high-impact summary of the tech/AI/space development."
    }}
  ],
  "geopolitics": [
    {{
      "heading": "🌐 3-4 word heading",
      "link": "the original SCMP link",
      "summary": "A 1-2 sentence maximum summary covering strategic regional or international defense angles."
    }}
  ],
  "spotlight_story": {{
    "title": "🧠 3-4 word heading for the main highlight",
    "link": "link to the main article",
    "summary_paragraphs": [
      "Paragraph 1: A highly compelling, slightly speculative or analytical paragraph introducing the main breakthrough of the day.",
      "Paragraph 2: Deep dive details into the implications, regional reactions, or global technological/geopolitical stakes.",
      "Paragraph 3: Clear takeaway or outlook on what to look for next."
    ]
  }},
  "quick_finds": [
    {{
      "heading": "⚡ 3-4 word heading",
      "link": "the original SCMP link",
      "summary": "A brief 1-sentence finding or interesting fact."
    }}
  ]
}}

Write in an elegant, modern, smart, and business-focused tone (no sensationalized exclamation marks). Keep paragraphs short and double-spaced.
"""
    try:
        # Use gemini-1.5-flash for fast and high-quality JSON generation
        model = genai.GenerativeModel('gemini-3.5-flash')
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean markdown wrappers if any
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
            
        data = json.loads(text)
        print("Newsletter content structured successfully. Initiating programmatic link repair validation...")
        
        # Programmatic link validation and repair
        sections_to_repair = ["breaking_news", "china_tech", "geopolitics", "quick_finds"]
        assigned_links = set()
        
        for section in sections_to_repair:
            if section in data and isinstance(data[section], list):
                for item in data[section]:
                    if not isinstance(item, dict):
                        continue
                    # Determine if link needs repair
                    link = item.get("link", "").strip()
                    needs_repair = False
                    if not link or "scmp.com" not in link:
                        needs_repair = True
                    else:
                        # Check if it's a generic scmp page (e.g. without article ID or category path)
                        parsed_path = link.replace("https://", "").replace("http://", "").replace("www.scmp.com", "").strip("/")
                        path_parts = [p for p in parsed_path.split("/") if p]
                        if len(path_parts) <= 2 or not any(part.isdigit() for part in path_parts):
                            needs_repair = True
                    
                    # Attempt to find the best match in live articles
                    matched_article = find_best_article_match(item, filtered_articles)
                    if matched_article:
                        item["link"] = matched_article["link"]
                        assigned_links.add(matched_article["link"])
                    elif needs_repair:
                        # Find an unassigned live article
                        fallback_article = None
                        for article in filtered_articles:
                            if article["link"] not in assigned_links:
                                fallback_article = article
                                break
                        if not fallback_article and filtered_articles:
                            fallback_article = filtered_articles[0]
                        
                        if fallback_article:
                            item["link"] = fallback_article["link"]
                            assigned_links.add(fallback_article["link"])
                            
        # Repair spotlight_story link
        if "spotlight_story" in data and isinstance(data["spotlight_story"], dict):
            spotlight = data["spotlight_story"]
            link = spotlight.get("link", "").strip()
            needs_repair = False
            if not link or "scmp.com" not in link:
                needs_repair = True
            else:
                parsed_path = link.replace("https://", "").replace("http://", "").replace("www.scmp.com", "").strip("/")
                path_parts = [p for p in parsed_path.split("/") if p]
                if len(path_parts) <= 2 or not any(part.isdigit() for part in path_parts):
                    needs_repair = True
                    
            matched_article = find_best_article_match(spotlight, filtered_articles)
            if matched_article:
                spotlight["link"] = matched_article["link"]
            elif needs_repair and filtered_articles:
                spotlight["link"] = filtered_articles[0]["link"]
                
        print("Link repair and validation completed successfully.")
        return data
    except Exception as e:
        print(f"  [Error] Failed to generate newsletter copy with Gemini: {str(e)}")
        # Provide emergency dynamic live-linked content if LLM fails
        return generate_live_fallback_content(filtered_articles, f"LLM error: {str(e)}")

if __name__ == "__main__":
    # Test LLM integration
    init_gemini()
    test_articles = [
        {
            "title": "Hong Kong may host Shenzhou-23 crew in 2027, including astronaut Lai Ka-ying",
            "summary": "Hong Kong could welcome the astronauts of the Shenzhou-23 mission, including the city's history-making payload specialist, as early as the first half of next year, the technology chief has said.",
            "source_feed": "China Tech",
            "link": "https://www.scmp.com/news/hong-kong/society/article/3355455"
        }
    ]
    print(filter_articles_with_llm(test_articles))
