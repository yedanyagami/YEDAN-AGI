import multiprocessing
from multiprocessing import shared_memory, resource_tracker
import time
import os

def test_shm_hack():
    name = "yedan_test_shm"
    size = 1024
    
    print(f"[TEST] Creating SharedMemory: {name}...")
    try:
        shm = shared_memory.SharedMemory(name=name, create=True, size=size)
    except FileExistsError:
        shm = shared_memory.SharedMemory(name=name)

    print("[TEST] SharedMemory Created.")
    print(f"[TEST] Attempting 'Zombie Killer' Hack (unregistering {name})...")
    
    # THE HACK verification
    try:
        # Python 3.8+ changed resource_tracker internals slightly, checking if this valid
        resource_tracker.unregister(shm._name, "shared_memory")
        print("[SUCCESS] Unregistered from resource_tracker without error.")
    except Exception as e:
        print(f"[FAILURE] Hack failed: {e}")
        return

    print("[TEST] Writing data...")
    shm.buf[0] = 1
    
    print("[TEST] Closing...")
    shm.close()
    
    print("[TEST] Unlinking (Manually)...")
    try:
        shm.unlink()
        print("[SUCCESS] Unlinked successfully.")
    except Exception as e:
        print(f"[FAILURE] Unlink failed (Checking if double-free happens): {e}")

if __name__ == "__main__":
    test_shm_hack()
