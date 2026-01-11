"""
Simple Camoufox Smoke Test
Just verify the browser can launch and navigate to a simple page.
"""
import asyncio
from camoufox.async_api import AsyncCamoufox

async def smoke_test():
    print("[Test] Launching Camoufox...")
    try:
        async with AsyncCamoufox(headless=True) as browser:
            print("[Test] Browser launched successfully")
            page = await browser.new_page()
            print("[Test] Navigating to example.com...")
            await page.goto("https://example.com", timeout=30000)
            title = await page.title()
            print(f"[Result] SUCCESS - Page title: {title}")
            return True
    except Exception as e:
        print(f"[Result] FAILED - {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(smoke_test())
    print(f"\n[Final] Camoufox Basic Test: {'PASS' if result else 'FAIL'}")
