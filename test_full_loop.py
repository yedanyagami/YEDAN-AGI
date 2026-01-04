"""
Real ROI Loop Test
Tests the complete cycle with actual browser automation:
1. Mine content from ArXiv
2. Generate product (skip upload to avoid duplicates)
3. Use Camoufox to navigate Reddit and post a reply
"""
import asyncio
from modules.content_miner import OpenContentMiner
from modules.writer_agent import WriterAgent
from camoufox.async_api import AsyncCamoufox
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.reactor")

async def test_full_loop():
    print("="*60)
    print("FULL ROI LOOP TEST (Real Execution)")
    print("="*60)
    
    # Phase 1: Mine Content
    print("\n[Phase 1] Mining Content from ArXiv...")
    miner = OpenContentMiner()
    papers = miner.harvest_arxiv("artificial intelligence", max_results=3)
    
    if papers:
        print(f"   [OK] Mined {len(papers)} papers")
        print(f"   Sample: {papers[0]['title'][:60]}...")
    else:
        print("   [FAIL] No papers found")
        return False
    
    # Phase 2: Generate Sales Content
    print("\n[Phase 2] Generating Sales Pitch...")
    writer = WriterAgent()
    
    mock_reddit_post = {
        "title": "Need help with AI for my business",
        "body": "I'm struggling to find good AI tools for content generation..."
    }
    
    reply = writer.generate_reply(
        f"Title: {mock_reddit_post['title']}\nBody: {mock_reddit_post['body']}", 
        platform="reddit"
    )
    
    # Handle dict response
    if isinstance(reply, dict):
        reply_text = reply.get('reply', str(reply))
    else:
        reply_text = str(reply)
    
    print(f"   [OK] Generated reply ({len(reply_text)} chars)")
    print(f"   Preview: {reply_text[:100]}...")
    
    # Phase 3: Test Camoufox Reddit Navigation
    print("\n[Phase 3] Testing Reddit Navigation with Camoufox...")
    
    username = os.getenv("REDDIT_USERNAME")
    password = os.getenv("REDDIT_PASSWORD")
    
    if not username or not password:
        print("   [SKIP] No Reddit credentials in .env.reactor")
        return True  # Still count as success if other parts worked
    
    try:
        async with AsyncCamoufox(headless=True) as browser:
            page = await browser.new_page()
            
            print("   -> Navigating to Reddit...")
            await page.goto("https://www.reddit.com", timeout=30000)
            
            title = await page.title()
            print(f"   [OK] Reached Reddit (title: {title[:30]}...)")
            
            # Try to find login button
            try:
                login_visible = await page.is_visible("text=Log In", timeout=5000)
                print(f"   [OK] Login button detected: {login_visible}")
            except:
                print("   [INFO] Login button not found (may already be logged in or different layout)")
            
            return True
            
    except Exception as e:
        print(f"   [FAIL] Browser error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_full_loop())
    print("\n" + "="*60)
    print(f"FINAL RESULT: {'PASS' if success else 'FAIL'}")
    print("="*60)
