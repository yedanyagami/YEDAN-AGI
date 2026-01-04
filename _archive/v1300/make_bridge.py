"""
# FILE: make_bridge.py
# OPERATION: MIDDLEWARE BRIDGE
# OBJECTIVE: Route traffic to Make.com when direct APIs fail.
"""
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

MAKE_WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")

def trigger_make_scenario(action: str, payload: dict) -> bool:
    """
    Triggers a Make.com scenario via Webhook.
    """
    if not MAKE_WEBHOOK_URL:
        print("[FAIL] Missing MAKE_WEBHOOK_URL in .env")
        return False
    
    data = {
        "action": action,
        "payload": payload,
        "source": "YEDAN_AGI_V5",
        "key_chain": os.getenv("MAKE_KEY_CHAIN")
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('MAKE_KEY_CHAIN')}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"[BRIDGE] sending '{action}' to Make.com...")
        response = requests.post(MAKE_WEBHOOK_URL, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"[SUCCESS] Make.com Accepted: {response.text}")
            return True
        else:
            print(f"[FAIL] Make.com Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Connection Failed: {e}")
        return False

if __name__ == "__main__":
    # Test Payload
    trigger_make_scenario("test_ping", {"message": "Hello from YEDAN V5.1"})
