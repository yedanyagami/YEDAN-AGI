"""
Telegram Handshake Script
Run this, then message your bot to auto-configure the Chat ID.
"""
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.reactor")

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def get_chat_id():
    print(f"Connecting to Bot ({TOKEN[:5]}...)...")
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    
    print("\n[Waiting] Please send a message (e.g., /start) to your Telegram Bot NOW...")
    
    for i in range(30): # Wait 30 seconds
        try:
            r = requests.get(url, timeout=10)
            data = r.json()
            results = data.get('result', [])
            
            if results:
                # Get the last message
                last_update = results[-1]
                chat_id = last_update['message']['chat']['id']
                user = last_update['message']['from'].get('username', 'Unknown')
                
                print(f"\n[Success] Message received from @{user}!")
                print(f"[Config] Chat ID detected: {chat_id}")
                return str(chat_id)
                
        except Exception as e:
            print(f".", end="", flush=True)
            
        time.sleep(1)
        print(".", end="", flush=True)
        
    print("\n[Timeout] No message received. Please try again.")
    return None

if __name__ == "__main__":
    if not TOKEN:
        print("Error: No TELEGRAM_BOT_TOKEN in .env.reactor")
        exit()
        
    chat_id = get_chat_id()
    
    if chat_id:
        # Append to .env.reactor
        with open(".env.reactor", "a", encoding="utf-8") as f:
            f.write(f"\nTELEGRAM_CHAT_ID={chat_id}\n")
        print("[Done] Saved TELEGRAM_CHAT_ID to .env.reactor")
