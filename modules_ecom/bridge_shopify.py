#!/usr/bin/env python3
"""
YEDAN AGI - Shopify Bridge (Action Arm)
Provides physical intervention capability: modify prices and copy on Shopify.

SAFETY: DRY_RUN mode is ON by default. Set DRY_RUN=False to enable real changes.
"""

import os
import requests
import json
from dotenv import load_dotenv
from typing import Optional, Dict, Any

load_dotenv()

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL") or os.getenv("SHOPIFY_SHOP_URL")  # e.g., "your-store.myshopify.com"
# Also strip https:// if present
if SHOPIFY_STORE_URL and SHOPIFY_STORE_URL.startswith("https://"):
    SHOPIFY_STORE_URL = SHOPIFY_STORE_URL.replace("https://", "")
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
API_VERSION = "2024-01"

# SAFETY FLAG: Set to False to enable REAL changes
DRY_RUN = os.getenv("SHOPIFY_DRY_RUN", "true").lower() == "true"

BASE_URL = f"https://{SHOPIFY_STORE_URL}/admin/api/{API_VERSION}" if SHOPIFY_STORE_URL else ""


def _get_headers() -> Dict[str, str]:
    """Get authorization headers for Shopify API."""
    return {
        "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN or "",
        "Content-Type": "application/json"
    }


def _check_config() -> bool:
    """Verify Shopify configuration is present."""
    if not SHOPIFY_STORE_URL or not SHOPIFY_ACCESS_TOKEN:
        print("[Shopify] Missing configuration!")
        print("   Set SHOPIFY_STORE_URL and SHOPIFY_ACCESS_TOKEN in .env")
        return False
    return True


def get_product_details(product_id: str) -> Optional[Dict[str, Any]]:
    """
    Get product details from Shopify.
    Required to retrieve variant_id for price updates.
    """
    if not _check_config():
        return None
        
    url = f"{BASE_URL}/products/{product_id}.json"
    
    try:
        response = requests.get(url, headers=_get_headers(), timeout=10)
        
        if response.status_code == 200:
            return response.json().get("product")
        else:
            print(f"[Shopify] Get Error [{response.status_code}]: {response.text}")
            return None
            
    except requests.RequestException as e:
        print(f"[Shopify] Request Failed: {e}")
        return None


