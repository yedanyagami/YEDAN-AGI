"""
Product Investigator
Analyzes the origin of existing Shopify products.
Checks Vendor, Product Type, and Tags to determine if they are dropshipping, digital, or placeholders.
"""
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.reactor")

def investigate_products():
    store_url = os.getenv("SHOPIFY_STORE_URL")
    access_token = os.getenv("SHOPIFY_ACCESS_TOKEN") or os.getenv("SHOPIFY_ADMIN_TOKEN")
    
    if store_url.startswith("https://"):
        store_url = store_url.replace("https://", "")
        
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }
    
    print(f"[Info] Investigating Products on {store_url}...")
    
    url = f"https://{store_url}/admin/api/2024-01/products.json?limit=10"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            products = response.json().get('products', [])
            print(f"\nFound {len(products)} products. Analysis:")
            print("-" * 60)
            
            non_digital_count = 0
            
            for p in products:
                # Safe title print
                try: title = p['title'].encode('ascii', 'ignore').decode('ascii')
                except: title = "Unknown"
                
                vendor = p.get('vendor', 'N/A')
                p_type = p.get('product_type', 'N/A')
                tags = p.get('tags', '')
                variants = p.get('variants', [])
                price = variants[0]['price'] if variants else "0.00"
                requires_shipping = variants[0]['requires_shipping'] if variants else False
                
                print(f"[ID: {p['id']}] {title}")
                print(f"   - Vendor: {vendor}")
                print(f"   - Type: {p_type}")
                print(f"   - Price: ${price}")
                print(f"   - Physical Item? {'YES (Requires Shipping)' if requires_shipping else 'NO (Digital?)'}")
                print(f"   - Tags: {tags}")
                
                if requires_shipping:
                    non_digital_count += 1
                print("-" * 30)
                
            print(f"\n[REALITY CHECK]: {non_digital_count}/{len(products)} products require shipping.")
            if non_digital_count > 0:
                print("   ⚠️ These appear to be PHYSICAL dropshipping items (likely from DSers/AliExpress).")
                print("   If you don't have a supplier connected, selling these is risky (unfulfilled orders).")
            else:
                print("   ✅ All items look digital/service-based.")
                
        else:
            print(f"Failed to fetch: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    investigate_products()
