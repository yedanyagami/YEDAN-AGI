import os
import sys
import ast

class DeepAuditor:
    def __init__(self):
        self.target = "yedan_wallet.py"

    def analyze(self):
        print(f"🔬 DEEP SCANNING: {self.target} ...")
        
        if not os.path.exists(self.target):
            print("❌ File Missing!")
            sys.exit(1)

        with open(self.target, "r") as f:
            source = f.read()
            tree = ast.parse(source)

        # 1. 檢查進口藥水 (Imports)
        imports = [n.names[0].name for n in ast.walk(tree) if isinstance(n, ast.Import)]
        print(f"   - Imports Detected: {imports}")
        if "imaplib" not in imports or "time" not in imports:
             print("❌ CRITICAL: Missing conscious modules (imaplib/time).")
             sys.exit(1)

        # 2. 檢查大腦迴路 (Infinite Loop)
        loops = [n for n in ast.walk(tree) if isinstance(n, ast.While)]
        has_infinite = False
        for loop in loops:
            # 檢查是否為 while True
            if isinstance(loop.test, ast.Constant) and loop.test.value is True:
                has_infinite = True
                print(f"   - Infinite Consciousness Loop: FOUND (Line {loop.lineno})")

        if not has_infinite:
            print("❌ CRITICAL: No 'while True' loop found. AGI will die after one run.")
            sys.exit(1)

        # 3. 檢查環境變數讀取
        secrets_check = "os.environ.get" in source
        if secrets_check:
             print("   - Security Protocol: ACTIVE (Reading Env Vars)")
        else:
             print("❌ CRITICAL: Hardcoded credentials or missing secrets logic.")
             sys.exit(1)

        print("\n✅ AUDIT PASSED: Code structure is IMMORTAL.")
        sys.exit(0)

if __name__ == "__main__":
    DeepAuditor().analyze()
