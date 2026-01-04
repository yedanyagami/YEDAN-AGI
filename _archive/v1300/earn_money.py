#!/usr/bin/env python3
"""
YEDAN AGI: EARN MONEY - EXECUTE SALES OUTREACH
Uses existing Chrome session to send sales DMs.
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# === SALES TARGETS ===
REDDIT_TARGET = {
    "url": "https://www.reddit.com/message/compose/?to=potentially_billions",
    "subject": "Re: Inventory System Recs and ERP Failures",
    "message": """Hey. Regarding the ERP failures you mentioned:

Most ERPs fail because of polling latency (API rate limits). I built a middleware binary that uses Webhooks to lock inventory immediately when orders come in, acting as a safety buffer.

If you are building custom solutions for high-growth clients, this tool can handle the sync protection logic for you.

Agency License: https://yesinyagami.gumroad.com/l/jwblmj"""
}

def connect_to_chrome():
    """Connect to existing Chrome session."""
    print("[*] Connecting to existing Chrome...")
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=options)
    print(f"[+] Connected! Current page: {driver.title}")
    return driver

def send_reddit_dm(driver):
    """Navigate to Reddit and attempt to send DM."""
    print("\n[*] EARNING MONEY: Sending Reddit DM...")
    driver.get(REDDIT_TARGET["url"])
    time.sleep(3)
    
    # Check if we're on compose page
    if "compose" in driver.current_url:
        print("[+] Reddit compose page loaded!")
        try:
            # Try to find and fill subject
            subject = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "subject"))
            )
            subject.clear()
            subject.send_keys(REDDIT_TARGET["subject"])
            print("[+] Subject filled!")
            
            # Try to find and fill message
            message = driver.find_element(By.NAME, "text")
            message.clear()
            message.send_keys(REDDIT_TARGET["message"])
            print("[+] Message filled!")
            
            print("\n[!] READY TO SEND. Review the message in browser.")
            print("[?] Type 'SEND' to click send button, or press ENTER to skip:")
            choice = input("> ").strip().upper()
            
            if choice == "SEND":
                send_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Send')]")
                send_btn.click()
                print("[+] MESSAGE SENT! Potential revenue incoming!")
                return True
            else:
                print("[*] Skipped sending.")
                return False
                
        except Exception as e:
            print(f"[!] Error filling form: {e}")
            print("[*] You may need to log in to Reddit first.")
            return False
    else:
        print("[!] Not on compose page. May need Reddit login.")
        print(f"[*] Current URL: {driver.current_url}")
        return False

def main():
    print("=" * 60)
    print("YEDAN AGI: EARN MONEY - SALES EXECUTION")
    print("=" * 60)
    
    try:
        driver = connect_to_chrome()
        
        # Execute Reddit DM
        success = send_reddit_dm(driver)
        
        if success:
            print("\n" + "=" * 60)
            print("POTENTIAL REVENUE: $299 (Agency License)")
            print("=" * 60)
        else:
            print("\n[*] Manual action may be required.")
            print("[*] Copy this message and paste it manually:")
            print("-" * 50)
            print(f"To: u/potentially_billions")
            print(f"Subject: {REDDIT_TARGET['subject']}")
            print(REDDIT_TARGET['message'])
            print("-" * 50)
            
    except Exception as e:
        print(f"[!] Error: {e}")
        print("[*] Make sure Chrome is running with --remote-debugging-port=9222")

if __name__ == "__main__":
    main()
