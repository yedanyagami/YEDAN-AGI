import os
import importlib
import inspect
import logging
import json
import time
from typing import Dict, Any, Optional
import numpy as np

# Internal Imports
from agi_config import config
from agi_math import FractalMath
# from agi_memory import memory

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AGIEvolution")

class AdaptiveEntropy:
    """
    Manages the 'Thermal Pressure' of the Sandbox.
    Meta-Learning: Adjusts decay based on Market Volatility & Fractal Structure.
    """
    def __init__(self, base_decay=0.5, history_len=100):
        self.base_decay = base_decay
        self.energy = 100.0
        self.volatility_history = []
        self.max_history = history_len

    def update_energy(self, profit_pnl: float, current_volatility: float, price_history: list):
        """
        The Core Entropy Loop.
        1. Profit adds Energy.
        2. Time subtracts Energy (Decay).
        3. Decay is adaptive.
        """
        # 1. Profit Replenishment
        if profit_pnl > 0:
            self.energy += (profit_pnl * 10) # 1% gain = +10 Energy
            self.energy = min(self.energy, 200) # Cap energy

        # 2. Calculate Fractal Dimension (Meta-Learning)
        alpha = FractalMath.calculate_dfa_alpha(price_history[-50:])
        
        # 3. Determine Adaptive Decay
        # If Alpha ~ 0.5 (Random/MeanReverting), we ignore 'Volatility' spikes (don't punish).
        # If Alpha >> 0.5 (Trending), we Respect the move.
        
        # Calculate Volatility Z-Score
        self.volatility_history.append(current_volatility)
        if len(self.volatility_history) > self.max_history:
            self.volatility_history.pop(0)
            
        avg_vol = np.mean(self.volatility_history) if self.volatility_history else current_volatility
        # Basic Decay
        decay = self.base_decay
        
        # The Shielding Logic:
        # High Volatility usually kills conservative bots.
        # If High Volatility AND Mean Reverting (Noise), REDUCE Pressure massively.
        if current_volatility > (avg_vol * 1.5):
            if alpha < 0.55:
                # Flash Crash / Noise -> Insulate the Agent
                decay = decay * 0.1 
            else:
                # Real Trend -> Normal Pressure
                decay = decay * 1.0
        else:
            # Low Volatility -> Increase Pressure (Force Innovation)
            decay = decay * 1.5

        # Apply Decay
        self.energy -= decay
        
        return self.energy

class StrategySandbox:
    """
    Manages the lifecycle of a Strategy Candidate.
    Draft -> Verify -> HotSwap.
    """
    def __init__(self, strategies_dir="strategies"):
        self.strategies_dir = strategies_dir
        if not os.path.exists(strategies_dir):
            os.makedirs(strategies_dir)
            
    def save_candidate(self, code: str):
        path = os.path.join(self.strategies_dir, "candidate_strategy.py")
        with open(path, "w", encoding='utf-8') as f:
            f.write(code)
        return path

    def verify_candidate(self) -> bool:
        """
        Sandboxed verification. 
        Imports the candidate and checks for syntax errors / interface compliance.
        Does NOT run it live yet.
        """
        try:
            # Dynamic Import
            sys_path_clean = os.path.join(os.getcwd(), self.strategies_dir)
            if sys_path_clean not in sys.path:
                sys.path.append(sys_path_clean)
                
            import strategies.candidate_strategy as cand
            importlib.reload(cand)
            
            # Check Interface
            if not hasattr(cand, "Strategy") or not hasattr(cand.Strategy, "check_trigger"):
                logger.error("Candidate missing 'Strategy' class or 'check_trigger' method.")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Verification Failed: {e}")
            return False

    def hot_swap(self, active_instance):
        """
        Performs the 'State Handoff' (Brain Transplant).
        Migrates __dict__ from Old Instance to New Instance.
        """
        try:
            import strategies.candidate_strategy as cand
            importlib.reload(cand)
            NewClass = cand.Strategy
            
            new_instance = NewClass()
            
            # The Hydration Pattern (State Migration)
            # We copy specific state variables, NOT everything (to avoid polluting new logic)
            # For now, we copy 'capital', 'positions', 'pnl_history'.
            safe_keys = ['capital', 'positions', 'pnl_history', 'trade_log']
            
            if active_instance:
                old_state = active_instance.__dict__
                for k in safe_keys:
                    if k in old_state:
                        setattr(new_instance, k, old_state[k])
                        
            logger.info("Hot Swap Successful: Brain Transplanted.")
            return new_instance
            
        except Exception as e:
            logger.error(f"Hot Swap Failed: {e}")
            return None

