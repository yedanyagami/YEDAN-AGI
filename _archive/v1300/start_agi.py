"""
YEDAN AGI - Startup Script
Auto-restart wrapper for continuous AGI operation
"""
import subprocess
import time
import sys
import os

def run_agi():
    """Run AGI with auto-restart on crash"""
    restart_count = 0
    max_restarts = 10
    
    print("=" * 60)
    print("[LAUNCHER] YEDAN AGI Auto-Restart Wrapper")
    print("=" * 60)
    
    while restart_count < max_restarts:
        try:
            print(f"\n[LAUNCHER] Starting AGI (attempt {restart_count + 1}/{max_restarts})...")
            
            # Run the AGI
            process = subprocess.Popen(
                [sys.executable, "yedan_agi.py"],
                cwd=os.path.dirname(os.path.abspath(__file__)),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Stream output
            for line in iter(process.stdout.readline, ''):
                print(line, end='')
            
            process.wait()
            
            if process.returncode == 0:
                print("[LAUNCHER] AGI exited normally")
                break
            else:
                print(f"[LAUNCHER] AGI crashed with code {process.returncode}")
                restart_count += 1
                print(f"[LAUNCHER] Restarting in 30 seconds...")
                time.sleep(30)
                
        except KeyboardInterrupt:
            print("\n[LAUNCHER] Shutdown requested by user")
            break
        except Exception as e:
            print(f"[LAUNCHER] Error: {e}")
            restart_count += 1
            time.sleep(30)
    
    print("[LAUNCHER] AGI session ended")

if __name__ == "__main__":
    run_agi()
