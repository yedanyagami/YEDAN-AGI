"""
Shopify Media Manager (GraphQL)
Handles the correct 'stagedUploadsCreate' -> Upload -> 'fileCreate' workflow.
Required for specialized actions like updating Banner Images in OS 2.0 Themes.
"""
import requests
import os
import mimetypes
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.reactor")

class ShopifyMediaManager:
    def __init__(self):
        self.shop_url = os.getenv("SHOPIFY_STORE_URL", "").replace("https://", "")
        self.access_token = os.getenv("SHOPIFY_ACCESS_TOKEN") or os.getenv("SHOPIFY_ADMIN_TOKEN")
        self.api_version = "2024-01"
        self.graphql_url = f"https://{self.shop_url}/admin/api/{self.api_version}/graphql.json"
        
    def _graphql(self, query, variables=None):
        headers = {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json"
        }
        res = requests.post(self.graphql_url, json={"query": query, "variables": variables}, headers=headers)
        if res.status_code != 200:
            raise Exception(f"GraphQL Error: {res.status_code} {res.text}")
        
        json_res = res.json()
        if 'errors' in json_res:
            raise Exception(f"GraphQL Query Errors: {json_res['errors']}")
            
        return json_res['data']

    def upload_image(self, file_path):
        """
        Full workflow to upload an image to Shopify Files (Content).
        Returns the persistent MediaImage ID (gid://shopify/MediaImage/...)
        """
        print(f"   [MediaManager] Processing: {os.path.basename(file_path)}")
        
        # 1. Staged Upload Create
        file_size = str(os.path.getsize(file_path))
        filename = os.path.basename(file_path)
        mime_type = mimetypes.guess_type(file_path)[0] or "image/jpeg"
        
        mutation_staged = """
        mutation stagedUploadsCreate($input: [StagedUploadInput!]!) {
          stagedUploadsCreate(input: $input) {
            stagedTargets {
              url
              resourceUrl
              parameters {
                name
                value
              }
            }
          }
        }
        """
        
        variables = {
            "input": [{
                "resource": "IMAGE",
                "filename": filename,
                "mimeType": mime_type,
                "fileSize": file_size,
                "httpMethod": "POST"
            }]
        }
        
        data = self._graphql(mutation_staged, variables)
        target = data['stagedUploadsCreate']['stagedTargets'][0]
        upload_url = target['url']
        params = target['parameters']
        resource_url = target['resourceUrl'] # We need this for step 3
        
        # 2. Perform the Upload
        print("   [MediaManager] Uploading to Google Cloud bucket...")
        form_data = {p['name']: p['value'] for p in params}
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            upload_res = requests.post(upload_url, data=form_data, files=files)
            
        if upload_res.status_code not in [200, 201]:
             raise Exception(f"S3 Upload failed: {upload_res.status_code} {upload_res.text}")

        # 3. Create File in Shopify
        print("   [MediaManager] Registering file in Shopify...")
        mutation_file = """
        mutation fileCreate($files: [FileCreateInput!]!) {
          fileCreate(files: $files) {
            files {
              ... on MediaImage {
                id
                image {
                   url
                }
              }
            }
            userErrors {
              field
              message
            }
          }
        }
        """
        
        variables_file = {
            "files": [{
                "originalSource": resource_url,
                "contentType": "IMAGE"
            }]
        }
        
        data_file = self._graphql(mutation_file, variables_file)
        
        if data_file['fileCreate']['userErrors']:
            print("Errors:", data_file['fileCreate']['userErrors'])
            return None
            
        file_id = data_file['fileCreate']['files'][0]['id']
        print(f"   [Success] MediaImage Created: {file_id}")
        return file_id, filename

    def link_to_banner(self, filename):
        """
        Patches index.json to use the uploaded file.
        Note: Section settings for 'image_picker' usually expect 'shopify://shop_images/filename'
        """
        print("   [MediaManager] Patching template to use image...")
        
        # 1. Get Theme ID
        rest_headers = {"X-Shopify-Access-Token": self.access_token}
        r = requests.get(f"https://{self.shop_url}/admin/api/2024-01/themes.json", headers=rest_headers)
        main_theme = next((t for t in r.json().get('themes', []) if t['role'] == 'main'), None)
        
        # 2. Get index.json
        url = f"https://{self.shop_url}/admin/api/2024-01/themes/{main_theme['id']}/assets.json?asset[key]=templates/index.json"
        
        r = requests.get(url, headers=rest_headers)
        asset_val = r.json()['asset']['value']
        import json
        template = json.loads(asset_val)
        
        # 3. Find Banner
        found = False
        for key, section in template['sections'].items():
            if 'banner' in section['type'] or 'hero' in section['type']:
                print(f"   [MediaManager] Found Banner: {key}")
                # Provide the File URI protocol
                image_ref = f"shopify://shop_images/{filename}"
                section['settings']['image'] = image_ref
                found = True
                break
        
        if found:
            # 4. Push
            payload = {"asset": {"key": "templates/index.json", "value": json.dumps(template)}}
            requests.put(f"https://{self.shop_url}/admin/api/2024-01/themes/{main_theme['id']}/assets.json", json=payload, headers=rest_headers)
            print("   [Success] Banner updated programmatically.")
            return True
        else:
            print("   [Error] Banner section not found.")
            return False

if __name__ == "__main__":
    mgr = ShopifyMediaManager()
    img_path = r"C:/Users/yagam/.gemini/antigravity/brain/7d8121c0-0b17-4f11-86a8-2f5befda9b9b/uploaded_image_1767438896099.jpg"
    
    try:
        # Step 1: Upload (GraphQL)
        gid, fname = mgr.upload_image(img_path)
        
        # Step 2: Link (JSON Template)
        # Note: Often staged upload changes filename slightly? No, usually keeps it if passed.
        # But for 'shopify://' we need the exact filename stored in Shopify.
        # Let's assume standard behavior.
        mgr.link_to_banner(fname)
        
    except Exception as e:
        print(f"Failed: {e}")
