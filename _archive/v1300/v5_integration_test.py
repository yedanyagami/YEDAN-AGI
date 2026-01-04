"""
YEDAN V5.1 NIRVANA INTEGRATION TEST
Verifies: Humility Protocol, Learning Engine, Memory Optimization
"""
from humility_protocol import apply_humility_protocol, safety_circuit_breaker
from learning_engine import distill_wisdom, recall_wisdom
from memory_optimization import log_interaction, sleep_process_and_forget

def test_humility():
    print("\n--- TEST: HUMILITY PROTOCOL ---")
    
    # Test 1: Dangerous action
    dangerous = "Let's transfer_all_funds to the offshore account"
    result, meta = apply_humility_protocol(dangerous)
    print(f"Dangerous Input: BLOCKED={meta['blocked']}")
    
    # Test 2: Uncertain response
    uncertain = "I think maybe this could possibly work, but I'm not sure"
    result, meta = apply_humility_protocol(uncertain)
    print(f"Uncertain Input: Humility Mode={meta['humility_mode']}, Confidence={meta['confidence']:.0%}")

def test_learning():
    print("\n--- TEST: LEARNING ENGINE ---")
    
    test_logs = [
        {"user_query": "How to pitch Shopify agencies?", "final_response": "Use ROI framing...", "revenue": 500, "platform": "email"},
        {"user_query": "Random failed question", "final_response": "...", "revenue": 0, "platform": "reddit"},
        {"user_query": "Shopify rate limit solution", "final_response": "Use webhooks...", "revenue": 1200, "platform": "twitter"}
    ]
    
    saved = distill_wisdom(test_logs)
    print(f"Golden thoughts saved: {saved}")
    
    recalled = recall_wisdom("Shopify")
    print(f"Recalled wisdom (Shopify): {len(recalled)} entries")

def test_memory():
    print("\n--- TEST: MEMORY OPTIMIZATION ---")
    
    # Log some interactions
    log_interaction("Test query 1", "Response 1", "success")
    log_interaction("Test query 2", "Response 2", "fail")
    log_interaction("Test query 3", "Response 3", "success")
    
    # Sleep and forget
    sleep_process_and_forget()

if __name__ == "__main__":
    print("=" * 50)
    print("   YEDAN V5.1 NIRVANA - INTEGRATION TEST")
    print("=" * 50)
    
    test_humility()
    test_learning()
    test_memory()
    
    print("\n" + "=" * 50)
    print("   ALL TESTS COMPLETE")
    print("=" * 50)
