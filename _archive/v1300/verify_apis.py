
"""
YEDAN AGI: API STATUS VERIFICATION SUITE
Checks connectivity and auth for consolidted keys in .env
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def check_deepseek():
    print("\n[TEST] DeepSeek API...")
    key = os.getenv("DEEPSEEK_API_KEY")
    if not key:
        print("❌ Missing Key")
        return
    
    try:
        # Simple models list check (or chat if models endpoint unavailable)
        headers = {"Authorization": f"Bearer {key}"}
        # DeepSeek often uses OpenAI compatible endpoints
        response = requests.get("https://api.deepseek.com/models", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("[OK] (Connected)")
        else:
            print(f"[FAIL] Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")

def check_shopify():
    print("\n[TEST] Shopify API...")
    token = os.getenv("SHOPIFY_ACCESS_TOKEN")
    url = os.getenv("SHOPIFY_STORE_URL")
    
    if not token or not url:
        print("[FAIL] Missing Config")
        return
        
    api_url = f"{url}/admin/api/2023-10/shop.json"
    headers = {"X-Shopify-Access-Token": token}
    
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            shop = response.json().get('shop', {})
            print(f"[OK] (Connected to {shop.get('name')})")
        else:
            print(f"[FAIL] Failed: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")

def check_telegram():
    print("\n[TEST] Telegram Bot...")
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("[FAIL] Missing Token")
        return
        
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            bot = response.json().get('result', {})
            print(f"[OK] (Connected as @{bot.get('username')})")
        else:
            print(f"[FAIL] Failed: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Error: {e}")

if __name__ == "__main__":
    print("=== API STATUS CHECK ===")
    check_deepseek()
    check_shopify()
    check_telegram()
    print("\n=== COMPLETE ===")
