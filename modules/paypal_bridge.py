"""
YEDAN AGI - PayPal Integration Module
Connects to PayPal API for payment verification and transaction monitoring
Supports both Sandbox and Live modes
"""
import sys
import io
import os
import json
import requests
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from dotenv import load_dotenv

# Fix Windows console encoding
# Encoding fix moved to __main__ or handled by caller

load_dotenv(dotenv_path=".env.reactor")


class PayPalBridge:
    """PayPal API integration for YEDAN"""
    
    def __init__(self):
        self.client_id = os.getenv("PAYPAL_CLIENT_ID")
        self.client_secret = os.getenv("PAYPAL_SECRET")
        self.mode = os.getenv("PAYPAL_MODE", "sandbox")  # sandbox or live
        
        # Set base URL based on mode
        if self.mode == "live":
            self.base_url = "https://api-m.paypal.com"
        else:
            self.base_url = "https://api-m.sandbox.paypal.com"
        
        self.access_token = None
        self.token_expiry = None
    
    def is_configured(self) -> bool:
        """Check if PayPal credentials are configured"""
        return bool(self.client_id and self.client_secret)
    
    def _get_access_token(self) -> Optional[str]:
        """Get OAuth2 access token from PayPal"""
        if self.access_token and self.token_expiry and datetime.now() < self.token_expiry:
            return self.access_token
        
        try:
            auth = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
            r = requests.post(
                f"{self.base_url}/v1/oauth2/token",
                headers={
                    "Authorization": f"Basic {auth}",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data="grant_type=client_credentials",
                timeout=30
            )
            
            if r.status_code == 200:
                data = r.json()
                self.access_token = data["access_token"]
                # Token expires in seconds, subtract 60 for safety margin
                expires_in = data.get("expires_in", 3600) - 60
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
                return self.access_token
            else:
                print(f"[PayPal] Token error: {r.status_code} - {r.text}")
        except Exception as e:
            print(f"[PayPal] Token error: {e}")
        return None
    
    def _api_request(self, method: str, endpoint: str, data: Dict = None) -> Optional[Dict]:
        """Make authenticated API request to PayPal"""
        token = self._get_access_token()
        if not token:
            return None
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            url = f"{self.base_url}{endpoint}"
            if method == "GET":
                r = requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
                r = requests.post(url, headers=headers, json=data, timeout=30)
            else:
                return None
            
            if r.status_code in [200, 201]:
                return r.json()
            else:
                print(f"[PayPal] API error: {r.status_code} - {r.text[:200]}")
        except Exception as e:
            print(f"[PayPal] Request error: {e}")
        return None
    
    def verify_connection(self) -> Dict:
        """Verify PayPal API connection"""
        result = {
            "configured": self.is_configured(),
            "connected": False,
            "mode": self.mode,
            "error": None
        }
        
        if not result["configured"]:
            result["error"] = "PayPal credentials not configured"
            return result
        
        token = self._get_access_token()
        if token:
            result["connected"] = True
            result["token_preview"] = token[:20] + "..."
        else:
            result["error"] = "Failed to get access token"
        
        return result
    
    def get_transactions(self, days: int = 7) -> List[Dict]:
        """Get recent transactions"""
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%dT00:00:00Z")
        end_date = datetime.now().strftime("%Y-%m-%dT23:59:59Z")
        
        endpoint = f"/v1/reporting/transactions?start_date={start_date}&end_date={end_date}&fields=all"
        result = self._api_request("GET", endpoint)
        
        if result:
            return result.get("transaction_details", [])
        return []
    
    def get_balance(self) -> Optional[Dict]:
        """Get PayPal account balance"""
        result = self._api_request("GET", "/v1/reporting/balances")
        if result:
            balances = result.get("balances", [])
            return {
                "balances": balances,
                "total_available": sum(
                    float(b.get("available_balance", {}).get("value", 0)) 
                    for b in balances
                )
            }
        return None
    
    def get_order(self, order_id: str) -> Optional[Dict]:
        """Get order details by ID"""
        return self._api_request("GET", f"/v2/checkout/orders/{order_id}")
    
    def capture_order(self, order_id: str) -> Optional[Dict]:
        """Capture payment for an order"""
        return self._api_request("POST", f"/v2/checkout/orders/{order_id}/capture")


class PayPalSynapseIntegration:
    """Integration layer between PayPal and Synapse"""
    
    def __init__(self):
        self.paypal = PayPalBridge()
        self.synapse_url = "https://synapse.yagami8095.workers.dev"
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat = os.getenv("TELEGRAM_CHAT_ID")
    
    def sync_revenue(self):
        """Sync PayPal revenue to Synapse ROI metrics"""
        if not self.paypal.is_configured():
            print("[PayPal] Not configured, skipping sync")
            return
        
        # Get recent transactions
        transactions = self.paypal.get_transactions(days=7)
        
        # Calculate totals
        total_revenue = 0
        transaction_count = 0
        for tx in transactions:
            amount = tx.get("transaction_info", {}).get("transaction_amount", {})
            if amount.get("value"):
                total_revenue += float(amount["value"])
                transaction_count += 1
        
        # Get balance
        balance_info = self.paypal.get_balance()
        
        metrics = {
            "paypal_revenue_7d": total_revenue,
            "paypal_transactions_7d": transaction_count,
            "paypal_balance": balance_info.get("total_available", 0) if balance_info else 0,
            "synced_at": datetime.now().isoformat()
        }
        
        # Send to Synapse
        try:
            requests.post(
                f"{self.synapse_url}/roi/metrics",
                json=metrics,
                timeout=10
            )
            print(f"[PayPal] Synced metrics: {metrics}")
        except Exception as e:
            print(f"[PayPal] Sync error: {e}")
        
        return metrics
    
    def notify_payment(self, amount: float, currency: str = "USD", transaction_id: str = ""):
        """Send payment notification to Telegram"""
        if not self.telegram_token or not self.telegram_chat:
            return
        
        message = f"💵 *PayPal Payment Received*\n\nAmount: ${amount:.2f} {currency}\nTransaction: {transaction_id}"
        
        try:
            requests.post(
                f"https://api.telegram.org/bot{self.telegram_token}/sendMessage",
                json={
                    "chat_id": self.telegram_chat,
                    "text": message,
                    "parse_mode": "Markdown"
                },
                timeout=5
            )
        except:
            pass


def main():
    """Test PayPal connection"""
    print("=" * 60)
    print("[PayPal Bridge] Testing connection...")
    print("=" * 60)
    
    bridge = PayPalBridge()
    status = bridge.verify_connection()
    
    print(f"Configured: {status['configured']}")
    print(f"Mode: {status['mode']}")
    print(f"Connected: {status['connected']}")
    
    if status.get('error'):
        print(f"Error: {status['error']}")
    
    if status['connected']:
        print(f"Token: {status.get('token_preview', 'N/A')}")
        
        # Try to get balance
        print("\nFetching balance...")
        balance = bridge.get_balance()
        if balance:
            print(f"Available Balance: ${balance['total_available']:.2f}")
        else:
            print("Could not fetch balance (may require specific permissions)")
    
    return status


if __name__ == "__main__":
    main()
