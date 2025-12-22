"""
YEDAN AGI - Telegram Auto-Fix & Broadcast
Dynamically finds the correct Chat ID and sends a message.
"""
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Start with configured ID, but be ready to update
CURRENT_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def get_updates_and_find_chat():
    """Polls for updates to find the user's Chat ID"""
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    try:
        # Offset 0 to get all unconfirmed messages
        resp = requests.get(url, params={"offset": 0, "timeout": 10})
        data = resp.json()
        
        if data.get("ok"):
            results = data.get("result", [])
            if not results:
                print("[-] No incoming messages found. Please send /start to the bot.")
                return None
            
            # Get the most recent message's chat ID
            last_update = results[-1]
            chat_id = last_update.get("message", {}).get("chat", {}).get("id")
            user = last_update.get("message", {}).get("from", {}).get("username", "Unknown")
            
            print(f"[+] Found User: {user} | Chat ID: {chat_id}")
            return str(chat_id)
        else:
            print(f"[!] Error getting updates: {data}")
            return None
    except Exception as e:
        print(f"[!] Connection error: {e}")
        return None

def send_message(chat_id, text):
    """Sends the message"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    resp = requests.post(url, json=payload)
    if resp.status_code == 200:
        print("[OK] Message sent successfully!")
        return True
    else:
        print(f"[X] Send failed: {resp.text}")
        return False

def update_env_file(new_id):
    """Updates the .env file with the new ID"""
    lines = []
    with open(".env", "r") as f:
        lines = f.readlines()
    
    with open(".env", "w") as f:
        for line in lines:
            if line.startswith("TELEGRAM_CHAT_ID="):
                f.write(f"TELEGRAM_CHAT_ID={new_id}\n")
            else:
                f.write(line)
    print(f"[SAVE] Updated .env with Chat ID: {new_id}")

def main():
    print("="*50)
    print("YEDAN TELEGRAM AUTO-FIX")
    print("="*50)
    
    # 1. Define Message (Will receive from Gemini Ultra via input arg or default)
    import sys
    msg = sys.argv[1] if len(sys.argv) > 1 else "<b>YEDAN SYSTEM: ONLINE</b>"
    
    # 2. Try to find new ID
    print("[*] Checking for new Chat ID...")
    found_id = get_updates_and_find_chat()
    
    target_id = found_id if found_id else CURRENT_CHAT_ID
    
    if found_id and found_id != CURRENT_CHAT_ID:
        update_env_file(found_id)
    
    # 3. Attempt Send
    if target_id:
        print(f"[*] Attempting send to: {target_id}")
        if send_message(target_id, msg):
             return
    
    # 4. If failed or no ID, POLL for 30 seconds
    if not found_id:
        print("\n[!] Loop: Waiting for you to message the bot...")
        for i in range(12): # 60 seconds
            print(f"[{i*5}s] Polling...", end="\r")
            found_id = get_updates_and_find_chat()
            if found_id:
                target_id = found_id
                update_env_file(target_id)
                send_message(target_id, msg)
                return
            time.sleep(5)
        
        print("\n[X] Timeout. Could not find Chat ID. Did you send /start?")

if __name__ == "__main__":
    main()
