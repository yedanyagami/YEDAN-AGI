"""
Force Upload Digital Product (Manual Override)
Uploads a high-ticket digital product immediately, bypassing AI latency.
Ensures 'The Cash' module has a sellable asset.
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.reactor")

def force_upload():
    store_url = os.getenv("SHOPIFY_STORE_URL")
    access_token = os.getenv("SHOPIFY_ACCESS_TOKEN") or os.getenv("SHOPIFY_ADMIN_TOKEN")
    
    if store_url.startswith("https://"):
        store_url = store_url.replace("https://", "")
        
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }
    
    print(f"[Info] Connecting to {store_url} to Upload Asset...")
    
    # Define High-Ticket Digital Product
    product_data = {
        "product": {
            "title": "The 2026 AI Dropshipping Blueprint (E-book)",
            "body_html": "<h2>Master E-commerce with AI</h2><p>Unlock the secrets of automated dropshipping using YEDAN technology. This comprehensive guide covers:</p><ul><li>AI-Driven Niche Selection</li><li>Automated SEO Optimization</li><li>Zero-Inventory Digital Transformation</li></ul><p><strong>Instant Download. Future-Proof Your Business.</strong></p>",
            "vendor": "YEDAN Digital",
            "product_type": "Digital Product",
            "tags": "digital, ebook, ai, automation",
            "variants": [
                {
                    "price": "97.00",
                    "sku": "AI-EBOOK-001",
                    "requires_shipping": False,
                    "taxable": False
                }
            ],
            "status": "active"
        }
    }
    
    url = f"https://{store_url}/admin/api/2024-01/products.json"
    
    try:
        response = requests.post(url, json=product_data, headers=headers, timeout=10)
        
        if response.status_code == 201:
            data = response.json().get('product')
            print(f"[SUCCESS] Product Created: {data['title']}")
            print(f"   - ID: {data['id']}")
            print(f"   - Price: ${data['variants'][0]['price']}")
            print(f"   - Type: {data['product_type']}")
            print("   - Status: Active")
            print("✅ Digital Transformation Complete. We are now a Digital Store.")
        else:
            print(f"[ERROR] Failed to create product: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"[Critical Error] {e}")

if __name__ == "__main__":
    force_upload()
