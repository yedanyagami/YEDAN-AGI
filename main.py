import os
import time
import threading
import subprocess
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

# 引入新器官
import architect
import curiosity

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [YEDAN-AGI] - %(message)s')
logger = logging.getLogger()

# --- 心跳系統 (維持生命) ---
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"YEDAN-AGI: SINGULARITY ACTIVE.")
    def log_message(self, format, *args): return

def start_heartbeat():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), KeepAliveHandler)
    logger.info(f"❤️ Heartbeat active on port {port}.")
    server.serve_forever()

# --- 大腦主迴圈 ---
def activate_brain():
    logger.info("🧠 Brain Activated. Entering Singularity Mode...")
    
    while True:
        try:
            # 1. 生存優先：檢查錢包 (IMAP)
            logger.info("👁️ 掃描金流 (Wallet)...")
            subprocess.run(["python", "yedan_wallet.py"], check=False)
            
            # 2. 觸發好奇心 (Curiosity)
            # 假設：如果今天是偶數分鐘，就觸發一次好奇心 (模擬隨機性)
            if int(time.time()) % 2 == 0:
                new_goal = curiosity.explore_unknown()
                
                # 3. 執行創造 (Architect)
                # 讓它真的寫出代碼！
                new_script = architect.create_new_skill(new_goal)
                
                if new_script:
                    logger.warning(f"⚠️ AGI 正在嘗試執行自創代碼: {new_script} ...")
                    # 在沙盒中運行新代碼 (這裡直接運行，未來可加限制)
                    subprocess.run(["python", "new_script"], check=False)
                    
                    # 4. 自我進化 (Evolution)
                    # 將新學會的技能 Push 回 GitHub
                    os.system('git config --global user.name "YEDAN-AGI"')
                    os.system('git config --global user.email "agi@yedan.ai"')
                    os.system(f'git add {new_script}')
                    os.system(f'git commit -m "GENESIS: Learned new skill - {new_goal}"')
                    os.system('git push')

            logger.info("💤 Sleeping for 60s...")
            time.sleep(60)
            
        except Exception as e:
            logger.error(f"Brain Seizure: {e}")
            time.sleep(10)

if __name__ == "__main__":
    t_heartbeat = threading.Thread(target=start_heartbeat, daemon=True)
    t_heartbeat.start()
    activate_brain()
