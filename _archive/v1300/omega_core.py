"""
YEDAN AGI - Omega Core (PayPal Payment Engine)
用於生成 PayPal 付款連結並處理資金流
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

PAYPAL_MODE = os.getenv("PAYPAL_MODE", "sandbox")
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")

# PayPal API Endpoints
PAYPAL_BASE_URL = "https://api-m.paypal.com" if PAYPAL_MODE == "live" else "https://api-m.sandbox.paypal.com"

def get_paypal_access_token():
    """獲取 PayPal API Access Token"""
    if not PAYPAL_CLIENT_ID or not PAYPAL_CLIENT_SECRET:
        print("[!] PayPal credentials not configured")
        return None
    
    url = f"{PAYPAL_BASE_URL}/v1/oauth2/token"
    headers = {"Accept": "application/json", "Accept-Language": "en_US"}
    data = {"grant_type": "client_credentials"}
    
    try:
        response = requests.post(url, headers=headers, data=data, 
                                auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET), timeout=30)
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"[OK] PayPal Access Token acquired ({PAYPAL_MODE.upper()} mode)")
            return token
        else:
            print(f"[X] PayPal Auth Failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"[X] PayPal Connection Error: {e}")
        return None

def create_paypal_payment(description, price):
    """建立 PayPal 付款連結"""
    access_token = get_paypal_access_token()
    if not access_token:
        return None
    
    url = f"{PAYPAL_BASE_URL}/v2/checkout/orders"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    order_data = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "description": description,
            "amount": {
                "currency_code": "USD",
                "value": price
            }
        }],
        "application_context": {
            "return_url": "https://yedanyagami.cc/success",
            "cancel_url": "https://yedanyagami.cc/cancel"
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=order_data, timeout=30)
        if response.status_code == 201:
            order = response.json()
            order_id = order.get("id")
            approve_link = None
            for link in order.get("links", []):
                if link.get("rel") == "approve":
                    approve_link = link.get("href")
                    break
            print(f"[OK] PayPal Order Created: {order_id}")
            print(f"[->] Approve Link: {approve_link}")
            return approve_link
        else:
            print(f"[X] PayPal Order Failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"[X] PayPal Order Error: {e}")
        return None

def execute_omega_report(alpha_signal):
    """執行 Omega 報告並生成付款連結"""
    print(f"\n[OMEGA] Generating payment link for: {alpha_signal}")
    # 修改後 (測試用真錢 - $0.01)
    pay_link = create_paypal_payment(f"Omega LIVE TEST: {alpha_signal}", "0.01")
    if pay_link:
        print(f"[SUCCESS] Payment Link: {pay_link}")
    return pay_link

if __name__ == "__main__":
    print("=" * 50)
    print("[OMEGA CORE] PayPal Payment Engine Test")
    print(f"[MODE] {PAYPAL_MODE.upper()}")
    print("=" * 50)
    
    # 測試獲取 Token
    token = get_paypal_access_token()
    if token:
        print("\n[TEST] Creating $0.01 test payment...")
        link = create_paypal_payment("YEDAN AGI Test Payment", "0.01")
        if link:
            print(f"\n[RESULT] Pay here: {link}")
        else:
            print("[RESULT] Failed to create payment link")
    else:
        print("[RESULT] Cannot proceed without valid token")