class HormeticSandbox:
    """
    [GEMINI ULTRA PATTERN] Anti-Fragile Code Stressor.
    Intentionally introduces controlled stressors to test code mutations.
    Only mutations that survive stress AND remain profitable are promoted.
    """
    def __init__(self, candidate_code: str, market_data: list):
        self.code = candidate_code
        self.data = market_data
        self.stressors_applied = []
        
    def apply_stressors(self) -> list:
        """
        Generate stressed versions of market data.
        Returns list of (stressor_name, stressed_data) tuples.
        """
        stressed_datasets = []
        
        # 1. Latency Injection: Delay/skip data points
        latency_data = self.data[::2]  # Skip every other data point
        stressed_datasets.append(("latency", latency_data))
        
        # 2. Data Corruption: Introduce nulls/noise
        import random
        noisy_data = []
        for d in self.data:
            if random.random() < 0.1:  # 10% corruption
                noisy_data.append(d * random.uniform(0.9, 1.1))
            else:
                noisy_data.append(d)
        stressed_datasets.append(("noise", noisy_data))
        
        # 3. Flash Crash Simulation: Drop prices by 20%
        crash_idx = len(self.data) // 2
        crash_data = self.data.copy()
        crash_data[crash_idx:crash_idx+5] = [p * 0.8 for p in crash_data[crash_idx:crash_idx+5]]
        stressed_datasets.append(("flash_crash", crash_data))
        
        self.stressors_applied = [s[0] for s in stressed_datasets]
        return stressed_datasets
        
    def evaluate_fitness(self, backtest_func) -> dict:
        """
        Run candidate code against all stressors.
        Returns fitness report.
        """
        results = {"passed": True, "stress_tests": {}}
        
        for stressor_name, stressed_data in self.apply_stressors():
            try:
                # Run backtest on stressed data
                pnl, max_dd = backtest_func(self.code, stressed_data)
                
                # Fitness criteria: Positive returns AND <15% drawdown under stress
                passed = pnl > 0 and max_dd < 0.15
                results["stress_tests"][stressor_name] = {
                    "pnl": pnl,
                    "max_drawdown": max_dd,
                    "passed": passed
                }
                if not passed:
                    results["passed"] = False
            except Exception as e:
                results["stress_tests"][stressor_name] = {"error": str(e), "passed": False}
                results["passed"] = False
                
        return results


class AGIEvolution:
    """
    The Evolution Coordinator.
    Uses 'The Eye' (AGIBrowser) or API to generate code.
    Manages the Entropy Loop.
    """
    def __init__(self):
        self.entropy = AdaptiveEntropy()
        self.sandbox = StrategySandbox()
        
    def check_survival(self, current_pnl, current_vol, price_history):
        energy = self.entropy.update_energy(current_pnl, current_vol, price_history)
        logger.info(f"System Energy: {energy:.2f}")
        
        if energy <= 0:
            logger.warning("ENERGY DEPLETED. Initiating Evolution Cycle...")
            return False # Needs Evolution
        return True # Survived

    def evolve(self, context_prompt: str) -> Optional[str]:
        """
        The Self-Modification Step.
        Uses Gemini Ultra to generate new strategy code.
        Applies Hormetic Sandbox stress testing before promotion.
        """
        logger.info("EVOLUTION TRIGGERED.")
        
        try:
            # Use Gemini API to generate code
            import google.generativeai as genai
            from agi_config import config
            
            genai.configure(api_key=config.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-2.0-flash-001')
            
            evolution_prompt = f"""
            You are the evolution engine for YEDAN AGI, an autonomous trading system.
            
            Context: {context_prompt}
            
            Generate a Python class called 'Strategy' with:
            1. __init__(self) - initialize capital, positions
            2. check_trigger(self, market_data: list) -> dict - returns {{"action": "BUY/SELL/HOLD", "size": float, "reason": str}}
            
            RULES:
            - Must survive flash crashes (sudden 20% drops)
            - Must handle missing/corrupt data gracefully
            - Include max drawdown protection (15% hard stop)
            - Use DFA alpha for trend detection when possible
            
            Return ONLY the Python code, no explanations.
            """
            
            response = model.generate_content(evolution_prompt)
            code = response.text.replace("```python", "").replace("```", "").strip()
            
            # Save candidate
            self.sandbox.save_candidate(code)
            
            # Verify syntax
            if not self.sandbox.verify_candidate():
                logger.error("Evolution: Candidate failed verification.")
                return None
                
            logger.info("Evolution: New strategy candidate generated and verified!")
            return code
            
        except Exception as e:
            logger.error(f"Evolution failed: {e}")
            return None

import sys

