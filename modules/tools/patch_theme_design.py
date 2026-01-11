"""
Modern Design Patcher (OS 2.0)
Manipulates templates/index.json directly to update content.
"""
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.reactor")

class ThemePatcher:
    def __init__(self):
        self.shop_url = os.getenv("SHOPIFY_STORE_URL", "").replace("https://", "")
        self.access_token = os.getenv("SHOPIFY_ACCESS_TOKEN") or os.getenv("SHOPIFY_ADMIN_TOKEN")
        self.headers = {"X-Shopify-Access-Token": self.access_token, "Content-Type": "application/json"}

    def run(self):
        print("Fetching Main Theme...")
        r = requests.get(f"https://{self.shop_url}/admin/api/2024-01/themes.json", headers=self.headers)
        themes = r.json().get('themes', [])
        main_theme = next((t for t in themes if t['role'] == 'main'), None)
        
        if not main_theme:
            print("No main theme found.")
            return

        print(f"Targeting Theme: {main_theme['name']} (ID: {main_theme['id']})")
        
        # 1. Get index.json
        url = f"https://{self.shop_url}/admin/api/2024-01/themes/{main_theme['id']}/assets.json?asset[key]=templates/index.json"
        r = requests.get(url, headers=self.headers)
        asset = r.json().get('asset', {})
        
        if not asset:
            print("Could not read templates/index.json")
            return
            
        template = json.loads(asset['value'])
        
        # 2. Find Banner Section
        banner_id = None
        for key, section in template['sections'].items():
            if 'banner' in section['type'] or 'hero' in section['type']:
                banner_id = key
                print(f"Found Banner Section: {key} (Type: {section['type']})")
                break
        
        if banner_id:
            # 3. Update Text Content inside Blocks
            # Dawn/Horizon structure: Section -> Blocks -> Heading
            blocks = template['sections'][banner_id].get('blocks', {})
            
            for b_key, block in blocks.items():
                if block['type'] == 'heading':
                    print(f"   -> Updating Heading Block ({b_key})")
                    block['settings']['heading'] = "YEDAN AI: Unlock the Future"
                    
                if block['type'] == 'text':
                     print(f"   -> Updating Text Block ({b_key})")
                     block['settings']['text'] = "<p>Empowering your digital evolution with AI-driven insights.</p>"
                     
                if block['type'] == 'buttons':
                     print(f"   -> Updating Button Block ({b_key})")
                     block['settings']['button_label_1'] = "Explore Products"

            # 4. Push Update
            new_value = json.dumps(template)
            payload = {
                "asset": {
                    "key": "templates/index.json",
                    "value": new_value
                }
            }
            
            put_url = f"https://{self.shop_url}/admin/api/2024-01/themes/{main_theme['id']}/assets.json"
            r = requests.put(put_url, json=payload, headers=self.headers)
            
            if r.status_code == 200:
                print("SUCCESS: Homepage text updated via OS 2.0 JSON Template.")
            else:
                print(f"Failed to update: {r.status_code} {r.text}")
        else:
            print("No banner section found to update.")

if __name__ == "__main__":
    patcher = ThemePatcher()
    patcher.run()
