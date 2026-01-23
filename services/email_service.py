import yagmail
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EmailService:
    def __init__(self):
        # Gmail credentials from environment variables
        self.sender_email = os.getenv("GMAIL_EMAIL")
        self.sender_password = os.getenv("GMAIL_PASSWORD")

        if not self.sender_email or not self.sender_password:
            print("Gmail credentials not found in environment variables")
            print("Please set GMAIL_EMAIL and GMAIL_PASSWORD in .env file")
            self.yag = None
            return

        try:
            self.yag = yagmail.SMTP(self.sender_email, self.sender_password)
            print("✅ Email service initialized successfully")
        except Exception as e:
            print(f"Email service initialization failed: {e}")
            print("Make sure you have:")
            print("1. Correct Gmail email and app password")
            print("2. 2-factor authentication enabled on Gmail")
            print("3. App password generated for 'Mail' application")
            self.yag = None

    def send_password_reset_email(self, recipient_email: str, reset_token: str) -> bool:
        """
        Send password reset email to user
        """
        if not self.yag:
            print(" Email service not available")
            return False

        try:
            reset_link = f"http://localhost:5174/reset-password?token={reset_token}"

            subject = "SumItUp - Password Reset Request"

            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="color: white; margin: 0; font-size: 28px;">SumItUp</h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">Password Reset</p>
                </div>

                <div style="background: white; padding: 40px; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h2 style="color: #333; margin-top: 0;">Reset Your Password</h2>

                    <p style="color: #666; line-height: 1.6;">
                        We received a request to reset your password for your SumItUp account.
                        Click the button below to reset your password:
                    </p>

                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}"
                           style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                  color: white;
                                  padding: 15px 30px;
                                  text-decoration: none;
                                  border-radius: 8px;
                                  font-weight: bold;
                                  display: inline-block;
                                  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);">
                            Reset Password
                        </a>
                    </div>

                    <p style="color: #666; font-size: 14px; margin-bottom: 20px;">
                        This link will expire in 1 hour for security reasons.
                    </p>

                    <p style="color: #666; font-size: 14px;">
                        If you didn't request this password reset, please ignore this email.
                        Your password will remain unchanged.
                    </p>

                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">

                    <p style="color: #999; font-size: 12px; text-align: center;">
                        If the button doesn't work, copy and paste this link into your browser:<br>
                        <a href="{reset_link}" style="color: #667eea; word-break: break-all;">{reset_link}</a>
                    </p>
                </div>

                <div style="text-align: center; padding: 20px; color: #999; font-size: 12px;">
                    <p>© 2026 SumItUp Inc. All rights reserved.</p>
                </div>
            </div>
            """

            self.yag.send(
                to=recipient_email,
                subject=subject,
                contents=html_content
            )

            print(f"✅ Password reset email sent to {recipient_email}")
            return True

        except Exception as e:
            print(f"Failed to send email to {recipient_email}: {e}")
            return False

# Global email service instance
email_service = EmailService()