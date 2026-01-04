"""
Fix Camoufox Download
Aggressively retries the Camoufox browser download until successful.
Handles network interruptions/timeouts automatically.
"""
import subprocess
import time
import sys
import os

def install_camoufox():
    max_retries = 50
    print(f"[*] Starting Robust Camoufox Downloader...")
    
    # Clean up potentially corrupted partial downloads if possible?
    # Camoufox usually handles this, but we'll trust the tool first.
    
    for i in range(max_retries):
        print(f"\n[Attempt {i+1}/{max_retries}] Fetching Camoufox binary...")
        try:
            # Using -m camoufox fetch to trigger the standard downloader
            # Using a larger timeout if implicit, but here we just catch the crash
            start_time = time.time()
            result = subprocess.run(
                [sys.executable, "-m", "camoufox", "fetch"], 
                check=True,
                capture_output=False  # Let output flow to console for visibility
            )
            print(f"✅ Download Complete! (Time: {time.time() - start_time:.1f}s)")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Attempt failed (Exit code {e.returncode}). Retrying in 5s...")
            time.sleep(5)
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            time.sleep(5)
            
    print("!! Critical Failure: Could not download after all retries.")
    sys.exit(1)

if __name__ == "__main__":
    success = install_camoufox()
    if success:
        # Verify
        print("Verifying installation...")
        try:
            from camoufox.engine import get_executable_path
            path = get_executable_path()
            print(f"Binary found at: {path}")
        except Exception as e:
            print(f"Verification warning: {e}")
