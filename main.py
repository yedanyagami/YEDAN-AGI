import os
import time
import threading
import subprocess
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- 配置區 ---
REDIS_URL = os.getenv("REDIS_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GITHUB_TOKEN = os.getenv("GH_PAT")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [YEDAN-AGI] - %(message)s')
logger = logging.getLogger()

# --- 1. 心跳系統 (Heartbeat) ---
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"YEDAN-AGI: SYSTEM ONLINE. OMEGA STABLE.")
    def log_message(self, format, *args): return

def start_heartbeat():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), KeepAliveHandler)
    logger.info(f"❤️ Heartbeat System active on port {port}.")
    server.serve_forever()

# --- 2. 大腦主迴圈 ---
def activate_brain():
    while True:
        try:
            logger.info("👁️ Nexus Eye: Activating Wallet Module...")
            
            # === 這裡執行剛寫好的錢包腳本 ===
            subprocess.run(["python", "yedan_wallet.py"], check=False)
            
            # 嘗試執行邏輯核心 (如果有)
            if os.path.exists("logic_core.py"):
                subprocess.run(["python", "logic_core.py"], check=False)
            
            # 自我反思
            if os.path.exists("self_reflection.py"):
                subprocess.run(["python", "self_reflection.py"], check=False)

            logger.info("💤 Brain entering sleep cycle (60s)...")
            time.sleep(60)
            
        except Exception as e:
            logger.error(f"Brain Seizure: {e}")
            time.sleep(10)

if __name__ == "__main__":
    logger.info("🚀 INITIALIZING YEDAN-AGI OMEGA...")
    t_heartbeat = threading.Thread(target=start_heartbeat, daemon=True)
    t_heartbeat.start()
    activate_brain()
