"""
Apply Theme
1. Uploads the brand image as 'assets/brand_hero.jpg'
2. Updates theme settings to use the extracted Golden Palette
"""
import requests
import os
import base64
import json
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.reactor")

class ThemeApplicator:
    def __init__(self):
        self.shop_url = os.getenv("SHOPIFY_STORE_URL", "").replace("https://", "")
        self.access_token = os.getenv("SHOPIFY_ACCESS_TOKEN") or os.getenv("SHOPIFY_ADMIN_TOKEN")
        self.image_path = r"C:/Users/yagam/.gemini/antigravity/brain/7d8121c0-0b17-4f11-86a8-2f5befda9b9b/uploaded_image_1767438896099.jpg"
        
        # Colors from extraction
        self.primary_color = "#ae8733" # Gold
        self.accent_color = "#b2892d"  # Darker Gold
        # Lighter background for readability (derived manually for now)
        self.bg_color = "#f9f4e6"      # Soft Cream/Paper color (Warm)

    def upload_hero_image(self, theme_id):
        print("\n[1/3] Uploading Brand Hero Image...")
        try:
            with open(self.image_path, "rb") as f:
                encoded_string = base64.b64encode(f.read()).decode('utf-8')
            
            asset_key = "assets/brand_hero.jpg"
            payload = {
                "asset": {
                    "key": asset_key,
                    "attachment": encoded_string
                }
            }
            
            headers = {"X-Shopify-Access-Token": self.access_token}
            url = f"https://{self.shop_url}/admin/api/2024-01/themes/{theme_id}/assets.json"
            
            r = requests.put(url, json=payload, headers=headers)
            if r.status_code in [200, 201]:
                print(f"   [Success] Brand image uploaded to {asset_key}")
                return True
            else:
                print(f"   [Error] Upload failed: {r.status_code}")
        except Exception as e:
            print(f"   [Error] {e}")
        return False

    def update_colors(self, theme_id):
        print("\n[2/3] Applying Golden Palette...")
        headers = {"X-Shopify-Access-Token": self.access_token}
        
        # 1. Read current settings
        url = f"https://{self.shop_url}/admin/api/2024-01/themes/{theme_id}/assets.json?asset[key]=config/settings_data.json"
        
        try:
            r = requests.get(url, headers=headers)
            current_settings = json.loads(r.json()['asset']['value'])
            
            # 2. Modify colors (This depends on the theme structure, assuming standard Dawn/Horizon structure)
            # We will try to find keys related to colors.
            # Note: This is a robust attempt, might vary by theme.
            
            current = current_settings.get('current', {})
            if 'colors_solid_button_background' in current: current['colors_solid_button_background'] = self.primary_color
            if 'colors_accent_1' in current: current['colors_accent_1'] = self.primary_color
            if 'colors_accent_2' in current: current['colors_accent_2'] = self.accent_color
            if 'colors_background_1' in current: current['colors_background_1'] = self.bg_color
            
            # Structure for some themes usually inside 'sections' or 'colors' blocks
            # We'll just save it back.
            
            payload = {
                "asset": {
                    "key": "config/settings_data.json",
                    "value": json.dumps(current_settings)
                }
            }
            
            r = requests.put(f"https://{self.shop_url}/admin/api/2024-01/themes/{theme_id}/assets.json", json=payload, headers=headers)
            if r.status_code == 200:
                print("   [Success] Theme colors updated to Warm Gold.")
            else:
                print(f"   [Error] Color update failed: {r.status_code}")
                
        except Exception as e:
            print(f"   [Error] {e}")

    def run(self):
        # Find Main Theme
        headers = {"X-Shopify-Access-Token": self.access_token}
        r = requests.get(f"https://{self.shop_url}/admin/api/2024-01/themes.json", headers=headers)
        themes = r.json().get('themes', [])
        main_theme = next((t for t in themes if t['role'] == 'main'), None)
        
        if main_theme:
            print(f"[Info] Target Theme: {main_theme['name']} ({main_theme['id']})")
            self.upload_hero_image(main_theme['id'])
            self.update_colors(main_theme['id'])
        else:
            print("[Error] No main theme found.")

if __name__ == "__main__":
    app = ThemeApplicator()
    app.run()
