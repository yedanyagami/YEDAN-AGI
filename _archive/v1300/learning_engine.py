"""
# FILE: learning_engine.py - V5.1 DISTILLATION
YEDAN AGI: WISDOM DISTILLATION ENGINE
Extracts winning strategies from successful interactions.
(Truth #2) Distills large model wisdom into compact knowledge base.
"""
import json
import os
from datetime import datetime

WISDOM_VAULT = "wisdom_vault.json"

def distill_wisdom(reasoning_logs: list) -> int:
    """
    Distillation Loop: Extract and save only the profitable interactions.
    Returns: Number of golden thoughts saved.
    """
    print("[DISTILLATION] Starting wisdom extraction...")
    
    golden_dataset = []
    for log in reasoning_logs:
        # Only learn from successful (revenue > 0) cases
        if log.get('revenue', 0) > 0:
            golden_dataset.append({
                "timestamp": datetime.now().isoformat(),
                "input": log.get('user_query', ''),
                "output": log.get('final_response', ''),
                "revenue": log.get('revenue', 0),
                "platform": log.get('platform', 'unknown')
            })
            
    if not golden_dataset:
        print("[DISTILLATION] No golden data found. Nothing to distill.")
        return 0

    # Load existing wisdom
    existing_data = []
    if os.path.exists(WISDOM_VAULT):
        try:
            with open(WISDOM_VAULT, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            existing_data = []
    
    # Append new wisdom
    existing_data.extend(golden_dataset)
    
    # Save
    with open(WISDOM_VAULT, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
    print(f"[SAVED] {len(golden_dataset)} golden thoughts distilled into {WISDOM_VAULT}.")
    return len(golden_dataset)

def recall_wisdom(topic: str, limit: int = 3) -> list:
    """
    Recall past successful strategies related to a topic.
    """
    if not os.path.exists(WISDOM_VAULT):
        return []
    
    with open(WISDOM_VAULT, 'r', encoding='utf-8') as f:
        all_wisdom = json.load(f)
    
    # Simple keyword matching (can be upgraded to embeddings)
    relevant = [w for w in all_wisdom if topic.lower() in w.get('input', '').lower()]
    
    # Sort by revenue (highest first)
    relevant.sort(key=lambda x: x.get('revenue', 0), reverse=True)
    
    return relevant[:limit]

if __name__ == "__main__":
    # Test
    test_logs = [
        {"user_query": "How to pitch Shopify agencies?", "final_response": "Use ROI framing...", "revenue": 500, "platform": "email"},
        {"user_query": "Random question", "final_response": "...", "revenue": 0, "platform": "reddit"}
    ]
    distill_wisdom(test_logs)
    print(recall_wisdom("Shopify"))
