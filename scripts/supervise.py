"""
THE INFINITY LOOP (Supervisor)
Ensures the YEDAN Engine never dies.
If it crashes, it logs the error and restarts it.
"""
import subprocess
import time
import logging
from datetime import datetime
import sys
import os

# Setup simple logger
log_dir = os.path.join("logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    filename=os.path.join(log_dir, "supervisor.log"),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('supervisor')

def run_forever():
    logger.info("♾️ SUPERVISOR STARTED: The Money Loop")
    print("♾️ SUPERVISOR STARTED: The Money Loop")
    
    script = "run_roi_loop.py"
    cmd = [sys.executable, script]
    
    restart_count = 0
    
    while True:
        try:
            logger.info(f"🚀 Launching {script} (Attempt {restart_count + 1})...")
            print(f"🚀 Launching {script}...")
            
            # Start process
            process = subprocess.Popen(cmd)
            pid = process.pid
            logger.info(f"   -> PID: {pid}")
            
            # Wait for it to complete (or crash)
            exit_code = process.wait()
            
            if exit_code == 0:
                logger.info("✅ Engine stopped gracefully (Exit Code 0).")
                print("✅ Engine stopped gracefully.")
                # Maybe user asked to stop? But for "Infinity Loop" we might restart anyway?
                # Let's assume standard stop means maintenance, so we pause 10s then restart.
                time.sleep(10)
            else:
                logger.warning(f"⚠️ Engine CRASHED (Exit Code {exit_code}).")
                print(f"⚠️ Engine CRASHED (Exit Code {exit_code}). Restarting in 5s...")
                
            restart_count += 1
            time.sleep(5) # Cool down
            
        except KeyboardInterrupt:
            logger.info("🛑 Supervisor stopped by user.")
            print("\n🛑 Supervisor stopped by user.")
            break
        except Exception as e:
            logger.critical(f"🔥 SUPERVISOR ERROR: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_forever()
