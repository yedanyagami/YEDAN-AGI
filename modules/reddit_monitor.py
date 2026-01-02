"""
YEDAN V1300 - Reddit Monitor (Tri-Core Integrated)
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

logger = logging.getLogger('reddit_monitor')

class RedditMonitor:
    def __init__(self, reasoner, guard, config):
        self.reasoner = reasoner
        self.guard = guard
        self.config = config["reddit"]
        self.footer = config["disclosure_footer"]["reddit"]
        self.simulation_mode = False
        self.hive = None  # Injected by reactor
        
        # V1300 Tri-Core Components
        self.sensor = Crawl4AISensor(simulation_mode=True)
        self.executor = BrowserUseExecutor(simulation_mode=True)
        
        load_dotenv(dotenv_path=".env.reactor")
        
        # Legacy PRAW (only for live mode)
        self.reddit = None
        try:
            import praw
            self.reddit = praw.Reddit(
                client_id=os.getenv("REDDIT_CLIENT_ID"),
                client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
                user_agent=f"script:YedanTechSupport:v1.0 (by u/{os.getenv('REDDIT_USERNAME')})",
                username=os.getenv("REDDIT_USERNAME"),
                password=os.getenv("REDDIT_PASSWORD")
            )
        except:
            pass

    def start_stream(self):
        if self.simulation_mode:
            logger.info("🔮 [Reddit] Starting SIMULATION STREAM (Tri-Core V1300)")
            asyncio.run(self._run_tricore_loop())
            return
            
        if not self.reddit:
            logger.error("Reddit client not initialized. Aborting stream.")
            return

        # Legacy live mode
        try:
            logger.info(f"Logged into Reddit as {self.reddit.user.me()}")
            sub_list = "+".join(self.config["subreddits"])
            subreddit = self.reddit.subreddit(sub_list)
            
            for submission in subreddit.stream.submissions(skip_existing=True):
                try:
                    self._process_legacy(submission)
                except Exception as e:
                    logger.error(f"Error processing submission: {e}")
                    time.sleep(30)
        except Exception as e:
            logger.error(f"Reddit Login Failed: {e}")

    async def _run_tricore_loop(self):
        """
        V1300 Tri-Core Loop:
        1. EYES: Crawl4AI scans for posts
        2. BRAIN: HiveMind generates HiveAction
        3. HANDS: Browser-Use executes reply
        """
        logger.info("🧬 [V1300] Tri-Core Loop Activated")
        
        while True:
            delay = random.uniform(10, 25)
            logger.info(f"🔮 [Scan] Waiting {delay:.1f}s...")
            await asyncio.sleep(delay)
            
            try:
                # 1. EYES: Scan with Crawl4AI
                results = await self.sensor.scan_subreddit(
                    "shopify", 
                    self.config.get("keywords", ["help", "shopify", "store"])
                )
                
                for post in results:
                    # Safety Check
                    if not self.guard.is_safe_to_post(post.author, post.title + " " + post.body_markdown):
                        continue
                    
                    logger.info(f"📡 [EYES] Found: {post.title[:50]}...")
                    logger.info(f"   Panic Score: {post.panic_score}/10")
                    
                    # 2. BRAIN: Generate HiveAction
                    if self.hive:
                        action = self.hive.create_hive_action(
                            target_thread=post.thread_id,
                            user_input=f"Title: {post.title}\nBody: {post.body_markdown}",
                            platform="reddit"
                        )
                        
                        logger.info(f"🧠 [BRAIN] HiveAction created:")
                        logger.info(f"   Tool: {action.tool_used}")
                        logger.info(f"   Panic: {action.panic_score}")
                        logger.info(f"   Agent: {'ALPHA' if action.panic_score >= 7 else 'BETA' if action.panic_score >= 4 else 'GAMMA'}")
                        
                        # Apply footer
                        final_reply = f"{action.generated_reply}\n{self.footer}"
                        
                        # 3. HANDS: Execute with Browser-Use
                        result = await self.executor.execute_reply(
                            url=f"https://reddit.com/r/shopify/comments/{post.thread_id}",
                            message=final_reply,
                            config=action.mimicry_config
                        )
                        
                        logger.info(f"🖐️ [HANDS] Execution: {result.action_taken}")
                        logger.info(f"   Latency: {result.latency_ms}ms")
                        
                        # Log interaction
                        log_interaction(
                            "reddit_tricore",
                            post.thread_id,
                            final_reply,
                            {"panic_score": action.panic_score, "tool": action.tool_used}
                        )
                        
                        self.guard.record_action(post.author, is_promo=True)
                    else:
                        # Fallback to legacy reasoner
                        response = self.reasoner.generate_response(
                            f"Title: {post.title}\nBody: {post.body_markdown}",
                            platform="reddit"
                        )
                        if response:
                            logger.info(f"✅ [LEGACY] Generated response: {response[:80]}...")
                            
            except Exception as e:
                logger.error(f"Tri-Core Loop Error: {e}")

    def _process_legacy(self, submission):
        """Legacy PRAW processing for live mode"""
        if not self.is_relevant(submission):
            return

        if not self.guard.is_safe_to_post(submission.author.name, submission.title + " " + submission.selftext):
            return

        logger.info(f"Found relevant post: {submission.title}")
        
        if hasattr(self, 'hive') and self.hive:
            response_text = self.hive.swarm_debate(
                f"Title: {submission.title}\nBody: {submission.selftext}", 
                context_platform="reddit"
            )
            response_text = self.hive.apply_stealth_pulse(response_text)
        else:
            response_text = self.reasoner.generate_response(
                f"Title: {submission.title}\nBody: {submission.selftext}", 
                platform="reddit"
            )
        
        if not response_text:
            return

        final_response = f"{response_text}{self.footer}"
        
        add_random_delay(2.0, 5.0)
        try:
            submission.reply(final_response)
            logger.info(f"✅ Replied to post {submission.id}")
            self.guard.record_action(submission.author.name, is_promo=True)
        except Exception as e:
            logger.error(f"Failed to reply: {e}")

    def is_relevant(self, submission):
        if submission.author.link_karma + submission.author.comment_karma < self.config["min_karma"]:
            return False
        text = (submission.title + " " + submission.selftext).lower()
        return any(kw.lower() in text for kw in self.config["keywords"])
