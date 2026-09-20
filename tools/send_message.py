import os
import smtplib
from email.mime.text import MIMEText
from agent.confirmation import confirm_action
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

def send_message(to: str, subject: str, body: str) -> str:
    """Sends an email, with user confirmation first."""
    description = f"Send email to: {to}\nSubject: {subject}\nBody: {body}"
    if not confirm_action(description):
        return "Message cancelled by user."

    # Read credentials from the .env file
    email_address = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    
    if not email_address or not password:
        return "Failed to send: EMAIL_ADDRESS or EMAIL_PASSWORD not found in .env file."

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["To"] = to
    msg["From"] = email_address

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(email_address, password)
            server.send_message(msg)
        return f"Email sent to {to}"
    except Exception as e:
        return f"Failed to send email: {e}"
