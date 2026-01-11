"""
測試 playwright-stealth 能否繞過 Reddit 反偵測
"""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env.reactor")

async def test_reddit_stealth():
    from playwright.async_api import async_playwright
    from playwright_stealth import Stealth
    
    username = os.getenv("REDDIT_USERNAME")
    password = os.getenv("REDDIT_PASSWORD")
    
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password)}")
    
    async with async_playwright() as p:
        print("Launching browser with STEALTH mode...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        
        # Apply stealth using context manager
        stealth = Stealth()
        await stealth.apply_stealth_async(page)
        print("Stealth mode applied!")
        
        page.set_default_timeout(60000)
        
        try:
            print("Navigating to Reddit login...")
            await page.goto("https://www.reddit.com/login", wait_until="networkidle")
            await asyncio.sleep(3)
            
            print(f"URL: {page.url}")
            
            # Check for input fields
            inputs = await page.query_selector_all('input')
            print(f"Total inputs found: {len(inputs)}")
            
            # Look for username field
            username_field = await page.query_selector('input[name="username"]')
            password_field = await page.query_selector('input[name="password"]')
            
            if username_field:
                print("✅ Username field: FOUND")
            else:
                print("❌ Username field: NOT FOUND")
                # Try alternative selectors
                alt_username = await page.query_selector('input[id="loginUsername"]')
                if alt_username:
                    print("✅ Alt username field: FOUND")
                    username_field = alt_username
                    
            if password_field:
                print("✅ Password field: FOUND")
            else:
                print("❌ Password field: NOT FOUND")
                alt_password = await page.query_selector('input[id="loginPassword"]')
                if alt_password:
                    print("✅ Alt password field: FOUND")
                    password_field = alt_password
            
            if username_field and password_field:
                print("Filling login form...")
                await username_field.fill(username)
                await asyncio.sleep(0.5)
                await password_field.fill(password)
                await asyncio.sleep(0.5)
                
                submit_btn = await page.query_selector('button[type="submit"]')
                if submit_btn:
                    print("Clicking submit...")
                    await submit_btn.click()
                    await asyncio.sleep(5)
                    
                    print(f"After login URL: {page.url}")
                    
                    if "login" not in page.url.lower():
                        print("🎉 LOGIN SUCCESS!")
                    else:
                        print("❌ LOGIN FAILED - still on login page")
            else:
                print("Cannot proceed - form fields not found")
                
        except Exception as e:
            print(f"ERROR: {e}")
        finally:
            await browser.close()
            print("Browser closed")

if __name__ == "__main__":
    asyncio.run(test_reddit_stealth())
