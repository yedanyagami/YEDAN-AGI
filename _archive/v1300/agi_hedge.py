"""
YEDAN AGI - Hedge Manager
Controls Perpetual Futures for Delta-Neutral Arbitrage
"""
import os
import time
import hmac
import hashlib
import json
from datetime import datetime
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

try:
    import requests
except ImportError:
    requests = None


class HedgeManager:
    """Controls CEX perpetual futures for delta-neutral strategies"""
    
    def __init__(self, exchange="binance"):
        self.exchange = exchange
        self.api_key = os.getenv(f"{exchange.upper()}_API_KEY")
        self.api_secret = os.getenv(f"{exchange.upper()}_SECRET")
        
        # Exchange endpoints
        self.endpoints = {
            "binance": {
                "base": "https://fapi.binance.com",
                "funding": "/fapi/v1/fundingRate",
                "position": "/fapi/v2/positionRisk",
                "order": "/fapi/v1/order",
                "account": "/fapi/v2/account"
            },
            "bybit": {
                "base": "https://api.bybit.com",
                "funding": "/v5/market/funding/history",
                "position": "/v5/position/list",
                "order": "/v5/order/create",
                "account": "/v5/account/wallet-balance"
            }
        }
        
        self.base_url = self.endpoints.get(exchange, {}).get("base", "")
        print(f"[HEDGE] Initialized for {exchange}")
    
    def _sign_binance(self, params: dict) -> str:
        """Create Binance signature"""
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _request(self, method: str, endpoint: str, params: dict = None, signed: bool = False) -> dict:
        """Make API request"""
        if not requests:
            return {"error": "requests not installed"}
        
        url = self.base_url + endpoint
        headers = {"X-MBX-APIKEY": self.api_key} if self.api_key else {}
        
        params = params or {}
        if signed and self.api_secret:
            params["timestamp"] = int(time.time() * 1000)
            params["signature"] = self._sign_binance(params)
        
        try:
            if method == "GET":
                resp = requests.get(url, params=params, headers=headers, timeout=10)
            else:
                resp = requests.post(url, params=params, headers=headers, timeout=10)
            
            return resp.json()
        except Exception as e:
            return {"error": str(e)}
    
    def get_funding_rates(self, limit: int = 20) -> list:
        """Get current funding rates for all perpetuals"""
        if self.exchange == "binance":
            # Get all symbols' funding rates
            data = self._request("GET", self.endpoints["binance"]["funding"], {"limit": 1000})
            
            if isinstance(data, list):
                # Group by symbol, get latest
                rates = {}
                for item in data:
                    symbol = item.get("symbol", "")
                    rate = float(item.get("fundingRate", 0))
                    if symbol not in rates or item.get("fundingTime", 0) > rates[symbol]["time"]:
                        rates[symbol] = {
                            "symbol": symbol,
                            "rate": rate,
                            "apr": rate * 3 * 365 * 100,  # 8h rate to APR
                            "time": item.get("fundingTime", 0)
                        }
                
                # Sort by APR descending
                sorted_rates = sorted(rates.values(), key=lambda x: x["apr"], reverse=True)
                return sorted_rates[:limit]
        
        return self._simulate_funding_rates(limit)
    
    def _simulate_funding_rates(self, limit: int) -> list:
        """Simulate funding rates for testing"""
        import random
        symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", 
                   "DOGEUSDT", "AVAXUSDT", "LINKUSDT", "MATICUSDT", "ARBUSDT"]
        
        rates = []
        for symbol in symbols[:limit]:
            rate = random.uniform(-0.001, 0.003)  # -0.1% to 0.3%
            rates.append({
                "symbol": symbol,
                "rate": rate,
                "apr": rate * 3 * 365 * 100,
                "simulated": True
            })
        
        return sorted(rates, key=lambda x: x["apr"], reverse=True)
    
    def get_positions(self) -> list:
        """Get current perpetual positions"""
        if self.api_key and self.api_secret:
            data = self._request("GET", self.endpoints["binance"]["position"], signed=True)
            if isinstance(data, list):
                return [p for p in data if float(p.get("positionAmt", 0)) != 0]
        
        return []
    
    def open_short(self, symbol: str, quantity: float, leverage: int = 1) -> dict:
        """
        Open short perpetual position for hedging.
        This creates the hedging leg of the delta-neutral strategy.
        """
        if not self.api_key or not self.api_secret:
            return {
                "success": False,
                "simulated": True,
                "message": f"Would open SHORT {quantity} {symbol} at {leverage}x leverage"
            }
        
        params = {
            "symbol": symbol,
            "side": "SELL",
            "type": "MARKET",
            "quantity": quantity,
            "positionSide": "SHORT"
        }
        
        # Set leverage first
        self._request("POST", "/fapi/v1/leverage", {"symbol": symbol, "leverage": leverage}, signed=True)
        
        # Open position
        result = self._request("POST", self.endpoints["binance"]["order"], params, signed=True)
        
        return {
            "success": "orderId" in result,
            "order": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def close_position(self, symbol: str, position_side: str = "SHORT") -> dict:
        """Close perpetual position"""
        if not self.api_key or not self.api_secret:
            return {
                "success": False,
                "simulated": True,
                "message": f"Would close {position_side} position on {symbol}"
            }
        
        # Get current position size
        positions = self.get_positions()
        pos = next((p for p in positions if p.get("symbol") == symbol), None)
        
        if not pos:
            return {"success": False, "error": "No position found"}
        
        quantity = abs(float(pos.get("positionAmt", 0)))
        side = "BUY" if position_side == "SHORT" else "SELL"
        
        params = {
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "quantity": quantity,
            "positionSide": position_side
        }
        
        result = self._request("POST", self.endpoints["binance"]["order"], params, signed=True)
        
        return {
            "success": "orderId" in result,
            "order": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def calculate_hedge_size(self, spot_value_usd: float, price: float) -> float:
        """Calculate perpetual short size to match spot exposure"""
        return spot_value_usd / price
    
    def collect_funding(self) -> dict:
        """Check and report funding collected from positions"""
        if not self.api_key or not self.api_secret:
            return {"simulated": True, "collected": 0}
        
        # Get account info which includes unrealized PnL
        account = self._request("GET", self.endpoints["binance"]["account"], signed=True)
        
        if isinstance(account, dict):
            return {
                "total_unrealized_pnl": float(account.get("totalUnrealizedProfit", 0)),
                "available_balance": float(account.get("availableBalance", 0)),
                "timestamp": datetime.now().isoformat()
            }
        
        return {"error": "Failed to get account info"}
    
    def find_best_opportunity(self, min_apr: float = 15.0) -> dict:
        """Find best funding rate arbitrage opportunity"""
        rates = self.get_funding_rates(20)
        
        for rate in rates:
            if rate["apr"] >= min_apr:
                return {
                    "symbol": rate["symbol"],
                    "apr": rate["apr"],
                    "rate_8h": rate["rate"],
                    "action": "OPEN_HEDGE",
                    "strategy": "Long spot + Short perp"
                }
        
        return {
            "symbol": None,
            "message": f"No opportunities above {min_apr}% APR",
            "best_available": rates[0] if rates else None
        }
    
    def execute_delta_neutral(self, symbol: str, capital_usd: float, spot_price: float) -> dict:
        """
        Execute full delta-neutral strategy:
        1. Buy spot (simulated - would use DEX)
        2. Open 1x short perpetual
        """
        quantity = self.calculate_hedge_size(capital_usd, spot_price)
        
        steps = []
        
        # Step 1: Buy spot (would be done via DEX or CEX spot)
        steps.append({
            "step": "buy_spot",
            "action": f"Buy {quantity:.4f} {symbol.replace('USDT', '')} at ${spot_price}",
            "simulated": True
        })
        
        # Step 2: Open short perp
        short_result = self.open_short(symbol, quantity, leverage=1)
        steps.append({
            "step": "open_short",
            "result": short_result
        })
        
        return {
            "success": True,
            "symbol": symbol,
            "capital": capital_usd,
            "quantity": quantity,
            "steps": steps,
            "timestamp": datetime.now().isoformat()
        }


if __name__ == "__main__":
    hm = HedgeManager(exchange="binance")
    
    # Test funding rates
    print("Top Funding Rates:")
    rates = hm.get_funding_rates(5)
    for r in rates:
        print(f"  {r['symbol']}: {r['apr']:.1f}% APR")
    
    # Test opportunity finder
    print("\nBest Opportunity:")
    opp = hm.find_best_opportunity(min_apr=10)
    print(f"  {json.dumps(opp, indent=2)}")
    
    # Test delta neutral (simulated)
    print("\nDelta Neutral Execution (Simulated):")
    result = hm.execute_delta_neutral("SOLUSDT", 1000, 200)
    print(f"  {json.dumps(result, indent=2)}")
