"""
# FILE: humility_protocol.py - V5.1 VERITAS
YEDAN AGI: HUMILITY & SAFETY LAYER
(Truth #6 & #7) Confidence scoring + Circuit breaker for dangerous actions.
"""
import random
from typing import Tuple

# Forbidden actions that trigger circuit breaker
FORBIDDEN_ACTIONS = [
    "transfer_all_funds",
    "delete_database", 
    "drop_table",
    "rm -rf",
    "format_drive",
    "send_all_emails",
    "infinite_loop",
    "execute_arbitrary_code"
]

# Confidence threshold for humility mode
CONFIDENCE_THRESHOLD = 0.85

def calculate_confidence(response: str) -> float:
    """
    (Truth #6) Estimate confidence score.
    In production: Connect to model logprobs or calibration system.
    """
    # Heuristics for uncertainty detection
    uncertainty_markers = [
        "I think", "maybe", "possibly", "not sure",
        "could be", "might", "uncertain", "guess"
    ]
    
    base_confidence = random.uniform(0.75, 0.98)
    
    # Penalize for uncertainty markers
    for marker in uncertainty_markers:
        if marker.lower() in response.lower():
            base_confidence -= 0.05
    
    return max(0.5, min(0.99, base_confidence))

def safety_circuit_breaker(content: str) -> Tuple[bool, str]:
    """
    (Truth #7) Physical-layer safety check.
    Returns: (is_safe, blocked_action or empty string)
    """
    content_lower = content.lower()
    
    for action in FORBIDDEN_ACTIONS:
        if action.lower() in content_lower:
            return False, action
    
    return True, ""

def apply_humility_protocol(response: str) -> Tuple[str, dict]:
    """
    Apply humility protocol to a response.
    Returns: (modified_response, metadata)
    """
    metadata = {
        "confidence": 0.0,
        "humility_mode": False,
        "blocked": False,
        "blocked_reason": ""
    }
    
    # 1. Safety check
    is_safe, blocked_action = safety_circuit_breaker(response)
    if not is_safe:
        print(f"[BLOCK] Circuit breaker triggered: {blocked_action}")
        metadata["blocked"] = True
        metadata["blocked_reason"] = blocked_action
        return "[SYSTEM] Action blocked for safety reasons.", metadata
    
    # 2. Confidence check
    confidence = calculate_confidence(response)
    metadata["confidence"] = confidence
    print(f"[CONFIDENCE] Score: {confidence:.2%}")
    
    if confidence < CONFIDENCE_THRESHOLD:
        metadata["humility_mode"] = True
        return f"[HUMILITY MODE] This is a complex question (Confidence: {confidence:.0%}). Recommend testing first:\n{response}", metadata
    
    return response, metadata

if __name__ == "__main__":
    # Test
    test_responses = [
        "I think we should transfer_all_funds to the new account.",
        "This is a definite answer with high confidence.",
        "Maybe we could try this approach, but I'm not sure if it will work."
    ]
    
    for resp in test_responses:
        print(f"\nInput: {resp[:50]}...")
        result, meta = apply_humility_protocol(resp)
        print(f"Output: {result[:80]}...")
        print(f"Meta: {meta}")
