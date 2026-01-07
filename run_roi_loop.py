"""
YEDAN V2.0 ENGINE - ROI Infinite Loop
The "V2 Engine" that orchestrates the entire cloud-native business cycle:
1. MINING: ArXiv/Wikipedia -> Content
2. FACTORY: Writer Agent -> Shopify Product (Real)
3. TRAFFIC: CloudSocial -> Reddit/Twitter (Automated)
4. LOGISTICS: n8n Workflow -> Order Processing
5. FINANCE: PayPal/Shopify -> ROI Metrics -> Synapse
"""
import sys
import subprocess
import logging
from time import sleep
import time
import random
import traceback
import requests
import gc
from datetime import datetime

# --- SELF-HEAL: Dependency Medic ---
def check_and_install_dependencies():
    """Ensure critical libs are installed"""
    required = ["requests", "python-dotenv", "pytrends", "tweepy", "PyNaCl"]
    missing = []
    
    for lib in required:
        try:
            __import__(lib.replace("-", "_").replace("PyNaCl", "nacl"))
        except ImportError:
            missing.append(lib)
    
    if missing:
        print(f"[Medic] Dependency Medic: Installing missing libs: {missing}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            print("[Medic] Dependencies restored.")
        except Exception as e:
            print(f"[Error] Failed to auto-install: {e}")

check_and_install_dependencies()
# -----------------------------------

import asyncio
from modules.config import Config, setup_logging

# V2.0 Modules
from modules.content_miner import OpenContentMiner
from modules.writer_agent import WriterAgent
from modules.opal_bridge import OpalBridge
from modules.cloud_social import CloudSocialAgent
from modules.paypal_bridge import PayPalBridge
from modules.n8n_bridge import N8nBridge
from modules.echo_analytics import EchoAnalytics
from modules.market_scanner import MarketScanner
from generate_digest_asset import generate_daily_digest

logger = setup_logging('reactor')

class YEDAN_V2_Engine:
    def __init__(self):
        logger.info("[*] Initializing YEDAN V2.0 Engine (Async/Turbo)...")
        self.miner = OpenContentMiner()
        self.writer = WriterAgent()
        
        # Bridge Modules
        self.opal = OpalBridge()
        self.social = CloudSocialAgent()
        self.paypal = PayPalBridge()
        self.n8n = N8nBridge()
        self.echo = EchoAnalytics()
        self.scanner = MarketScanner()
        
        # Config
        self.mode = "LIVE" if not Config.DRY_RUN else "SIMULATION"
        logger.info(f"[*] Engine Mode: {self.mode}")
        
    async def async_check_finance_pulse(self):
        """Check real financial status (Non-blocking)"""
        logger.info("[Finance] Checking Pulse...")
        
        def _check():
            # 1. Check PayPal
            try:
                if self.paypal.is_configured():
                    balance = self.paypal.get_balance()
                    if balance:
                        logger.info(f"   -> PayPal Balance: ${balance['total_available']:.2f} ({Config.DRY_RUN or 'Live'})")
            except Exception as e:
                logger.error(f"PayPal check failed: {e}")
            
            # 2. Check Synapse ROI Metrics
            try:
                r = requests.get(f"{Config.SYNAPSE_URL}/roi/daily?days=1", timeout=5)
                if r.status_code == 200:
                    data = r.json()
                    today = data.get("revenue", [])[0]
                    logger.info(f"   -> Today's Revenue: ${today.get('revenue', 0)} ({today.get('count', 0)} sales)")
            except Exception as e:
                logger.warning(f"   -> [Warn] Synapse pulse failed: {e}")

        await asyncio.to_thread(_check)

    async def async_run_mining(self):
        """Phase 1: Mining & Direct Product Creation (NO OPAL DEPENDENCY)"""
        logger.info("[Phase 1] MINING -> FACTORY -> SHOPIFY (Direct Pipeline)")
        
        def _mine_and_create():
            try:
                # 1. Get trending content directly from ContentMiner
                topics = self.miner.harvest_hackernews(max_results=3)
                if not topics:
                    topics = self.miner.harvest_wikipedia("trending technology")
                
                if not topics:
                    logger.info("   -> No topics found. Skipping cycle.")
                    return
                
                logger.info(f"   -> Found {len(topics)} trending topics. Creating products...")
                
                # 2. For each topic, generate product and push to Shopify
                for topic in topics[:1]:  # Limit to 1 product per cycle to avoid spam
                    title = topic.get("title", "Trending Product")
                    
                    # Generate SEO content using WriterAgent
                    seo_result = self.writer.generate_seo_content({
                        "title": title,
                        "current_description": topic.get("summary", ""),
                        "keywords": ["AI", "trending", "2026"]
                    })
                    
                    # Create product on Shopify
                    if not Config.DRY_RUN:
                        result = self.opal._handle_product({
                            "title": seo_result.get("optimized_title", title),
                            "body_html": seo_result.get("optimized_description_html", ""),
                            "price": "9.99"
                        })
                        if result:
                            logger.info(f"   ✅ PRODUCT CREATED: {title[:30]}...")
                    else:
                        logger.info(f"   [DRY_RUN] Would create: {title[:30]}...")
                        
            except Exception as e:
                logger.error(f"Direct mining failed: {e}")

        await asyncio.to_thread(_mine_and_create)


    async def async_run_traffic(self):
        """Phase 2: Traffic Generation (Non-blocking)"""
        logger.info("[Phase 2] TRAFFIC OPERATION (Viral Schedule)")
        
        def _traffic():
            try:
                status = self.social.check_browserless_status()
                if not status.get("available"):
                    logger.warning("   -> [Warn] Cloud Browser unavailable. Skipping automated posting.")
                    return

                logger.info("   -> Cloud Browser Active.")
                from modules.cloud_social import CloudSocialOrchestrator
                orch = CloudSocialOrchestrator()
                orch.run_cycle()
            except Exception as e:
                logger.error(f"Traffic operation failed: {e}")

        await asyncio.to_thread(_traffic)

    async def async_run_logistics(self):
        """Phase 3: Logistics (Non-blocking)"""
        logger.info("[Phase 3] LOGISTICS & AUTOMATION")
        
        def _logistics():
            try:
                n8n_status = self.n8n.status_check()
                if n8n_status['connected']:
                    logger.info(f"   -> n8n Connected ({n8n_status['workflows']} workflows live).")
                else:
                    logger.warning("   -> [Warn] n8n disconnected.")
            except Exception as e:
                logger.error(f"Logistics check failed: {e}")

        await asyncio.to_thread(_logistics)

    async def async_rapid_response(self):
        """Phase 4: Rapid Response (Competitor Scan)"""
        logger.info("[Phase 4] RAPID RESPONSE (Market Scan)")
        try:
            await self.scanner.monitor_pricing()
        except Exception as e:
            logger.error(f"Rapid Response failed: {e}")

    async def execute_cycle(self):
        """Run one full async business cycle"""
        logger.info("=" * 60)
        logger.info(f"[*] YEDAN V2.0 ASYNC CYCLE | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        # Run ALL operations concurrently
        await asyncio.gather(
            self.async_check_finance_pulse(),
            self.async_run_mining(),
            self.async_run_traffic(),
            self.async_run_logistics(),
            self.async_rapid_response()
        )
        
        logger.info("=" * 60)
        logger.info("[*] CYCLE COMPLETE.")
        logger.info("=" * 60)

    def run_safe_loop(self):
        """Entry point for async execution"""
        logger.info("🚀 STARTING ASYNC CORE (Eco Mode Enabled)") if Config.ECO_MODE else logger.info("🚀 STARTING ASYNC CORE")
        
        while True:
            try:
                # 1. Execute Cycle
                asyncio.run(self.execute_cycle())
                
                # 2. Eco Mode Optimization
                if Config.ECO_MODE:
                    logger.info("🍃 [Eco] Running Garbage Collection...")
                    gc.collect()
                    # Sleep longer in Eco Mode
                    sleep_duration = 60 # 1 minute
                else:
                    sleep_duration = 10 # 10 seconds
                
                # 3. Sleep
                logger.info(f"[*] Sleeping {sleep_duration}s...")
                time.sleep(sleep_duration)
                
            except KeyboardInterrupt:
                logger.info("🛑 Stopped by user")
                sys.exit(0)
            except Exception as e:
                logger.critical(f"🔥 CRITICAL CORE FAILURE: {e}")
                logger.critical(traceback.format_exc())
                # Crash reporting
                try:
                    if Config.TELEGRAM_BOT_TOKEN:
                        requests.post(
                            f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage",
                            json={"chat_id": Config.TELEGRAM_CHAT_ID, "text": f"🔥 YEDAN CORE CRASH: {e}"}
                        )
                except:
                    pass
                # If critical error, wait before retry to avoid rapid-fire loops
                time.sleep(30)


if __name__ == "__main__":
    engine = YEDAN_V2_Engine()
    engine.run_safe_loop()
