"""
THE BIG RED BUTTON 🔴
Ignites the YEDAN Engine V2.0 in ULTRA MODE.
Verifies all systems are GO before launch.
"""
import sys
import os
import time
import requests
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.config import Config, setup_logging

logger = setup_logging("IGNITION")

def check_system():
    print("\n🚀 INITIALIZING PRE-FLIGHT CHECKS...")
    all_clear = True
    
    # 1. Check Config Modes
    if Config.SAFETY_MODE:
        print("❌ SAFETY_MODE is ON. Engine is Leashed.")
        all_clear = False
    else:
        print("✅ SAFETY_MODE is OFF. Weapons Free.")
        
    if Config.DRY_RUN:
        print("❌ DRY_RUN is ON. Revenue is Simulated.")
        all_clear = False
    else:
        print("✅ DRY_RUN is OFF. Real Money Active.")
        
    if not Config.ECO_MODE:
        print("⚠️ ECO_MODE is OFF. High RAM Usage Expected.")
    else:
        print("✅ ECO_MODE is ON. Stealth & Efficiency Optimized.")
        
    # 2. Check Internet/Synapse
    try:
        r = requests.get(f"{Config.SYNAPSE_URL}/health", timeout=5)
        if r.status_code == 200:
             print("✅ Synapse Cloud: CONNECTED")
        else:
             print(f"❌ Synapse Cloud: ERROR ({r.status_code})")
             all_clear = False
    except:
        print("❌ Synapse Cloud: UNREACHABLE")
        all_clear = False
        
    # 3. Check n8n
    try:
        # Assuming n8n has a basic health check or we check the webhook
        r = requests.get(Config.N8N_BASE_URL, timeout=5, headers={"X-N8N-API-KEY": Config.N8N_API_TOKEN})
        # 404 or 200 is fine, connection is what matters
        print("✅ n8n Cloud: REACHABLE")
    except:
        print("⚠️ n8n Cloud: UNREACHABLE (Automation may fail)")
        # Non-blocking for now
        
    return all_clear

def launch():
    print("\n🔥 IGNITING ENGINE...")
    time.sleep(2)
    # Execute the bat file or the python script directly
    if sys.platform == "win32":
        os.system("start start_v2.bat")
    else:
        # Fallback for non-windows (though user is windows)
        os.system("python run_roi_loop.py")
    
    print("✅ ENGINE LAUNCHED. GOOD LUCK, REVENUE ARCHITECT.")

if __name__ == "__main__":
    if check_system():
        launch()
    else:
        print("\n⛔ LAUNCH ABORTED DUE TO FAILED CHECKS.")
        input("Press Enter to scan again...")
