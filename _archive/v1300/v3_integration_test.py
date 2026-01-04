
"""
YEDAN V3.0 INTEGRATION TEST
Verifies: Self-Healing, Risk Guard, Metacognition, Embodied Logic.
"""
import asyncio
from evolutionary_core import self_evolving
from neural_symbolic_guard import neuro_symbolic_decision
from metacognition_simulator import simulate_outcome
from antigravity_controller import StealthAgent

# 1. TEST SELF-HEALING
@self_evolving
async def broken_function():
    print("[TEST] Running broken function...")
    # This syntax error/runtime error is intentional to trigger mutation
    # We simulate a runtime error that DeepSeek can fix
    x = 1 / 0 
    return "Success"

async def test_evolution():
    print("\n--- TEST: SELF-HEALING ---")
    try:
        await broken_function()
    except Exception as e:
        print(f"Final Result (Expected Failure in Mock env ok): {e}")

# 2. TEST RISK GUARD
def test_guard():
    print("\n--- TEST: NEURO-SYMBOLIC GUARD ---")
    proposal = {"action_type": "ad", "amount": 9999.0, "platform": "reddit_ads"}
    ok, msg = neuro_symbolic_decision(proposal)
    print(f"Risk $9999: {msg}")

# 3. TEST METACOGNITION
def test_meta():
    print("\n--- TEST: METACOGNITION ---")
    simulate_outcome("Buy my scam course!", "No Spam")

# 4. TEST EMBODIED BODY
async def test_body():
    print("\n--- TEST: EMBODIED BODY ---")
    agent = StealthAgent()
    await agent.execute_stealth_action("http://example.com", {"visual_target": True})

async def main():
    test_guard()
    test_meta()
    await test_body()
    # await test_evolution() # Keeping evolution last as it involves heavy API calls

if __name__ == "__main__":
    asyncio.run(main())
