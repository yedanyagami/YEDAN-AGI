import imaplib
import email
from email.header import decode_header
import os
import re
import time
import socket
import sys  # 新增 sys 模組以控制退出狀態
from product_delivery import DeliveryBot

# --- 配置 ---
EMAIL_USER = os.environ.get('GMAIL_USER')
EMAIL_PASS = os.environ.get('GMAIL_PASS')
IMAP_SERVER = "imap.gmail.com"
POLL_INTERVAL = 15
MAX_RUNTIME = 19800

class RevenueStream:
    def __init__(self):
        self.mail = None
        self.delivery = DeliveryBot()
        
    def connect(self):
        """建立持久連線"""
        try:
            print(f"🔌 Connecting to {IMAP_SERVER} as {EMAIL_USER}...")
            self.mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            self.mail.login(EMAIL_USER, EMAIL_PASS)
            print("✅ Connected & Authenticated.")
            return True
        except Exception as e:
            print(f"❌ [FATAL] Connection Failed: {e}")
            return False

    def process_email(self, msg_bytes):
        # ... (保持原樣)
        try:
            msg = email.message_from_bytes(msg_bytes)
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")
            body = str(msg)
            amount_match = re.search(r'\$(\d+\.\d{2})', body)
            amount = float(amount_match.group(1)) if amount_match else 0.0
            buyer = msg.get("Reply-To")
            if not buyer:
                match = re.search(r'[\w\.-]+@[\w\.-]+', body)
                buyer = match.group(0) if match else "unknown"
            return subject, amount, buyer
        except Exception as e:
            print(f"⚠️ Parse Error: {e}")
            return "Error", 0.0, "unknown"

    def start_watching(self):
        start_time = time.time()
        
        # 🔥 關鍵修正：如果連線失敗，直接殺死程序 (Exit 1)
        if not self.connect():
            print("🚫 System Aborting: Unable to establish initial connection.")
            sys.exit(1) 

        print(f"👁️ AGI Watchtower Active. Cycle: {MAX_RUNTIME}s")

        while True:
            if time.time() - start_time > MAX_RUNTIME:
                print("👋 Cycle finished. Rescheduling...")
                try:
                    self.mail.logout()
                except:
                    pass
                break

            try:
                self.mail.noop()
                self.mail.select("inbox")
                typ, data = self.mail.search(None, '(UNSEEN OR (SUBJECT "sale") (SUBJECT "donation"))')
                
                for num in data[0].split():
                    typ, msg_data = self.mail.fetch(num, '(RFC822)')
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            subject, amount, buyer = self.process_email(response_part[1])
                            if amount > 0:
                                print(f"💰 DETECTED: ${amount} from {buyer}")
                                self.delivery.send_product(buyer, "YEDAN SEO Auditor")
                            else:
                                print(f"ℹ️ Ignored: {subject}")
                                
            except (imaplib.IMAP4.abort, socket.error) as e:
                print(f"⚠️ Connection lost ({e}). Reconnecting...")
                time.sleep(5)
                # 如果重連也失敗，這里也會報錯
                if not self.connect():
                     print("❌ Reconnection failed.")
            except Exception as e:
                print(f"⚠️ Loop Error: {e}")

            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    if not EMAIL_USER or not EMAIL_PASS:
        print("❌ FATAL: Secrets (GMAIL_USER/GMAIL_PASS) are missing in Environment.")
        sys.exit(1) # 強制紅燈
    else:
        agi = RevenueStream()
        agi.start_watching()
