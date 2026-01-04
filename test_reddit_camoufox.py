"""
Test Reddit Login with Camoufox (Anti-Detect Browser)
"""
import asyncio
import os
from dotenv import load_dotenv
from camoufox.async_api import AsyncCamoufox

load_dotenv(dotenv_path=".env.reactor")

async def test_reddit_camoufox():
    print("="*60)
    print("Camoufox Anti-Detect Test")
    print("="*60)
    
    username = os.getenv("REDDIT_USERNAME")
    password = os.getenv("REDDIT_PASSWORD")
    
    print(f"Username: {username}")
    
    # Camoufox automatically handles stealth
    try:
        print("Launching Camoufox...")
        async with AsyncCamoufox(headless=True) as browser:
            page = await browser.new_page()
            
            print("Navigating to Reddit login...")
            await page.goto("https://www.reddit.com/login", wait_until="domcontentloaded")
            await asyncio.sleep(5)
            
            print(f"URL: {page.url}")
            
            # Check inputs again
            print("Checking page content...")
            inputs = await page.query_selector_all('input')
            print(f"Total inputs found: {len(inputs)}")
            
            username_field = await page.query_selector('input[name="username"]')
            password_field = await page.query_selector('input[name="password"]')
            
            if username_field:
                print("[SUCCESS] Username field FOUND!")
            else:
                print("[FAILED] Username field NOT found")
                
                # Debug: Print title
                title = await page.title()
                print(f"Page Title: {title}")
                
            if username_field and password_field:
                print("Filling login form...")
                await username_field.fill(username)
                await asyncio.sleep(1)
                await password_field.fill(password)
                await asyncio.sleep(1)
                
                print("Submitting...")
                await page.keyboard.press("Enter")
                await asyncio.sleep(10)
                
                # Verification
                print(f"Final URL: {page.url}")
                if "login" not in page.url.lower():
                    print("[SUCCESS] Login Successful (redirected)!")
                else:
                    print("[WARN] Still on login page.")

    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    asyncio.run(test_reddit_camoufox())
