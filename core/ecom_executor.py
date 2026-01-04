#!/usr/bin/env python3
"""
YEDAN AGI - ECOM Executor (Full Autonomous Loop)
Connects the Brain (decision_engine) to the Hands (bridges).

The complete autonomous cycle:
感知 (Perceive) → 思考 (Think) → 行動 (Act)
"""

import os
import sys
import io
import json
from datetime import datetime
from typing import Optional, Dict, Any

# Fix Windows console encoding
if sys.platform == 'win32' and __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Ensure imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules_ecom import bridge_shopify, bridge_gumroad
from core.decision_engine import ECOMDecisionEngine


class ECOMExecutor:
    """
    The Autonomous ECOM Agent.
    Executes the full AGI cycle: Perceive → Think → Act
    """
    
    def __init__(self):
        self.engine = ECOMDecisionEngine()
        self.action_log = []
    
    def execute_decision(self, decision: Dict[str, Any]) -> bool:
        """
        Route decision to appropriate bridge and execute.
        
        Supported actions:
        - UPDATE_PRICE: Change product price
        - MODIFY_COPY: Update description/title
        - HOLD: Do nothing
        - RETARGET: (Future) Adjust ad targeting
        """
        if not decision:
            print("⚠️ No decision to execute")
            return False
        
        action_type = decision.get("decision", "").upper()
        params = decision.get("parameters", {})
        
        print(f"\n⚡ [EXECUTOR] Action: {action_type}")
        print(f"   Parameters: {json.dumps(params, indent=2, ensure_ascii=False)}")
        
        # Log action attempt
        self.action_log.append({
            "timestamp": datetime.now().isoformat(),
            "action": action_type,
            "params": params,
            "executed": False
        })
        
        # Route to handler
        success = False
        
        if action_type in ["UPDATE_PRICE", "ADJUST_PRICE"]:
            success = self._handle_price_update(params)
            
        elif action_type in ["MODIFY_COPY", "UPDATE_COPY", "OPTIMIZE_COPY"]:
            success = self._handle_copy_update(params)
            
        elif action_type == "HOLD":
            print("   🙌 Decision: HOLD - No action taken")
            success = True
            
        elif action_type == "RETARGET":
            print("   🎯 RETARGET not implemented yet")
            success = False
            
        else:
            print(f"   ⚠️ Unknown action type: {action_type}")
            success = False
        
        # Update log
        self.action_log[-1]["executed"] = success
        
        return success
    
    def _get_platform(self, params: Dict) -> str:
        """Extract platform from params, default to gumroad."""
        return params.get("platform", "gumroad").lower()
    
    def _handle_price_update(self, params: Dict) -> bool:
        """Handle price update action."""
        platform = self._get_platform(params)
        product_id = params.get("product_id")
        new_price = params.get("new_price") or params.get("price")
        
        if not product_id:
            print("   ❌ Missing product_id")
            return False
        
        if not new_price:
            print("   ❌ Missing new_price")
            return False
        
        try:
            new_price = float(new_price)
        except (ValueError, TypeError):
            print(f"   ❌ Invalid price: {new_price}")
            return False
        
        print(f"   Platform: {platform}")
        print(f"   Product: {product_id}")
        print(f"   New Price: ${new_price}")
        
        if platform == "shopify":
            return bridge_shopify.update_price(product_id, new_price)
        elif platform == "gumroad":
            return bridge_gumroad.update_price(product_id, new_price)
        else:
            print(f"   ❌ Unsupported platform: {platform}")
            return False
    
    def _handle_copy_update(self, params: Dict) -> bool:
        """Handle copy/description update action."""
        platform = self._get_platform(params)
        product_id = params.get("product_id")
        content = params.get("content") or params.get("description")
        target = params.get("target", "description")  # description, title, etc.
        
        if not product_id:
            print("   ❌ Missing product_id")
            return False
        
        if not content:
            print("   ❌ Missing content")
            return False
        
        print(f"   Platform: {platform}")
        print(f"   Product: {product_id}")
        print(f"   Target: {target}")
        print(f"   Content preview: {content[:100]}...")
        
        if platform == "shopify":
            if target == "title":
                return bridge_shopify.update_title(product_id, content)
            else:
                return bridge_shopify.update_description(product_id, content)
        elif platform == "gumroad":
            if target == "title" or target == "name":
                return bridge_gumroad.update_product(product_id, new_name=content) is not None
            else:
                return bridge_gumroad.update_description(product_id, content)
        else:
            print(f"   ❌ Unsupported platform: {platform}")
            return False
    
    def run_cycle(self, trigger_event: str = "daily_optimization_check") -> bool:
        """
        [ULTRA UPGRADE] AGI cycle with Confidence Safety Valve.
        
        Truth #6: AI must know when NOT to act.
        If confidence < 80%, action is aborted. Better to do nothing than do wrong.
        
        Cycle: Perceive → Think (3-step) → Validate Confidence → Act
        """
        
        # [DYNAMIC CONFIDENCE] Read from config
        # Load config to check risk tolerance
        current_threshold = 0.80 # Default
        try:
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                    params = cfg.get("strategy_parameters", {})
                    risk = params.get("risk_tolerance", "medium").lower()
                    
                    if risk in ["high", "aggressive", "profit_maximization"]:
                        current_threshold = 0.60
                    elif risk in ["medium", "balanced"]:
                        current_threshold = 0.70
                    else:
                        current_threshold = 0.85
        except Exception as e:
            print(f"⚠️ Error reading config for threshold: {e}")

        # CONFIDENCE_THRESHOLD = 0.80 (OLD)
        CONFIDENCE_THRESHOLD = current_threshold
        
        print("\n" + "=" * 60)
        print("🤖 [YEDAN AGI] Starting Autonomous ECOM Cycle")
        print(f"   Trigger: {trigger_event}")
        print(f"   Time: {datetime.now().isoformat()}")
        print(f"   Confidence Threshold: {CONFIDENCE_THRESHOLD:.0%} (Risk Mode: {params.get('risk_tolerance', 'default')})")
        print("=" * 60)
        
        # 1. THINK - Run 3-step recursive critic loop
        decision = self.engine.analyze_and_decide(trigger_event=trigger_event)
        
        if not decision:
            print("\n⚠️ Brain returned silence (No valid JSON). Sleeping.")
            return False
        
        # 2. EXTRACT DECISION METADATA
        action_type = decision.get("decision", "HOLD").upper()
        confidence = float(decision.get("confidence_score", 0.0))
        reasoning = decision.get("reasoning", "No reasoning provided.")
        risks_mitigated = decision.get("risks_mitigated", [])
        
        print(f"\n🧠 [Brain Proposal]")
        print(f"   Action: {action_type}")
        print(f"   Confidence: {confidence:.0%}")
        print(f"   Reasoning: {reasoning[:150]}...")
        if risks_mitigated:
            print(f"   Risks Mitigated: {len(risks_mitigated)}")
        
        # ═══════════════════════════════════════════════════════════
        # 3. SAFETY VALVE - Metacognition Check
        # ═══════════════════════════════════════════════════════════
        
        # Check for explicit PASS/HOLD
        if action_type in ["PASS", "HOLD"]:
            print(f"\n🛑 [STRATEGIC INACTION] Brain decided to {action_type}")
            print("   The AI knows uncertainty is high. Doing nothing is the right call.")
            self.action_log.append({
                "timestamp": datetime.now().isoformat(),
                "action": action_type,
                "params": {},
                "executed": True,
                "confidence": confidence,
                "blocked_by_safety": False
            })
            return True
        
        # Check confidence threshold
        if confidence < CONFIDENCE_THRESHOLD:
            print(f"\n🛡️ [SAFETY VALVE TRIGGERED]")
            print(f"   Action: {action_type}")
            print(f"   Confidence: {confidence:.0%} < Threshold: {CONFIDENCE_THRESHOLD:.0%}")
            print(f"   → Action ABORTED. The AI knows it is uncertain.")
            print(f"   → Doing nothing is better than doing wrong.")
            
            self.action_log.append({
                "timestamp": datetime.now().isoformat(),
                "action": action_type,
                "params": decision.get("parameters", {}),
                "executed": False,
                "confidence": confidence,
                "blocked_by_safety": True,
                "reason": f"Confidence {confidence:.0%} below threshold {CONFIDENCE_THRESHOLD:.0%}"
            })
            return False
        
        # ═══════════════════════════════════════════════════════════
        # 4. EXECUTE - Only if confidence is sufficient
        # ═══════════════════════════════════════════════════════════
        print(f"\n✅ [CONFIDENCE CHECK PASSED] {confidence:.0%} >= {CONFIDENCE_THRESHOLD:.0%}")
        print(f"⚡ [EXECUTING] Proceeding with high-confidence action...")
        
        success = self.execute_decision(decision)
        
        # Update log with execution result
        if self.action_log:
            self.action_log[-1]["confidence"] = confidence
            self.action_log[-1]["blocked_by_safety"] = False
        
        # 5. LOG RESULT
        print("\n" + "=" * 60)
        if success:
            print(f"🏁 [CYCLE COMPLETE] Action executed successfully")
        else:
            print(f"⚠️ [CYCLE COMPLETE] Action failed during execution")
        print("=" * 60)
        
        return success
    
    def get_action_history(self) -> list:
        """Return action history for analysis."""
        return self.action_log
    
    def get_safety_stats(self) -> Dict[str, Any]:
        """Get statistics about safety valve activations."""
        total = len(self.action_log)
        blocked = sum(1 for a in self.action_log if a.get("blocked_by_safety"))
        executed = sum(1 for a in self.action_log if a.get("executed") and not a.get("blocked_by_safety"))
        holds = sum(1 for a in self.action_log if a.get("action") in ["HOLD", "PASS"])
        
        return {
            "total_decisions": total,
            "executed": executed,
            "blocked_by_safety": blocked,
            "strategic_holds": holds,
            "safety_block_rate": blocked / total if total > 0 else 0
        }


# ═══════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════

def main():
    """Main entry point for autonomous ECOM execution."""
    print("\n" + "=" * 60)
    print("YEDAN AGI - ECOM Autonomous Executor")
    print("=" * 60)
    
    # Get trigger event from args
    trigger = "daily_optimization_check"
    if len(sys.argv) > 1:
        trigger = sys.argv[1]
    
    # Safety notice
    print("\n🔒 SAFETY NOTICE:")
    print("   Shopify DRY_RUN:", bridge_shopify.DRY_RUN)
    print("   Gumroad DRY_RUN:", bridge_gumroad.DRY_RUN)
    if bridge_shopify.DRY_RUN and bridge_gumroad.DRY_RUN:
        print("   All platforms in DRY_RUN mode - no real changes will be made")
    else:
        print("   ⚠️  WARNING: Real changes enabled!")
    
    # Run the cycle
    executor = ECOMExecutor()
    success = executor.run_cycle(trigger_event=trigger)
    
    # Print history
    print("\n📜 Action History:")
    for action in executor.get_action_history():
        status = "✅" if action["executed"] else "❌"
        print(f"   {status} {action['timestamp']}: {action['action']}")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
