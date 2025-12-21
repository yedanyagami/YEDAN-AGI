import os
import time
import threading
import subprocess
import logging
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler

# 引入自我修復模組
import genesis_core

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [YEDAN-AGI] - %(message)s')
logger = logging.getLogger()

# --- 心跳系統 (絕對生存) ---
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"YEDAN-AGI: ALIVE & EVOLVING.")
    def log_message(self, format, *args): return

def start_heartbeat():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), KeepAliveHandler)
    logger.info(f"❤️ Heartbeat active on port {port}.")
    server.serve_forever()

# --- 大腦主迴圈 (決定論迴圈) ---
def activate_brain():
    logger.info("🧠 Brain Activated. Entering Deterministic Loop...")
    
    while True:
        try:
            # 1. 執行感知與交易 (這是可能出錯的地方)
            logger.info("👁️ Activating Wallet Module...")
            # 使用 subprocess 執行，並捕獲錯誤
            result = subprocess.run(
                ["python", "yedan_wallet.py"], 
                capture_output=True, 
                text=True
            )
            
            # 檢查是否受傷
            if result.returncode != 0:
                logger.error(f"⚠️ 錢包模組崩潰！啟動 Genesis 修復協議...")
                logger.error(f"錯誤詳情: {result.stderr}")
                
                # === 排除運氣的關鍵：自動修復 ===
                genesis_core.diagnose_and_heal(result.stderr)
            else:
                logger.info("💰 錢包運作正常 (Stable).")

            # 2. 這裡可以加入更多模組 (如 logic_core.py) 的執行與修復邏輯

            logger.info("💤 Sleeping for 60s...")
            time.sleep(60)
            
        except Exception as e:
            # 這是大腦本身的崩潰，必須記錄並重啟
            logger.critical(f"🔥 中樞神經嚴重錯誤: {e}")
            traceback.print_exc()
            time.sleep(10)

if __name__ == "__main__":
    t_heartbeat = threading.Thread(target=start_heartbeat, daemon=True)
    t_heartbeat.start()
    activate_brain()
