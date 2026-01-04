import time
import json
import os
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options

def start_browser():
    print("🚀 初始化 Antigravity 本地瀏覽器 (Edge)...")
    options = Options()
    options.add_argument("--guest")
    
    # [關鍵設定] 尋找放在旁邊的驅動程式
    driver_path = "msedgedriver.exe"
    
    if os.path.exists(driver_path):
        print(f"✅ 檢測到本地驅動: {driver_path}，正在啟動...")
        service = Service(executable_path=driver_path)
    else:
        print("❌ 錯誤: 找不到 msedgedriver.exe")
        print(f"請確認 msedgedriver.exe 是否在: {os.getcwd()}")
        input("按 Enter 鍵退出...")
        raise FileNotFoundError("msedgedriver.exe missing")

    driver = webdriver.Edge(service=service, options=options)
    return driver

def steal_reddit_cookies(driver):
    print("\n-------------------------------------------------")
    print("🕵️ 任務 1: Reddit 身份竊取")
    print("-------------------------------------------------")
    driver.get("https://www.reddit.com/login/")
    print("⚠️ [等待指令] 請在彈出的瀏覽器中手動登入 Reddit。")
    input("👉 登入完成後，請回到這裡按下 [Enter] 鍵繼續...")
    
    cookies = driver.get_cookies()
    with open("reddit_session.json", "w") as f:
        json.dump(cookies, f)
    print(f"✅ Reddit Cookies 已保存。")

def verify_deepseek_balance(driver):
    print("\n-------------------------------------------------")
    print("💰 任務 2: DeepSeek 餘額盤點")
    print("-------------------------------------------------")
    driver.get("https://platform.deepseek.com/top_up")
    print("⚠️ [等待指令] 請手動登入 DeepSeek。")
    input("👉 看到餘額畫面後，請回到這裡按下 [Enter] 鍵...")
    
    driver.save_screenshot("deepseek_balance.png")
    print(f"✅ 餘額截圖已保存。")

def sniff_tiktok_api(driver):
    print("\n-------------------------------------------------")
    print("🎵 任務 3: TikTok API 嗅探")
    print("-------------------------------------------------")
    driver.get("https://www.tiktok.com/explore")
    print("⚠️ [等待指令] 請隨意滾動頁面 10 秒。")
    input("👉 滾動完畢後，請按下 [Enter] 結束任務...")
    
    cookies = driver.get_cookies()
    with open("tiktok_session.json", "w") as f:
        json.dump(cookies, f)
    print("✅ TikTok 憑證已保存。")

def main():
    try:
        driver = start_browser()
        steal_reddit_cookies(driver)
        verify_deepseek_balance(driver)
        sniff_tiktok_api(driver)
        print("\n🏆 任務全部完成。")
        driver.quit()
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")

if __name__ == "__main__":
    main()