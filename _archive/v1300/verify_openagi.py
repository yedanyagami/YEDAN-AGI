"""
Verify OpenAGI Key compatibility
Probes the key against common AGI/LLM endpoints
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

KEY = os.getenv("OPENAGI_API_KEY")
print(f"Testing Key: {KEY[:5]}...{KEY[-4:] if KEY else ''}")

ENDPOINTS = [
    "https://api.openai.com/v1/models",
    "https://api.openagi.ai/v1/models",
    "https://api.lux.ai/v1/models",
    "https://api.groq.com/openai/v1/models"
]

def test_endpoint(url):
    print(f"Probing {url}...")
    try:
        resp = requests.get(url, headers={"Authorization": f"Bearer {KEY}"}, timeout=5)
        print(f"Result: {resp.status_code}")
        if resp.status_code == 200:
            print("SUCCESS! Key works with this endpoint.")
            print(resp.json())
            return True
        else:
            print(f"Failed: {resp.text[:100]}")
    except Exception as e:
        print(f"Error: {e}")
    return False

if __name__ == "__main__":
    if not KEY:
        print("No OPENAGI_API_KEY found")
    else:
        for ep in ENDPOINTS:
            if test_endpoint(ep):
                break
