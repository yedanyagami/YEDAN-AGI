"""
YEDAN V1300 - Twitter Monitor (Tri-Core Integrated)
Uses: Crawl4AI (Eyes) → HiveMind (Brain) → Browser-Use (Hands)
"""
import os
import time
import random
import logging
import asyncio
from dotenv import load_dotenv

from modules.pydantic_models import HiveAction, MimicryConfig
from modules.crawl4ai_sensor import Crawl4AISensor
from modules.browser_use_executor import BrowserUseExecutor
from modules.utils import add_random_delay, log_interaction

logger = logging.getLogger('twitter_monitor')

class TwitterMonitor:
    def __init__(self, reasoner, guard, config):
        self.reasoner = reasoner
        self.guard = guard
        self.config = config["twitter"]
        self.footer = config["disclosure_footer"]["twitter"]
        self.simulation_mode = False
        self.hive = None  # Injected by reactor
        
        # V1300 Tri-Core Components
        self.sensor = Crawl4AISensor(simulation_mode=True)
        self.executor = BrowserUseExecutor(simulation_mode=True)
        
        load_dotenv(dotenv_path=".env.reactor")
        
        # Legacy Tweepy (only for live mode)
        self.client = None
        try:
            import tweepy
            self.client = tweepy.Client(
                bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
                consumer_key=os.getenv("TWITTER_API_KEY"),
                consumer_secret=os.getenv("TWITTER_API_SECRET"),
                wait_on_rate_limit=True
            )
            logger.info("Twitter Client initialized")
        except:
            pass

    def start_stream(self):
        if self.simulation_mode:
            logger.info("🔮 [Twitter] Starting SIMULATION STREAM (Tri-Core V1300)")
            asyncio.run(self._run_tricore_loop())
            return

        if not self.client:
            logger.error("Twitter Client not initialized.")
            return

        # Legacy live mode
        self._run_legacy_poll()

    async def _run_tricore_loop(self):
        """
        V1300 Tri-Core Loop:
        1. EYES: Generate mock tweets (simulation) or scrape
        2. BRAIN: HiveMind generates HiveAction
        3. HANDS: Browser-Use executes reply
        """
        logger.info("🧬 [V1300] Twitter Tri-Core Loop Activated")
        
        mock_tweets = [
            ("Just set up my first #Shopify store! Any tips?", "NewbieSeller_42"),
            ("eCommerce is dying. Dropshipping is over. #marketing", "SkepticalCEO"),
            ("Looking for a VA to manage my store. DM me. #hiring", "BusyFounder"),
            ("Why is my ROAS so low on FB ads? Help! #facebookads", "FrustratedMarketer"),
            ("YEDAN is fascinating. Is it real AI?", "CuriousTech"),
            ("My Shopify theme broke after update. Anyone else?", "PanickedMerchant"),
        ]
        
        while True:
            delay = random.uniform(15, 30)
            logger.info(f"🔮 [Scan] Waiting {delay:.1f}s...")
            await asyncio.sleep(delay)
            
            try:
                # 1. EYES: Get tweet (mock in simulation)
                tweet_text, author = random.choice(mock_tweets)
                author = f"{author}_{random.randint(10, 99)}"
                tweet_id = f"tweet_{int(time.time())}"
                
                # Calculate panic score
                panic_score = self.sensor.calculate_panic_score(tweet_text)
                
                # Safety Check
                if not self.guard.is_safe_to_post(author, tweet_text):
                    continue
                
                logger.info(f"📡 [EYES] Tweet from @{author}: {tweet_text[:40]}...")
                logger.info(f"   Panic Score: {panic_score}/10")
                
                # 2. BRAIN: Generate HiveAction
                if self.hive:
                    action = self.hive.create_hive_action(
                        target_thread=tweet_id,
                        user_input=f"Tweet: {tweet_text}",
                        platform="twitter"
                    )
                    
                    logger.info(f"🧠 [BRAIN] HiveAction created:")
                    logger.info(f"   Tool: {action.tool_used}")
                    logger.info(f"   Panic: {action.panic_score}")
                    
                    # Truncate for Twitter
                    reply = action.generated_reply
                    if len(reply) > 200:
                        reply = reply[:190] + "..."
                    
                    final_reply = f"{reply}\n{self.footer}"
                    
                    # 3. HANDS: Execute with Browser-Use
                    result = await self.executor.execute_reply(
                        url=f"https://twitter.com/{author}/status/{tweet_id}",
                        message=final_reply,
                        config=action.mimicry_config
                    )
                    
                    logger.info(f"🖐️ [HANDS] Execution: {result.action_taken}")
                    logger.info(f"   Reply preview: {final_reply[:60]}...")
                    
                    # Log interaction
                    log_interaction(
                        "twitter_tricore",
                        tweet_id,
                        final_reply,
                        {"panic_score": action.panic_score, "author": author}
                    )
                    
                    self.guard.record_action(author, is_promo=True)
                else:
                    # Fallback to legacy
                    response = self.reasoner.generate_response(
                        f"Tweet: {tweet_text}",
                        platform="twitter"
                    )
                    if response:
                        logger.info(f"✅ [LEGACY] Response: {response[:60]}...")
                        
            except Exception as e:
                logger.error(f"Tri-Core Loop Error: {e}")

    def _run_legacy_poll(self):
        """Legacy Tweepy polling for live mode"""
        logger.info("Starting Twitter Legacy Polling Loop")
        
        query = "(" + " OR ".join(self.config["keywords"]) + ") " + " OR ".join(self.config["hashtags"]) + " -is:retweet -is:reply lang:en"
        
        while True:
            try:
                response = self.client.search_recent_tweets(
                    query=query, 
                    max_results=10, 
                    tweet_fields=['author_id', 'created_at', 'text'],
                    expansions=['author_id'],
                    user_fields=['username', 'public_metrics']
                )

                if response.data:
                    users = {u.id: u for u in response.includes['users']}
                    for tweet in response.data:
                        author = users[tweet.author_id]
                        self._process_legacy_tweet(tweet, author)
                
                time.sleep(120)

            except Exception as e:
                logger.error(f"Twitter poll error: {e}")
                time.sleep(300)

    def _process_legacy_tweet(self, tweet, author):
        """Legacy processing for live mode"""
        if author.public_metrics['followers_count'] < self.config["min_followers"]:
            return

        if not self.guard.is_safe_to_post(author.username, tweet.text):
            return

        logger.info(f"Found relevant tweet: {tweet.text[:50]}...")
        time.sleep(random.uniform(2, 5))

        if self.hive:
            response_text = self.hive.swarm_debate(f"Tweet: {tweet.text}", "twitter")
            response_text = self.hive.apply_stealth_pulse(response_text)
        else:
            response_text = self.reasoner.generate_response(f"Tweet: {tweet.text}", "twitter")
        
        if not response_text:
            return

        if len(response_text) > 200:
            response_text = response_text[:190] + "..."

        final_response = f"{response_text}\n{self.footer}"

        try:
            self.client.create_tweet(text=final_response, in_reply_to_tweet_id=tweet.id)
            logger.info(f"✅ Replied to tweet {tweet.id}")
            self.guard.record_action(author.username, is_promo=True)
        except Exception as e:
            logger.error(f"Failed to reply tweet: {e}")
