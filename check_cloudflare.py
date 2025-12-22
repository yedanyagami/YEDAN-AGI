import os
import requests
from dotenv import load_dotenv

load_dotenv()

def mask_key(k):
    if not k: return "None"
    return f"{k[:4]}...{k[-4:]}"

def print_header(title):
    print(f"\n[{title}]")

def check_key_details(name, headers):
    print(f"[*] Testing {name} against /user endpoint...")
    try:
        r = requests.get("https://api.cloudflare.com/client/v4/user", headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            if data['success']:
                user = data['result']
                print(f"  [OK] SUCCESS! Logged in as: {user['email']}")
                print(f"  > ID: {user['id']}")
                return True
        else:
            print(f"  [X] Failed (Status {r.status_code})")
            if r.status_code == 400: print(f"      Msg: {r.json()['errors'][0]['message']}")
    except Exception as e:
        print(f"  [!] Error: {e}")
    return False

if __name__ == "__main__":
    print("[CLOUDFLARE DEEP DIAGNOSTIC]")
    
    # Try all tokens as Bearer
    tokens = {
        "Worker Token": os.getenv("CF_WORKER_TOKEN"),
        "OAuth Token": os.getenv("CF_OAUTH_TOKEN")
    }
    
    valid_auth = False
    
    for name, t in tokens.items():
        if t:
            if check_key_details(name, {"Authorization": f"Bearer {t}"}):
                valid_auth = True
    
    # Try Global Key with potential emails if provided, otherwise skip
    g_key = os.getenv("CF_GLOBAL_KEY")
    if g_key:
        print(f"[*] Testing Global Key with presumed email 'yedanyagami@gmail.com'...")
        headers = {
            "X-Auth-Key": g_key,
            "X-Auth-Email": "yedanyagami@gmail.com"
        }
        if check_key_details("Global Key (gmail)", headers):
            valid_auth = True
            
    if not valid_auth:
        print("\n[CONCLUSION]")
        print("All automated login attempts failed.")
        print("Reason: Invalid keys or missing correct Email for Global Key.")
        print("Action: Manual deployment is required.")
