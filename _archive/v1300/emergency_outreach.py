#!/usr/bin/env python3
"""
EMERGENCY REVENUE SCRIPT: Send Outreach Email to Charle Agency
Uses existing GMAIL_USER / GMAIL_PASS from environment.
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_outreach_email():
    # Get credentials from environment
    sender_email = os.environ.get('GMAIL_USER') or os.environ.get('GMAIL_USERNAME')
    sender_password = os.environ.get('GMAIL_PASS') or os.environ.get('GMAIL_PASSWORD')
    
    if not sender_email or not sender_password:
        print("❌ ERROR: GMAIL_USER and GMAIL_PASS environment variables not set.")
        print("Set them with:")
        print('  $env:GMAIL_USER = "your_email@gmail.com"')
        print('  $env:GMAIL_PASS = "your_app_password"')
        return False
    
    # Target: Charle Agency
    recipient_email = "hello@charle.co.uk"
    
    # Compose the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "For Nic Dunn: Hiring Developers vs. Sync Automation"
    
    body = """Hey Nic / Team,

Saw you're actively recruiting developers in London.

If your team manages high-volume inventory syncs for Plus clients, you've likely hit the 429 Rate Limit walls during BFCM. I built a compiled middleware specifically to kill-switch these errors using Webhooks (bypassing the need for custom dev hours).

It's an Agency-First binary (Self-Hosted). Might save your new hires 40+ hours of debugging sync drifts.

Docs & License: https://payhip.com/b/GJc5k

Best,
YEDAN
"""
    
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        print(f"📧 Connecting to Gmail SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        print(f"📧 Sending email to {recipient_email}...")
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        
        print(f"✅ EMAIL SENT to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    send_outreach_email()
