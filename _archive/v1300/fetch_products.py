
import os
import requests
import json
from dotenv import load_dotenv

# Load env directly to be sure
load_dotenv()

# Get Config
SHOP_URL = os.getenv("SHOPIFY_SHOP_URL") or os.getenv("SHOPIFY_STORE_URL")
TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")

print(f"Checking Shopify Connection...")
print(f"URL: {SHOP_URL}")
print(f"Token: {TOKEN[:5]}...{TOKEN[-5:] if TOKEN else ''}")

if not SHOP_URL or not TOKEN:
    print("❌ Missing Credentials in .env")
    exit(1)

# Clean URL
if "https://" in SHOP_URL:
    SHOP_URL = SHOP_URL.replace("https://", "")
if "/" in SHOP_URL:
    SHOP_URL = SHOP_URL.split("/")[0]

url = f"https://{SHOP_URL}/admin/api/2024-01/products.json"
headers = {
    "X-Shopify-Access-Token": TOKEN,
    "Content-Type": "application/json"
}

try:
    print(f"Fetching from: {url}")
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        products = data.get("products", [])
        print(f"\n📦 Found {len(products)} Products:")
        for p in products:
            variant = p['variants'][0]
            print(f"   - ID: {p['id']}")
            print(f"     Name: {p['title']}")
            print(f"     Price: ${variant['price']}")
            print(f"     Status: {p['status']}")
            print(f"     Link: https://{SHOP_URL}/products/{p['handle']}")
            print("---")
            
        # Save to a file for the system to use
        with open("data/shopify_products.json", "w") as f:
            json.dump(products, f, indent=2)
            
    else:
        print(f"Error: {response.text}")

except Exception as e:
    print(f"Exception: {e}")
