"""
Shopify Connectivity Tester
Verifies:
1. API Access Token validity
2. Store Reachability
3. Product List (Inventory check)
"""
import requests
import os
import json
from dotenv import load_dotenv

# Load explicitly from .env.reactor
load_dotenv(dotenv_path=".env.reactor")

def check_store(url_domain, token):
    print(f"\n[INFO] Connecting to {url_domain}...")
    
    # Strip protocol if present
    if url_domain.startswith("https://"):
        url_domain = url_domain.replace("https://", "")
        
    headers = {
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    }
    
    # Try getting Shop info
    url = f"https://{url_domain}/admin/api/2024-01/shop.json"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            shop_data = response.json().get('shop', {})
            print(f"[SUCCESS] Connected to store: {shop_data.get('name')}")
            print(f"   Domain: {shop_data.get('domain')}")
            print(f"   Email: {shop_data.get('email')}")
            print(f"   Currency: {shop_data.get('currency')}")
            
            # Check Products
            check_products(url_domain, headers)
            return True
            
        elif response.status_code == 401:
            print("[FAILED] Unauthorized (Invalid Access Token)")
        elif response.status_code == 404:
            print("[FAILED] Store Not Found (Check URL)")
        else:
            print(f"[FAILED] Error: {response.text}")
            
    except Exception as e:
        print(f"[EXCEPTION] {e}")
        
    return False

def check_products(url_domain, headers):
    print("\n[INFO] Checking Inventory...")
    products_url = f"https://{url_domain}/admin/api/2024-01/products.json?limit=5"
    try:
        p_response = requests.get(products_url, headers=headers, timeout=10)
        if p_response.status_code == 200:
            products = p_response.json().get('products', [])
            print(f"[SUCCESS] Found {len(products)} products:")
            for p in products:
                # Safe print without emojis
                try:
                    title = p['title'].encode(
                        'ascii', 'ignore').decode('ascii')
                except:
                    title = "Unknown Title"
                    
                price = "N/A"
                if p.get('variants'):
                    price = p['variants'][0]['price']
                    
                print(f"   - {title} (ID: {p['id']}) - ${price}")
        else:
            print(f"[WARN] Could not fetch products: {p_response.status_code}")
    except Exception as e:
        print(f"[WARN] Product check error: {e}")

def test_connectivity():
    print("="*60)
    print("Shopify Connection Test")
    print("="*60)

    # 1. Config Check
    env_store_url = os.getenv("SHOPIFY_STORE_URL")
    access_token = os.getenv("SHOPIFY_ACCESS_TOKEN") or os.getenv("SHOPIFY_ADMIN_TOKEN")
    
    print(f"Token: {access_token[:6]}...{access_token[-4:] if access_token else ''}")
    
    if not access_token:
        print("[ERROR] No Access Token found in .env.reactor")
        return

    # Test 1: URL from env
    if env_store_url:
        print(f"\n--- Testing Env URL: {env_store_url} ---")
        success = check_store(env_store_url, access_token)
        if success:
            print("\n[FINAL RESULT] Env URL works!")
            return

    # Test 2: Alternate URL (io)
    alt_url = "yedanyagami-io.myshopify.com"
    print(f"\n--- Testing Alt URL: {alt_url} ---")
    success = check_store(alt_url, access_token)
    
    if success:
        print("\n[FINAL RESULT] Alt URL works! Please update .env.reactor")
    else:
        print("\n[FINAL RESULT] Both URLs failed. Check Token.")

if __name__ == "__main__":
    test_connectivity()
