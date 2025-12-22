"""
YEDAN AGI - OMEGA TELEGRAM PRIME
專為 Telegram 優化的情報與收款系統
"""
import os
import sys
import io
import time
import requests
import paypalrestsdk
from datetime import datetime
from dotenv import load_dotenv

# 強制 UTF-8 輸出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 引入核心套件
from cerebras.cloud.sdk import Cerebras
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# 1. 啟動系統
load_dotenv()
print("[BLUE] OMEGA TELEGRAM PRIME: ONLINE")
print("[LIGHTNING] MODE: TELEGRAM ONLY")

# === 初始化 ===
# A. Firebase (可選)
db = None
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    if not firebase_admin._apps:
        cred_path = os.getenv("FIREBASE_CRED_PATH")
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            print("[OK] Firebase: Connected")
        else:
            print("[!] Firebase: No credentials file, skipping")
except Exception as e:
    print(f"[!] Firebase skipped: {e}")

# B. Cerebras AI
cerebras_client = None
try:
    cerebras_client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY"))
    print("[OK] Cerebras: Ready")
except Exception as e:
    print(f"[X] Cerebras Error: {e}")

# C. PayPal
paypalrestsdk.configure({
    "mode": os.getenv("PAYPAL_MODE", "live"),
    "client_id": os.getenv("PAYPAL_CLIENT_ID"),
    "client_secret": os.getenv("PAYPAL_CLIENT_SECRET")
})
print("[OK] PayPal: Live Mode")

# === 核心功能 ===

def telegram_send(message):
    """專用的 Telegram 發送通道"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("[X] Error: Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",  # 改用 HTML 避免 Markdown 解析問題
        "disable_web_page_preview": False
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            print("[OK] Telegram: Message delivered")
            return True
        else:
            print(f"[X] Telegram Failed: {resp.text}")
            return False
    except Exception as e:
        print(f"[X] Telegram Error: {e}")
        return False

def fast_ai_analysis(topic):
    """Cerebras 光速生成"""
    print(f"[BRAIN] Analyzing: {topic}...")
    if not cerebras_client:
        return "AI offline - please check CEREBRAS_API_KEY"
    
    try:
        completion = cerebras_client.chat.completions.create(
            model="llama3.1-70b", 
            messages=[
                {"role": "system", "content": "You are a top crypto analyst. Output format:\n1. URGENT SIGNAL\n2. Entry Point\n3. Target Price\nKeep it short, impactful, Telegram-friendly."},
                {"role": "user", "content": f"Analyze: {topic}"}
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"[X] AI Error: {e}")
        return f"AI analysis failed: {e}"

def create_payment(product_name, price="0.01"):
    """建立真錢收款連結"""
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "https://t.me/yesinyagami_novel_bot",
            "cancel_url": "https://yedanyagami.myshopify.com"
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": product_name,
                    "sku": "TEL-PRIME-001",
                    "price": str(price),
                    "currency": "USD",
                    "quantity": 1
                }]
            },
            "amount": {"total": str(price), "currency": "USD"},
            "description": "YEDAN PREMIUM INTEL"
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                print(f"[OK] PayPal: Payment link created")
                return link.href
    print(f"[X] PayPal Error: {payment.error}")
    return None

def generate_pdf(filename, content):
    """生成 PDF 存檔"""
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(50, 750, "YEDAN CONFIDENTIAL")
    c.line(50, 740, 550, 740)
    text = c.beginText(50, 700)
    for line in content.split('\n'):
        text.textLine(line[:80])
    c.drawText(text)
    c.save()
    print(f"[OK] PDF saved: {filename}")
    return filename

# === 主循環 ===
def prime_cycle():
    print("\n" + "="*50)
    print("[SATELLITE] Scanning market signals...")
    print("="*50)
    
    # 1. 鎖定目標
    target = "AI Agent Economy (FET & TAO)"
    print(f"[EAGLE] Target locked: {target}")
    
    # 2. AI 生成情報
    intel = fast_ai_analysis(target)
    print(f"\n[INTEL]\n{intel}\n")
    
    # 3. 建立 PDF
    pdf_name = f"Intel_{int(time.time())}.pdf"
    generate_pdf(pdf_name, intel)
    
    # 4. 建立收款連結 ($0.01 測試)
    price = "0.01"
    pay_link = create_payment(f"Intel: {target}", price)
    
    if pay_link:
        # 5. Telegram 廣播 (使用 HTML 格式)
        tg_msg = f"""<b>YEDAN INTELLIGENCE ALERT</b>

<b>Target:</b> {target}
------------------------------
{intel}
------------------------------
<b>Full Report Generated</b>
<b>Get Access (${price}):</b>
<a href="{pay_link}">Click to Pay</a>

<i>Powered by Cerebras AI</i>"""
        
        telegram_send(tg_msg)
        
    print("\n" + "="*50)
    print("[DONE] Mission Complete")
    print(f"PDF: {pdf_name}")
    print(f"Pay: {pay_link}")
    print("="*50)
    
    return {"pdf": pdf_name, "pay_link": pay_link, "intel": intel}

if __name__ == "__main__":
    prime_cycle()