def update_price(product_id: str, new_price: float) -> bool:
    """
    Update Shopify product price.
    Note: Price is attached to 'variant', not product directly.
    
    Args:
        product_id: Shopify product ID
        new_price: New price in dollars (e.g., 19.99)
    
    Returns:
        True if successful, False otherwise
    """
    print(f"[Shopify] Price Update Request: Product {product_id} -> ${new_price}")
    
    if not _check_config():
        return False
    
    # Safety check: price must be reasonable
    if new_price <= 0 or new_price > 10000:
        print(f"[Shopify] Invalid price: ${new_price} (must be $0.01-$10000)")
        return False
    
    # 1. Get product to find variant ID
    product = get_product_details(product_id)
    if not product:
        return False
    
    # Assuming single variant (first one)
    if not product.get("variants"):
        print("[Shopify] No variants found for product")
        return False
        
    variant_id = product["variants"][0]["id"]
    old_price = product["variants"][0]["price"]
    
    print(f"   Current price: ${old_price}")
    print(f"   New price: ${new_price}")
    print(f"   Change: {((new_price - float(old_price)) / float(old_price) * 100):.1f}%")
    
    # DRY RUN CHECK
    if DRY_RUN:
        print("   [DRY RUN] No changes made. Set DRY_RUN=false to enable.")
        return True
    
    # 2. Send update request
    url = f"{BASE_URL}/variants/{variant_id}.json"
    payload = {
        "variant": {
            "id": variant_id,
            "price": str(new_price)  # Shopify requires string
        }
    }
    
    try:
        response = requests.put(url, json=payload, headers=_get_headers(), timeout=10)
        
        if response.status_code == 200:
            print(f"[Shopify] Price updated successfully to ${new_price}")
            return True
        else:
            print(f"[Shopify] Update Failed [{response.status_code}]: {response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"[Shopify] Request Failed: {e}")
        return False


def update_description(product_id: str, new_html_content: str) -> bool:
    """
    Update product description (supports HTML).
    Used for SEO optimization and conversion rate improvements.
    
    Args:
        product_id: Shopify product ID
        new_html_content: New HTML description
    
    Returns:
        True if successful, False otherwise
    """
    print(f"[Shopify] Description Update Request: Product {product_id}")
    
    if not _check_config():
        return False
    
    # Safety: limit description length
    if len(new_html_content) > 50000:
        print("[Shopify] Description too long (max 50000 chars)")
        return False
    
    print(f"   Content length: {len(new_html_content)} chars")
    print(f"   Preview: {new_html_content[:100]}...")
    
    # DRY RUN CHECK
    if DRY_RUN:
        print("   [DRY RUN] No changes made. Set DRY_RUN=false to enable.")
        return True
    
    url = f"{BASE_URL}/products/{product_id}.json"
    payload = {
        "product": {
            "id": product_id,
            "body_html": new_html_content
        }
    }
    
    try:
        response = requests.put(url, json=payload, headers=_get_headers(), timeout=10)
        
        if response.status_code == 200:
            print("[Shopify] Description updated successfully")
            return True
        else:
            print(f"[Shopify] Update Failed [{response.status_code}]: {response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"[Shopify] Request Failed: {e}")
        return False


def update_title(product_id: str, new_title: str) -> bool:
    """
    Update product title.
    
    Args:
        product_id: Shopify product ID
        new_title: New product title
    
    Returns:
        True if successful, False otherwise
    """
    print(f"[Shopify] Title Update Request: Product {product_id}")
    
    if not _check_config():
        return False
    
    print(f"   New title: {new_title}")
    
    # DRY RUN CHECK
    if DRY_RUN:
        print("   [DRY RUN] No changes made. Set DRY_RUN=false to enable.")
        return True
    
    url = f"{BASE_URL}/products/{product_id}.json"
    payload = {
        "product": {
            "id": product_id,
            "title": new_title
        }
    }
    
    try:
        response = requests.put(url, json=payload, headers=_get_headers(), timeout=10)
        
        if response.status_code == 200:
            print("[Shopify] Title updated successfully")
            return True
        else:
            print(f"[Shopify] Update Failed [{response.status_code}]: {response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"[Shopify] Request Failed: {e}")
        return False


def create_product(title: str, body_html: str, vendor: str, product_type: str, price: str) -> Optional[str]:
    \"\"\"
    Create a new product on Shopify.
    Returns: Product ID if successful, None otherwise.
    \"\"\"
    print(f"[Shopify] Create Product Request: {title}")
    
    if not _check_config():
        return None
        
    if DRY_RUN:
        print("   [DRY RUN] Would create product. Returning fake ID '123456789'.")
        return "123456789"
        
    url = f"{BASE_URL}/products.json"
    payload = {
        "product": {
            "title": title,
            "body_html": body_html,
            "vendor": vendor,
            "product_type": product_type,
            "status": "active",
            "variants": [
                {
                    "price": price,
                    "requires_shipping": False
                }
            ]
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=_get_headers(), timeout=10)
        
        if response.status_code == 201:
            data = response.json()
            pid = str(data['product']['id'])
            print(f"[Shopify] Product created successfully. ID: {pid}")
            return pid
        else:
            print(f"[Shopify] Creation Failed [{response.status_code}]: {response.text}")
            return None
            
    except requests.RequestException as e:
        print(f"[Shopify] Request Failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
# CLI TESTING
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("YEDAN AGI - Shopify Bridge Test")
    print(f"Store: {SHOPIFY_STORE_URL}")
    print(f"DRY_RUN: {DRY_RUN}")
    print("=" * 60)
    
    if not _check_config():
        print("\nPlease configure .env file first:")
        print("  SHOPIFY_STORE_URL=your-store.myshopify.com")
        print("  SHOPIFY_ACCESS_TOKEN=shpat_xxxxxxxx")
    else:
        print("\n[OK] Configuration OK. Ready for operations.")
        # Example: update_price("1234567890", 19.99)
