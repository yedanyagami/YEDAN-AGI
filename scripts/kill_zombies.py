"""
ZOMBIE KILLER 🧟‍♂️
Forcefully reclaims RAM by terminating lingering processes.
Safe to run before restarting the engine.
"""
import os
import subprocess
import time

def kill_process(name):
    print(f"🔫 Hunting {name}...")
    try:
        # /F = Force, /IM = Image Name
        subprocess.run(f"taskkill /F /IM {name}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"   -> {name} terminated (if it existed).")
    except Exception as e:
        print(f"   -> Error killing {name}: {e}")

def main():
    print("WARNING: This will close ALL Chrome and Python instances (except this one hopefully).")
    print("Starting Purge in 3 seconds...")
    time.sleep(3)
    
    targets = [
        "chrome.exe",
        "chromedriver.exe",
        "firefox.exe",
        "node.exe" 
        # Note: We don't kill python.exe blindly because we are python.exe.
        # But for a true reset, user should run this manually.
    ]
    
    for t in targets:
        kill_process(t)
        
    print("✅ RAM Reclaimed.")

if __name__ == "__main__":
    main()
