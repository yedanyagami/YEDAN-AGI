"""
YEDAN AGI - Market Eye Cloud
Cloud-based market monitoring and data aggregation service.
Fetches real-time market data from multiple sources.
"""
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class MarketEyeCloud:
    """
    Cloud-based market intelligence service.
    Aggregates data from multiple free APIs for trading decisions.
    """
    
    # API endpoints (free tier)
    COINGECKO_BASE = "https://api.coingecko.com/api/v3"
    FEAR_GREED_API = "https://api.alternative.me/fng/"
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 60  # seconds
        self.last_fetch = {}
        print("[MARKET_EYE] Cloud vision initialized")
    
    def _cached_get(self, key: str, url: str, params: dict = None) -> dict:
        """Fetch with caching to respect rate limits"""
        now = time.time()
        if key in self.cache and (now - self.last_fetch.get(key, 0)) < self.cache_ttl:
            return self.cache[key]
        
        if not REQUESTS_AVAILABLE:
            return {"error": "requests not installed"}
        
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                self.cache[key] = data
                self.last_fetch[key] = now
                return data
            return {"error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_prices(self, symbols: list = None) -> dict:
        """Get current prices for tokens"""
        if symbols is None:
            symbols = ["bitcoin", "ethereum", "solana", "binancecoin"]
        
        url = f"{self.COINGECKO_BASE}/simple/price"
        params = {
            "ids": ",".join(symbols),
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_market_cap": "true"
        }
        
        data = self._cached_get("prices", url, params)
        if "error" in data:
            return {"success": False, **data}
        
        return {
            "success": True,
            "prices": data,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_fear_greed_index(self) -> dict:
        """Get crypto Fear & Greed Index"""
        data = self._cached_get("fear_greed", self.FEAR_GREED_API)
        if "error" in data:
            return {"success": False, **data}
        
        try:
            fng = data.get("data", [{}])[0]
            return {
                "success": True,
                "value": int(fng.get("value", 50)),
                "label": fng.get("value_classification", "Neutral"),
                "timestamp": fng.get("timestamp")
            }
        except:
            return {"success": False, "error": "Parse error"}
    
    def get_trending(self) -> dict:
        """Get trending coins"""
        url = f"{self.COINGECKO_BASE}/search/trending"
        data = self._cached_get("trending", url)
        if "error" in data:
            return {"success": False, **data}
        
        try:
            coins = [
                {
                    "name": c["item"]["name"],
                    "symbol": c["item"]["symbol"],
                    "rank": c["item"]["market_cap_rank"]
                }
                for c in data.get("coins", [])[:7]
            ]
            return {"success": True, "trending": coins}
        except:
            return {"success": False, "error": "Parse error"}
    
    def get_global_stats(self) -> dict:
        """Get global crypto market statistics"""
        url = f"{self.COINGECKO_BASE}/global"
        data = self._cached_get("global", url)
        if "error" in data:
            return {"success": False, **data}
        
        try:
            gd = data.get("data", {})
            return {
                "success": True,
                "total_market_cap_usd": gd.get("total_market_cap", {}).get("usd", 0),
                "total_volume_24h": gd.get("total_volume", {}).get("usd", 0),
                "btc_dominance": gd.get("market_cap_percentage", {}).get("btc", 0),
                "active_cryptos": gd.get("active_cryptocurrencies", 0),
                "market_cap_change_24h": gd.get("market_cap_change_percentage_24h_usd", 0)
            }
        except:
            return {"success": False, "error": "Parse error"}
    
    def get_market_snapshot(self) -> dict:
        """Get complete market snapshot for AGI decision-making"""
        prices = self.get_prices()
        fear_greed = self.get_fear_greed_index()
        trending = self.get_trending()
        global_stats = self.get_global_stats()
        
        # Extract key trading signals
        btc_data = prices.get("prices", {}).get("bitcoin", {})
        sol_data = prices.get("prices", {}).get("solana", {})
        
        return {
            "success": True,
            "btc_price": btc_data.get("usd", 0),
            "btc_change_24h": btc_data.get("usd_24h_change", 0),
            "sol_price": sol_data.get("usd", 0),
            "sol_change_24h": sol_data.get("usd_24h_change", 0),
            "fear_greed": fear_greed.get("value", 50),
            "fear_greed_label": fear_greed.get("label", "Neutral"),
            "trending": trending.get("trending", [])[:3],
            "btc_dominance": global_stats.get("btc_dominance", 0),
            "market_cap_change": global_stats.get("market_cap_change_24h", 0),
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_signal(self) -> dict:
        """Generate trading signal based on market conditions"""
        snapshot = self.get_market_snapshot()
        if not snapshot.get("success"):
            return {"signal": "HOLD", "reason": "Data fetch failed"}
        
        fear = snapshot.get("fear_greed", 50)
        btc_change = snapshot.get("btc_change_24h", 0)
        
        # Simple signal logic
        if fear < 25:
            signal = "BUY"
            reason = f"Extreme Fear ({fear}) = Opportunity"
        elif fear > 75:
            signal = "SELL"
            reason = f"Extreme Greed ({fear}) = Risk"
        elif btc_change < -5:
            signal = "DCA_BUY"
            reason = f"Dip detected ({btc_change:.1f}%)"
        elif btc_change > 8:
            signal = "TAKE_PROFIT"
            reason = f"Rally ({btc_change:.1f}%)"
        else:
            signal = "HOLD"
            reason = f"Neutral market (F&G: {fear})"
        
        return {
            "signal": signal,
            "reason": reason,
            "confidence": abs(50 - fear) / 50,  # 0-1 scale
            "data": snapshot
        }


if __name__ == "__main__":
    print("=" * 60)
    print("[MARKET_EYE_CLOUD] Testing...")
    print("=" * 60)
    
    eye = MarketEyeCloud()
    
    print("\n[1] Prices:")
    print(json.dumps(eye.get_prices(), indent=2))
    
    print("\n[2] Fear & Greed:")
    print(json.dumps(eye.get_fear_greed_index(), indent=2))
    
    print("\n[3] Trending:")
    print(json.dumps(eye.get_trending(), indent=2))
    
    print("\n[4] Full Snapshot:")
    print(json.dumps(eye.get_market_snapshot(), indent=2))
    
    print("\n[5] Trading Signal:")
    print(json.dumps(eye.generate_signal(), indent=2))