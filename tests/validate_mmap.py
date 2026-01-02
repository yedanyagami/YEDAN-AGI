import mmap
import os
import struct
import time

def test_mmap_bridge():
    # Create valid file for mmap (backed by temp file)
    filename = "yedan_bridge.dat"
    size = 1024
    
    # Create sparse file
    with open(filename, "wb") as f:
        f.seek(size - 1)
        f.write(b'\0')
        
    print(f"[TEST] Created backing file: {filename}")

    try:
        # Open mmap
        with open(filename, "r+b") as f:
            # tagname is Windows specific for named shared memory
            mm = mmap.mmap(f.fileno(), size, tagname="Global\\YedanBridge")
            
            print("[TEST] mmap created successfully.")
            
            # Write Float (Strategy Trigger)
            # Write 3.1415 at offset 0
            mm.seek(0)
            mm.write(struct.pack('f', 3.1415))
            
            # Read back
            mm.seek(0)
            val = struct.unpack('f', mm.read(4))[0]
            print(f"[TEST] Read back value: {val}")
            
            assert abs(val - 3.1415) < 1e-4
            print("[SUCCESS] Data integrity verified.")
            
            mm.close()
            print("[TEST] Closed mmap.")
            
    except Exception as e:
        print(f"[FAILURE] mmap failed: {e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)
            print("[TEST] Cleanup done.")

if __name__ == "__main__":
    test_mmap_bridge()
