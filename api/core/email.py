"""
Email utilities for sending password reset and other emails.
Handles SMTP connection and sending with fallback to console logging in development.
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from api.config import settings

logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Send an email using SMTP settings from config.
    Falls back to console logging if SMTP is not configured.
    """
    # Check if SMTP is configured
    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP not configured. Logging email to console.")
        print(f"\n{'='*60}\nEMAIL TO: {to_email}\nSUBJECT: {subject}\n{'='*60}\n{html_content}\n{'='*60}\n")
        return False

    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = settings.SMTP_FROM_EMAIL
        message["To"] = to_email

        # Add HTML content
        part = MIMEText(html_content, "html")
        message.attach(part)

        # Connect to SMTP server
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()  # Secure the connection
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, to_email, message.as_string())
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        # Fallback to console log on error
        print(f"\n[ERROR SENDING EMAIL] To: {to_email}\nSubject: {subject}\nContent:\n{html_content}\n")
        return False


def send_password_reset_email(email: str, token: str, frontend_url: str = "http://localhost:3000"):
    """
    Send password reset email to user.
    """
    reset_link = f"{frontend_url}/reset-password?token={token}"
    
    subject = "Reset Your Password - Lexicon"
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
        <h2 style="color: #333;">Reset Your Password</h2>
        <p>Hello,</p>
        <p>We received a request to reset the password for your Lexicon account.</p>
        <p>Click the button below to reset your password. This link will expire in 1 hour.</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_link}" style="background-color: #0070f3; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">Reset Password</a>
        </div>
        <p style="color: #666; font-size: 14px;">If you didn't request this, you can safely ignore this email.</p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="color: #999; font-size: 12px;">Link not working? Copy and paste this URL into your browser:<br>{reset_link}</p>
    </div>
    """
    
    return send_email(email, subject, html_content)


def send_password_changed_email(email: str):
    """
    Send confirmation email when password is successfully changed.
    """
    subject = "Password Changed Successfully - Lexicon"
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 10px;">
        <h2 style="color: #333;">Password Changed</h2>
        <p>Hello,</p>
        <p>Your password for Lexicon has been successfully changed.</p>
        <p>If you did not make this change, please contact support immediately.</p>
    </div>
    """
    
    return send_email(email, subject, html_content)
