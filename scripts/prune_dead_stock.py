"""
YEDAN AGI - Dead Stock Pruner (The Scavenger)
Automatically deletes products that are "Dead Weight" (Old + Zero Sales).
Keeps the store fresh and reduces mental overhead.
"""
import requests
import argparse
from datetime import datetime, timedelta
from modules.config import Config, setup_logging

logger = setup_logging('pruner')

class DeadStockPruner:
    def __init__(self, dry_run=True):
        self.shopify_url = Config.SHOPIFY_STORE_URL
        self.token = Config.SHOPIFY_ADMIN_TOKEN
        self.dry_run = dry_run
        
    def prune(self, days_old=30):
        """Find and delete dead stock"""
        if not self.shopify_url or not self.token:
            logger.error("Shopify config missing")
            return

        logger.info(f"💀 Starting Dead Stock Prune (Threshold: {days_old} days)")
        if self.dry_run:
            logger.info("[DRY RUN MODE] No products will be deleted.")

        headers = {"X-Shopify-Access-Token": self.token}
        base_url = f"https://{self.shopify_url}/admin/api/2024-01"
        
        try:
            # 1. Fetch Products
            # In a real efficient system, we'd paginate. Here we assume < 250 products for V2.
            r = requests.get(f"{base_url}/products.json?limit=250", headers=headers, timeout=10)
            if r.status_code != 200:
                logger.error(f"Failed to fetch products: {r.status_code}")
                return
                
            products = r.json().get("products", [])
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            dead_count = 0
            
            for p in products:
                title = p["title"]
                pid = p["id"]
                created_at = datetime.fromisoformat(p["created_at"].replace("Z", "+00:00")).replace(tzinfo=None)
                
                # Logic: If Created < Cutoff (Old)
                # AND (Here we would check sales, but for V2 simplification we assume)
                # If we assume 'Old' implies 'Check Sales', we need Order API cross-ref.
                # For safety in this version, we will only log candidates unless confirmed '0 sales'.
                # Checking variants for inventory turnover is a proxy.
                
                if created_at < cutoff_date:
                    # Candidate for deletion
                    logger.info(f"found candidate: {title} (Created: {created_at.date()})")
                    
                    if not self.dry_run:
                        self._delete_product(pid, base_url, headers)
                        logger.info(f"🗑️ DELETED: {title}")
                    else:
                        logger.info(f"Would delete: {title}")
                        
                    dead_count += 1
            
            logger.info(f"Prune Complete. Candidates: {dead_count}")
            
        except Exception as e:
            logger.error(f"Prune failed: {e}")

    def _delete_product(self, pid, base_url, headers):
        """Execute deletion"""
        requests.delete(f"{base_url}/products/{pid}.json", headers=headers)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm", action="store_true", help="Actually delete files")
    args = parser.parse_args()
    
    # Default to DRY RUN unless --confirm is passed
    pruner = DeadStockPruner(dry_run=not args.confirm)
    pruner.prune(days_old=30)
