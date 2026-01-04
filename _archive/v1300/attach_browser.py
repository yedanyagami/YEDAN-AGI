#!/usr/bin/env python3
"""
YEDAN AGI: ATTACH TO EXISTING BROWSER (NO NEW WINDOW)
This script connects to YOUR existing Chrome browser session.
You must start Chrome with remote debugging enabled first.

STEP 1: Close Chrome completely
STEP 2: Reopen Chrome with this command:
    chrome.exe --remote-debugging-port=9222
STEP 3: Run this script
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# === TARGETS ===
TARGETS = {
    "reddit_whale": {
        "url": "https://www.reddit.com/message/compose/?to=potentially_billions",
        "subject": "Re: Inventory System Recs and ERP Failures",
        "message": """Hey. Regarding the ERP failures you mentioned:

Most ERPs fail because of polling latency (API rate limits). I built a middleware binary that uses Webhooks to lock inventory immediately when orders come in, acting as a safety buffer.

If you are building custom solutions for high-growth clients, this tool can handle the sync protection logic for you.

Agency License: https://yesinyagami.gumroad.com/l/jwblmj"""
    },
    "linkedin_cesar": {
        "url": "https://www.linkedin.com/in/cbeltran17",
        "message": """Hey Cesar. Regarding your agency's scale:

Most sync failures happen because of polling latency. I built a middleware binary that uses Webhooks to lock inventory immediately, acting as a buffer for high-volume stores.

If you're looking for backend stability without subscriptions, this tool handles the sync logic.

Agency License: https://payhip.com/b/GJc5k"""
    }
}

def attach_to_existing_browser():
    """Attach to existing Chrome session with remote debugging."""
    print("[*] Connecting to your existing Chrome browser...")
    print("[*] Make sure Chrome was started with: chrome.exe --remote-debugging-port=9222")
    
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    
    try:
        driver = webdriver.Chrome(options=options)
        print("[+] Successfully attached to existing Chrome!")
        return driver
    except Exception as e:
        print(f"[!] Failed to attach: {e}")
        print("\n[!] To fix this:")
        print("    1. Close ALL Chrome windows completely")
        print("    2. Open PowerShell and run:")
        print('       Start-Process "chrome.exe" -ArgumentList "--remote-debugging-port=9222"')
        print("    3. Run this script again")
        return None

def navigate_and_interact(driver):
    """Navigate to targets using existing browser."""
    # LinkedIn
    target = TARGETS["linkedin_cesar"]
    print(f"\n[*] Navigating to LinkedIn: {target['url']}")
    driver.get(target["url"])
    
    time.sleep(3)
    
    print("[*] LinkedIn profile loaded.")
    print("[*] Click 'Message' button manually, then paste this:")
    print("-" * 50)
    print(target["message"])
    print("-" * 50)
    input("[*] Press ENTER when done or to continue...")
    
    # Reddit
    target = TARGETS["reddit_whale"]
    print(f"\n[*] Navigating to Reddit: {target['url']}")
    driver.get(target["url"])
    
    time.sleep(3)
    
    print("[*] Reddit message page loaded.")
    print("[*] Fill in manually:")
    print(f"    Subject: {target['subject']}")
    print("-" * 50)
    print(target["message"])
    print("-" * 50)
    input("[*] Press ENTER when done...")

def main():
    print("=" * 60)
    print("YEDAN AGI: ATTACH TO EXISTING BROWSER")
    print("NO NEW WINDOW - USES YOUR LOGGED-IN SESSION")
    print("=" * 60)
    
    driver = attach_to_existing_browser()
    
    if driver:
        try:
            navigate_and_interact(driver)
            print("\n[+] ALL TARGETS PROCESSED.")
            print("[*] Browser remains open (your session).")
        except Exception as e:
            print(f"[!] Error during interaction: {e}")
    else:
        print("\n[!] Could not attach to browser. See instructions above.")

if __name__ == "__main__":
    main()
