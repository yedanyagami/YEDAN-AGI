import requests
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def test_telegram():
    print("[TELEGRAM DIAGNOSTIC]")
    print(f"Bot Token: {BOT_TOKEN[:15]}...{BOT_TOKEN[-5:]}" if BOT_TOKEN else "NOT SET")
    print(f"Chat ID: {CHAT_ID}")
    
    if not BOT_TOKEN or not CHAT_ID:
        print("[X] Missing credentials in .env")
        return
    
    # Test 1: getMe (verify bot token)
    print("\n[Test 1] Verifying Bot Token (getMe)...")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get("ok"):
            bot = data["result"]
            print(f"  [OK] Bot is valid: @{bot['username']} (ID: {bot['id']})")
        else:
            print(f"  [X] Bot token INVALID: {data.get('description')}")
            return
    except Exception as e:
        print(f"  [!] Network error: {e}")
        return
    
    # Test 2: sendMessage (verify chat_id and permissions)
    print("\n[Test 2] Testing sendMessage to Chat ID...")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": "[Diagnostic] Telegram connection test successful!"
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        data = r.json()
        if data.get("ok"):
            print(f"  [OK] Message sent successfully!")
        else:
            err_code = data.get("error_code")
            err_desc = data.get("description")
            print(f"  [X] Failed ({err_code}): {err_desc}")
            
            if err_code == 403:
                print("\n  [!] 403 Forbidden means:")
                print("      1. The bot was blocked by the user, OR")
                print("      2. The bot never received a /start from this chat, OR")
                print("      3. The chat_id is wrong.")
                print(f"\n  [FIX] Please open Telegram, find bot @{bot['username']}, and send /start")
            elif err_code == 400:
                print("  [!] 400 Bad Request: Chat ID is likely invalid.")
    except Exception as e:
        print(f"  [!] Network error: {e}")

if __name__ == "__main__":
    test_telegram()
