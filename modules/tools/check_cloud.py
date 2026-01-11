"""
Cloud Status Monitor
Checks the health of all cloud integrations: Shopify, DeepSeek, ArXiv.
"""
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.reactor")

def check_cloud_health():
    print("="*60)
    print("[*] YEDAN CLOUD STATUS MONITOR")
    print("="*60)
    
    # 1. Shopify Storefront
    store_url = os.getenv("SHOPIFY_STORE_URL")
    if store_url and store_url.startswith("https://"): store_url = store_url.replace("https://", "")
    
    print(f"\n[1] Shopify Storefront ({store_url})")
    try:
        t0 = time.time()
        # Clean URL ensures no double https
        resp = requests.get(f"https://{store_url}/products.json?limit=1", timeout=10)
        lat = (time.time() - t0) * 1000
        if resp.status_code == 200:
            print(f"   [OK] ONLINE (Latency: {lat:.0f}ms)")
            products = resp.json().get('products', [])
            if products:
                print(f"   [Info] Live Product: {products[0]['title']}")
            else:
                print("   [Warn] Store empty.")
        else:
             print(f"   [Error] ERROR (Status: {resp.status_code})")
    except Exception as e:
        print(f"   ❌ UNREACHABLE: {e}")

    # 2. DeepSeek API / Writer Brain
    print(f"\n[2] DeepSeek Brain (API)")
    try:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
             print("   ⚠️ No API Key found.")
        else:
            # Simple simulation of connectivity check (don't burn tokens just for ping if possible, 
            # but user wants status. We'll do a simple verify if possible, or just assume alive if prior calls worked)
            # Actually, let's just ping a public endpoint to check internet first
            t0 = time.time()
            requests.get("https://api.deepseek.com", timeout=5) # Just checking reachability
            lat = (time.time() - t0) * 1000
            print(f"   [OK] REACHABLE (Latency: {lat:.0f}ms)")
    except Exception as e:
        print(f"   ❌ UNREACHABLE: {e}")

    # 3. ArXiv (Content Source)
    print(f"\n[3] ArXiv Content Cloud")
    try:
        t0 = time.time()
        requests.get("http://export.arxiv.org/api/query?search_query=all:electron&max_results=1", timeout=10)
        lat = (time.time() - t0) * 1000
        print(f"   [OK] ONLINE (Latency: {lat:.0f}ms)")
    except Exception as e:
        print(f"   ❌ UNREACHABLE: {e}")

if __name__ == "__main__":
    check_cloud_health()
