"""
Browserless Cloud Browser Integration
Alternative to local Camoufox - runs headless Chrome in the cloud.
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.reactor")

class BrowserlessIntegrator:
    def __init__(self):
        self.token = os.getenv("BROWSERLESS_TOKEN")
        self.base_url = "https://chrome.browserless.io"
        
    def verify_connection(self):
        """Verify Browserless API is accessible."""
        print("\n[Browserless] Verifying Connection...")
        
        if not self.token:
            print("   [Error] No BROWSERLESS_TOKEN found.")
            return False
            
        # Test using the /content endpoint (simple HTML fetch)
        try:
            url = f"{self.base_url}/content?token={self.token}"
            payload = {
                "url": "https://example.com"
            }
            
            r = requests.post(url, json=payload, timeout=30)
            
            if r.status_code == 200:
                # Check if we got HTML back
                if "Example Domain" in r.text:
                    print("   [Success] Browserless connected! Cloud browser ready.")
                    return True
                else:
                    print("   [Partial] Got response but unexpected content.")
                    return True
            elif r.status_code == 401:
                print("   [Error] Invalid API Token.")
            elif r.status_code == 429:
                print("   [Warning] Rate limited. Try again later.")
            else:
                print(f"   [Error] API Status: {r.status_code}")
                
        except Exception as e:
            print(f"   [Error] Connection failed: {e}")
            
        return False
    
    def scrape_page(self, target_url):
        """Scrape a page using Browserless cloud browser."""
        if not self.token:
            return None
            
        url = f"{self.base_url}/content?token={self.token}"
        payload = {"url": target_url}
        
        try:
            r = requests.post(url, json=payload, timeout=60)
            if r.status_code == 200:
                return r.text
        except:
            pass
        return None
    
    def take_screenshot(self, target_url):
        """Take a screenshot using Browserless."""
        if not self.token:
            return None
            
        url = f"{self.base_url}/screenshot?token={self.token}"
        payload = {
            "url": target_url,
            "options": {
                "fullPage": False,
                "type": "png"
            }
        }
        
        try:
            r = requests.post(url, json=payload, timeout=60)
            if r.status_code == 200:
                return r.content  # Binary PNG data
        except:
            pass
        return None

if __name__ == "__main__":
    print("=== Browserless Integration ===")
    integrator = BrowserlessIntegrator()
    
    if integrator.verify_connection():
        print("\n[Test] Scraping HackerNews...")
        html = integrator.scrape_page("https://news.ycombinator.com")
        if html:
            print(f"   Got {len(html)} bytes of HTML")
        else:
            print("   Scrape failed")
