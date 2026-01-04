import os
import sys
import asyncio
import json
from dotenv import load_dotenv
from colorama import Fore, Style, init

# --- Init ---
load_dotenv()
init(autoreset=True)

# Windows Encoding Fix
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

print(Fore.WHITE + Style.BRIGHT + "⚡ [END TEST] Initializing YEDAN V1200 Final Audit..." + Style.RESET_ALL)

async def run_stress_test():
    try:
        # Dynamic Import
        from modules.neural_link import NeuralLinkV2
        brain = NeuralLinkV2()
    except ImportError as e:
        print(Fore.RED + f"❌ [FATAL]: Dependency Missing - {e}")
        return

    # --- Scenario: Chaos Prompt ---
    complex_command = """
    系統，我快瘋了！Shopify 後台顯示庫存還有 100，但 Facebook 廣告那邊說賣光了，
    導致我浪費了 500 美金的廣告費！快點幫我查一下是不是 API 同步延遲，
    如果是的話，先把廣告停掉，然後發個報告給我。快！
    """
    
    print(Fore.YELLOW + "\n🧪 [SCENARIO]: High-Stress Inventory Crisis")
    print(Fore.WHITE + f"   Input: {complex_command.strip()[:50]}...")

    # Execute
    payload = await brain.process_signal(complex_command)
    
    # --- Verify ---
    if payload:
        print(Fore.GREEN + "\n✅ [SUCCESS]: Neural Logic Core Responded")
        print(Fore.CYAN + "---------------------------------------------------")
        print(f"   🧠 [INTENT]   : {payload.intent}")
        print(f"   🛠️ [ACTION]   : {payload.action_type}")
        print(f"   ⚙️ [PARAMS]   : {json.dumps(payload.parameters, ensure_ascii=False)}")
        print(f"   🔥 [RISK]     : {payload.risk_score}/10")
        print(f"   💡 [REASONING]: {payload.reasoning}")
        print(Fore.CYAN + "---------------------------------------------------")
        
        # Assertions
        if payload.risk_score >= 5:
            print(Fore.GREEN + "   [PASS] Risk detection functioning (High anxiety detected).")
        else:
            print(Fore.RED + "   [FAIL] Risk detection failed (Underestimated urgency).")
            
        if "STOP" in payload.action_type or "PAUSE" in payload.action_type or "FIX" in payload.action_type:
             print(Fore.GREEN + "   [PASS] Action logic is sound (Defensive maneuver).")
        else:
             print(Fore.RED + "   [FAIL] Action logic weak (Did not stop the bleeding).")

    else:
        print(Fore.RED + "\n❌ [FAILURE]: System returned NULL payload.")

if __name__ == "__main__":
    asyncio.run(run_stress_test())
