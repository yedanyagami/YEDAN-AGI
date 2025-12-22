import os
import time
import sys
import io
import requests
import google.generativeai as genai
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# 強制 UTF-8 輸出，避免 Windows 亂碼
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. 載入金庫
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 設定監控間隔 (900秒 = 15分鐘)
MONITOR_INTERVAL = 900 

def send_telegram_alert(message):
    """發送 Telegram 通知"""
    if not TG_TOKEN or not TG_CHAT_ID:
        print("⚠️ [Warn] Telegram 設定不完整，跳過通知。")
        return
    
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            print("✅ [Telegram] 戰報已送達指揮官手機。")
        else:
            print(f"❌ [Telegram] 發送失敗: {response.text}")
    except Exception as e:
        print(f"❌ [Telegram] 連線錯誤: {e}")

def run_sentry_cycle():
    print(f"\n🚀 [Sentry] 哨兵掃描開始... ({time.strftime('%H:%M:%S')})")
    
    if not API_KEY:
        print("❌ [Error] 缺少 GEMINI_API_KEY！")
        return

    genai.configure(api_key=API_KEY)
    # 使用 2.5 Flash 模型
    model = genai.GenerativeModel('gemini-2.5-flash')

    with sync_playwright() as p:
        # headless=True 背景執行，不干擾您工作
        browser = p.chromium.launch(headless=True) 
        page = browser.new_page()
        
        try:
            target_url = "https://www.coingecko.com/"
            print(f"🌐 [Browser] 正在潛入: {target_url}")
            page.goto(target_url, timeout=60000)
            time.sleep(5) 
            
            # 截圖
            screenshot_path = "sentry_vision.png"
            page.screenshot(path=screenshot_path)
            
            # 分析
            print("🧠 [Brain] Gemini 2.5 正在分析市場情緒...")
            img = genai.upload_file(screenshot_path)
            
            response = model.generate_content([
                "你是一個軍事級加密貨幣哨兵。請簡潔回報：",
                "1. 🎯 **BTC & ETH 價格**。",
                "2. 📊 **市場情緒** (恐慌/貪婪/觀望)。",
                "3. ⚠️ **是否需要介入？** (只有在大跌或暴漲時才建議介入，否則維持觀望)",
                img
            ])
            
            report = response.text
            print("-" * 30)
            print(report)
            print("-" * 30)
            
            # 發送手機通知
            tg_message = f"🤖 **利維坦哨兵戰報** 🤖\n\n{report}\n\n[查看詳情]({target_url})"
            send_telegram_alert(tg_message)
            
        except Exception as e:
            err_msg = f"❌ [Error] 任務失敗: {e}"
            print(err_msg)
            send_telegram_alert(err_msg)
        finally:
            browser.close()

if __name__ == "__main__":
    print("🛡️ 利維坦哨兵 (Leviathan Sentry) 已上線。")
    print(f"📡 監控目標: CoinGecko | 頻率: 每 {MONITOR_INTERVAL/60} 分鐘")
    print("按 Ctrl+C 可以隨時中止。")
    
    # 立即執行第一次，然後進入循環
    while True:
        run_sentry_cycle()
        print(f"💤 [Sleep] 哨兵休眠中...")
        time.sleep(MONITOR_INTERVAL)
