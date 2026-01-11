"""
真實測試: Reddit Playwright 登入
"""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env.reactor")

async def test_reddit_login():
    from playwright.async_api import async_playwright
    
    username = os.getenv("REDDIT_USERNAME")
    password = os.getenv("REDDIT_PASSWORD")
    
    print(f"Reddit Username: {username}")
    print(f"Password length: {len(password) if password else 0}")
    
    async with async_playwright() as p:
        print("Launching browser...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        page.set_default_timeout(30000)
        
        try:
            print("Navigating to Reddit login...")
            await page.goto("https://www.reddit.com/login", wait_until="domcontentloaded")
            print(f"URL: {page.url}")
            
            await asyncio.sleep(2)
            
            # Check for login form
            username_field = await page.query_selector('input[name="username"]')
            password_field = await page.query_selector('input[name="password"]')
            
            print(f"Username field: {'FOUND' if username_field else 'NOT FOUND'}")
            print(f"Password field: {'FOUND' if password_field else 'NOT FOUND'}")
            
            if username_field and password_field:
                print("Filling login form...")
                await username_field.fill(username)
                await password_field.fill(password)
                
                submit_btn = await page.query_selector('button[type="submit"]')
                if submit_btn:
                    print("Clicking submit...")
                    await submit_btn.click()
                    await asyncio.sleep(5)
                    
                    print(f"After login URL: {page.url}")
                    
                    if "login" not in page.url.lower():
                        print("LOGIN SUCCESS!")
                    else:
                        print("LOGIN FAILED - still on login page")
                        
        except Exception as e:
            print(f"ERROR: {e}")
        finally:
            await browser.close()
            print("Browser closed")

if __name__ == "__main__":
    asyncio.run(test_reddit_login())
