import imaplib
import email
from email.header import decode_header
import os
import re
import datetime
from product_delivery import DeliveryBot # 引入發貨模組

# --- 配置區 ---
EMAIL_USER = os.environ.get('GMAIL_USER')
EMAIL_PASS = os.environ.get('GMAIL_PASS')
IMAP_SERVER = "imap.gmail.com"

PAYMENT_SOURCES = {
    "gumroad": {"sender": "noreply@gumroad.com", "subject_keyword": "You made a sale"},
    "kofi": {"sender": "noreply@ko-fi.com", "subject_keyword": "Donation"},
}

def connect_gmail():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        return mail
    except Exception as e:
        print(f"❌ [CRITICAL] Gmail Login Failed: {e}")
        return None

def parse_email_content(msg_bytes):
    msg = email.message_from_bytes(msg_bytes)
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding if encoding else "utf-8")
    
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode()
                break
    else:
        body = msg.get_payload(decode=True).decode()

    # Regex 提取金額
    amount_match = re.search(r'\$(\d+\.\d{2})', body)
    amount = float(amount_match.group(1)) if amount_match else 0.0
    
    # 提取買家 Email (優先找 Reply-To, 其次找 body 內的 email pattern)
    buyer_email = msg.get("Reply-To")
    if not buyer_email:
        email_match = re.search(r'[\w\.-]+@[\w\.-]+', body)
        buyer_email = email_match.group(0) if email_match else "unknown@buyer.com"

    return subject, amount, buyer_email

def check_revenue(mail):
    total_revenue = 0.0
    delivery = DeliveryBot() # 初始化發貨員
    
    mail.select("inbox")
    
    for source, criteria in PAYMENT_SOURCES.items():
        print(f"🔍 Scanning for {source}...")
        search_criteria = f'(UNSEEN FROM "{criteria["sender"]}")'
        status, messages = mail.search(None, search_criteria)
        
        email_ids = messages[0].split()
        if not email_ids:
            print(f"   No new sales from {source}.")
            continue
            
        print(f"   �� Found {len(email_ids)} new orders from {source}!")
        
        for e_id in email_ids:
            res, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    subject, amount, buyer = parse_email_content(response_part[1])
                    print(f"      Processing: {subject} | Amt: ${amount} | User: {buyer}")
                    
                    # === 觸發發貨 ===
                    product_name = "YEDAN SEO Auditor" # 預設產品，未來可根據金額判斷
                    delivery.send_product(buyer, product_name)
                    
                    total_revenue += amount
                    # IMAP 自動標記為 Seen，無需手動
                    
    return total_revenue

if __name__ == "__main__":
    if not EMAIL_USER or not EMAIL_PASS:
        print("⚠️ [Simulation Mode] Missing Secrets. Code logic verification only.")
    else:
        print(f"⏰ AGI Wallet Active: {datetime.datetime.now()}")
        mail_session = connect_gmail()
        if mail_session:
            revenue_captured = check_revenue(mail_session)
            print(f"==========================================")
            print(f"💵 Total Revenue: ${revenue_captured}")
            print(f"==========================================")
            mail_session.close()
            mail_session.logout()
