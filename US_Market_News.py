import os
import ssl
import smtplib
import time
from email.message import EmailMessage
from google import genai

# --- CONFIGURATION (Safe for GitHub) ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SENDER_EMAIL = "cnpkarthi@gmail.com"
RECIPIENTS = ["cnpkarthi@gmail.com", "cnpkarthi1@gmail.com"]
APP_PASSWORD = os.environ.get("APP_PASSWORD") 

client = genai.Client(api_key=GEMINI_API_KEY)


def get_geminiMarketNews_update():
    marketNews_Prompt = (
        f"Today is {time.strftime('%A, %B %d, %Y')}. "
        f"2. Search for today's US Market news"
        f"Format each sections separately in clean HTML with headings and links."
    )
    
       
    # Wait longer each time: 30s, 60s, 120s
    wait_times = [30, 60, 120] 
    
    for attempt, wait_sec in enumerate(wait_times):
        try:
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite-preview",
    contents=[
        marketNews_Prompt
    ],
    config={}
            )
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                print(f"Rate limit hit (Attempt {attempt + 1}). Retrying in {wait_sec}s...")
                time.sleep(wait_sec)
            else:
                return f"<p>Error fetching updates: {error_msg}</p>"
    
    return "<p>Error: Still hitting rate limits after 3 retries. Please try again later.</p>"
    
def get_gemininews_update():
    
    news_Prompt = (
        f"Today is {time.strftime('%A, %B %d, %Y')}. "
        f"Search for today's   news"
        f"Format each sections separately in clean HTML with headings and links."
    )
    
    # Wait longer each time: 30s, 60s, 120s
    wait_times = [30, 60, 120] 
    
    for attempt, wait_sec in enumerate(wait_times):
        try:
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite-preview",
    contents=[
        news_Prompt
    ],
    config={}
            )
            return response.text
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                print(f"Rate limit hit (Attempt {attempt + 1}). Retrying in {wait_sec}s...")
                time.sleep(wait_sec)
            else:
                return f"<p>Error fetching updates: {error_msg}</p>"
    
    return "<p>Error: Still hitting rate limits after 3 retries. Please try again later.</p>"
    
        
    
def send_email():
    """Formats and sends the email to multiple recipients."""
    print(f"Generating update for {time.strftime('%Y-%m-%d %H:%M:%S')}...")
    
    # 1. Fetch both sections
    events_newshtml = get_gemininews_update()
    market_news = get_geminiMarketNews_update()
    
    # 2. Combine them into one HTML body
    full_html = f"""
    <html>
        <body>
            <h1>Market, News Daily Update</h1>
            <hr>
            {events_newshtml}
            <hr>
            {market_news}
        </body>
    </html>
    """

    msg = EmailMessage()
    msg['Subject'] = f"Daily Update: {time.strftime('%b %d, %Y')}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = ", ".join(RECIPIENTS) 
    
    msg.set_content("Please enable HTML to view this update.")
    # Use the combined full_html here:
    msg.add_alternative(full_html, subtype='html')
    
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
        print(f"Email sent successfully to {len(RECIPIENTS)} recipients!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Run once for GitHub Actions
if __name__ == "__main__":
    send_email()
