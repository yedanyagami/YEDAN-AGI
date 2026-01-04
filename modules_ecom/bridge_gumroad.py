#!/usr/bin/env python3
"""
YEDAN AGI - Gumroad Bridge (Action Arm)
Provides physical intervention capability: modify prices and copy on Gumroad.

SAFETY: DRY_RUN mode is ON by default. Set DRY_RUN=False to enable real changes.
"""

import os
import requests
from dotenv import load_dotenv
from typing import Optional, Dict, Any

load_dotenv()

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
GUMROAD_ACCESS_TOKEN = os.getenv("GUMROAD_ACCESS_TOKEN")
BASE_URL = "https://api.gumroad.com/v2"

# SAFETY FLAG: Set to False to enable REAL changes
DRY_RUN = os.getenv("GUMROAD_DRY_RUN", "true").lower() == "true"


def _check_config() -> bool:
    """Verify Gumroad configuration is present."""
    if not GUMROAD_ACCESS_TOKEN:
        print("⚠️ [Gumroad] Missing configuration!")
        print("   Set GUMROAD_ACCESS_TOKEN in .env")
        return False
    return True


def get_products() -> Optional[list]:
    """
    Get all products from Gumroad account.
    Useful for discovering product IDs.
    """
    if not _check_config():
        return None
        
    url = f"{BASE_URL}/products"
    params = {"access_token": GUMROAD_ACCESS_TOKEN}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                products = data.get("products", [])
                print(f"📦 [Gumroad] Found {len(products)} products")
                for p in products:
                    print(f"   - {p.get('id')}: {p.get('name')} (${p.get('price', 0)/100:.2f})")
                return products
        
        print(f"❌ [Gumroad] Get Error: {response.text}")
        return None
        
    except requests.RequestException as e:
        print(f"❌ [Gumroad] Request Failed: {e}")
        return None


def get_product_details(product_id: str) -> Optional[Dict[str, Any]]:
    """
    Get details for a specific product.
    """
    if not _check_config():
        return None
        
    url = f"{BASE_URL}/products/{product_id}"
    params = {"access_token": GUMROAD_ACCESS_TOKEN}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data.get("product")
        
        print(f"❌ [Gumroad] Get Error: {response.text}")
        return None
        
    except requests.RequestException as e:
        print(f"❌ [Gumroad] Request Failed: {e}")
        return None


def update_product(
    product_id: str, 
    new_price: Optional[float] = None, 
    new_description: Optional[str] = None,
    new_name: Optional[str] = None,
    custom_permalink: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Update Gumroad product (price, description, name, permalink).
    
    Args:
        product_id: Gumroad product ID
        new_price: New price in dollars (e.g., 9.99) - converted to cents
        new_description: New product description (Markdown supported)
        new_name: New product name
        custom_permalink: Custom URL slug
    
    Returns:
        Updated product data or None on failure
    """
    print(f"🎨 [Gumroad] Product Update Request: {product_id}")
    
    if not _check_config():
        return None
    
    # Build payload
    data = {
        "access_token": GUMROAD_ACCESS_TOKEN
    }
    
    if new_price is not None:
        # Safety check: price must be reasonable
        if new_price < 0 or new_price > 10000:
            print(f"❌ [Gumroad] Invalid price: ${new_price} (must be $0-$10000)")
            return None
            
        # Gumroad uses cents ($1 = 100 cents)
        price_in_cents = int(float(new_price) * 100)
        data["price"] = price_in_cents
        print(f"   → Price: ${new_price} ({price_in_cents} cents)")
    
    if new_description is not None:
        if len(new_description) > 50000:
            print("❌ [Gumroad] Description too long (max 50000 chars)")
            return None
        data["description"] = new_description
        print(f"   → Description: {len(new_description)} chars")
    
    if new_name is not None:
        data["name"] = new_name
        print(f"   → Name: {new_name}")
    
    if custom_permalink is not None:
        data["custom_permalink"] = custom_permalink
        print(f"   → Permalink: {custom_permalink}")
    
    # DRY RUN CHECK
    if DRY_RUN:
        print("   🔒 [DRY RUN] No changes made. Set GUMROAD_DRY_RUN=false to enable.")
        return {"dry_run": True, "would_update": data}
    
    # Send PUT request
    url = f"{BASE_URL}/products/{product_id}"
    
    try:
        response = requests.put(url, data=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ [Gumroad] Product updated successfully")
                return result.get("product")
            else:
                print(f"⚠️ [Gumroad] Update Failed: {result.get('message')}")
                return None
        else:
            print(f"⚠️ [Gumroad] Update Failed [{response.status_code}]: {response.text}")
            return None
            
    except requests.RequestException as e:
        print(f"❌ [Gumroad] Request Failed: {e}")
        return None


def update_price(product_id: str, new_price: float) -> bool:
    """
    Convenience wrapper for price-only updates.
    """
    result = update_product(product_id, new_price=new_price)
    return result is not None


def update_description(product_id: str, new_description: str) -> bool:
    """
    Convenience wrapper for description-only updates.
    """
    result = update_product(product_id, new_description=new_description)
    return result is not None


# ═══════════════════════════════════════════════════════════════
# CLI TESTING
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("YEDAN AGI - Gumroad Bridge Test")
    print(f"DRY_RUN: {DRY_RUN}")
    print("=" * 60)
    
    if not _check_config():
        print("\nPlease configure .env file first:")
        print("  GUMROAD_ACCESS_TOKEN=xxxxxxxx")
    else:
        print("\n✅ Configuration OK. Fetching products...")
        get_products()
