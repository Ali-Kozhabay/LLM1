import logging
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List

from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD

    async def send_email(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: str = None
    ) -> bool:
        """Send email using SMTP"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.smtp_user
            message["To"] = ", ".join(to_emails)

            # Add text content
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)

            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=True,
                username=self.smtp_user,
                password=self.smtp_password,
            )
            
            logger.info(f"Email sent successfully to {to_emails}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    async def send_otp_email(self, email: str, otp_code: str, expires_minutes: int = 5) -> bool:
        """Send OTP code via email"""
        subject = "Password Reset - OTP Code"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Password Reset OTP</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    text-align: center;
                    padding: 20px 0;
                    border-bottom: 2px solid #007bff;
                }}
                .content {{
                    padding: 30px 20px;
                    text-align: center;
                }}
                .otp-code {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #007bff;
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    letter-spacing: 8px;
                    margin: 20px 0;
                }}
                .warning {{
                    color: #dc3545;
                    font-weight: bold;
                    margin-top: 20px;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #dee2e6;
                    text-align: center;
                    color: #6c757d;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Intelligent LMS</h1>
                <h2>Password Reset Request</h2>
            </div>
            
            <div class="content">
                <p>You have requested to reset your password. Please use the following OTP code:</p>
                
                <div class="otp-code">{otp_code}</div>
                
                <p>This OTP code will expire in <strong>{expires_minutes} minutes</strong>.</p>
                
                <p>If you did not request this password reset, please ignore this email.</p>
                
                <div class="warning">
                    ⚠️ Never share this OTP code with anyone!
                </div>
            </div>
            
            <div class="footer">
                <p>This is an automated message from Intelligent LMS.</p>
                <p>Please do not reply to this email.</p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Intelligent LMS - Password Reset Request
        
        You have requested to reset your password.
        
        Your OTP code is: {otp_code}
        
        This code will expire in {expires_minutes} minutes.
        
        If you did not request this password reset, please ignore this email.
        
        Never share this OTP code with anyone!
        """
        
        return await self.send_email([email], subject, html_content, text_content)

# Create global instance
email_service = EmailService()
