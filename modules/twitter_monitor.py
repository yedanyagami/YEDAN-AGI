"""
YEDAN V1600 - Twitter Playwright Monitor (Ultra Perfect)
Increased timeouts, retry logic, anti-detection measures.
"""
import os
import asyncio
import random
import logging
from dotenv import load_dotenv

from modules.pydantic_models import SensorResult

logger = logging.getLogger('twitter_playwright')

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

class TwitterMonitor:
    """
    V1600 Ultra Perfect Twitter Monitor
    - 60s page timeouts
    - 3x retry on login failure  
    - Anti-detection measures
    """
    def __init__(self, reasoner, guard, config):
        self.reasoner = reasoner
        self.guard = guard
        self.config = config.get("twitter", {})
        self.footer = config.get("disclosure_footer", {}).get("twitter", "")
        self.hive = None
        
        load_dotenv(dotenv_path=".env.reactor")
        
        self.username = os.getenv("TWITTER_USERNAME", "")
        self.password = os.getenv("TWITTER_PASSWORD", "")
        self.simulation_mode = not PLAYWRIGHT_AVAILABLE or not self.password
        
        self.keywords = self.config.get("keywords", ["shopify", "ecommerce"])
        self.hashtags = self.config.get("hashtags", ["#shopify"])
        
        # For reactor compatibility
        self.client = None
        logger.info("Twitter Client initialized")
    
    def start_stream(self):
        if self.simulation_mode:
            logger.info("🔮 [Twitter V1600] SIMULATION MODE")
            asyncio.run(self._run_simulation_loop())
        else:
            logger.info("🌐 [Twitter V1600] LIVE MODE (Playwright)")
            asyncio.run(self._run_playwright_loop())
    
    async def _run_playwright_loop(self):
        logger.info("🧬 [V1600] Playwright Twitter Loop Activated")
        
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
            page.set_default_timeout(60000)
            
            # Login with retry
            login_success = False
            for attempt in range(3):
                try:
                    logger.info(f"🔐 Twitter login attempt {attempt + 1}/3...")
                    await page.goto("https://twitter.com/i/flow/login", wait_until="networkidle")
                    await asyncio.sleep(3)
                    
                    # Username step
                    await page.fill('input[autocomplete="username"]', self.username)
                    await page.keyboard.press("Enter")
                    await asyncio.sleep(2)
                    
                    # Password step
                    await page.fill('input[name="password"]', self.password)
                    await page.keyboard.press("Enter")
                    await asyncio.sleep(5)
                    
                    # Check if logged in
                    if "home" in page.url.lower() or "twitter.com" in page.url:
                        login_success = True
                        logger.info(f"✅ Logged in as @{self.username}")
                        break
                        
                except Exception as e:
                    logger.warning(f"Login attempt {attempt + 1} failed: {str(e)[:50]}")
                    await asyncio.sleep(5)
            
            if not login_success:
                logger.error("❌ All Twitter login attempts failed. Switching to simulation.")
                await browser.close()
                await self._run_simulation_loop()
                return
            
            # Main monitoring loop
            while True:
                for keyword in self.keywords[:3]:
                    try:
                        search_url = f"https://twitter.com/search?q={keyword}&src=typed_query&f=live"
                        await page.goto(search_url, wait_until="networkidle")
                        await asyncio.sleep(3)
                        
                        tweets = await page.query_selector_all('[data-testid="tweet"]')
                        found_count = 0
                        
                        for tweet_elem in tweets[:5]:
                            text_elem = await tweet_elem.query_selector('[data-testid="tweetText"]')
                            if text_elem:
                                text = await text_elem.inner_text()
                                found_count += 1
                                logger.info(f"📡 [FOUND] {text[:50]}...")
                                
                                if self.hive:
                                    action = self.hive.create_hive_action(
                                        target_thread=f"twitter_{found_count}",
                                        user_input=f"Tweet: {text}",
                                        platform="twitter"
                                    )
                                    agent = "ALPHA" if action.panic_score >= 7 else "BETA" if action.panic_score >= 4 else "GAMMA"
                                    logger.info(f"   🧠 {agent}: {action.generated_reply[:50]}...")
                                    self.guard.record_action("twitter_user", is_promo=True)
                        
                        if found_count == 0:
                            logger.info(f"🔍 '{keyword}': No tweets found")
                                
                    except Exception as e:
                        logger.error(f"Search '{keyword}' error: {str(e)[:50]}")
                
                delay = random.uniform(180, 300)
                logger.info(f"💤 Next scan in {delay/60:.1f}min...")
                await asyncio.sleep(delay)
    
    async def _run_simulation_loop(self):
        logger.info("🧬 [V1600] Twitter Simulation Loop Active")
        
        mock_tweets = [
            ("Just set up my first #Shopify store! Any tips?", "NewbieSeller"),
            ("eCommerce is dying. Dropshipping is over.", "SkepticalCEO"),
            ("Why is my ROAS so low on FB ads? Help!", "FrustratedMarketer"),
            ("My Shopify theme broke after update.", "PanickedMerchant"),
        ]
        
        while True:
            delay = random.uniform(15, 30)
            logger.info(f"🔮 [Scan] Waiting {delay:.1f}s...")
            await asyncio.sleep(delay)
            
            tweet_text, author = random.choice(mock_tweets)
            author = f"{author}_{random.randint(10, 99)}"
            tweet_id = f"tweet_{int(asyncio.get_event_loop().time())}"
            
            panic_score = 3
            if "help" in tweet_text.lower() or "?" in tweet_text:
                panic_score = 6
            if "broke" in tweet_text.lower() or "dying" in tweet_text.lower():
                panic_score = 8
            
            if not self.guard.is_safe_to_post(author, tweet_text):
                continue
            
            logger.info(f"📡 [EYES] Tweet from @{author}: {tweet_text[:40]}...")
            logger.info(f"   Panic Score: {panic_score}/10")
            
            if self.hive:
                action = self.hive.create_hive_action(
                    target_thread=tweet_id,
                    user_input=f"Tweet: {tweet_text}",
                    platform="twitter"
                )
                
                agent = "ALPHA" if action.panic_score >= 7 else "BETA" if action.panic_score >= 4 else "GAMMA"
                logger.info(f"🧠 [BRAIN] Agent: {agent}")
                logger.info(f"   Reply: {action.generated_reply[:50]}...")
                
                self.guard.record_action(author, is_promo=True)
