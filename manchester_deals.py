import os
import ssl
import smtplib
import time
from email.message import EmailMessage
from google import genai

# --- CONFIGURATION (Safe for GitHub) ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SENDER_EMAIL = "cnpkarthi@gmail.com"
APP_PASSWORD = os.environ.get("APP_PASSWORD") 
TARGET_CITY = "Manchester, CT"

client = genai.Client(api_key=GEMINI_API_KEY)

def get_gemini_update():
    """Fetches real-time local updates using Gemini with Google Search."""
    # We enable 'google_search' so Gemini can find actual current deals
    prompt = (
        f"Today is {time.strftime('%A, %B %d, %Y')}. Search for today's food freebies, "
        f"restaurant BOGO offers, and community events in and around {TARGET_CITY}. "
        "Include library events and retail deals. Format as a clean HTML summary "
        "with restaurant links included."
    )
    
    try:
        # Using the search tool allows for real-time local data
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-preview", # Latest stable fast model
            contents=prompt,
            config={
                'tools': [{'google_search': {}}]
            }
        )
        return response.text
    except Exception as e:
        return f"<p>Error fetching updates: {e}</p>"

def send_email():
    """Formats and sends the email."""
    print("Generating real-time Manchester update...")
    content = get_gemini_update()
    
    msg = EmailMessage()
    msg['Subject'] = f"Daily Manchester Update: {time.strftime('%b %d, %Y')}"
    msg['From'] = SENDER_EMAIL
    msg['To'] = SENDER_EMAIL
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
