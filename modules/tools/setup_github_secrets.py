"""
YEDAN Cloud Integrator - Set GitHub Secrets for Autonomous Operation
"""
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import requests
import base64
import json
from nacl import public, encoding
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env.reactor")

# GitHub API setup
GITHUB_TOKEN = os.getenv('GH_PAT')
REPO = 'yedanyagami/YEDAN-AGI'
if not GITHUB_TOKEN:
    print("❌ Error: GH_PAT not found in environment variables")
    sys.exit(1)
headers = {'Authorization': f'token {GITHUB_TOKEN}', 'Accept': 'application/vnd.github.v3+json'}

def encrypt_secret(public_key: str, secret_value: str) -> str:
    """Encrypt a secret using GitHub's public key."""
    public_key_bytes = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key_bytes)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def set_secret(name: str, value: str, key_id: str, public_key: str) -> bool:
    """Set a GitHub Actions secret."""
    encrypted_value = encrypt_secret(public_key, value)
    url = f'https://api.github.com/repos/{REPO}/actions/secrets/{name}'
    data = {
        'encrypted_value': encrypted_value,
        'key_id': key_id
    }
    r = requests.put(url, headers=headers, json=data)
    if r.status_code in [201, 204]:
        print(f"  ✅ {name}: Set successfully")
        return True
    else:
        print(f"  ❌ {name}: Failed ({r.status_code})")
        return False

def main():
    print("=" * 60)
    print("YEDAN Cloud Integrator - GitHub Secrets Setup")
    print("=" * 60)
    
    # 1. Get public key
    r = requests.get(f'https://api.github.com/repos/{REPO}/actions/secrets/public-key', headers=headers)
    if r.status_code != 200:
        print(f"❌ Failed to get public key: {r.status_code}")
        print(r.text)
        return
    
    key_data = r.json()
    key_id = key_data['key_id']
    public_key = key_data['key']
    print(f"✅ Connected to GitHub: {REPO}")
    print(f"   Key ID: {key_id[:10]}...")
    
    # 2. Secrets to set (from .env.reactor)
    secrets = {
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID'),
        'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY'),
        'GROK_API_KEY': os.getenv('GROK_API_KEY'),
        'SHOPIFY_ADMIN_TOKEN': os.getenv('SHOPIFY_ADMIN_TOKEN'),
        'SHOPIFY_STORE_URL': os.getenv('SHOPIFY_STORE_URL'),
        'INFURA_API_KEY': os.getenv('INFURA_API_KEY'),
        'BROWSERLESS_TOKEN': os.getenv('BROWSERLESS_TOKEN'),
    }
    
    print(f"\n📤 Setting {len(secrets)} secrets...")
    
    success = 0
    for name, value in secrets.items():
        if value:
            if set_secret(name, value, key_id, public_key):
                success += 1
        else:
            print(f"  ⚠️ {name}: Skipped (no value)")
    
    print(f"\n✅ {success}/{len(secrets)} secrets configured")
    print("=" * 60)

if __name__ == "__main__":
    main()
