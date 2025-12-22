"""
YEDAN AGI - Sensors Module
Market data, Telegram messages, and external event sensors
"""
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

class AGISensors:
    """Input sensors for AGI"""
    
    def __init__(self):
        self.tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.last_update_id = 0
    
    def scan_market(self):
        """Scan CoinGecko for market data"""
        try:
            url = "https://api.coingecko.com/api/v3/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": 10,
                "page": 1,
                "sparkline": False,
                "price_change_percentage": "24h"
            }
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "success": True,
                    "coins": [
                        {
                            "symbol": c["symbol"].upper(),
                            "price": c["current_price"],
                            "change_24h": c.get("price_change_percentage_24h", 0),
                            "market_cap": c["market_cap"]
                        }
                        for c in data
                    ],
                    "timestamp": datetime.now().isoformat()
                }
            return {"success": False, "error": f"Status {resp.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def scan_trending(self):
        """Get trending coins from CoinGecko"""
        try:
            url = "https://api.coingecko.com/api/v3/search/trending"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "success": True,
                    "trending": [
                        {
                            "name": c["item"]["name"],
                            "symbol": c["item"]["symbol"],
                            "rank": c["item"]["market_cap_rank"]
                        }
                        for c in data.get("coins", [])[:5]
                    ]
                }
            return {"success": False, "error": f"Status {resp.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_telegram_messages(self):
        """Get new Telegram messages (for bot interactions)"""
        if not self.tg_token:
            return {"success": False, "error": "Telegram not configured"}
        
        try:
            url = f"https://api.telegram.org/bot{self.tg_token}/getUpdates"
            params = {"offset": self.last_update_id + 1, "timeout": 0}
            resp = requests.get(url, params=params, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                messages = []
                for update in data.get("result", []):
                    self.last_update_id = update["update_id"]
                    if "message" in update:
                        msg = update["message"]
                        messages.append({
                            "from": msg.get("from", {}).get("username", "unknown"),
                            "chat_id": msg.get("chat", {}).get("id"),
                            "text": msg.get("text", ""),
                            "date": msg.get("date")
                        })
                return {"success": True, "messages": messages}
            return {"success": False, "error": f"Status {resp.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def visual_scan(self, url="https://www.coingecko.com/en/watchlists/trending-crypto"):
        """Perform a visual scan using Computer Use (Playwright)"""
        print(f"[EYE] Scanning {url}...")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=30000)
                page.wait_for_load_state("networkidle")
                
                # Extract text content from top trending list (CoinGecko specific)
                # This selector targets the coin names in the trending list
                coins = page.locator("span.font-bold").all_inner_texts()
                
                # Take evidence screenshot
                screenshot_path = f"visual_evidence_{int(datetime.now().timestamp())}.png"
                page.screenshot(path=screenshot_path)
                
                browser.close()
                
                # Filter valid text (simple heuristic)
                valid_coins = [c for c in coins[:10] if len(c) > 1]
                
                return {
                    "success": True,
                    "visual_data": valid_coins,
                    "evidence": screenshot_path,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {"success": False, "error": f"Visual scan failed: {str(e)}"}
    
    def gather_all(self):
        """Gather all sensor data including visual"""
        return {
            "market": self.scan_market(),
            "trending": self.scan_trending(),
            "telegram": self.get_telegram_messages(),
            "visual": self.visual_scan(),  # New Computer Use Capability
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    sensors = AGISensors()
    print("[TEST] Market:", sensors.scan_market())
    print("[TEST] Trending:", sensors.scan_trending())
    print("[TEST] Telegram:", sensors.get_telegram_messages())
