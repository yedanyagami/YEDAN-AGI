import sys
import os
sys.path.append(os.getcwd())
print("Attempting imports...")
try:
    from modules.config import Config
    print("Config loaded.")
    # Mocking run_roi_loop execution to avoid starting the loop
    import run_roi_loop
    print("Engine loaded.")
except ImportError as e:
    print(f"FAILED: {e}")
    sys.exit(1)
print("Sanity Check Passed.")
