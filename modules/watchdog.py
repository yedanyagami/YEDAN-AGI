"""
YEDAN WATCHDOG - System Health Monitor
Pings all critical services and reports status to Telegram.
"""
import requests
import logging
import shutil
from datetime import datetime
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

    def check_log_size(self):
        """Check if log file is too large and rotate if needed"""
        try:
            log_path = Config.LOG_DIR / "reactor.log"
            if log_path.exists() and log_path.stat().st_size > 10 * 1024 * 1024: # 10MB
                self.rotate_logs()
                return True, "Rotated"
            return True, "Normal"
        except Exception as e:
            return False, str(e)

    def rotate_logs(self):
        """Archive current log and start fresh"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_dir = Config.LOG_DIR / "archive"
            archive_dir.mkdir(exist_ok=True)
            
            log_path = Config.LOG_DIR / "reactor.log"
            new_path = archive_dir / f"reactor_{timestamp}.log"
            
            # Rename (Atomic on POSIX, usually works on Windows)
            # On Windows, logging handler might lock it. 
            # We assume the main reactor releases it or we force move.
            shutil.move(log_path, new_path)
            
            logger.info(f"♻️ Log rotated: {new_path}")
            self.send_alert(f"Log rotated to {new_path.name}")
        except Exception as e:
            logger.error(f"Log rotation failed: {e}")

    def attempt_heal(self, component: str, error: str):
        """Attempt to fix failed component"""
        logger.info(f"🚑 Attempting to heal {component}...")
        
        if component == "Internet":
            # Can't fix internet, but can log specific diagnostic
            pass
        elif component == "Synapse (Brain)":
            # Retry connection or clear session (conceptual)
            logger.info("Retrying Synapse connection...")
        
        # In a real OS integration, this could restart services
        # e.g., os.system("systemctl restart yedan")

    def run_diagnostics(self):
        """Run all checks and report"""
        logger.info("Running Watchdog diagnostics...")
        
        results = {
            "Internet": self.check_internet(),
            "Synapse (Brain)": self.check_synapse(),
            "Shopify (Store)": self.check_shopify_storefront(),
            "Log Status": self.check_log_size()
        }
        
        failures = []
        report = []
        
        for name, (status, msg) in results.items():
            icon = "✅" if status else "❌"
            report.append(f"{icon} **{name}**: {msg}")
            if not status:
                failures.append(f"{name}: {msg}")
                self.attempt_heal(name, msg)
        
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
