"""
V1800 Hive Mind (The Co-Pilot Daemon)
Interacts with User via Telegram. Uses Browserless for web tasks.
"""
import os
import time
import requests
import asyncio
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
from datetime import datetime
from dotenv import load_dotenv

# Import our modular engines
from dashboard import ROIDashboard
from modules.content_miner import OpenContentMiner
from modules.writer_agent import WriterAgent
from integrate_browserless import BrowserlessIntegrator

load_dotenv(dotenv_path=".env.reactor")

class HiveMind:
    def __init__(self):
        self.dashboard = ROIDashboard()
        self.miner = OpenContentMiner()
        self.writer = WriterAgent()
        self.browserless = BrowserlessIntegrator()
        
        # Telegram Config
        self.tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.tg_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        
        self.cycle_count = 0
        self.running = True

    def log(self, message):
        """Log locally and send to Telegram."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {message}"
        print(formatted_msg)
        
        if self.tg_token and self.tg_chat_id:
            try:
                url = f"https://api.telegram.org/bot{self.tg_token}/sendMessage"
                payload = {"chat_id": self.tg_chat_id, "text": message}
                requests.post(url, json=payload, timeout=5)
            except:
                pass # Don't crash if network fails

    def run_daily_cycle(self):
        """The main loop that runs alongside the user."""
        self.log("🚀 Hive Mind V1800 STARTED. Taking control.")
        
        while self.running:
            try:
                self.cycle_count += 1
                self.log(f"--- Cycle #{self.cycle_count} ---")
                
                # 1. Health Check
                metrics = self.dashboard.check_all_systems()
                all_systems_ok = all(metrics[d]["status"] == "OK" for d in metrics if "status" in metrics[d])
                
                if not all_systems_ok:
                    self.log("⚠️ Some systems reported WARN/ERROR. Checking self-healing...")
                
                # 2. Mining (Browserless Enhanced)
                self.log("⛏️ Mining fresh content...")
                # Try HackerNews first
                stories = self.miner.harvest_hackernews(max_results=3)
                if stories:
                    top_story = stories[0]
                    self.log(f"   Found: {top_story['title']} (Score: {top_story.get('score')})")
                    
                    # 3. Visuals (Browserless -> TinyWow/Tools)
                    # For now, we simulate taking a screenshot of the source as a 'cover'
                    self.log("📸 Generating visual asset (Browserless)...")
                    if self.browserless.token:
                        self.browserless.take_screenshot(top_story['url'])
                        self.log("   Screenshot captured (Visual Asset).")
                    
                    # 4. Product Creation logic would go here
                    # self.factory.create_product(...)
                    
                # 5. Reporting
                self.log(f"✅ Cycle #{self.cycle_count} Complete. Value: ${metrics['revenue']['total_value']}")
                
                # Wait for next cycle (e.g., 1 hour or user trigger)
                self.log("💤 Sleeping for 60 minutes...")
                time.sleep(3600) 
                
            except KeyboardInterrupt:
                self.log("🛑 User stopped the Hive Mind.")
                break
            except Exception as e:
                self.log(f"❌ CRITICAL ERROR: {e}")
                time.sleep(60) # Wait before retry

if __name__ == "__main__":
    bot = HiveMind()
    # If no Telegram token, warn user
    if not bot.tg_token:
        print("NOTE: No TELEGRAM_BOT_TOKEN found. Logs will only appear here.")
    
    bot.run_daily_cycle()
