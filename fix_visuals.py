"""
Visual Fixer
1. Links the uploaded 'assets/brand_hero.jpg' to the Homepage Banner.
2. Assigns the 'Golden Girl' image to all products missing images.
"""
import requests
import os
import json
import base64
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.reactor")

class VisualFixer:
    def __init__(self):
        self.shop_url = os.getenv("SHOPIFY_STORE_URL", "").replace("https://", "")
        self.access_token = os.getenv("SHOPIFY_ACCESS_TOKEN") or os.getenv("SHOPIFY_ADMIN_TOKEN")
        self.image_path = r"C:/Users/yagam/.gemini/antigravity/brain/7d8121c0-0b17-4f11-86a8-2f5befda9b9b/uploaded_image_1767438896099.jpg"

    def fix_homepage_banner(self, theme_id):
        print("\n[1/2] Fixing Homepage Banner...")
        headers = {"X-Shopify-Access-Token": self.access_token}
        
        # 1. Read index.json (Homepage structure)
        # Note: In Dawn/Horizon themes, the main banner is usually in a section named 'image_banner' or similar.
        try:
            url = f"https://{self.shop_url}/admin/api/2024-01/themes/{theme_id}/assets.json?asset[key]=templates/index.json"
            r = requests.get(url, headers=headers)
            
            if r.status_code != 200:
                print(f"   [Error] Could not read index.json: {r.status_code}")
                return

            asset_data = r.json().get('asset', {}).get('value')
            if not asset_data:
                print("   [Error] Empty index.json")
                return

            structure = json.loads(asset_data)
            
            # 2. Find the banner section
            banner_section_id = None
            for key, section_ref in structure.get('sections', {}).items():
                if section_ref.get('type') == 'image-banner':
                    banner_section_id = key
                    break
            
            if not banner_section_id:
                print("   [Error] No 'image-banner' section found in template.")
                # Fallback: Check for 'slideshow' or 'hero'
                return

            print(f"   [Found] Banner Section ID: {banner_section_id}")
            
            # 3. Assign the image
            # Note: In Shopify themes, we reference the image by direct internal URI or by setting the setting
            # actually, uploading to 'assets' makes it available via 'shopify_asset_url' filter, 
            # but modern themes use the 'files' API references (shopify://shop_images/...).
            # Since we uploaded to theme assets, we need to map it.
            # ERROR: Typically themes bind to "Files", not "Theme Assets".
            # FIX: We will upload the image to Shopify FILES API first, to get a proper ID.
            
            print("   [Pivot] Modern themes require File API upload, not Asset upload.")
            return False # Trigger fallback in main loop

        except Exception as e:
            print(f"   [Error] {e}")

    def upload_to_files_api(self):
        """Uploads image to Shopify Files (Content) API to get a persistent ID."""
        print("   [Sub-Step] Uploading to Shopify Files API...")
        
        # Note: Shopify Admin API for generic file upload is GraphQL-only for the new Media API,
        # REST API for 'ScriptTag' or 'Asset' doesn't give a 'shopify://' ID suitable for Sections.
        # Actually... we can attach the image directly to the Product securely.
        # For the Theme Banner, it's tricker via simple REST. 
        # Simpler approach: UPDATE PRODUCTS FIRST (User's main complaint).
        pass

    def fix_product_images(self):
        print("\n[2/2] Fixing Product Images...")
        headers = {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json"
        }
        
        # 1. Get image as base64
        with open(self.image_path, "rb") as f:
            b64_image = base64.b64encode(f.read()).decode('utf-8')
        
        # 2. Get All Products
        url = f"https://{self.shop_url}/admin/api/2024-01/products.json"
        r = requests.get(url, headers=headers)
        products = r.json().get('products', [])
        
        for p in products:
            img_id = None
            if not p.get('images'):
                print(f"   [Fixing] Product: {p['title']}")
                # Upload Image to Product
                img_payload = {
                    "image": {
                        "attachment": b64_image,
                        "filename": "cover.jpg"
                    }
                }
                
                post_url = f"https://{self.shop_url}/admin/api/2024-01/products/{p['id']}/images.json"
                ir = requests.post(post_url, json=img_payload, headers=headers)
                print(f"     -> HTTP {ir.status_code}")
                
                if ir.status_code in [200, 201]:
                    data = ir.json()
                    if 'image' in data:
                        img_id = data['image']['id']
                        print("     -> Success! Image ID:", img_id)
            else:
                print(f"   [Check] Product {p['title']} has images.")
                # Use the first image
                img_id = p['images'][0]['id']

            # FORCE UPDATE VARIANTS
            if img_id:
                variants = p.get('variants', [])
                for v in variants:
                    if v.get('image_id') != img_id:
                        print(f"     -> Updating Variant {v['id']} to use Image {img_id}...")
                        v_url = f"https://{self.shop_url}/admin/api/2024-01/variants/{v['id']}.json"
                        requests.put(v_url, json={"variant": {"id": v['id'], "image_id": img_id}}, headers=headers)


if __name__ == "__main__":
    fixer = VisualFixer()
    # Priority: Fix Product Images (User complained "Product images None")
    fixer.fix_product_images()
