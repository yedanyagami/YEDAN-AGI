import os
import time
import sys
import io
import google.generativeai as genai
from playwright.sync_api import sync_playwright

# === 0. 強制修復 Windows 中文亂碼 ===
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# === 1. 設定區 ===
# 請確保這裡填入您的 API Key (如果環境變數沒抓到的話)
API_KEY = "AIzaSyD-Wkf-Ks0VxOggjPm_Nu1DTbCCBuG6DdQ" 

def run_vision_mission():
    print("🚀 [System] Agent 啟動：正在呼叫 Gemini 2.5 視覺中樞...")
    
    if "您的" in API_KEY:
        print("❌ [Error] 請先在代碼第 13 行填入您的 Gemini API Key！")
        return
        
    genai.configure(api_key=API_KEY)
    
    # 【關鍵升級】使用您清單中確認存在的最新模型
    model = genai.GenerativeModel('gemini-2.5-flash') 

    with sync_playwright() as p:
        print("🌐 [Browser] 正在開啟隱形瀏覽器...")
        # headless=False 讓您看得到，改為 True 則背景執行
        browser = p.chromium.launch(headless=False) 
        page = browser.new_page()
        
        target_url = "https://www.coingecko.com/"
        print(f"🎯 [Target] 鎖定目標：{target_url}")
        
        try:
            page.goto(target_url, timeout=60000)
            print("⏳ [Wait] 等待數據載入 (5秒)...")
            time.sleep(5) 
            
            # 模擬人類滾動，確保數據加載
            page.mouse.wheel(0, 500)
            time.sleep(1)

            print("📸 [Vision] 正在截取視網膜影像...")
            screenshot_path = "target_intel.png"
            page.screenshot(path=screenshot_path)
            
            print("🧠 [Brain] 影像上傳中... Gemini 2.5 正在分析市場...")
            img = genai.upload_file(screenshot_path)
            
            # 讓 AI 扮演華爾街交易員
            response = model.generate_content([
                "你是一個冷酷的加密貨幣操盤手。請分析這張截圖：",
                "1. 【報價】比特幣 (BTC) 和 以太幣 (ETH) 的價格是多少？",
                "2. 【情緒】畫面主要是紅色(跌)還是綠色(漲)？",
                "3. 【決策】根據這些數據，現在該『買入』、『賣出』還是『觀望』？",
                img
            ])
            
            print("\n" + "=" * 40)
            print("🤖 ULTRA AGENT 戰略報告：")
            print(response.text)
            print("=" * 40 + "\n")
            
        except Exception as e:
            print(f"❌ [Error] 任務失敗: {e}")
        finally:
            browser.close()
            print("✅ [System] 任務完成，連結斷開。")

if __name__ == "__main__":
    run_vision_mission()
