"""
YEDAN V1300 - Crawl4AI Sensor (Eyes)
Stealth web scraping for Reddit/Twitter data extraction.
Converts raw HTML to Markdown for LLM consumption.
"""
import logging
import random
import time
import asyncio
from typing import List, Optional
from modules.pydantic_models import SensorResult

logger = logging.getLogger('crawl4ai_sensor')

# Attempt to import crawl4ai, fallback to simulation
try:
    from crawl4ai import AsyncWebCrawler
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    logger.warning("[Crawl4AI] Not installed. Running in SIMULATION MODE.")

class Crawl4AISensor:
    """
    Stealth sensor using Crawl4AI for Reddit/Twitter scraping.
    Falls back to mock data when library unavailable.
    """
    def __init__(self, simulation_mode: bool = False):
        self.simulation_mode = simulation_mode or not CRAWL4AI_AVAILABLE
        self.crawler = None
        
        if not self.simulation_mode:
            try:
                self.crawler = AsyncWebCrawler()
            except Exception as e:
                logger.error(f"Failed to init Crawl4AI: {e}")
                self.simulation_mode = True
    
    async def scan_subreddit(self, subreddit: str, keywords: List[str]) -> List[SensorResult]:
        """
        Scans a subreddit for posts matching keywords.
        Returns list of SensorResult objects.
        """
        if self.simulation_mode:
            return await self._generate_mock_results(subreddit, keywords)
        
        # Real crawl4ai implementation
        try:
            url = f"https://www.reddit.com/r/{subreddit}/new/.json"
            result = await self.crawler.arun(url)
            # Parse and convert to SensorResult
            # (Implementation would depend on crawl4ai output format)
            return self._parse_reddit_response(result, keywords)
        except Exception as e:
            logger.error(f"Crawl4AI scan failed: {e}")
            return await self._generate_mock_results(subreddit, keywords)
    
    async def _generate_mock_results(self, subreddit: str, keywords: List[str]) -> List[SensorResult]:
        """
        Generates simulated Reddit posts for testing.
        """
        logger.info(f"[SIMULATION] Generating mock posts for r/{subreddit}")
        
        mock_posts = [
            SensorResult(
                thread_id=f"sim_{int(time.time())}_{random.randint(100,999)}",
                title="Help! My Shopify store sales dropped to zero overnight!",
                body_markdown="I updated my theme yesterday and now I'm getting zero orders. The checkout seems to work but something is broken. Anyone else experiencing this?",
                author=f"User_{random.randint(100,999)}",
                panic_score=8,
                keywords_matched=["shopify", "sales", "broken"]
            ),
            SensorResult(
                thread_id=f"sim_{int(time.time())}_{random.randint(100,999)}",
                title="Best way to scale Facebook ads in 2026?",
                body_markdown="I'm spending $50/day but getting terrible ROAS (0.5x). Should I switch to TikTok? What's working for you guys right now?",
                author=f"User_{random.randint(100,999)}",
                panic_score=6,
                keywords_matched=["facebook", "ads", "roas"]
            ),
            SensorResult(
                thread_id=f"sim_{int(time.time())}_{random.randint(100,999)}",
                title="Review my dropshipping store please",
                body_markdown="Just launched after 2 weeks of work. Looking for honest feedback on design and trust signals. www.mock-store-demo.com",
                author=f"User_{random.randint(100,999)}",
                panic_score=3,
                keywords_matched=["dropshipping", "store", "review"]
            ),
        ]
        
        # Simulate network delay
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Return random subset
        return random.sample(mock_posts, k=min(len(mock_posts), 2))
    
    def _parse_reddit_response(self, raw_result, keywords: List[str]) -> List[SensorResult]:
        """
        Parses Crawl4AI output into SensorResult objects.
        (Real implementation would extract from markdown/json)
        """
        # Placeholder - would parse actual crawl4ai response
        return []
    
    def calculate_panic_score(self, text: str) -> int:
        """
        Analyzes text for anxiety indicators.
        Returns score 1-10.
        """
        panic_keywords = {
            10: ["emergency", "urgent", "immediately", "lost everything"],
            8: ["help!", "broken", "stopped working", "zero sales"],
            6: ["struggling", "confused", "not working", "frustrating"],
            4: ["advice", "tips", "best way", "recommend"],
            2: ["curious", "wondering", "thoughts on"],
        }
        
        text_lower = text.lower()
        for score, keywords in sorted(panic_keywords.items(), reverse=True):
            if any(kw in text_lower for kw in keywords):
                return score
        
        return 1
