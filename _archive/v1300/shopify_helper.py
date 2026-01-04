"""
YEDAN AGI: SHOPIFY TOKEN HELPER (EDGE EDITION)
Automates navigation to the difficult-to-find API key settings using Microsoft Edge.
"""
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
import time

TARGET_URL = "https://yedanyagami-io.myshopify.com/admin/settings/apps/development"

def launch_browser():
    print("[*] Launching Microsoft Edge (Visible Mode)...")
    options = EdgeOptions()
    options.add_argument("--start-maximized")
    # Make sure we don't start headless
    options.add_experimental_option("detach", True) # Keep browser open after script ends
    try:
        driver = webdriver.Edge(options=options)
        return driver
    except Exception as e:
        print(f"Error launching Edge: {e}")
        print("Ensure 'msedgedriver' is in your PATH or installed via 'pip install selenium'.")
        raise e

def main():
    driver = launch_browser()
    
    print("\n" + "="*60)
    print("   STEP 1: LOGIN (EDGE)")
    print("   Please log in to Shopify in the opened Edge window.")
    print("="*60)
    
    driver.get("https://yedanyagami-io.myshopify.com/admin")
    
    input("\n[*] Press ENTER *after* you have successfully logged in...")
    
    print("\n" + "="*60)
    print("   STEP 2: NAVIGATING TO API SETTINGS")
    print("="*60)
    
    driver.get(TARGET_URL)
    
    print("\n[*] Navigated to Developer Apps.")
    print("[!] INSTRUCTIONS:")
    print("1. Click 'Create an app' (top right). Name it 'YEDAN'.")
    print("2. Click 'Configure Admin API scopes'.")
    print("3. Search & Check: 'Products', 'Orders', 'Customers' (Read/Write).")
    print("4. Click 'Save' -> 'Install app' (top right).")
    print("5. REVEAL the 'Admin API access token' (starts with shpat_).")
    
    print("\n" + "="*60)
    token = input("[?] PASTE TOKEN HERE: ").strip()
    
    if token.startswith("shpat_"):
        with open(".env", "a") as f:
            f.write(f"\nSHOPIFY_ACCESS_TOKEN={token}\n")
        print("✅ Token saved to .env!")
    else:
        print("❌ That doesn't look like a valid token (should start with shpat_).")

if __name__ == "__main__":
    main()
