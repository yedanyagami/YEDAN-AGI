"""
CLOUD MONITOR (Mission Control) ☁️
Lightweight polling script for Local "Eco Mode".
Fetches status from Synapse & n8n without running heavy logic.
Updates the Dashboard.
"""
import time
import json
import logging
import requests
import sys
import os

# Add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.config import Config, setup_logging
from modules.n8n_bridge import N8nBridge
from generate_dashboard import generate_dashboard

# Setup pure file logging to avoid console spam
logger = setup_logging('cloud_monitor')

class CloudMonitor:
    def __init__(self):
        self.n8n = N8nBridge()
        self.synapse_url = Config.SYNAPSE_URL
        
    def check_n8n_health(self):
        """Get n8n workflow stats"""
        try:
            status = self.n8n.status_check()
            if status['connected']:
                # Save status to a lightweight JSON for dashboard to read
                stats = {
                    "connected": True,
                    "workflows": status['workflows'],
                    "last_check": time.time()
                }
            else:
                stats = {"connected": False, "error": status['error']}
                
            # Write to monitoring cache
            cache_path = Config.DATA_DIR / "n8n_status.json"
            with open(cache_path, "w") as f:
                json.dump(stats, f)
                
            logger.info(f"msg='n8n Status' connected={stats['connected']} workflows={stats.get('workflows')}")
            return stats
        except Exception as e:
            logger.error(f"n8n check failed: {e}")
            return {"connected": False, "error": str(e)}

    def check_synapse_pulse(self):
        """Check Synapse ROI"""
        try:
            r = requests.get(f"{self.synapse_url}/roi/daily?days=1", timeout=5)
            if r.status_code == 200:
                data = r.json()
                # Synapse data is already being pulled by EchoAnalytics in generate_dashboard
                # We just verify connectivity here
                logger.info("msg='Synapse Pulse' status='online'")
                return True
            else:
                logger.warning(f"msg='Synapse Pulse' status='error' code={r.status_code}")
                return False
        except Exception as e:
            logger.error(f"Synapse check failed: {e}")
            return False

    def run_forever(self):
        print(f"☁️ Cloud Monitor Active (Eco Mode: {Config.ECO_MODE})")
        print(f"   -> Polling n8n: {Config.N8N_BASE_URL}")
        print(f"   -> Polling Synapse: {Config.SYNAPSE_URL}")
        
        while True:
            try:
                # 1. Fetch Cloud Stats
                self.check_n8n_health()
                self.check_synapse_pulse()
                
                # 2. Update Dashboard
                # generate_dashboard() now pulls from EchoAnalytics, 
                # we might need to update Echo to read our n8n cache if we want that data.
                # For now, we run it to refresh revenue numbers.
                generate_dashboard()
                
                # 3. Sleep (Eco Pacing)
                sleep_time = 60 if Config.ECO_MODE else 30
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                print("🛑 Monitor stopped.")
                break
            except Exception as e:
                logger.critical(f"Monitor crashed: {e}")
                time.sleep(10)

if __name__ == "__main__":
    monitor = CloudMonitor()
    monitor.run_forever()
