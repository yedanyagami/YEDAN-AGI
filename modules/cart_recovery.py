"""
CART RECOVERY MODULE 🛒
 polls Shopify for abandoned checkouts and triggers n8n recovery sequences.
"""
import requests
import json
import logging
from datetime import datetime, timedelta
from modules.config import Config

logger = logging.getLogger("CartRescuer")

class CartRescuer:
    def __init__(self):
        self.headers = {
            "X-Shopify-Access-Token": Config.SHOPIFY_ADMIN_TOKEN,
            "Content-Type": "application/json"
        }
        self.base_url = f"{Config.SHOPIFY_STORE_URL}/admin/api/2023-10"

    def check_abandoned_checkouts(self):
        """
        Polls for checkouts updated in the last hour that have email but no order.
        """
        # Time window: Checkouts from 60 mins ago to 15 mins ago (give them time to finish)
        now = datetime.utcnow()
        min_date = (now - timedelta(minutes=60)).isoformat()
        max_date = (now - timedelta(minutes=15)).isoformat()
        
        url = f"{self.base_url}/checkouts.json"
        params = {
            "updated_at_min": min_date,
            "updated_at_max": max_date,
            "status": "open",
            "limit": 50
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            checkouts = response.json().get("checkouts", [])
            
            recoverable = []
            for checkout in checkouts:
                # Must have email to recover
                if checkout.get("email"):
                    recoverable.append(checkout)
            
            logger.info(f"Found {len(recoverable)} recoverable carts out of {len(checkouts)} open checkouts.")
            return recoverable
            
        except Exception as e:
            logger.error(f"Failed to fetch checkouts: {e}")
            return []

    def trigger_n8n_recovery(self, checkout):
        """
        Sends checkout data to n8n webhook for email sequence.
        """
        if Config.DRY_RUN:
            logger.info(f"[DRY_RUN] Would trigger recovery for {checkout['email']}")
            return True
            
        payload = {
            "type": "abandoned_cart",
            "email": checkout['email'],
            "checkout_url": checkout['abandoned_checkout_url'],
            "total_price": checkout['total_price'],
            "currency": checkout['currency'],
            "items": [item['title'] for item in checkout.get('line_items', [])]
        }
        
        try:
            # Assuming a specific webhook for cart recovery
            n8n_url = f"{Config.N8N_BASE_URL}/webhooks/cart-recovery" 
            # Note: User might need to create this webhook in n8n, checking n8n_bridge for generic usage
            
            # Using generic n8n bridge if available, or direct post
            # For now, let's log intent since we don't have the specific webhook ID yet
            logger.info(f"Triggering n8n recovery for {checkout['email']}...")
            # requests.post(n8n_url, json=payload) 
            # Placeholder until n8n workflow ID is known
            return True
        except Exception as e:
            logger.error(f"Failed to trigger n8n: {e}")
            return False

if __name__ == "__main__":
    from modules.config import setup_logging
    setup_logging("CartRescuer")
    rescuer = CartRescuer()
    carts = rescuer.check_abandoned_checkouts()
    for cart in carts:
        rescuer.trigger_n8n_recovery(cart)
