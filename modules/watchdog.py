"""
YEDAN WATCHDOG - System Health Monitor
Pings all critical services and reports status to Telegram.
"""
import requests
import logging
from modules.config import Config, setup_logging

logger = setup_logging('watchdog')

class Watchdog:
    def __init__(self):
        self.telegram_token = Config.TELEGRAM_BOT_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID
        self.synapse_url = Config.SYNAPSE_URL
        self.shopify_url = Config.SHOPIFY_STORE_URL
        
    def send_alert(self, message):
        """Send critical alert to Telegram"""
        if not self.telegram_token:
            logger.error("No Telegram token found")
            return
            
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        data = {
            "chat_id": self.chat_id,
            "text": f"🚨 WATCHDOG ALERT 🚨\n\n{message}",
            "parse_mode": "Markdown"
        }
        try:
            requests.post(url, json=data)
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")

    def check_synapse(self):
        """Check if Cloudflare Worker is alive"""
        try:
            r = requests.post(f"{self.synapse_url}/heartbeat", timeout=10)
            if r.status_code == 200:
                return True, "Online"
            return False, f"Status {r.status_code}"
        except Exception as e:
            return False, str(e)

    def check_shopify_storefront(self):
        """Check if store is accessible"""
        try:
            # Simple GET request to the store
            url = f"https://{self.shopify_url}"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                return True, "Online"
            return False, f"Status {r.status_code}"
        except Exception as e:
            return False, str(e)

    def check_internet(self):
        """Basic connectivity check"""
        try:
            requests.get("https://1.1.1.1", timeout=5)
            return True, "Connected"
        except:
            return False, "Disconnected"

    def run_diagnostics(self):
        """Run all checks and report"""
        logger.info("Running Watchdog diagnostics...")
        
        results = {
            "Internet": self.check_internet(),
            "Synapse (Brain)": self.check_synapse(),
            "Shopify (Store)": self.check_shopify_storefront()
        }
        
        failures = []
        report = []
        
        for name, (status, msg) in results.items():
            icon = "✅" if status else "❌"
            report.append(f"{icon} **{name}**: {msg}")
            if not status:
                failures.append(f"{name}: {msg}")
        
        # If failures, alert immediately
        if failures:
            self.send_alert("\n".join(failures))
            logger.error("❌ ISSUES DETECTED")
        else:
            logger.info("✅ SYSTEM HEALTHY")
            
        return failures

if __name__ == "__main__":
    dog = Watchdog()
    dog.run_diagnostics()
