
"""
# FILE: neural_symbolic_guard.py
YEDAN AGI: NEURO-SYMBOLIC GUARD
Symbolic Logic Gatekeeper to prevent Neural Hallucinations (Risk > Logic).
"""
from pydantic import BaseModel, field_validator, ValidationError
from typing import Optional

class FinancialAction(BaseModel):
    action_type: str
    amount: float
    platform: str
    target_id: Optional[str] = None

    # [SYMBOLIC LOGIC] Hard constraints
    @field_validator('amount')
    @classmethod
    def check_risk_tolerance(cls, v: float) -> float:
        # [V5.4 REAL-WORLD MOD] SafetyGuard Hard Parameters
        MAX_DAILY_SPEND = 50.0 # Hard Limit
        MAX_RISK_PER_TRADE = 0.02 # 2% Risk Limit
        
        # Mocking wallet balance for safety check
        # In real-world, this would query the DB/Wallet API
        TOTAL_CAPITAL = 1000.0 
        
        # 1. 5% Daily Cap Check (Simplified as fixed $50 for now)
        if v > MAX_DAILY_SPEND:
             raise ValueError(f"Risk Alert: ${v} exceeds daily cap (${MAX_DAILY_SPEND})")

        # 2. 2% Risk Limit Check
        # Ensure single trade doesn't risk > 2% of total capital
        risk_limit = TOTAL_CAPITAL * MAX_RISK_PER_TRADE
        if v > risk_limit:
            raise ValueError(f"⚠️ SafetyGuard Triggered: ${v} exceeds 2% risk limit (${risk_limit})")

        if v < 0:
            raise ValueError("Risk Alert: Negative spend detected.")
        return v
    
    @field_validator('platform')
    @classmethod
    def check_platform_trust(cls, v: str) -> str:
        TRUSTED_PLATFORMS = ["reddit_ads", "twitter_ads", "shopify_app_store"]
        if v.lower() not in TRUSTED_PLATFORMS:
            raise ValueError(f"Risk Alert: Platform '{v}' is not in TRUSTED_PLATFORMS.")
        return v

def neuro_symbolic_decision(proposal_dict):
    """
    Validates a raw dictionary (from AI) against Symbolic Logic.
    Returns: (Accepted (bool), Message (str))
    """
    try:
        # 2. Symbolic Logic Review
        action = FinancialAction(**proposal_dict)
        return True, f"Action Approved: {action}"
    except ValidationError as e:
        # Log constraint violations
        errors = e.errors()
        msg = f"[LOGIC BLOCK] Neural proposal rejected. Reason: {errors[0]['msg']}"
        print(msg)
        return False, msg
    except Exception as e:
        msg = f"[LOGIC BLOCK] Unknown error: {e}"
        print(msg)
        return False, msg

if __name__ == "__main__":
    # Test
    risky_proposal = {"action_type": "ad_spend", "amount": 1000.0, "platform": "reddit_ads"}
    safe_proposal = {"action_type": "ad_spend", "amount": 25.0, "platform": "reddit_ads"}
    
    print(neuro_symbolic_decision(risky_proposal))
    print(neuro_symbolic_decision(safe_proposal))
