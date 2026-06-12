import os
import re
import glob
from datetime import datetime, timedelta
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
AGENT_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.dirname(AGENT_DIR)
load_dotenv(os.path.join(AGENT_DIR, ".env"))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def init_gemini():
    if not GEMINI_API_KEY:
        print("[Error] GEMINI_API_KEY is not set.")
        return False
    genai.configure(api_key=GEMINI_API_KEY)
    return True

def run_weekly_analysis():
    print("============================================================")
    print("  SCMP WEEKLY BRAIN ANALYZER: INITIATING EXTRACT & STUDY")
    print("============================================================")
    
    if not init_gemini():
        return
        
    digests_dir = os.path.join(ROOT_DIR, "digests")
    if not os.path.exists(digests_dir):
        print(f"[Error] Digests directory not found at: {digests_dir}")
        return
        
    # Get all markdown files in digests/
    md_files = glob.glob(os.path.join(digests_dir, "*.md"))
    if not md_files:
        print("[Warning] No digests found to analyze.")
        return
        
    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)
    
    weekly_digests = []
    
    for filepath in md_files:
        filename = os.path.basename(filepath)
        # Parse YYYY-MM-DD from filename
        match = re.match(r"^(\d{4}-\d{2}-\d{2})\.md$", filename)
        if not match:
            continue
            
        file_date_str = match.group(1)
        try:
            file_date = datetime.strptime(file_date_str, "%Y-%m-%d")
        except Exception:
            continue
            
        # Check if the file date falls within the last 7 days
        if seven_days_ago <= file_date <= today:
            print(f"Including digest: {filename}")
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            weekly_digests.append({
                "date": file_date_str,
                "content": content
            })
            
    if not weekly_digests:
        print("[Warning] No digests found from the past 7 days.")
        return
        
    # Sort digests by date
    weekly_digests.sort(key=lambda x: x["date"])
    
    # Construct prompt payload
    payload = []
    for item in weekly_digests:
        payload.append(f"### Digest Date: {item['date']}\n\n{item['content']}\n\n---\n")
        
    aggregated_content = "\n".join(payload)
    
    # Determine the week identifier (e.g. 2026-W24)
    year, week_num, _ = today.isocalendar()
    week_id = f"{year}-W{week_num:02d}"
    
    prompt = f"""
You are the lead intelligence analyst and research assistant for Aman's "Second Brain".
Analyze the following South China Morning Post (SCMP) daily newsletter digests collected over the past week (last 7 days):

{aggregated_content}

Your goal is to synthesize these digests into a high-value, structured weekly analysis report that Aman can study and ingest into his Obsidian vault.

INSTRUCTIONS:
1. **Identify Repeating Patterns & Concepts**: Extract technologies, geopolitics topics, or scientific concepts that appeared multiple times across different days (e.g., semiconductor export bans, specific AI startups, space payload launches, maritime friction). Explain the trend.
2. **Geopolitical & Tech Decoupling Analysis**: Detail how Chinese tech advancements or GBA integration are intersecting with international sanctions and trade friction.
3. **Study Guide & Deep Dives**: Create a dedicated section listing 3-5 specific technical concepts, research labs, or policy frameworks that emerged this week that Aman should study in-depth. For each concept, provide a concise explanation and tell him why it matters.
4. **Formatting for Obsidian**:
   - Write in clean, beautiful Markdown.
   - Use headings, sub-headings, and clear bullet points.
   - Cross-reference the source dates using Obsidian wiki-links (e.g. `[[{weekly_digests[0]['date']}]]`, `[[{weekly_digests[-1]['date']}]]`) so Aman can click through to the original daily notes.
   - Add frontmatter tags: `[scmp, weekly-synthesis, patterns, study-guide]`.

Create a title for the note: "Weekly Synthesis & Patterns - {week_id}"
"""
    
    try:
        print("Analyzing weekly digests using Gemini...")
        model = genai.GenerativeModel('gemini-3.5-flash')
        if model._client is None:
            from google.generativeai import client as genai_client
            model._client = genai_client.get_default_generative_client()
        request = model._prepare_request(contents=prompt)
        raw_response = model._client.generate_content(request, timeout=240.0)
        from google.generativeai.types import generation_types
        response = generation_types.GenerateContentResponse.from_response(raw_response)
        synthesis = response.text.strip()
        
        # Format the Obsidian note with frontmatter if the model didn't add it
        frontmatter = ""
        if not synthesis.startswith("---"):
            frontmatter = f"""---
date: {today.strftime("%Y-%m-%d")}
week: {week_id}
tags: [scmp, weekly-synthesis, patterns, study-guide]
type: weekly-synthesis
---

"""
        
        reports_dir = os.path.join(ROOT_DIR, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        
        report_path = os.path.join(reports_dir, f"weekly_synthesis_{week_id}.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(frontmatter + synthesis)
            
        print(f"\n[Report Saved] Successfully wrote weekly synthesis report to:\n  {os.path.abspath(report_path)}")
        print("============================================================")
    except Exception as e:
        print(f"  [Error] Failed to generate weekly synthesis: {str(e)}")
        
if __name__ == "__main__":
    run_weekly_analysis()
