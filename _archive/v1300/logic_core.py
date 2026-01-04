import requests
import os
import json
from itertools import cycle

# --- 1. NEXUS WASHER (資產: 反偵測邏輯) ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

class APIWasher:
    def __init__(self):
        self.session = requests.Session()
        self.agent_cycle = cycle(USER_AGENTS)

    def get(self, url):
        try: 
            # 使用您的輪替邏輯
            headers = {'User-Agent': next(self.agent_cycle)}
            return self.session.get(url, headers=headers, timeout=10)
        except Exception as e: 
            print(f"⚠️ [NET] Connection Error: {e}")
            return None

# --- 2. MARKET EYE (資產: CoinGecko 抓取邏輯) ---
def fetch_market_data():
    nexus = APIWasher()
    print("👁️ [EYE] 啟動 Nexus Washer... 連線至 CoinGecko")
    
    # 您的 V6 原始邏輯
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,solana&vs_currencies=usd"
    resp = nexus.get(url)
    
    data_map = {"BTC": "N/A", "SOL": "N/A"}
    
    if resp and resp.status_code == 200:
        try:
            data = resp.json()
            data_map["BTC"] = f"${data.get('bitcoin', {}).get('usd', 'N/A')}"
            data_map["SOL"] = f"${data.get('solana', {}).get('usd', 'N/A')}"
            print(f"✅ [EYE] 數據獲取成功: {data_map}")
        except:
            print("❌ [EYE] JSON 解析失敗")
    else:
        print(f"❌ [EYE] 請求失敗 (Status: {getattr(resp, 'status_code', 'Unknown')})")
        
    return data_map

# === GEMINI 神經連結 ===
def ask_gemini(prompt):
    """
    AGI 向 Gemini 尋求建議的通道
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ [BRAIN] 未連接 Gemini API (無 Token)"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"❌ [BRAIN] 思考失敗: {response.text}"
    except Exception as e:
        return f"❌ [BRAIN] 連線錯誤: {str(e)}"
