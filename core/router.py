
import random
from typing import Dict, Any, Tuple

class MetaCognitiveRouter:
    """
    [SOFAI Architecture] Meta-Cognitive Router
    
    Implements a dual-process theory (System 1 vs System 2) arbitration mechanism.
    
    Phases:
    1. MC1 (Fast Gate): Risk Assessment & S1 Confidence Check.
    2. MC2 (Deliberation Gate): Value of Information (VOI) Analysis.
    
    Goal: "Don't spend $10 of compute to save $5."
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.CONFIDENCE_THRESHOLD = 0.85  # System 1 must be this sure to bypass System 2
        self.COST_THRESHOLD_USD = 50.0    # If risk is below this $, always use Fast Lane
        self.API_COST_SYSTEM_2 = 0.50     # Est. cost of a deep thinking cycle
        
    def _system_1_fast_predict(self, context: Dict[str, Any]) -> Tuple[str, float]:
        """
        [System 1] Intuition / Heuristic Rule Base (Fast & Cheap)
        
        In a real scenario, this would be a lightweight ML model or
        lookup table based on historical data.
        
        Returns:
            (Proposed Action, Confidence Score)
        """
        # Simulation: fast intuition based on data quality
        # If we have good data, System 1 is confident.
        data_quality = context.get('data_quality_score', 0.5)
        
        # Simple heuristic: Confidence scales with data quality
        # 0.5 quality -> 0.75 confidence
        # 0.8 quality -> 0.99 confidence
        predicted_confidence = min(data_quality * 1.5, 0.99)
        
        # System 1 usually suggests "Maintain" or "Small Tweak"
        return "MAINTAIN_STATUS_QUO", predicted_confidence

    def _assess_value_of_information(self, context: Dict[str, Any]) -> bool:
        """
        [MC2] Value of Information (VOI) Analysis.
        
        Calculates if the expected gain from "Thinking Harder" (System 2)
        exceeds the cost of thinking (Tokens/Time).
        """
        potential_revenue = context.get('potential_revenue', 0.0)
        profit_margin = 0.2
        
        # Assumption: System 2 can optimize the outcome by +10% relative to System 1
        expected_gain = potential_revenue * profit_margin * 0.10
        
        if expected_gain < self.API_COST_SYSTEM_2:
            print(f"📉 [MC2] VOI Analysis: Gain (${expected_gain:.2f}) < Cost (${self.API_COST_SYSTEM_2}). Skip thinking.")
            return False
            
        print(f"📈 [MC2] VOI Analysis: Gain (${expected_gain:.2f}) > Cost (${self.API_COST_SYSTEM_2}). Worth thinking.")
        return True

    def route_decision(self, context: Dict[str, Any]) -> str:
        """
        [SOFAI Core] Arbitration Algorithm
        
        Returns:
            "SYSTEM_1_EXECUTE" | "SYSTEM_2_REASON" | "PASS"
        """
        print("\n🚦 [ROUTER] Processing Request...")

        # --- Phase 1: MC1 (Fast Risk Assessment) ---
        # If the stakes are trivial, forced Fast Lane.
        current_value = context.get('potential_revenue', 0.0)
        if current_value < self.COST_THRESHOLD_USD:
            print(f"⚡ [FAST LANE] Low Risk (Value ${current_value:.2f} < ${self.COST_THRESHOLD_USD}). Using System 1.")
            return "SYSTEM_1_EXECUTE"

        # --- Phase 2: System 1 Prediction ---
        fast_action, fast_confidence = self._system_1_fast_predict(context)
        print(f"   -> System 1 Proposal: {fast_action} (Confidence: {fast_confidence:.2f})")

        # --- Phase 3: Confidence Gate ---
        if fast_confidence >= self.CONFIDENCE_THRESHOLD:
            print(f"🚀 [FAST LANE] High Confidence ({fast_confidence:.2f} >= {self.CONFIDENCE_THRESHOLD}). Executing System 1.")
            return "SYSTEM_1_EXECUTE"

        # --- Phase 4: MC2 (Deliberation Gate) ---
        # Only activate System 2 if confidence is low AND it's worth the cost.
        if self._assess_value_of_information(context):
            print(f"🤔 [SLOW LANE] Low Confidence & High Value. Escalating to System 2...")
            return "SYSTEM_2_REASON"
        else:
            print(f"🛑 [BLOCK] Confidence low, but not worth thinking cost. Defaulting to Safety (PASS).")
            return "PASS"
