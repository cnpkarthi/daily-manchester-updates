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
TARGET_CITY = "Manchester, CT"

client = genai.Client(api_key=GEMINI_API_KEY)

def get_geminifreeevent_update():
    freeEvent_Prompt = ("/gen "
        f"Today is {time.strftime('%A, %B %d, %Y')}. Search for free events in Manchester, CT. Format each sections separately in clean HTML with headings and links."
    )
    
       
    # Wait longer each time: 30s, 60s, 120s
    wait_times = [30, 60, 120] 
    
    for attempt, wait_sec in enumerate(wait_times):
        try:
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite-preview",
    contents=[
        freeEvent_Prompt
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
    
def get_geminifoodfreebies_update():
    
    freeFood_Prompt = ("/gen "
        f"Today is {time.strftime('%A, %B %d, %Y')}. "
        f"today freebies and offers for food in and around Manchester, CT."
        f"Format each sections separately in clean HTML with headings and links."
    )
    
    # Wait longer each time: 30s, 60s, 120s
    wait_times = [30, 60, 120] 
    
    for attempt, wait_sec in enumerate(wait_times):
        try:
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite-preview",
    contents=[
        freeFood_Prompt
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
    events_html = get_geminifreeevent_update()
    food_html = get_geminifoodfreebies_update()
    
    # 2. Combine them into one HTML body
    full_html = f"""
    <html>
        <body>
            <h1>Manchester, CT Daily Update</h1>
            <hr>
            {events_html}
            <hr>
            {food_html}
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
