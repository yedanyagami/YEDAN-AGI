"""
Nano Cover Uploader
Uploads specific AI-generated covers to their respective products.
"""
import requests
import os
import base64
import json
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.reactor")

class CoverUploader:
    def __init__(self):
        self.shop_url = os.getenv("SHOPIFY_STORE_URL", "").replace("https://", "")
        self.access_token = os.getenv("SHOPIFY_ACCESS_TOKEN") or os.getenv("SHOPIFY_ADMIN_TOKEN")
        self.headers = {"X-Shopify-Access-Token": self.access_token, "Content-Type": "application/json"}
        
        # Map Product Keywords to Generated Images
        self.image_map = {
            "Insider": r"C:/Users/yagam/.gemini/antigravity/brain/7d8121c0-0b17-4f11-86a8-2f5befda9b9b/cover_ai_insider_1767439997995.png",
            "Dropshipping": r"C:/Users/yagam/.gemini/antigravity/brain/7d8121c0-0b17-4f11-86a8-2f5befda9b9b/cover_dropshipping_1767440016734.png",
            "Digest": r"C:/Users/yagam/.gemini/antigravity/brain/7d8121c0-0b17-4f11-86a8-2f5befda9b9b/cover_research_digest_1767440032878.png"
        }

    def run(self):
        print("Fetching products...")
        url = f"https://{self.shop_url}/admin/api/2024-01/products.json"
        try:
            r = requests.get(url, headers=self.headers)
            products = r.json().get('products', [])
            
            for p in products:
                title = p['title']
                matched_path = None
                
                # Find matching image
                for key, path in self.image_map.items():
                    if key in title:
                        matched_path = path
                        break
                
                if matched_path:
                    print(f"\n[Updating] {title} -> {os.path.basename(matched_path)}")
                    self.upload_image(p, matched_path)
                else:
                    print(f"\n[Skip] No specific cover for: {title}")
                    
        except Exception as e:
            print(f"Error: {e}")

    def upload_image(self, product, image_path):
        try:
            with open(image_path, "rb") as f:
                b64_image = base64.b64encode(f.read()).decode('utf-8')
                
            payload = {
                "image": {
                    "attachment": b64_image,
                    "filename": "cover_v2.png"
                }
            }
            
            # Post new image
            url = f"https://{self.shop_url}/admin/api/2024-01/products/{product['id']}/images.json"
            r = requests.post(url, json=payload, headers=self.headers)
            
            if r.status_code in [200, 201]:
                data = r.json()
                new_img_id = data['image']['id']
                print(f"   Success! ID: {new_img_id}")
                
                # Update ALL variants to use this new image
                for v in product['variants']:
                     v_url = f"https://{self.shop_url}/admin/api/2024-01/variants/{v['id']}.json"
                     requests.put(v_url, json={"variant": {"id": v['id'], "image_id": new_img_id}}, headers=self.headers)
                print("   Variants updated.")
                
            else:
                print(f"   Failed: {r.status_code} {r.text}")
                
        except Exception as e:
            print(f"   Upload Error: {e}")

if __name__ == "__main__":
    uploader = CoverUploader()
    uploader.run()
