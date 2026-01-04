"""
YEDAN AGI: BROWSER ATTACHMENT HELPER
Connects to your EXISTING Chrome window via Remote Debugging Port 9222.
Requirement: Chrome started with `chrome.exe --remote-debugging-port=9222`
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

TARGET_URL = "https://yedanyagami-io.myshopify.com/admin/settings/apps/development"

def attach_to_browser():
    print("[*] Attempting to attach to existing Chrome (Port 9222)...")
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=options)
        print("✅ Attached successfully!")
        return driver
    except Exception as e:
        print("❌ Could not attach.")
        print(f"   Error: {e}")
        return None

def main():
    print("\n" + "="*60)
    print("   YEDAN: LOCAL BROWSER ASSISTANT")
    print("   Objective: Navigate you to Shopify API Settings")
    print("="*60)
    
    driver = attach_to_browser()
    
    if not driver:
        print("\n[!] Please RESTART your Chrome with this command:")
        print('    chrome.exe --remote-debugging-port=9222')
        print("\nThen run this script again.")
        return

    # Once attached, navigate
    print("\n[*] Navigating current tab to Shopify Admin...")
    driver.get("https://yedanyagami-io.myshopify.com/admin")
    
    # Wait for manual login
    print("\n[?] Are you logged in? (Check your browser)")
    input("    Press ENTER once you see the Shopify Admin dashboard...")
    
    print("\n[*] Moving to API Settings...")
    driver.get(TARGET_URL)
    
    print("\n" + "="*60)
    print("   INSTRUCTIONS (As before):")
    print("   1. Create App -> 'YEDAN'")
    print("   2. Config Admin API Scopes -> Check Products/Orders/Customers")
    print("   3. Install App -> Reveal Admin Token (shpat_)")
    print("="*60)
    
    token = input("[?] PASTE TOKEN HERE: ").strip()
    
    if token.startswith("shpat_"):
        with open(".env", "a") as f:
            f.write(f"\nSHOPIFY_ACCESS_TOKEN={token}\n")
        print("✅ Token saved to .env!")
    else:
        print("⚠️ Invalid format (should start with shpat_). Not saved.")

if __name__ == "__main__":
    main()
