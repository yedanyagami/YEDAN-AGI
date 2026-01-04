import os
import sys
import asyncio
from dotenv import load_dotenv

# 1. Priority Env Load
load_dotenv()

# 2. Windows Encoding Fix
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

print("[BOOT SEQUENCE] Initializing YEDAN-ANTIGRAVITY V1200...")

async def system_check():
    try:
        from modules.neural_link import NeuralLinkV2
    except ImportError as e:
        print(f"\n[CRITICAL ERROR] Dependency Missing: {e}")
        print("Solution: Please run 'pip install -r requirements.txt'")
        return

    brain = NeuralLinkV2()
    
    print("\n---------------------------------------------------")
    print("[TEST SCENARIO]: User reports Shopify API Failure")
    print("---------------------------------------------------")
    
    # Test Chinese Input
    test_command = "幫我看看這個 Shopify API 報錯是怎麼回事 (測試中文編碼)"
    test_image = "http://mock-image.com/error.jpg"
    
    payload = await brain.process_signal(test_command, image_url=test_image)
    
    if payload:
        print("\n[SYSTEM OUTPUT]:")
        print(f"   > ACTION: {payload.action_type}")
        print(f"   > REASONING: {payload.reasoning}")
        print(f"   > RISK SCORE: {payload.risk_score}/10")
        print("\n[STATUS]: SYSTEM GREEN. READY FOR DEPLOYMENT.")
    else:
        print("\n[STATUS]: SYSTEM FAILED.")

if __name__ == "__main__":
    try:
        asyncio.run(system_check())
    except KeyboardInterrupt:
        print("\nSystem Halted by User.")
