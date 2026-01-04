import requests

# 定義您六個月來的「價值資產」地圖
ASSET_MAP = {
    "CORE_V6": "https://raw.githubusercontent.com/yedanyagami/yedan-core/main/YEDAN_EVOLUTION_V6.py",
    "MARKET_EYE": "https://raw.githubusercontent.com/yedanyagami/yedan-core/main/MARKET_EYE_CLOUD.py",
    "SALES_CONFIG": "https://raw.githubusercontent.com/yedanyagami/yedan-sales-engine/main/wrangler.toml",
    "MAIN_PY": "https://raw.githubusercontent.com/yedanyagami/yedan-core/main/MAIN.py"
}

def scan_assets():
    print("="*60)
    print("🕵️ YEDAN AGI 全局資產審計報告 (Holistic Audit)")
    print("="*60)
    
    for name, url in ASSET_MAP.items():
        print(f"\n\n>>> 正在讀取資產: [{name}]")
        print(f">>> 來源: {url}")
        print("-" * 40)
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # 為了避免太長，這裡會顯示代碼，請長官複製這部分的內容給我
                print(response.text) 
                print("-" * 40)
                print(f"✅ [{name}] 讀取成功 (Size: {len(response.text)} bytes)")
            else:
                print(f"❌ [{name}] 讀取失敗 (Status: {response.status_code})")
                print("可能原因：檔案不存在或為 Private 倉庫 (需要 Token)")
        except Exception as e:
            print(f"⚠️ 讀取錯誤: {str(e)}")
    
    print("\n" + "="*60)
    print("審計完成。請將以上內容貼給 Gemini 進行架構分析。")
    print("="*60)

if __name__ == "__main__":
    scan_assets()
