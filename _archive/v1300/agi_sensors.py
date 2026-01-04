"""
YEDAN AGI - Sensors Module (Ultra Optimized)
Centralized input processing with connection pooling and unified config.
"""
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright
from agi_config import config

class AGISensors:
    """Input sensors for AGI with connection pooling"""
    
    def __init__(self):
        # Use session for connection pooling (Performance +)
        self.session = requests.Session()
        self.last_update_id = 0
        
        # Verify config
        if not config.TELEGRAM_BOT_TOKEN:
            print("[WARN] Telegram token missing in config")
    
    def _get(self, url, params=None):
        """Optimized GET with error handling"""
        try:
            resp = self.session.get(url, params=params, timeout=config.REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            return {"error": str(e)}
            
    def scan_market(self):
        """Scan CoinGecko for market data"""
        url = f"{config.COINGECKO_API}/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 10,
            "page": 1,
            "sparkline": str(False).lower(),
            "price_change_percentage": "24h"
        }
        
        data = self._get(url, params)
        if isinstance(data, list):
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
        return {"success": False, "error": data.get("error", "Unknown error")}

    def scan_trending(self):
        """Get trending coins"""
        url = f"{config.COINGECKO_API}/search/trending"
        data = self._get(url)
        
        if "coins" in data:
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
        return {"success": False, "error": data.get("error", "Unknown error")}
    
    def get_telegram_messages(self):
        """Get processed Telegram messages with automatic acknowledgment"""
        if not config.TELEGRAM_BOT_TOKEN:
            return {"success": False, "error": "Telegram not configured"}
        
        # 1. Get updates
        url = f"{config.TELEGRAM_API}/getUpdates"
        params = {"offset": self.last_update_id + 1, "timeout": 0}
        
        data = self._get(url, params)
        
        if "result" in data:
            messages = []
            max_update_id = 0
            
            for update in data["result"]:
                update_id = update["update_id"]
                if update_id > max_update_id:
                    max_update_id = update_id
                
                if "message" in update:
                    msg = update["message"]
                    messages.append({
                        "from": msg.get("from", {}).get("username", "unknown"),
                        "chat_id": msg.get("chat", {}).get("id"),
                        "text": msg.get("text", ""),
                        "date": msg.get("date")
                    })
            
            # 2. Acknowledge immediately (Fix replay loop)
            if max_update_id > 0:
                self.last_update_id = max_update_id
                # Async confirm (non-blocking scan)
                try:
                    self.session.get(url, params={"offset": max_update_id + 1, "timeout": 0}, timeout=1)
                except:
                    pass
                    
            return {"success": True, "messages": messages}
            
        return {"success": False, "error": data.get("error", "API Error")}

    def visual_scan(self, url="https://www.coingecko.com/en/watchlists/trending-crypto"):
        """Visual verification using Playwright"""
        print(f"[EYE] Scanning {url}...")
        browser = None
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=30000)
                page.wait_for_load_state("networkidle")
                
                coins = page.locator("span.font-bold").all_inner_texts()
                
                screenshot_path = f"visual_evidence_{int(datetime.now().timestamp())}.png"
                page.screenshot(path=screenshot_path)
                
                valid_coins = [c for c in coins[:10] if len(c) > 1]
                
                return {
                    "success": True,
                    "visual_data": valid_coins,
                    "evidence": screenshot_path,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            if browser:
                try:
                    browser.close()
                except:
                    pass
    
    def gather_all(self):
        """Aggregate all sensor data"""
        return {
            "market": self.scan_market(),
            "trending": self.scan_trending(),
            "telegram": self.get_telegram_messages(),
            "visual": self.visual_scan(),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    sensors = AGISensors()
    print("[TEST] Market:", sensors.scan_market().get("success"))
    print("[TEST] Telegram:", sensors.get_telegram_messages())
