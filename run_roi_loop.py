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
import io
import os
import time
import random
from datetime import datetime
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

load_dotenv(dotenv_path=".env.reactor")

# V2.0 Modules
from modules.content_miner import OpenContentMiner
from modules.writer_agent import WriterAgent
from modules.opal_bridge import OpalBridge
from modules.cloud_social import CloudSocialAgent
from modules.paypal_bridge import PayPalBridge
from modules.n8n_bridge import N8nBridge
from modules.echo_analytics import EchoAnalytics
from generate_digest_asset import generate_daily_digest

class YEDAN_V2_Engine:
    def __init__(self):
        print(f"\n[*] Initializing YEDAN V2.0 Engine...")
        self.miner = OpenContentMiner()
        self.writer = WriterAgent()
        
        # Bridge Modules
        self.opal = OpalBridge()
        self.social = CloudSocialAgent()
        self.paypal = PayPalBridge()
        self.n8n = N8nBridge()
        self.echo = EchoAnalytics()
        
        # Config
        self.mode = "LIVE" if os.getenv("SHOPIFY_DRY_RUN", "true").lower() == "false" else "SIMULATION"
        print(f"[*] Engine Mode: {self.mode}")
        
    def check_finance_pulse(self):
        """Check real financial status"""
        print("\n[Finance] Checking Pulse...")
        
        # 1. Check PayPal
        if self.paypal.is_configured():
            balance = self.paypal.get_balance()
            if balance:
                print(f"   -> PayPal Balance: ${balance['total_available']:.2f} ({os.getenv('PAYPAL_MODE')})")
        
        # 2. Check Synapse ROI Metrics
        # (This connects to our Cloudflare Worker to see what's happening cloud-side)
        try:
            import requests
            r = requests.get("https://synapse.yagami8095.workers.dev/roi/daily?days=1")
            if r.status_code == 200:
                data = r.json()
                today = data.get("revenue", [])[0]
                print(f"   -> Today's Revenue: ${today.get('revenue', 0)} ({today.get('count', 0)} sales)")
        except Exception as e:
            print(f"   -> [Warn] Synapse pulse failed: {e}")

    def run_mining_operation(self):
        """Phase 1: Mining & Content Creation"""
        print("\n[Phase 1] MINING OPERATION")
        
        # Check if we have Opal content pending first (Higher priority)
        opal_content = self.opal.fetch_pending_content()
        if opal_content:
            print(f"   -> Found {len(opal_content)} items from Google Opal. Processing...")
            self.opal.run_cycle()
            return
            
        # Fallback to standard mining
        print("   -> No Opal content. Running standard mining cycle...")
        generate_daily_digest()

    def run_traffic_operation(self):
        """Phase 2: Traffic Generation"""
        print("\n[Phase 2] TRAFFIC OPERATION")
        
        # Check Browserless status
        status = self.social.check_browserless_status()
        if not status.get("available"):
            print("   -> [Warn] Cloud Browser unavailable. Skipping automated posting.")
            return

        print("   -> Cloud Browser Active.")
        target_subreddits = ["Dropshipping", "SaaS", "Entrepreneur"]
        
        # In a real scenario, this would loop through subreddits
        # For safety/demonstration, we pick one and "scan"
        sub = random.choice(target_subreddits)
        print(f"   -> Scanning r/{sub} for opportunities...")
        
        # (Here we would call self.social.reddit_search_and_engage...)
        # But to avoid spamming while testing, we just log intent
        print(f"   -> [Strategy] Would engage with top 3 posts in r/{sub} using persona 'Alpha'")

    def run_logistics(self):
        """Phase 3: Logistics (n8n & Webhooks)"""
        print("\n[Phase 3] LOGISTICS & AUTOMATION")
        
        # Check n8n status
        n8n_status = self.n8n.status_check()
        if n8n_status['connected']:
            print(f"   -> n8n Connected ({n8n_status['workflows']} workflows live).")
            # If we had a specific workflow to trigger daily, we'd do it here
            # self.n8n.execute_workflow("daily-checkup")
        else:
            print("   -> [Warn] n8n disconnected.")

    def execute_cycle(self):
        """Run one full business cycle"""
        print("\n" + "="*60)
        print(f"[*] YEDAN V2.0 EXECUTION CYCLE | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        self.check_finance_pulse()
        self.run_mining_operation()
        self.run_traffic_operation()
        self.run_logistics()
        
        print("\n" + "="*60)
        print("[*] CYCLE COMPLETE. Sleeping...")
        print("="*60)

if __name__ == "__main__":
    engine = YEDAN_V2_Engine()
    engine.execute_cycle()
