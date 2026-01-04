#!/usr/bin/env python3
"""
YEDAN AGI: 24/7 Autonomous Revenue Engine
Runs continuously. Scans for leads. Sends outreach. Never stops.
"""
import smtplib
import os
import time
import json
import sqlite3
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# === CONFIGURATION ===
DB_PATH = "yedan_memory.db"
SCAN_INTERVAL_SECONDS = 300  # Check every 5 minutes
LOG_FILE = "revenue_engine.log"

# === TARGETS (Pre-loaded) ===
TARGETS = [
    {
        "name": "Charle Agency",
        "email": "hello@charle.co.uk",
        "subject": "For Nic Dunn: Hiring Developers vs. Sync Automation",
        "body": """Hey Nic / Team,

Saw you're actively recruiting developers in London.

If your team manages high-volume inventory syncs for Plus clients, you've likely hit the 429 Rate Limit walls during BFCM. I built a compiled middleware specifically to kill-switch these errors using Webhooks.

It's an Agency-First binary (Self-Hosted). Might save your new hires 40+ hours of debugging sync drifts.

Docs & License: https://payhip.com/b/GJc5k

Best,
YEDAN"""
    },
    {
        "name": "Blackbelt Commerce",
        "email": "info@blackbeltcommerce.com",
        "subject": "Re: Scaling Operations for Plus Clients",
        "body": """Hey Cesar,

Regarding your agency's scale:

Most sync failures happen because of polling latency. I built a middleware binary that uses Webhooks to lock inventory immediately, acting as a buffer for high-volume stores.

If you're looking for backend stability without subscriptions, this tool handles the sync logic.

Agency License: https://payhip.com/b/GJc5k

Best,
YEDAN"""
    }
]

def log(message):
    """Write to log file and print."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    print(entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

def init_db():
    """Initialize SQLite database for tracking."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS outreach_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_name TEXT,
            email TEXT,
            status TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def is_already_contacted(email):
    """Check if we already emailed this target."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM outreach_log WHERE email = ? AND status = 'SENT'", (email,))
    result = c.fetchone()
    conn.close()
    return result is not None

def log_outreach(target_name, email, status):
    """Log outreach attempt to database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO outreach_log (target_name, email, status, timestamp) VALUES (?, ?, ?, ?)",
        (target_name, email, status, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def send_email(target):
    """Send outreach email to target."""
    sender_email = os.environ.get('GMAIL_USER') or os.environ.get('GMAIL_USERNAME')
    sender_password = os.environ.get('GMAIL_PASS') or os.environ.get('GMAIL_PASSWORD')
    
    if not sender_email or not sender_password:
        log("ERROR: Gmail credentials not set. Skipping email.")
        return False
    
    if is_already_contacted(target["email"]):
        log(f"SKIP: {target['name']} already contacted.")
        return False
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = target["email"]
    msg['Subject'] = target["subject"]
    msg.attach(MIMEText(target["body"], 'plain'))
    
    try:
        log(f"SENDING: Email to {target['name']} ({target['email']})...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, target["email"], msg.as_string())
        server.quit()
        
        log_outreach(target["name"], target["email"], "SENT")
        log(f"SUCCESS: Email sent to {target['name']}")
        return True
        
    except Exception as e:
        log_outreach(target["name"], target["email"], f"FAILED: {e}")
        log(f"ERROR: {e}")
        return False

def run_engine():
    """Main loop - runs 24/7."""
    log("=" * 50)
    log("YEDAN 24/7 REVENUE ENGINE STARTED")
    log("=" * 50)
    
    init_db()
    
    cycle = 0
    while True:
        cycle += 1
        log(f"--- CYCLE {cycle} ---")
        
        # Process all targets
        for target in TARGETS:
            send_email(target)
            time.sleep(10)  # Avoid spam detection
        
        log(f"Sleeping {SCAN_INTERVAL_SECONDS} seconds until next cycle...")
        time.sleep(SCAN_INTERVAL_SECONDS)

if __name__ == "__main__":
    run_engine()
