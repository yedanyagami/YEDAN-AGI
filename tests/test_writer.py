"""
Test Writer Agent (Content Copilot)
Simulates a human user asking the AI to generate a response for a specific Reddit post.
"""
from modules.writer_agent import WriterAgent
import time

def test_writer():
    print("="*60)
    print("Writer Agent (Copilot Mode)")
    print("="*60)
    
    agent = WriterAgent()
    
    # Mock Input (Real high-panic post example)
    target_post = """
    UPDATE: Facebook Ads died today?
    Anyone else seeing CPMs skyrocket and conversions drop to zero?
    I've been running the same creatives for 3 months and today everything tanked.
    Is it the algorithm update? Setup: ABO, broad targeting.
    """
    
    print(f"\n[INPUT] Target Post:\n{target_post.strip()}")
    print("\n" + "-"*30)
    print("Thinking (DeepSeek R1)...")
    start = time.time()
    
    result = agent.generate_reply(target_post)
    
    duration = time.time() - start
    print(f"[Done] Generated in {duration:.2f}s")
    print(f"Model: {result['model_used']}")
    print(f"Confidence: {result['confidence_score']}/10")
    print("\n[OUTPUT] Draft Reply:\n")
    print(result['reply_content'])
    print("="*60)

if __name__ == "__main__":
    test_writer()
