import os
import time
import threading
import subprocess
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [YEDAN-AGI] - %(message)s')
logger = logging.getLogger()

# --- 心跳系統 ---
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"YEDAN-AGI: ONLINE.")
    def log_message(self, format, *args): return

def start_heartbeat():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), KeepAliveHandler)
    logger.info(f"❤️ Heartbeat active on port {port}.")
    server.serve_forever()

# --- 大腦主迴圈 ---
def activate_brain():
    logger.info("🧠 Brain Activated. Starting Loop...")
    while True:
        try:
            logger.info("👁️ Activating Wallet Module (Gmail Scan)...")
            subprocess.run(["python", "yedan_wallet.py"], check=False)
            
            logger.info("💤 Sleeping for 60s...")
            time.sleep(60)
            
        except Exception as e:
            logger.error(f"Brain Seizure: {e}")
            time.sleep(10)

if __name__ == "__main__":
    t_heartbeat = threading.Thread(target=start_heartbeat, daemon=True)
    t_heartbeat.start()
    activate_brain()
