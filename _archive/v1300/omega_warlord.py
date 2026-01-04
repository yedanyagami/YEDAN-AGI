"""
YEDAN AGI - OMEGA WARLORD PROTOCOL
終極整合：AI分析 + PDF生成 + PayPal收款 + 社群轟炸
"""
import os
import sys
import io
import time
import requests
import paypalrestsdk
from openai import OpenAI
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from dotenv import load_dotenv

# 強制 UTF-8 輸出，避免 Windows 亂碼
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. 載入全套軍火
load_dotenv()
print("[FIRE] OMEGA WARLORD PROTOCOL: ONLINE")
print("[MONEY] MODE: LIVE REVENUE GENERATION")

# === 初始化 API ===
# PayPal (Live Mode)
paypalrestsdk.configure({
    "mode": os.getenv("PAYPAL_MODE", "live"),
    "client_id": os.getenv("PAYPAL_CLIENT_ID"),
    "client_secret": os.getenv("PAYPAL_CLIENT_SECRET")
})

# AI 三巨頭
grok = OpenAI(api_key=os.getenv("GROK_API_KEY"), base_url="https://api.x.ai/v1")
pplx = OpenAI(api_key=os.getenv("PPLX_API_KEY"), base_url="https://api.perplexity.ai")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini = genai.GenerativeModel('gemini-2.5-flash')

# Social Media
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def generate_pdf_product(filename, title, content):
    """生產實體商品：PDF 報告"""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # 標題
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"YEDAN INTEL: {title}")
    c.line(50, height - 60, width - 50, height - 60)
    
    # 內容
    c.setFont("Helvetica", 10)
    text_object = c.beginText(50, height - 100)
    
    # 自動換行處理
    lines = content.split('\n')
    for line in lines:
        wrapped_lines = simpleSplit(line, "Helvetica", 10, width - 100)
        for wrapped in wrapped_lines:
            text_object.textLine(wrapped)
            
    c.drawText(text_object)
    c.showPage()
    c.save()
    print(f"📦 [Factory] 實體商品已生產: {filename}")
    return filename

def create_live_payment(product_name, price):
    """生成真實收款連結"""
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "https://t.me/yedanyagami",
            "cancel_url": "https://twitter.com"
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": product_name,
                    "sku": "OMEGA-LIVE",
                    "price": str(price),
                    "currency": "USD",
                    "quantity": 1
                }]
            },
            "amount": {"total": str(price), "currency": "USD"},
            "description": "Exclusive AI Crypto Intelligence"
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                print(f"💳 [PayPal] 收款連結已生成: {link.href}")
                return link.href
    else:
        print(f"❌ PayPal Error: {payment.error}")
        return None

def send_telegram(message):
    """發送 Telegram 通知"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[!] Telegram 未設定，跳過")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}, timeout=10)
        if r.status_code == 200:
            print("✅ [Telegram] 戰報已送達")
        else:
            print(f"❌ [Telegram] 失敗: {r.text}")
    except Exception as e:
        print(f"❌ [Telegram] 錯誤: {e}")

def send_discord(message):
    """發送 Discord Webhook"""
    if not DISCORD_WEBHOOK_URL:
        print("[!] Discord 未設定，跳過")
        return
    try:
        r = requests.post(DISCORD_WEBHOOK_URL, json={"content": message}, timeout=10)
        if r.status_code in [200, 204]:
            print("✅ [Discord] 戰報已送達")
        else:
            print(f"❌ [Discord] 失敗: {r.status_code}")
    except Exception as e:
        print(f"❌ [Discord] 錯誤: {e}")

def omega_execution():
    print("\n" + "="*50)
    print("⚔️ OMEGA WARLORD: 開始執行...")
    print("="*50)
    
    # 1. 鎖定目標 (模擬 Grok 獵殺)
    target = "AI Agent Coins (FET, TAO) Surge"
    print(f"🦅 [Grok] 鎖定目標: {target}")
    
    # 2. Gemini 生產報告
    print("🧠 [Gemini] 正在撰寫高價值報告...")
    report_prompt = f"""請針對 '{target}' 寫一份 500 字的深度投資分析報告。包含：
1. 發生了什麼？
2. 為什麼現在要買？
3. 短期目標價位。
語氣要專業且緊迫。"""

    try:
        response = gemini.generate_content(report_prompt)
        report_content = response.text
        print("📝 [Gemini] 報告撰寫完成")
    except Exception as e:
        print(f"❌ [Gemini] 錯誤: {e}")
        report_content = f"AI Agent 市場分析報告\n\n目標: {target}\n\n(報告生成失敗，請稍後重試)"
    
    # 3. 生產 PDF 商品
    pdf_filename = f"OMEGA_REPORT_{int(time.time())}.pdf"
    generate_pdf_product(pdf_filename, target, report_content)
    
    # 4. 生成收款連結 ($0.01 測試用)
    pay_link = create_live_payment(f"Omega LIVE TEST: {target}", "0.01")
    
    # 5. 社群轟炸
    blast_message = f"""🔥 *YEDAN INTEL ALERT* 🔥

📊 *新報告已生成*
🎯 目標: {target}

💰 *立即購買完整分析*:
{pay_link if pay_link else '[付款連結生成中...]'}

_YEDAN AGI 自動化系統_"""
    
    send_telegram(blast_message)
    send_discord(blast_message.replace("*", "**"))  # Discord markdown
    
    print("\n" + "="*50)
    print("✅ OMEGA WARLORD: 執行完成")
    print(f"📦 商品: {pdf_filename}")
    print(f"💳 收款: {pay_link}")
    print("="*50)
    
    return {"pdf": pdf_filename, "pay_link": pay_link, "report": report_content}

if __name__ == "__main__":
    omega_execution()
