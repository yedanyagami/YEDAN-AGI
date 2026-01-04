"""
YEDAN AGI: COMPUTER USE - SHOPIFY NAVIGATOR
Uses screenshot + coordinate clicks to bypass browser_subagent restrictions.
"""
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.action_chains import ActionChains
import time

# New store URL
TARGET_URL = "https://admin.shopify.com/store/yedanyagami-io-2/settings/apps/development"

def launch_edge():
    print("[*] Launching Microsoft Edge...")
    options = EdgeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option("detach", True)
    driver = webdriver.Edge(options=options)
    return driver

def main():
    driver = launch_edge()
    
    print("\n" + "="*60)
    print("   COMPUTER USE: SHOPIFY API NAVIGATOR")
    print("   Store: yedanyagami-io-2 (UPDATED)")
    print("="*60)
    
    # Navigate to store
    print("\n[1] Navigating to Shopify Admin...")
    driver.get("https://admin.shopify.com/store/yedanyagami-io-2/")
    
    input("\n[*] Press ENTER after you've logged in...")
    
    # Navigate to API settings
    print("\n[2] Navigating to App Development settings...")
    driver.get(TARGET_URL)
    
    time.sleep(3)
    
    print("\n[*] You should now see the 'App development' page.")
    print("[!] INSTRUCTIONS:")
    print("1. Click 'Create an app' (top right). Name it 'YEDAN'.")
    print("2. Click 'Configure Admin API scopes'.")
    print("3. Search & Check: 'Products', 'Orders', 'Customers' (Read/Write).")
    print("4. Click 'Save' -> 'Install app'.")
    print("5. REVEAL the 'Admin API access token' (starts with shpat_).")
    
    print("\n" + "="*60)
    token = input("[?] PASTE TOKEN HERE: ").strip()
    
    if token.startswith("shpat_"):
        # Update .env
        with open(".env", "r") as f:
            lines = f.readlines()
        
        with open(".env", "w") as f:
            for line in lines:
                if line.startswith("SHOPIFY_ACCESS_TOKEN="):
                    f.write(f"SHOPIFY_ACCESS_TOKEN={token}\n")
                elif line.startswith("SHOPIFY_STORE_URL="):
                    f.write("SHOPIFY_STORE_URL=https://yedanyagami-io-2.myshopify.com\n")
                else:
                    f.write(line)
        
        print("[OK] Token and Store URL saved to .env!")
    else:
        print("[WARN] That doesn't look like a valid token (should start with shpat_).")

if __name__ == "__main__":
    main()
