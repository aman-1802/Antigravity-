import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from .config import SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SENDER_EMAIL, RECEIVER_EMAIL

def send_newsletter_email(html_content, subject=None):
    """
    Sends the HTML newsletter to the recipient using the SMTP configuration.
    """
    if not subject:
        current_date = datetime.now().strftime("%B %d, %Y")
        subject = f"🦾 SCMP Daily Digest | {current_date}"
        
    print("=" * 60)
    print("  SCMP NEWS MAILER: INITIATING DISPATCH")
    print("=" * 60)
    
    # Check if credentials are set
    if not SMTP_USER or not SMTP_PASSWORD:
        print("[Warning] SMTP_USER or SMTP_PASSWORD is not configured. Email cannot be sent.")
        print("  Please check your '.env' file or environment variables.")
        print("  Falling back to saving the HTML preview locally.")
        print("=" * 60)
        return False
        
    print(f"Preparing email:")
    print(f"  Sender:    {SENDER_EMAIL}")
    print(f"  Recipient: {RECEIVER_EMAIL}")
    print(f"  Subject:   {subject.encode('ascii', errors='ignore').decode('ascii')}")
    print(f"  SMTP Host: {SMTP_SERVER}:{SMTP_PORT}")
    
    try:
        # Create message container
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        
        # Plain text fallback
        text_fallback = "Please use an HTML-compatible email client to read today's SCMP news digest."
        part1 = MIMEText(text_fallback, 'plain')
        part2 = MIMEText(html_content, 'html')
        
        msg.attach(part1)
        msg.attach(part2)
        
        # Connect to SMTP server
        print("Connecting to SMTP server...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.ehlo()
        
        # Secure the connection using TLS
        if SMTP_PORT == 587:
            print("Securing connection with STARTTLS...")
            server.starttls()
            server.ehlo()
            
        print("Logging in to SMTP server...")
        server.login(SMTP_USER, SMTP_PASSWORD)
        
        print("Sending email...")
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        
        print("Email sent successfully!")
        print("=" * 60)
        return True
    except Exception as e:
        print(f"  [Error] Failed to send email: {str(e)}")
        print("=" * 60)
        return False

if __name__ == "__main__":
    # Test mailer with mockup content
    mockup_html = "<h1>SCMP Daily Digest Test</h1><p>This is a test of the SCMP newsletter agent mailer component.</p>"
    send_newsletter_email(mockup_html, "SCMP Newsletter Test Mail")
