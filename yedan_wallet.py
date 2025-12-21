import imaplib
import email
from email.header import decode_header
import os
import re
import time
import socket
from product_delivery import DeliveryBot

# --- 配置 ---
EMAIL_USER = os.environ.get('GMAIL_USER')
EMAIL_PASS = os.environ.get('GMAIL_PASS')
IMAP_SERVER = "imap.gmail.com"
POLL_INTERVAL = 15      # 15秒檢查一次 (安全頻率)
MAX_RUNTIME = 19800     # 5.5 小時 (預留 30 分鐘緩衝)

class RevenueStream:
    def __init__(self):
        self.mail = None
        self.delivery = DeliveryBot()
        
    def connect(self):
        """建立持久連線"""
        try:
            print("🔌 Connecting to Gmail IMAP...")
            self.mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            self.mail.login(EMAIL_USER, EMAIL_PASS)
            print("✅ Connected & Authenticated.")
            return True
        except Exception as e:
            print(f"❌ Connection Failed: {e}")
            return False

    def process_email(self, msg_bytes):
        """解析郵件"""
        try:
            msg = email.message_from_bytes(msg_bytes)
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")
            
            # 簡化內容提取
            body = str(msg)
            
            # 尋找金額
            amount_match = re.search(r'\$(\d+\.\d{2})', body)
            amount = float(amount_match.group(1)) if amount_match else 0.0
            
            # 尋找買家 Email (優先抓 Reply-To)
            buyer = msg.get("Reply-To")
            if not buyer:
                match = re.search(r'[\w\.-]+@[\w\.-]+', body)
                buyer = match.group(0) if match else "unknown"
                
            return subject, amount, buyer
        except Exception as e:
            print(f"⚠️ Parse Error: {e}")
            return "Error", 0.0, "unknown"

    def start_watching(self):
        """進入冥想狀態 (Infinite Loop)"""
        start_time = time.time()
        
        # 初次連線
        if not self.connect():
            return

        print(f"👁️ AGI Watchtower Active. Cycle: {MAX_RUNTIME}s")

        while True:
            # 1. 檢查生命週期
            if time.time() - start_time > MAX_RUNTIME:
                print("👋 Cycle finished. Rescheduling...")
                try:
                    self.mail.logout()
                except:
                    pass
                break

            try:
                # 2. 保持連線活躍 (Heartbeat)
                self.mail.noop()
                
                # 3. 搜尋未讀 (Gumroad/Ko-fi)
                self.mail.select("inbox")
                # 搜尋條件: 未讀 且 (標題含 'sale' 或 'donation') - 減少誤判
                typ, data = self.mail.search(None, '(UNSEEN OR (SUBJECT "sale") (SUBJECT "donation"))')
                
                for num in data[0].split():
                    typ, msg_data = self.mail.fetch(num, '(RFC822)')
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            subject, amount, buyer = self.process_email(response_part[1])
                            
                            # 過濾掉非交易郵件 (簡單防呆)
                            if amount > 0:
                                print(f"💰 DETECTED: ${amount} from {buyer}")
                                self.delivery.send_product(buyer, "YEDAN SEO Auditor")
                            else:
                                print(f"ℹ️ Ignored non-transaction email: {subject}")
                                
            except (imaplib.IMAP4.abort, socket.error) as e:
                print(f"⚠️ Connection lost ({e}). Reconnecting...")
                time.sleep(5)
                self.connect()
            except Exception as e:
                print(f"⚠️ Loop Error: {e}")

            # 4. 休息
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    if not EMAIL_USER:
        print("❌ FATAL: Secrets missing.")
    else:
        agi = RevenueStream()
        agi.start_watching()
