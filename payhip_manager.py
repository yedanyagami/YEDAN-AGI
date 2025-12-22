import requests
import os
import json
from dotenv import load_dotenv

# 載入金庫
load_dotenv()
API_KEY = os.getenv("PAYHIP_API_KEY")

def check_payhip_status():
    """
    Payhip API Limitations (as of Dec 2024):
    - API only supports: Coupons, License Keys
    - Sales list endpoint does NOT exist
    - For sales tracking, use Webhooks instead
    
    This script tests API connectivity and shows available endpoints.
    """
    print("=" * 50)
    print("[Payhip] API Status Check")
    print("=" * 50)
    
    if not API_KEY:
        print("[Error] PAYHIP_API_KEY not found, please check .env file")
        return

    print(f"[OK] API Key loaded: {API_KEY[:8]}...{API_KEY[-4:]}")
    
    # Test API with license endpoint (supported)
    url = "https://payhip.com/api/v1/license/verify"
    headers = {
        "payhip-api-key": API_KEY  # Correct header format
    }
    
    # Test connectivity with a dummy request
    try:
        # Try listing coupons (actually supported endpoint)
        coupon_url = "https://payhip.com/api/v1/coupon/list"
        response = requests.get(coupon_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("[OK] API Connection successful!")
            data = response.json()
            print(f"[Info] Coupons found: {len(data.get('coupons', []))}")
        elif response.status_code == 404:
            print("[Info] API responding (endpoint not found - normal for limited API)")
        elif response.status_code == 403:
            print("[Warning] API Key might need different permissions")
        else:
            print(f"[Status] Response code: {response.status_code}")
            
    except Exception as e:
        print(f"[Network] Connection error: {e}")
    
    print("")
    print("[INFO] Payhip API Limitations:")
    print("  - Sales list endpoint: NOT AVAILABLE")
    print("  - Supported: Coupons, License Keys only")
    print("  - Recommendation: Use Webhooks for sales notifications")
    print("  - Webhook URL: https://payhip.com -> Settings -> Developer")
    print("=" * 50)

if __name__ == "__main__":
    check_payhip_status()
