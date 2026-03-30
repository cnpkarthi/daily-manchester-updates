import os
import ssl
import smtplib
import time
from email.message import EmailMessage
from google import genai

# --- CONFIGURATION (Safe for GitHub) ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SENDER_EMAIL = "cnpkarthi@gmail.com"
RECEIVER_EMAILS = ["cnpkarthi@gmail.com","cnpkarthi1@gmail.com"]
APP_PASSWORD = os.environ.get("APP_PASSWORD") 
TARGET_CITY = "Manchester, CT"

client = genai.Client(api_key=GEMINI_API_KEY)

def get_gemini_update():
    """Fetches real-time local updates using Gemini with Google Search."""
    # We enable 'google_search' so Gemini can find actual current deals
    prompt = (
        f"Today is {time.strftime('%A, %B %d, %Y')}. Search for today's US Market news and pick buy/sell stocks ideas  "
        "Format as a clean HTML summary with links included."
    )

    wait_times = [30, 60, 120] 
    for attempt, wait_sec in enumerate(wait_times):
        try:
            response = client.models.generate_content(
                model="gemini-3.1-pro-preview", 
                contents=prompt,
                 config={}
            )
            return response.text
            
        except Exception as e:
            error_msg = str(e)
            # If it's a 503 (Overloaded) or 429 (Too Many Requests)
            if "503" in error_msg or "429" in error_msg:
                print(f"Server busy (Attempt {attempt + 1}). Retrying in {wait_sec}s...")
                time.sleep(wait_sec)
            else:
                return f"<p>Permanent Error: {error_msg}</p>"
    
    return "<p>Error: Gemini servers were unavailable after 3 attempts. Please check back tomorrow.</p>"

def send_email():
    """Formats and sends the email."""
    print("Generating real-time Manchester update...")
    content = get_gemini_update()
    
    msg = EmailMessage()
    msg['Subject'] = f"Daily US Markets Update: {time.strftime('%b %d, %Y')}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = ", ".join(RECEIVER_EMAILS)
    msg.set_content("Please enable HTML to view this update.")
    msg.add_alternative(content, subtype='html')

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    send_email() 
