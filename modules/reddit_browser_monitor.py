"""
YEDAN V1600 - Reddit Playwright Monitor (Ultra Perfect)
Increased timeouts, retry logic, better error handling.
"""
import os
import asyncio
import random
import logging
from typing import List
from dotenv import load_dotenv

from modules.pydantic_models import SensorResult

logger = logging.getLogger('reddit_playwright')

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("[Playwright] Not installed")

class RedditBrowserMonitor:
    """
    V1600 Ultra Perfect Reddit Monitor
    - 60s page timeouts
    - 3x retry on login failure
    - Smart fallback to simulation
    """
    def __init__(self, hive, guard, config):
        self.hive = hive
        self.guard = guard
        self.config = config.get("reddit", {})
        self.footer = config.get("disclosure_footer", {}).get("reddit", "")
        self.simulation_mode = not PLAYWRIGHT_AVAILABLE
        
        load_dotenv(dotenv_path=".env.reactor")
        
        self.username = os.getenv("REDDIT_USERNAME")
        self.password = os.getenv("REDDIT_PASSWORD")
        
        self.subreddits = self.config.get("subreddits", ["shopify", "ecommerce"])
        self.keywords = self.config.get("keywords", ["help", "store", "sales"])
        
        logger.info(f"[Reddit V1600] Initialized for u/{self.username}")
        logger.info(f"[Reddit V1600] Monitoring: r/{', r/'.join(self.subreddits)}")
    
    def start_stream(self):
        if self.simulation_mode:
            logger.info("🔮 [Reddit V1600] SIMULATION MODE")
            asyncio.run(self._run_simulation_loop())
        else:
            logger.info("🌐 [Reddit V1600] LIVE MODE (Playwright)")
            asyncio.run(self._run_playwright_loop())
    
    async def _run_playwright_loop(self):
        logger.info("🧬 [V1600] Playwright Reddit Loop Activated")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            page.set_default_timeout(60000)  # 60 seconds
            
            # Login with retry
            login_success = False
            for attempt in range(3):
                try:
                    logger.info(f"🔐 Login attempt {attempt + 1}/3...")
                    await page.goto("https://www.reddit.com/login", wait_until="networkidle")
                    await asyncio.sleep(2)
                    
                    await page.fill('input[name="username"]', self.username)
                    await page.fill('input[name="password"]', self.password)
                    await page.click('button[type="submit"]')
                    
                    await page.wait_for_url("**/reddit.com/**", timeout=30000)
                    login_success = True
                    logger.info(f"✅ Logged in as u/{self.username}")
                    break
                    
                except Exception as e:
                    logger.warning(f"Login attempt {attempt + 1} failed: {str(e)[:50]}")
                    await asyncio.sleep(5)
            
            if not login_success:
                logger.error("❌ All login attempts failed. Switching to simulation.")
                await browser.close()
                await self._run_simulation_loop()
                return
            
            # Main monitoring loop
            while True:
                for subreddit in self.subreddits:
                    try:
                        await page.goto(f"https://www.reddit.com/r/{subreddit}/new", wait_until="networkidle")
                        await asyncio.sleep(2)
                        
                        posts = await page.query_selector_all('[data-testid="post-container"] h3')
                        found_count = 0
                        
                        for post_elem in posts[:10]:
                            title = await post_elem.inner_text()
                            
                            if any(kw.lower() in title.lower() for kw in self.keywords):
                                found_count += 1
                                logger.info(f"📡 [FOUND] r/{subreddit}: {title[:50]}...")
                                
                                # Generate response via HiveMind
                                if self.hive:
                                    action = self.hive.create_hive_action(
                                        target_thread=f"reddit_{subreddit}_{found_count}",
                                        user_input=f"Title: {title}",
                                        platform="reddit"
                                    )
                                    agent = "ALPHA" if action.panic_score >= 7 else "BETA" if action.panic_score >= 4 else "GAMMA"
                                    logger.info(f"   🧠 {agent}: {action.generated_reply[:60]}...")
                                    self.guard.record_action("reddit_user", is_promo=True)
                        
                        if found_count == 0:
                            logger.info(f"🔍 r/{subreddit}: No keyword matches in top 10 posts")
                                
                    except Exception as e:
                        logger.error(f"Error on r/{subreddit}: {str(e)[:50]}")
                
                delay = random.uniform(180, 300)  # 3-5 min
                logger.info(f"💤 Next scan in {delay/60:.1f}min...")
                await asyncio.sleep(delay)
    
    async def _run_simulation_loop(self):
        logger.info("🧬 [V1600] Simulation Loop Active")
        
        mock_posts = [
            SensorResult(
                thread_id=f"sim_{random.randint(1000,9999)}",
                title="Help! My Shopify store sales dropped to zero!",
                body_markdown="Theme update broke something.",
                author="PanickedMerchant",
                panic_score=8,
                keywords_matched=["help", "shopify"]
            ),
            SensorResult(
                thread_id=f"sim_{random.randint(1000,9999)}",
                title="Best Facebook ads strategy 2026?",
                body_markdown="$100/day, 0.8x ROAS.",
                author="FrustratedMarketer",
                panic_score=6,
                keywords_matched=["ads"]
            ),
        ]
        
        while True:
            delay = random.uniform(15, 30)
            logger.info(f"🔮 [Sim] Waiting {delay:.1f}s...")
            await asyncio.sleep(delay)
            
            post = random.choice(mock_posts)
            
            if not self.guard.is_safe_to_post(post.author, post.title):
                continue
            
            logger.info(f"📡 {post.title[:40]}... | Panic: {post.panic_score}/10")
            
            if self.hive:
                action = self.hive.create_hive_action(
                    target_thread=post.thread_id,
                    user_input=f"Title: {post.title}\nBody: {post.body_markdown}",
                    platform="reddit"
                )
                
                agent = "ALPHA" if action.panic_score >= 7 else "BETA" if action.panic_score >= 4 else "GAMMA"
                logger.info(f"🧠 Agent: {agent} | Reply: {action.generated_reply[:60]}...")
                
                self.guard.record_action(post.author, is_promo=True)
