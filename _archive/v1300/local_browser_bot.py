#!/usr/bin/env python3
"""
YEDAN AGI: LOCAL BROWSER AUTOMATION (NO LIMITS)
This script controls YOUR browser directly. No cloud API. No rate limits.
You will SEE everything happen on your screen.
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

def launch_browser():
    """Launch visible Chrome browser."""
    print("[*] Launching Chrome browser (you will see this)...")
    options = Options()
    options.add_argument("--start-maximized")
    # options.add_argument("--headless")  # COMMENTED OUT - we want visible
    driver = webdriver.Chrome(options=options)
    return driver

def send_reddit_dm(driver):
    """Navigate to Reddit and fill DM form."""
    target = TARGETS["reddit_whale"]
    print(f"[*] Navigating to Reddit: {target['url']}")
    driver.get(target["url"])
    
    time.sleep(3)  # Wait for page load
    
    # Check if logged in
    if "login" in driver.current_url.lower():
        print("[!] Reddit login required. Please log in manually.")
        input("[*] Press ENTER after you've logged in...")
        driver.get(target["url"])
        time.sleep(3)
    
    try:
        # Find subject field
        subject_field = driver.find_element(By.NAME, "subject")
        subject_field.clear()
        subject_field.send_keys(target["subject"])
        print("[+] Subject filled.")
        
        # Find message field
        message_field = driver.find_element(By.NAME, "text")
        message_field.clear()
        message_field.send_keys(target["message"])
        print("[+] Message filled.")
        
        print("\n[!] FORM READY. Review and click SEND manually, or press ENTER to auto-send.")
        user_input = input("[?] Type 'SEND' to auto-send, or press ENTER to skip: ")
        
        if user_input.upper() == "SEND":
            send_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Send')]")
            send_button.click()
            print("[+] MESSAGE SENT!")
            time.sleep(2)
        else:
            print("[*] Skipped sending.")
            
    except Exception as e:
        print(f"[!] Error: {e}")
        print("[*] You may need to fill the form manually.")

def visit_linkedin(driver):
    """Navigate to LinkedIn profile."""
    target = TARGETS["linkedin_cesar"]
    print(f"\n[*] Navigating to LinkedIn: {target['url']}")
    driver.get(target["url"])
    
    time.sleep(3)
    
    print("[*] LinkedIn profile loaded.")
    print("[*] Click 'Message' button manually, then paste this:")
    print("-" * 50)
    print(target["message"])
    print("-" * 50)
    input("[*] Press ENTER when done...")

def main():
    print("=" * 60)
    print("YEDAN AGI: LOCAL BROWSER AUTOMATION")
    print("NO LIMITS. FULL CONTROL. YOU WATCH.")
    print("=" * 60)
    
    driver = launch_browser()
    
    try:
        # Reddit DM
        print("\n--- STEP 1: REDDIT DM ---")
        send_reddit_dm(driver)
        
        # LinkedIn
        print("\n--- STEP 2: LINKEDIN ---")
        visit_linkedin(driver)
        
        print("\n[+] ALL TARGETS PROCESSED.")
        input("[*] Press ENTER to close browser...")
        
    finally:
        driver.quit()
        print("[*] Browser closed.")

if __name__ == "__main__":
    main()
