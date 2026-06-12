import os
import argparse
from datetime import datetime
from .fetcher import fetch_scmp_news
from .processor import filter_articles_with_llm, generate_newsletter_content
from .template import render_newsletter
from .mailer import send_newsletter_email

def run_pipeline(force_send=False):
    """
    Coordinates the entire daily news digest newsletter execution:
    1. Fetches articles from SCMP RSS feeds within the last 24 hours.
    2. Filters and processes the articles using Gemini.
    3. Renders the HTML template with 3-4 word hyperlinked headings.
    4. Saves a local preview HTML file.
    5. Dispatches the email if configured or requested.
    """
    print("\n" + "=" * 60)
    print(f"  SCMP DAILY NEWSLETTER DIGEST PIPELINE STARTED: {datetime.now()}")
    print("=" * 60)
    
    # 1. Fetch
    raw_articles = fetch_scmp_news()
    if not raw_articles:
        print("\n[Result] No new articles found in the last 24 hours. Pipeline finished.")
        print("=" * 60)
        return
        
    # 2. Filter using LLM
    filtered_articles = filter_articles_with_llm(raw_articles)
    if not filtered_articles:
        print("\n[Result] No articles matched the geopolitics or technology filters. Pipeline finished.")
        print("=" * 60)
        return
        
    # 3. Process and write copy using LLM
    newsletter_data = generate_newsletter_content(filtered_articles)
    if not newsletter_data:
        print("\n[Error] Failed to generate newsletter structured copy. Exiting.")
        print("=" * 60)
        return
        
    # 3b. Generate Obsidian Markdown
    from .processor import generate_obsidian_markdown
    markdown_content = generate_obsidian_markdown(newsletter_data)
    
    # 3c. Save Obsidian Markdown to digests/ at the repository root
    digests_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "digests")
    os.makedirs(digests_dir, exist_ok=True)
    
    date_header = newsletter_data.get("date_header", datetime.now().strftime("%B %d, %Y"))
    try:
        dt = datetime.strptime(date_header, "%B %d, %Y")
        file_date_str = dt.strftime("%Y-%m-%d")
    except Exception:
        file_date_str = datetime.now().strftime("%Y-%m-%d")
        
    markdown_path = os.path.join(digests_dir, f"{file_date_str}.md")
    with open(markdown_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"\n[Obsidian Markdown Saved] Saved digest note to:\n  {os.path.abspath(markdown_path)}")
        
    # 4. Render HTML
    html_content = render_newsletter(newsletter_data)
    
    # 5. Save local preview
    preview_dir = os.path.join(os.path.dirname(__file__), "previews")
    os.makedirs(preview_dir, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    preview_path = os.path.join(preview_dir, f"digest_{date_str}.html")
    
    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"\n[Preview Saved] Local HTML preview generated at:\n  {os.path.abspath(preview_path)}")
    
    # 6. Send email
    subject = f"🦾 SCMP Daily Digest | {newsletter_data.get('date_header', datetime.now().strftime('%B %d, %Y'))}"
    mail_sent = send_newsletter_email(html_content, subject)
    
    if mail_sent:
        print(f"\n[Result] Success! Newsletter sent to your inbox.")
    else:
        print(f"\n[Result] Local preview saved. To send emails, please configure your SMTP credentials in '.env'.")
        
    print("=" * 60 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SCMP Daily News Digest Agent Orchestrator")
    parser.add_argument("--send", action="store_true", help="Force send email if credentials are set")
    args = parser.parse_args()
    
    run_pipeline(force_send=args.send)
