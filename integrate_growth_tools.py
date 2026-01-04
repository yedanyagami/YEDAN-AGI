"""
Growth Tools Integrator
1. Connects Systeme.io (Email/Funnels)
2. Injects Hotjar/Contentsquare (Analytics) into Shopify
"""
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.reactor")

class GrowthIntegrator:
    def __init__(self):
        self.shopify_url = os.getenv("SHOPIFY_STORE_URL", "")
        if self.shopify_url.startswith("https://"): self.shopify_url = self.shopify_url.replace("https://", "")
        self.shopify_token = os.getenv("SHOPIFY_ACCESS_TOKEN") or os.getenv("SHOPIFY_ADMIN_TOKEN")
        self.systeme_key = os.getenv("SYSTEME_API_KEY")
        
        # Extracted from user input
        self.hotjar_src = "https://t.contentsquare.net/uxa/10cea713243dc.js"

    def verify_systeme(self):
        print("\n[1/2] Connecting to Systeme.io...")
        if not self.systeme_key:
            print("   [Error] No API Key found.")
            return False
            
        # Systeme.io API is a bit weird, usually requires email/password or key.
        # Assuming typical Bearer token structure or header key.
        # Note: Public documentation for Systeme.io API is sparse, usually X-API-Key.
        # We will try a basic contacts list check.
        
        headers = {
            "X-API-Key": self.systeme_key,
            "Accept": "application/json"
        }
        
        try:
            # Checking contacts endpoint
            r = requests.get("https://api.systeme.io/api/contacts", headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                count = len(data.get('items', []))
                print(f"   [Success] Connected! Contacts found: {count}")
                return True
            elif r.status_code == 401:
                print("   [Error] Invalid API Key.")
            else:
                print(f"   [Error] API Status: {r.status_code}")
        except Exception as e:
            print(f"   [Error] Connection failed: {e}")
        return False

    def inject_hotjar_shopify(self):
        print("\n[2/2] Injecting Hotjar to Shopify...")
        if not self.shopify_token:
            print("   [Error] No Shopify Token.")
            return False

        headers = {
            "X-Shopify-Access-Token": self.shopify_token,
            "Content-Type": "application/json"
        }
        
        # 1. Check existing
        try:
            get_url = f"https://{self.shopify_url}/admin/api/2024-01/script_tags.json"
            r = requests.get(get_url, headers=headers)
            if r.status_code == 200:
                tags = r.json().get('script_tags', [])
                for tag in tags:
                    if "contentsquare" in tag.get('src', ''):
                        print(f"   [Info] Hotjar already active (ID: {tag['id']})")
                        return True
        except Exception as e:
            print(f"   [Error] Check failed: {e}")
            
        # 2. Inject
        payload = {
            "script_tag": {
                "event": "onload",
                "src": self.hotjar_src
            }
        }
        
        try:
            post_url = f"https://{self.shopify_url}/admin/api/2024-01/script_tags.json"
            r = requests.post(post_url, json=payload, headers=headers)
            if r.status_code == 201:
                print("   [Success] Hotjar ScriptTag injected successfully.")
                return True
            else:
                print(f"   [Error] Injection failed: {r.status_code} {r.text}")
        except Exception as e:
            print(f"   [Error] Injection failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Growth Tools Integrator ===")
    integrator = GrowthIntegrator()
    integrator.verify_systeme()
    integrator.inject_hotjar_shopify()
