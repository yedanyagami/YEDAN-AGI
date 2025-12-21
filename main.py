import imaplib
import email
import os
import datetime
import requests
import json
from upstash_redis import Redis

# 初始化連線
REDIS_URL = os.environ.get("UPSTASH_REDIS_REST_URL")
REDIS_TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN")
redis = Redis(url=REDIS_URL, token=REDIS_TOKEN)

GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_PASS = os.environ.get("GMAIL_PASS")

def log(msg):
    print(msg)
    # 同步寫入 Redis 日誌
    try:
        redis.lpush("system_logs", f"{datetime.datetime.now()}: {msg}")
    except: pass

def scan_gmail():
    if not GMAIL_USER or not GMAIL_PASS:
        log("⚠️ Gmail 憑證未設定，跳過掃描")
        return 0
    
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(GMAIL_USER, GMAIL_PASS)
        mail.select("inbox")
        
        # 搜尋 Gumroad 銷售通知
        status, messages = mail.search(None, '(SUBJECT "You made a sale")')
        email_ids = messages[0].split()[-5:]
        
        count = 0
        for num in email_ids:
            _, msg_data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            order_id = msg.get('Message-ID', '').strip()
            
            # 檢查是否已處理 (Redis 記憶)
            if not redis.sismember("processed_orders", order_id):
                log(f"💰 發現新訂單: {order_id}")
                redis.sadd("processed_orders", order_id)
                redis.incrbyfloat("total_revenue", 27.0) # 假設單價
                count += 1
                
        mail.logout()
        return count
    except Exception as e:
        log(f"❌ Gmail 掃描失敗: {e}")
        return 0

def fetch_market():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,solana&vs_currencies=usd"
        data = requests.get(url, timeout=10).json()
        return data['bitcoin']['usd'], data['solana']['usd']
    except:
        return 0, 0

def generate_report():
    btc, sol = fetch_market()
    new_orders = scan_gmail()
    
    revenue = redis.get("total_revenue") or 0
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><meta http-equiv="refresh" content="900"></head>
    <body style="background:#000;color:#0f0;font-family:monospace;padding:20px;">
        <h1>👁️ YEDAN AGI OMEGA</h1>
        <p>狀態: ONLINE (GitHub Actions Hosted)</p>
        <hr>
        <h3>💰 財務中樞</h3>
        <p>總營收: <span style="color:gold;font-size:1.5em">${revenue}</span></p>
        <p>本次掃描新單: {new_orders}</p>
        <hr>
        <h3>📈 市場監控</h3>
        <p>BTC: ${btc}</p>
        <p>SOL: ${sol}</p>
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    generate_report()
