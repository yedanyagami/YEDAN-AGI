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
        print(f"🚑 Dependency Medic: Installing missing libs: {missing}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
            print("✅ Dependencies restored.")
        except Exception as e:
            print(f"❌ Failed to auto-install: {e}")

check_and_install_dependencies()
# -----------------------------------

from modules.config import Config, setup_logging

# V2.0 Modules
from modules.content_miner import OpenContentMiner
from modules.writer_agent import WriterAgent
from modules.opal_bridge import OpalBridge
from modules.cloud_social import CloudSocialAgent
from modules.paypal_bridge import PayPalBridge
from modules.n8n_bridge import N8nBridge
from modules.echo_analytics import EchoAnalytics
from generate_digest_asset import generate_daily_digest

logger = setup_logging('reactor')

class YEDAN_V2_Engine:
    def __init__(self):
        logger.info("[*] Initializing YEDAN V2.0 Engine...")
        self.miner = OpenContentMiner()
        self.writer = WriterAgent()
        
        # Bridge Modules
        self.opal = OpalBridge()
        self.social = CloudSocialAgent()
        self.paypal = PayPalBridge()
        self.n8n = N8nBridge()
        self.echo = EchoAnalytics()
        
        # Config
        self.mode = "LIVE" if not Config.DRY_RUN else "SIMULATION"
        logger.info(f"[*] Engine Mode: {self.mode}")
        
    def check_finance_pulse(self):
        """Check real financial status"""
        logger.info("[Finance] Checking Pulse...")
        
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
            r = requests.get(f"{Config.SYNAPSE_URL}/roi/daily?days=1")
            if r.status_code == 200:
                data = r.json()
                today = data.get("revenue", [])[0]
                logger.info(f"   -> Today's Revenue: ${today.get('revenue', 0)} ({today.get('count', 0)} sales)")
        except Exception as e:
            logger.warning(f"   -> [Warn] Synapse pulse failed: {e}")

    def run_mining_operation(self):
        """Phase 1: Mining & Content Creation"""
        logger.info("[Phase 1] MINING OPERATION")
        
        # Check if we have Opal content pending first (Higher priority)
        try:
            opal_content = self.opal.fetch_pending_content()
            if opal_content:
                logger.info(f"   -> Found {len(opal_content)} items from Google Opal. Processing...")
                self.opal.run_cycle()
                return
        except Exception as e:
            logger.error(f"Opal mining failed: {e}")
            
        # Fallback to standard mining
        logger.info("   -> No Opal content. Running standard mining cycle...")
        try:
            generate_daily_digest()
        except Exception as e:
            logger.error(f"Standard mining failed: {e}")

    def run_traffic_operation(self):
        """Phase 2: Traffic Generation"""
        logger.info("[Phase 2] TRAFFIC OPERATION")
        
        try:
            # Check Browserless status
            status = self.social.check_browserless_status()
            if not status.get("available"):
                logger.warning("   -> [Warn] Cloud Browser unavailable. Skipping automated posting.")
                return

            logger.info("   -> Cloud Browser Active.")
            
            # Use Orchestrator logic here or integrate directly
            # For simplicity, we trigger the orchestration cycle if available method exists
            # But the 'run_traffic_operation' in original just logged intent.
            # NOW WE EXECUTE REAL TRAFFIC via CloudSocialOrchestrator logic
            
            # Reuse the Orchestrator logic (creating instance locally to avoid import loops if any, 
            # though we imported CloudSocialAgent. Let's stick to the Agent methods directly if possible)
            
            # Since CloudSocialAgent is low level, we might want to invoke the orchestrator logic
            # OR simple define tasks here.
            # The 'run_cycle' in cloud_social.py is good. Let's replicate that logic or import Orchestrator.
            # importing Orchestrator from modules.cloud_social is better but I see I only imported Agent above.
            
            # Let's import orchestrator safely
            from modules.cloud_social import CloudSocialOrchestrator
            orch = CloudSocialOrchestrator()
            orch.run_cycle()
            
        except Exception as e:
            logger.error(f"Traffic operation failed: {e}")

    def run_logistics(self):
        """Phase 3: Logistics (n8n & Webhooks)"""
        logger.info("[Phase 3] LOGISTICS & AUTOMATION")
        
        try:
            # Check n8n status
            n8n_status = self.n8n.status_check()
            if n8n_status['connected']:
                logger.info(f"   -> n8n Connected ({n8n_status['workflows']} workflows live).")
            else:
                logger.warning("   -> [Warn] n8n disconnected.")
        except Exception as e:
            logger.error(f"Logistics check failed: {e}")

    def execute_cycle(self):
        """Run one full business cycle"""
        logger.info("=" * 60)
        logger.info(f"[*] YEDAN V2.0 EXECUTION CYCLE | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        self.check_finance_pulse()
        self.run_mining_operation()
        self.run_traffic_operation()
        self.run_logistics()
        
        logger.info("=" * 60)
        logger.info("[*] CYCLE COMPLETE. Sleeping...")
        logger.info("=" * 60)

    def run_safe_loop(self):
        """Infinite loop with crash protection"""
        logger.info("🚀 STARTING SAFE LOOP PROTOCOL")
        while True:
            try:
                self.execute_cycle()
            except KeyboardInterrupt:
                logger.info("🛑 Stopped by user")
                break
            except Exception as e:
                logger.critical(f"🔥 CRITICAL CORE FAILURE: {e}")
                logger.critical(traceback.format_exc())
                # Optional: Send Telegram alert via Watchdog/Config directly
                try:
                    if Config.TELEGRAM_BOT_TOKEN:
                        requests.post(
                            f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage",
                            json={"chat_id": Config.TELEGRAM_CHAT_ID, "text": f"🔥 YEDAN CORE CRASH: {e}"}
                        )
                except:
                    pass
                time.sleep(60) # Wait 1 min before retry
            
            # Sleep between cycles (e.g. 1 hour or just run once per invocation if controlled by OS)
            # Original script just ran once. But "run_roi_loop.py" implies a loop?
            # Creating an infinite loop here might conflict with `start_v2.bat` which also loops.
            # However, `start_v2.bat` calls python once per loop.
            # So I should NOT loop infinitely here if the BAT file handles it.
            # BUT the user asked for "Async/Robust Core Loop".
            # I will make it run ONCE safely, and let the BAT handle the repetition. 
            # OR I can change the BAT to just run this script once and this script loops.
            # Given `start_v2.bat` content: "python run_roi_loop.py ... goto LOOP"
            # It expects this script to exit.
            # So I will keep it single-run but SAFE.
            break

if __name__ == "__main__":
    engine = YEDAN_V2_Engine()
    engine.run_safe_loop()
