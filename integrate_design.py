"""
Design & Analytics Integrator
1. Inject Umami Tracking (via Theme.liquid)
2. Verify Penpot Connection
"""
import requests
import os
import re
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.reactor")

class DesignAnalyticsIntegrator:
    def __init__(self):
        self.shopify_url = os.getenv("SHOPIFY_STORE_URL", "")
        if self.shopify_url.startswith("https://"): self.shopify_url = self.shopify_url.replace("https://", "")
        self.shopify_token = os.getenv("SHOPIFY_ACCESS_TOKEN") or os.getenv("SHOPIFY_ADMIN_TOKEN")
        self.penpot_token = os.getenv("PENPOT_ACCESS_TOKEN")
        
        self.umami_script = '<script defer src="https://cloud.umami.is/script.js" data-website-id="0405e8a8-cbb5-49b0-b871-5368bfbdbe26"></script>'

    def verify_penpot(self):
        print("\n[1/2] Connecting to Penpot...")
        if not self.penpot_token:
            print("   [Error] No Penpot Token.")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.penpot_token}",
            "Accept": "application/json"
        }
        
        try:
            # Check 'me' endpoint
            r = requests.get("https://design.penpot.app/api/rpc/command/get-profile", headers=headers, timeout=10)
            
            # Penpot API often returns 200 even on some errors, check content
            if r.status_code == 200:
                print(f"   [Success] Connected to Penpot! (Status: {r.status_code})")
                return True
            elif r.status_code == 401:
                print("   [Error] Invalid Penpot Token.")
            else:
                print(f"   [Error] Penpot API Status: {r.status_code}")
        except Exception as e:
            # Penpot might need specific domain or self-host URL, assuming SaaS for now
            # If the user is self-hosting, we'd need that URL.
            # Trying a simpler connectivity check if RPC fails
            print(f"   [Error] Connection failed: {e}")
        return False

    def inject_umami_theme(self):
        print("\n[2/2] Injecting Umami to Theme.liquid...")
        if not self.shopify_token:
            print("   [Error] No Shopify Token.")
            return False

        headers = {
            "X-Shopify-Access-Token": self.shopify_token,
            "Content-Type": "application/json"
        }
        
        # 1. Get Main Theme ID
        theme_id = None
        try:
            r = requests.get(f"https://{self.shopify_url}/admin/api/2024-01/themes.json", headers=headers)
            if r.status_code == 200:
                themes = r.json().get('themes', [])
                for t in themes:
                    if t.get('role') == 'main':
                        theme_id = t['id']
                        break
            
            if not theme_id:
                print("   [Error] Could not find main theme.")
                return False
                
            print(f"   [Info] Main Theme ID: {theme_id}")
            
        except Exception as e:
            print(f"   [Error] Theme fetch failed: {e}")
            return False
            
        # 2. Read Theme.liquid
        asset_key = "layout/theme.liquid"
        try:
            url = f"https://{self.shopify_url}/admin/api/2024-01/themes/{theme_id}/assets.json?asset[key]={asset_key}"
            r = requests.get(url, headers=headers)
            if r.status_code != 200:
                print(f"   [Error] Could not read theme.liquid: {r.status_code}")
                return False
                
            asset = r.json().get('asset', {})
            content = asset.get('value', '')
            
            if not content:
                print("   [Error] Theme.liquid is empty.")
                return False
                
            # 3. Check and Inject
            if "umami.is/script.js" in content:
                print("   [Info] Umami already present in theme.")
                return True
                
            # Inject before </head>
            if "</head>" in content:
                new_content = content.replace("</head>", f"  {self.umami_script}\n</head>")
            else:
                print("   [Warning] No </head> tag found, appending to top.")
                new_content = self.umami_script + "\n" + content
                
            # 4. Save
            put_payload = {
                "asset": {
                    "key": asset_key,
                    "value": new_content
                }
            }
            put_url = f"https://{self.shopify_url}/admin/api/2024-01/themes/{theme_id}/assets.json"
            r = requests.put(put_url, json=put_payload, headers=headers)
            
            if r.status_code == 200:
                print("   [Success] Umami injected into theme.liquid!")
                return True
            else:
                print(f"   [Error] Save failed: {r.status_code}")
                return False
                
        except Exception as e:
            print(f"   [Error] Asset manipulation failed: {e}")
            return False

if __name__ == "__main__":
    print("=== Design & Analytics Integrator ===")
    integrator = DesignAnalyticsIntegrator()
    integrator.verify_penpot()
    integrator.inject_umami_theme()
