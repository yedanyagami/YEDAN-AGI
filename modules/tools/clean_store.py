"""
Store Cleaner (Liability Remover)
Deletes all physical products that require shipping.
SAFETY: This is DESTRUCTIVE. It removes products from Shopify.
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.reactor")

def clean_store():
    store_url = os.getenv("SHOPIFY_STORE_URL")
    access_token = os.getenv("SHOPIFY_ACCESS_TOKEN") or os.getenv("SHOPIFY_ADMIN_TOKEN")
    
    if store_url.startswith("https://"):
        store_url = store_url.replace("https://", "")
        
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }
    
    print(f"[Info] Connecting to {store_url} to CLEAN...")

    # Create a robust session
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=3)
    session.mount('https://', adapter)
    
    # 1. Fetch Products
    url = f"https://{store_url}/admin/api/2024-01/products.json?limit=50"
    
    try:
        response = session.get(url, headers=headers, timeout=10)
    except Exception as e:
        print(f"[Critical Error] Connection failed: {e}")
        return
    
    if response.status_code != 200:
        print(f"[Error] Failed to fetch products: {response.status_code}")
        return

    products = response.json().get('products', [])
    print(f"[Info] Found {len(products)} products.")
    
    deleted_count = 0
    
    for p in products:
        p_id = p['id']
        try:
             title = p['title'].encode('ascii', 'ignore').decode('ascii')
        except:
             title = "Unknown Product"
             
        variants = p.get('variants', [])
        requires_shipping = variants[0]['requires_shipping'] if variants else False
        
        if requires_shipping:
            print(f"   [DELETE] Excluding Physical Item: {title} (ID: {p_id})")
            
            del_url = f"https://{store_url}/admin/api/2024-01/products/{p_id}.json"
            try:
                del_resp = session.delete(del_url, headers=headers, timeout=10)
                
                if del_resp.status_code == 200:
                    print("      -> Successfully Deleted.")
                    deleted_count += 1
                else:
                    print(f"      -> Failed to delete: {del_resp.status_code}")
            except Exception as e:
                print(f"      -> Delete failed: {e}")
        else:
            print(f"   [KEEP] Digital/Safe Item: {title}")

    print("-" * 60)
    print(f"[Summary] Deleted {deleted_count} physical products.")
    print("[Success] Store liability removed.")

if __name__ == "__main__":
    clean_store()
