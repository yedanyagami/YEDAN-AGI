import imaplib
import email
import os
import json
from upstash_redis import Redis

class Wallet:
    def __init__(self):
        self.user = os.environ.get("GMAIL_USER")
        self.password = os.environ.get("GMAIL_PASS")
        # 連接雲端大腦
        self.redis = Redis(
            url=os.environ.get("UPSTASH_REDIS_REST_URL"),
            token=os.environ.get("UPSTASH_REDIS_REST_TOKEN")
        )

    def scan_for_payments(self):
        """掃描 Gmail 尋找 Gumroad/Ko-fi 收據"""
        if not self.user or not self.password:
            print("⚠️ [WALLET] 無 Gmail 憑證，跳過掃描")
            return []

        new_orders = []
        try:
            # 連接 Gmail
            mail = imaplib.IMAP4_SSL("imap.gmail.com")
            mail.login(self.user, self.password)
            mail.select("inbox")

            # 搜尋 Gumroad 銷售通知
            # 篩選未讀郵件以加快速度 (UNSEEN)，或者搜尋特定標題
            status, messages = mail.search(None, '(SUBJECT "You made a sale")')
            
            # 為了避免 API 超時，只處理最新的 5 封
            email_ids = messages[0].split()[-5:]

            for num in email_ids:
                _, msg_data = mail.fetch(num, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])
                
                # 解析訂單 ID (從 Message-ID 或標題雜湊)
                order_id = msg.get('Message-ID', '').strip()
                subject = msg.get('Subject', '')
                
                # 簡單解析客戶 Email (Gumroad 通常在 Reply-To 或內容中)
                # 這裡做簡化處理，實際需根據郵件格式調整
                customer_email = email.utils.parseaddr(msg.get('To'))[1]
                
                # 檢查 Redis：這筆訂單處理過了嗎？
                if not self.redis.sismember("processed_orders", order_id):
                    print(f"💰 [WALLET] 發現新訂單: {subject}")
                    new_orders.append({
                        "id": order_id,
                        "email": customer_email, # 暫時發回給自己或從內文解析
                        "product": "Shopify SEO Autopilot" # 假設是這個產品
                    })
            
            mail.logout()
        except Exception as e:
            print(f"❌ [WALLET] 郵件掃描錯誤: {e}")
        
        return new_orders

    def mark_as_done(self, order_id, amount=27.0):
        """在 Redis 標記訂單完成並記帳"""
        # 1. 加入已處理清單 (Set)
        self.redis.sadd("processed_orders", order_id)
        # 2. 增加總營收 (Float)
        self.redis.incrbyfloat("total_revenue", amount)
        # 3. 增加訂單數 (Int)
        self.redis.incr("total_orders")

    def get_balance(self):
        """從 Redis 讀取財務狀況"""
        revenue = self.redis.get("total_revenue") or 0
        count = self.redis.get("total_orders") or 0
        return float(revenue), int(count)
