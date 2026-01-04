#!/usr/bin/env python3
"""
YEDAN AGI: TRUE ATTACH TO EXISTING CHROME
Uses Chrome DevTools Protocol to connect to already-running Chrome.
NO NEW WINDOWS. NO NEW TABS. Just takes control of what's already open.

REQUIREMENT: Your Chrome must already be running with --remote-debugging-port=9222
"""
import subprocess
import time
import json
import requests

def check_chrome_debug_port():
    """Check if Chrome is running with debug port open."""
    try:
        response = requests.get("http://127.0.0.1:9222/json", timeout=2)
        if response.status_code == 200:
            tabs = response.json()
            print(f"[+] Found {len(tabs)} open tab(s) in Chrome:")
            for i, tab in enumerate(tabs):
                print(f"    [{i}] {tab.get('title', 'No title')} - {tab.get('url', 'No URL')}")
            return tabs
    except:
        pass
    return None

def restart_chrome_with_debug():
    """Kill Chrome and restart with debug port."""
    print("[*] Chrome debug port not available.")
    print("[*] Restarting Chrome with remote debugging...")
    
    # Kill existing Chrome
    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], 
                   capture_output=True, shell=True)
    time.sleep(2)
    
    # Start Chrome with debug port and user's profile
    chrome_cmd = [
        "chrome.exe",
        "--remote-debugging-port=9222",
        "--restore-last-session"  # Restore previous tabs
    ]
    subprocess.Popen(chrome_cmd, shell=True)
    time.sleep(3)
    
    return check_chrome_debug_port()

def main():
    print("=" * 60)
    print("YEDAN AGI: TRUE ATTACH TO EXISTING CHROME")
    print("NO NEW WINDOWS - USES YOUR CURRENT SESSION")
    print("=" * 60)
    
    # Check if Chrome debug port is available
    tabs = check_chrome_debug_port()
    
    if not tabs:
        print("\n[!] Chrome is not running with debug port.")
        print("[*] To enable, close Chrome and restart with:")
        print('    chrome.exe --remote-debugging-port=9222 --restore-last-session')
        print("\n[?] Do you want me to restart Chrome with debug mode? (y/n)")
        choice = input("> ").strip().lower()
        if choice == 'y':
            tabs = restart_chrome_with_debug()
    
    if tabs:
        print("\n[+] Chrome is ready for control!")
        print("[*] You can now use Selenium to attach to these tabs.")
        print("[*] Your login sessions are preserved.")
    else:
        print("\n[!] Could not connect to Chrome.")

if __name__ == "__main__":
    main()
