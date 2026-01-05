"""
YEDAN AGI - Google Opal Bridge
Receives AI-generated content from Opal workflows via Synapse webhook
Routes to appropriate action (Shopify product, social post, etc.)
"""
import sys
import io
import os
import json
import requests
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Fix Windows console encoding
# Encoding fix moved to __main__ or handled by caller

load_dotenv(dotenv_path=".env.reactor")

SYNAPSE_URL = "https://synapse.yagami8095.workers.dev"


class OpalBridge:
    """Bridge between Google Opal and YEDAN system"""
    
    def __init__(self):
        self.shopify_store = os.getenv("SHOPIFY_STORE_URL")
        self.shopify_token = os.getenv("SHOPIFY_ADMIN_TOKEN")
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat = os.getenv("TELEGRAM_CHAT_ID")
        
    def fetch_pending_content(self) -> list:
        """Fetch pending Opal content from Synapse"""
        try:
            r = requests.get(f"{SYNAPSE_URL}/opal/content", timeout=10)
            if r.status_code == 200:
                return r.json().get("contents", [])
        except Exception as e:
            print(f"[OpalBridge] Error fetching content: {e}")
        return []
    
    def process_content(self, content: Dict[str, Any]) -> bool:
        """Route content to appropriate handler"""
        content_type = content.get("type", "unknown")
        payload = content.get("content", {})
        
        print(f"[OpalBridge] Processing: {content_type}")
        
        if content_type == "product_description":
            return self._handle_product(payload)
        elif content_type == "social_post":
            return self._handle_social_post(payload)
        elif content_type == "blog_article":
            return self._handle_blog(payload)
        elif content_type == "price_update":
            return self._handle_price_update(payload)
        else:
            print(f"[OpalBridge] Unknown content type: {content_type}")
            return False
    
    def _handle_product(self, payload: dict) -> bool:
        """Create Shopify product from Opal content"""
        title = payload.get("title", "AI Generated Product")
        description = payload.get("description", "")
        price = payload.get("price", "9.99")
        
        product_data = {
            "product": {
                "title": title,
                "body_html": description,
                "vendor": "YEDAN AGI",
                "product_type": "Digital",
                "variants": [{"price": str(price), "inventory_policy": "continue"}]
            }
        }
        
        try:
            r = requests.post(
                f"https://{self.shopify_store}/admin/api/2024-01/products.json",
                headers={
                    "X-Shopify-Access-Token": self.shopify_token,
                    "Content-Type": "application/json"
                },
                json=product_data,
                timeout=30
            )
            if r.status_code == 201:
                product_id = r.json()["product"]["id"]
                print(f"[OpalBridge] Product created: {product_id}")
                self._notify(f"Product Created: {title}")
                return True
            else:
                print(f"[OpalBridge] Shopify error: {r.status_code}")
                return False
        except Exception as e:
            print(f"[OpalBridge] Error creating product: {e}")
            return False
    
    def _handle_social_post(self, payload: dict) -> bool:
        """Queue social post for processing"""
        platform = payload.get("platform", "reddit")
        content = payload.get("content", "")
        
        # Store in Synapse for later processing
        try:
            r = requests.post(
                f"{SYNAPSE_URL}/task/submit",
                json={
                    "type": "social_post",
                    "data": {
                        "platform": platform,
                        "content": content,
                        "scheduled_at": datetime.now().isoformat()
                    }
                },
                timeout=10
            )
            if r.status_code == 200:
                task_id = r.json().get("task_id")
                print(f"[OpalBridge] Social post queued: {task_id}")
                return True
        except Exception as e:
            print(f"[OpalBridge] Error queuing social post: {e}")
        return False
    
    def _handle_blog(self, payload: dict) -> bool:
        """Store blog article for later use"""
        title = payload.get("title", "Untitled")
        content = payload.get("content", "")
        
        # Save locally
        filename = f"data/blog_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n{content}")
        
        print(f"[OpalBridge] Blog saved: {filename}")
        return True
    
    def _handle_price_update(self, payload: dict) -> bool:
        """Update Shopify product price"""
        product_id = payload.get("product_id")
        new_price = payload.get("price")
        
        if not product_id or not new_price:
            return False
        
        # Queue for Shopify action
        try:
            r = requests.post(
                f"{SYNAPSE_URL}/shopify/action",
                json={
                    "action": "update_price",
                    "payload": {"product_id": product_id, "price": new_price}
                },
                timeout=10
            )
            return r.status_code == 200
        except:
            return False
    
    def _notify(self, message: str):
        """Send Telegram notification"""
        if self.telegram_token and self.telegram_chat:
            try:
                requests.post(
                    f"https://api.telegram.org/bot{self.telegram_token}/sendMessage",
                    json={
                        "chat_id": self.telegram_chat,
                        "text": f"[OpalBridge] {message}"
                    },
                    timeout=5
                )
            except:
                pass
    
    def run_cycle(self):
        """Process all pending Opal content"""
        print("=" * 60)
        print("[OpalBridge] Starting content processing cycle")
        print("=" * 60)
        
        contents = self.fetch_pending_content()
        print(f"[OpalBridge] Found {len(contents)} pending items")
        
        processed = 0
        for content in contents:
            if self.process_content(content):
                processed += 1
        
        print(f"[OpalBridge] Processed {processed}/{len(contents)} items")
        return processed


# Manual content sender for testing
def send_test_content(content_type: str, content: dict):
    """Send test content to Synapse webhook"""
    r = requests.post(
        f"{SYNAPSE_URL}/opal/webhook",
        json={
            "type": content_type,
            "content": content,
            "metadata": {"source": "manual_test"}
        },
        timeout=10
    )
    print(f"Response: {r.status_code} - {r.json()}")
    return r.json()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Send test content
        print("[OpalBridge] Sending test content...")
        send_test_content("product_description", {
            "title": "Test Product from Opal",
            "description": "<p>This is a test product created via the Opal Bridge.</p>",
            "price": "4.99"
        })
    else:
        # Run normal cycle
        bridge = OpalBridge()
        bridge.run_cycle()
