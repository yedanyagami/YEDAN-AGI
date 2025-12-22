
from agi_gems import GemRegistry
from agi_research import AGIResearch
import os

print("[TEST] Initializing Gem Registry...")
reg = GemRegistry()
gems = reg.list_gems()
print(f"[TEST] Available Gems: {gems}")

gem_name = "YEDAN_PRIME"
print(f"[TEST] Testing Prompt Generation for {gem_name}...")
prompt = reg.get_gem_prompt(gem_name)
if "Hedge Fund Analyst" in prompt:
    print("[TEST] Prompt Generation: SUCCESS")
else:
    print("[TEST] Prompt Generation: FAILED")

print("[TEST] Testing Research Module Integration...")
# Mock API key if needed, or rely on env
if os.getenv("GEMINI_API_KEY"):
    res = AGIResearch()
    if res.gems:
        print("[TEST] AGIResearch Gem Integration: SUCCESS")
    else:
        print("[TEST] AGIResearch Gem Integration: FAILED")
else:
    print("[TEST] Skipping API test (no key)")
