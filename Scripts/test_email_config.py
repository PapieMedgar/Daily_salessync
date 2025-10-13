#!/usr/bin/env python3
"""
Test Email Configuration

This script tests the email configuration without sending actual reports.
It verifies that the email settings are correct and can connect to the SMTP server.
"""

import os
import sys
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

def test_email_config():
    """Test email configuration and send a test email."""
    load_dotenv()
    
    # Get email configuration
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    recipients = os.getenv('EMAIL_RECIPIENTS', '').split(',')
    
    # Clean up recipients
    recipients = [email.strip() for email in recipients if email.strip()]
    
    print("Email Configuration Test")
    print("=" * 30)
    print(f"SMTP Server: {smtp_server}:{smtp_port}")
    print(f"Sender Email: {sender_email}")
    print(f"Recipients: {', '.join(recipients)}")
    print()
    
    # Validate configuration
    if not sender_email or not sender_password:
        print("❌ Error: SENDER_EMAIL and SENDER_PASSWORD must be set in .env file")
        return False
    
    if not recipients or recipients == ['']:
        print("❌ Error: EMAIL_RECIPIENTS must be set in .env file")
        return False
    
    try:
        # Test SMTP connection
        print("Testing SMTP connection...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        print("✅ SMTP connection successful")
        
        # Send test email
        print("Sending test email...")
        msg = MIMEText("This is a test email to verify the daily reports configuration.")
        msg['Subject'] = "Daily Reports - Configuration Test"
        msg['From'] = sender_email
        msg['To'] = ', '.join(recipients)
        
        server.sendmail(sender_email, recipients, msg.as_string())
        server.quit()
        
        print("✅ Test email sent successfully!")
        print(f"   Sent to: {', '.join(recipients)}")
        print()
        print("Your email configuration is working correctly.")
        print("The daily reports will be sent to these recipients at 4:00 PM daily.")
        
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ Error: Email authentication failed")
        print("   Please check your SENDER_EMAIL and SENDER_PASSWORD")
        print("   For Gmail, make sure you're using an App Password")
        return False
        
    except smtplib.SMTPException as e:
        print(f"❌ Error: SMTP error - {e}")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function."""
    if test_email_config():
        print("\n🎉 Email configuration test passed!")
        print("You can now set up the daily reports automation.")
        sys.exit(0)
    else:
        print("\n💥 Email configuration test failed!")
        print("Please fix the issues above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()