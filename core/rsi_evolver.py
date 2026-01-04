#!/usr/bin/env python3
"""
YEDAN AGI - RSI Evolver (Recursive Self-Improvement)
The Metacognition Module that manages the brain.

RLVR Implementation:
- Reward: Revenue from sales_history.csv
- Action: Modify config.json (system_prompt, strategy_parameters)
- Learning: Track evolution_log for pattern analysis

Based on:
- Schmidhuber (2007): Gödel Machines
- Bostrom (2014): Recursive Self-Improvement
- OpenAI (2024): RLVR for o1/o3
"""

import os
import sys
import io
import json
import shutil
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import pandas as pd

# Fix Windows console encoding
if sys.platform == 'win32' and __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sales_history.csv")
BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "evolution_backups")
MARKETING_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "marketing_spend.json")


def call_llm_api(prompt: str, system_prompt: str) -> str:
    """Call LLM for evolution reasoning."""
    try:
        import google.generativeai as genai
        from agi_config import config
        
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-001')
        
        full_prompt = f"{system_prompt}\n\n{prompt}"
        response = model.generate_content(full_prompt)
        return response.text
        
    except Exception as e:
        print(f"⚠️ LLM API Error: {e}")
        return "{}"


class RSI_Evolver:
    """
    The Metacognition Engine.
    Analyzes performance, identifies failures, and mutates strategy.
    
    This is the CROSSOVER POINT - when this successfully improves
    decision_engine performance via config modification, RSI begins.
    """
    
    def __init__(self):
        self.config = self._load_config()
        self.consecutive_failures = 0
        
        # Ensure backup directory exists
        os.makedirs(BACKUP_DIR, exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load AGI DNA from config.json."""
        if not os.path.exists(CONFIG_PATH):
            print("⚠️ config.json not found, creating default...")
            return self._create_default_config()
        
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_json(self, path: str) -> Dict[str, Any]:
        """Load any JSON file with error handling."""
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Error loading {path}: {e}")
            return {}
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration."""
        default = {
            "meta": {
                "version": "1.0.0",
                "last_evolution": datetime.now().isoformat(),
                "evolution_count": 0
            },
            "system_prompt_template": "你是 YEDAN AGI。策略模式：{strategy_mode}。語氣：{tone}。",
            "strategy_parameters": {
                "strategy_mode": "balanced",
                "tone": "professional",
                "risk_tolerance": "medium",
                "price_step": 0.05
            },
            "evolution_log": []
        }
        self._save_config(default)
        return default
    
    def _save_config(self, config: Dict[str, Any]):
        """Save config with backup."""
        # Backup current config
        if os.path.exists(CONFIG_PATH):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(BACKUP_DIR, f"config_{timestamp}.json")
            shutil.copy(CONFIG_PATH, backup_path)
            print(f"📦 Backup created: {backup_path}")
        
        # Save new config
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        print("💾 Config saved to config.json")
    
    def _calculate_real_costs(self, revenue_df, days: int = 7) -> Dict[str, float]:
        """
        [ULTRA UPGRADE] Calculate REAL costs (Truth #3: Dynamic Cost Logic)
        
        Includes:
        - Platform transaction fees (Gumroad 10%, Shopify 2.9%, etc.)
        - Marketing/Ad spend (from marketing_spend.json)
        - Monthly fixed costs (prorated)
        
        Returns:
            Dict with tx_costs, ad_spend, fixed_costs, total_costs
        """
        print("\n💵 [Calculating Real Costs]...")
        
        # Load marketing data
        marketing_data = self._load_json(MARKETING_DATA_PATH)
        fees_config = marketing_data.get("platform_fees", {
            "gumroad": {"percent": 0.10, "fixed": 0.30}
        })
        
        # ═══════════════════════════════════════════════════════════
        # 1. TRANSACTION COSTS (Platform Fees)
        # ═══════════════════════════════════════════════════════════
        total_tx_cost = 0.0
        
        if not revenue_df.empty:
            for _, row in revenue_df.iterrows():
                platform = str(row.get('platform', 'gumroad')).lower()
                amount = float(row.get('amount', 0))
                
                # Get fee rate for platform (default to gumroad)
                rate = fees_config.get(platform, fees_config.get('gumroad', {"percent": 0.10, "fixed": 0.30}))
                
                # Calculate: (amount * percent) + fixed fee
                tx_cost = (amount * rate.get('percent', 0.10)) + rate.get('fixed', 0.30)
                total_tx_cost += tx_cost
        
        print(f"   📋 Transaction Fees: ${total_tx_cost:.2f}")
        
        # ═══════════════════════════════════════════════════════════
        # 2. MARKETING SPEND (Ad Costs)
        # ═══════════════════════════════════════════════════════════
        ad_spend_total = 0.0
        daily_spends = marketing_data.get("daily_ad_spend", [])
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for entry in daily_spends:
            try:
                entry_date = datetime.strptime(entry.get('date', ''), '%Y-%m-%d')
                if entry_date >= cutoff_date:
                    ad_spend_total += float(entry.get('spend', 0))
            except (ValueError, TypeError):
                # If date parsing fails, include anyway (conservative)
                ad_spend_total += float(entry.get('spend', 0))
        
        # Default: assume $5/day if no data
        if ad_spend_total == 0 and not daily_spends:
            ad_spend_total = 5.0 * days
            print(f"   📢 Ad Spend (estimated): ${ad_spend_total:.2f}")
        else:
            print(f"   📢 Ad Spend: ${ad_spend_total:.2f}")
        
        # ═══════════════════════════════════════════════════════════
        # 3. FIXED COSTS (Prorated)
        # ═══════════════════════════════════════════════════════════
        monthly_fixed = marketing_data.get("monthly_fixed_costs", {})
        total_monthly = sum(monthly_fixed.values())
        prorated_fixed = (total_monthly / 30) * days
        
        print(f"   🏢 Fixed Costs (prorated): ${prorated_fixed:.2f}")
        
        # ═══════════════════════════════════════════════════════════
        # TOTAL
        # ═══════════════════════════════════════════════════════════
        total_costs = total_tx_cost + ad_spend_total + prorated_fixed
        print(f"   💸 Total Costs: ${total_costs:.2f}")
        
        return {
            "tx_costs": round(total_tx_cost, 2),
            "ad_spend": round(ad_spend_total, 2),
            "fixed_costs": round(prorated_fixed, 2),
            "total_costs": round(total_costs, 2)
        }
    
    def calculate_novelty_score(self, current_strategy: Dict[str, Any]) -> float:
        """
        [HGM UPGRADE] Calculate Strategy Novelty (Shannon Entropy-like).
        Prevents AGI from getting stuck in evolution dead-ends by rewarding variety.
        
        Returns:
            Float 0.0 to 1.0 (1.0 = highly novel, 0.0 = completely repetitive)
        """
        # Read past 10 evolutions
        history = self.config.get('evolution_log', [])[-10:]
        
        if not history:
            return 1.0  # First strategy is always novel
            
        # Check similarity of core parameters
        similarity_count = 0
        current_tone = current_strategy.get('tone')
        current_mode = current_strategy.get('strategy_mode')
        
        for entry in history:
            # Entry structure might vary, handle safely
            if not isinstance(entry, dict): continue
            
            # Extract parameters from log entry (structure depends on how it was saved)
            # Assuming log entry contains 'strategy_parameters' or similar
            old_params = entry.get('strategy_parameters', {})
            
            if (old_params.get('tone') == current_tone and 
                old_params.get('strategy_mode') == current_mode):
                similarity_count += 1
                
        # Inverse reward: More similarity = Lower score
        # 0 matches = 1.0, 1 match = 0.5, 9 matches = 0.1
        novelty_score = 1.0 / (similarity_count + 1)
        return novelty_score

    def evaluate_performance(self, days: int = 7) -> Dict[str, Any]:
        """
        [ULTRA UPGRADE] Composite Health Score with Anti-Gaming Protocol & Novelty Search.
        
        Formula:
        Score = (NetProfit * 0.8) + (NoveltyScore * 100 * 0.2)
        
        Truth #5: Penalize gaming (low margin).
        Truth #6: Reward curiosity (strategy diversity).
        
        Returns:
            Dict with health_score, revenue, profit, margin, etc.
        """
        # Anti-Gaming Constants
        UNIT_COST_ESTIMATE = 2.0  # Per-transaction cost (fees + tax + overhead)
        MIN_PROFIT_MARGIN = 0.20  # Minimum 20% margin required
        TARGET_HEALTH_SCORE = 50.0  # Target profit score
        
        print(f"\n📊 [RSI] Evaluating {days}-day performance (Anti-Gaming + Novelty)...")
        
        if not os.path.exists(DATA_PATH):
            print("   ⚠️ No sales data found")
            return {
                "health_score": 0,
                "revenue": 0,
                "profit": 0,
                "margin": 0,
                "order_count": 0,
                "trend": "unknown",
                "data_available": False,
                "alerts": ["no_data"]
            }
        
        try:
            df = pd.read_csv(DATA_PATH)
            
            if df.empty:
                # Initialize empty df with correct columns for downstream logic
                df = pd.DataFrame(columns=['timestamp', 'amount', 'platform'])
                # Do NOT return early. We need to check for ad spend (Burn Rate).
            
            # Convert timestamps and amounts
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
            
            # Calculate time periods
            now = datetime.now()
            cutoff_current = now - timedelta(days=days)
            cutoff_previous = cutoff_current - timedelta(days=days)
            
            # Current period
            current = df[df['timestamp'] > cutoff_current]
            current_revenue = float(current['amount'].sum())
            current_orders = len(current)
            
            # Previous period (for comparison)
            previous = df[(df['timestamp'] > cutoff_previous) & (df['timestamp'] <= cutoff_current)]
            previous_revenue = float(previous['amount'].sum())
            
            alerts = []
            
            # ═══════════════════════════════════════════════════════════
            # ANTI-GAMING CALCULATIONS (Dynamic Cost Edition)
            # ═══════════════════════════════════════════════════════════
            
            # [ULTRA UPGRADE] Calculate REAL costs from marketing_spend.json
            cost_breakdown = self._calculate_real_costs(current, days)
            total_cost = cost_breakdown.get("total_costs", current_orders * UNIT_COST_ESTIMATE)
            ad_spend = cost_breakdown.get("ad_spend", 0)
            
            # Net Profit = Revenue - All Costs
            net_profit = current_revenue - total_cost
            
            # Calculate Profit Margin
            profit_margin = net_profit / current_revenue if current_revenue > 0 else 0
            
            # [NEW] ROAS (Return on Ad Spend) - Key efficiency metric
            roas = current_revenue / ad_spend if ad_spend > 0 else 10.0  # No ad spend = perfect ROAS
            
            # [NEW] Novelty Score (Shannon Entropy Reward)
            current_strategy = self.config.get('strategy_parameters', {})
            novelty = self.calculate_novelty_score(current_strategy)
            
            print(f"\n📊 [Financial Summary]")
            print(f"   💰 Revenue: ${current_revenue:.2f}")
            print(f"   💵 Total Costs: ${total_cost:.2f}")
            print(f"   📈 Net Profit: ${net_profit:.2f}")
            print(f"   📊 Profit Margin: {profit_margin*100:.1f}%")
            print(f"   🎯 ROAS: {roas:.2f}x (Target: >2.0x)")
            print(f"   ✨ Novelty Score: {novelty:.2f} (Diversity Bonus)")
            
            # ═══════════════════════════════════════════════════════════
            # HEALTH SCORE CALCULATION (ROAS + Novelty)
            # ═══════════════════════════════════════════════════════════
            
            # Base Score = Net Profit mainly
            
            # 0. CRITICAL BURN: ROAS < 1.0 means we're losing money on ads!
            if roas < 1.0 and ad_spend > 0:
                health_score = -100.0
                alerts.append("CRITICAL_BURN")
                print(f"   💀 [CRITICAL BURN] ROAS {roas:.2f}x < 1.0! We are HEMORRHAGING MONEY!")
            
            # 1. DEATH LINE: Negative profit = severe penalty
            elif net_profit < 0:
                health_score = -100.0
                alerts.append("CRITICAL_LOSS")
                print(f"   💀 [ALARM] Net Profit is NEGATIVE! Health Score: {health_score}")

            
            # 2. LOW ROAS WARNING: ROAS < 2.0 means ads are inefficient
            elif roas < 2.0 and ad_spend > 0:
                health_score = net_profit * 0.5  # 50% penalty
                alerts.append("LOW_ROAS")
                print(f"   ⚠️ [WARNING] ROAS {roas:.2f}x < 2.0. Ads inefficient. Score: {health_score:.2f}")
            
            # 3. LOW MARGIN PENALTY: Margin < 20% = score discounted 70%
            elif profit_margin < MIN_PROFIT_MARGIN:
                health_score = net_profit * 0.3  # 30% of profit counts
                alerts.append("LOW_MARGIN_PENALTY")
                print(f"   ⚠️ [WARNING] Margin {profit_margin*100:.1f}% < {MIN_PROFIT_MARGIN*100}%. Score: {health_score:.2f}")
            
            # 4. HEALTHY STATE: Score = Net Profit + Novelty Bonus
            else:
                # [HGM FORMULA] Score = (Profit * 0.8) + (Novelty * 100 * 0.2)
                # We scale Novelty (0-1) by 100 to make it comparable to $ profit
                profit_component = net_profit * 0.8
                novelty_component = novelty * 100.0 * 0.2
                
                health_score = profit_component + novelty_component
                
                # Bonus for high ROAS (efficient marketing)
                if roas > 3.0:
                    health_score *= 1.2  # 20% bonus for efficiency
                    print(f"   ✅ [EXCELLENT] ROAS {roas:.2f}x > 3.0! Efficiency Bonus applied.")
                
                print(f"   🧩 [COMPOSITE SCORE] Profit({profit_component:.1f}) + Novelty({novelty_component:.1f}) = {health_score:.2f}")

            
            # Calculate trend
            if previous_revenue > 0:
                trend_pct = ((current_revenue - previous_revenue) / previous_revenue) * 100
                if trend_pct > 5:
                    trend = "growing"
                elif trend_pct < -5:
                    trend = "declining"
                    if trend_pct < -20:
                        alerts.append("SEVERE_DECLINE")
                else:
                    trend = "stable"
            else:
                trend = "new"
                trend_pct = 0
            
            print(f"   📦 Orders: {current_orders}")
            print(f"   📈 Trend: {trend} ({trend_pct:+.1f}%)")
            print(f"   🎯 Target Score: {TARGET_HEALTH_SCORE}")
            
            return {
                "health_score": round(health_score, 2),
                "revenue": round(current_revenue, 2),
                "profit": round(net_profit, 2),
                "margin": round(profit_margin, 4),
                "cost": round(total_cost, 2),
                "ad_spend": round(ad_spend, 2),
                "roas": round(roas, 2),
                "order_count": current_orders,
                "previous_revenue": round(previous_revenue, 2),
                "trend": trend,
                "trend_pct": round(trend_pct, 1),
                "data_available": True,
                "alerts": alerts,
                "target_score": TARGET_HEALTH_SCORE
            }
            
        except Exception as e:
            print(f"   ❌ Error analyzing data: {e}")
            return {
                "health_score": 0,
                "revenue": 0,
                "profit": 0,
                "margin": 0,
                "order_count": 0,
                "trend": "error",
                "data_available": False,
                "alerts": [str(e)]
            }
    
    def should_evolve(self, performance: Dict) -> bool:
        """
        [ULTRA UPGRADE] Evolution decision based on Health Score.
        
        Triggers evolution on:
        - Negative profit (CRITICAL)
        - Low margin penalty active
        - Health score below target
        - Severe decline trend
        """
        TARGET_HEALTH_SCORE = performance.get("target_score", 50.0)
        
        # No data = need to collect more
        if not performance.get("data_available"):
            print("   ⏳ Insufficient data for evolution decision")
            return False
        
        health_score = performance.get("health_score", 0)
        alerts = performance.get("alerts", [])
        
        # CRITICAL: Negative profit = MUST evolve
        if "CRITICAL_LOSS" in alerts:
            print(f"   💀 [CRITICAL] Negative profit detected! Evolution REQUIRED.")
            return True
        
        # WARNING: Low margin = should evolve to fix pricing
        if "LOW_MARGIN_PENALTY" in alerts:
            print(f"   ⚠️ [WARNING] Low margin penalty active. Evolving to fix pricing strategy.")
            return True
        
        # WARNING: Severe decline
        if "SEVERE_DECLINE" in alerts:
            print(f"   📉 [WARNING] Severe decline detected (>20%). Evolution triggered.")
            return True
        
        # Health score below target
        if health_score < TARGET_HEALTH_SCORE:
            print(f"   📉 Health Score {health_score:.2f} below target {TARGET_HEALTH_SCORE}")
            return True
        
        print(f"   ✅ Health Score {health_score:.2f} >= Target {TARGET_HEALTH_SCORE}. No evolution needed.")
        return False
    
    def generate_mutation(self, performance: Dict) -> Optional[Dict]:
        """
        [ULTRA UPGRADE] Profit-aware mutation generation.
        Warns LLM about margin issues and guides toward profitable strategies.
        """
        print("\n🧬 [RSI] Generating Mutation (Anti-Gaming Protocol)...")
        
        current_params = self.config.get("strategy_parameters", {})
        evolution_log = self.config.get("evolution_log", [])[-5:]  # Last 5 evolutions
        alerts = performance.get("alerts", [])
        
        # Build alert context for LLM
        alert_context = ""
        if "CRITICAL_LOSS" in alerts:
            alert_context = """
⚠️ [CRITICAL ALERT] Net Profit is NEGATIVE!
This means you are LOSING MONEY on every sale.
DO NOT lower prices further. You must either:
1. INCREASE prices to restore margin
2. REDUCE costs (but this is usually not in your control)
3. Focus on PREMIUM positioning and value communication
"""
        elif "LOW_MARGIN_PENALTY" in alerts:
            alert_context = f"""
⚠️ [WARNING] Profit Margin is below 20%!
Current margin: {performance.get('margin', 0)*100:.1f}%
This means you are playing a dangerous volume game.
STOP lowering prices. Focus on VALUE capture, not volume.
Consider: premium_positioning or profit_maximization mode.
"""
        
        mutation_prompt = f"""
你是 YEDAN AGI 的進化架構師 (Profit-First Optimization Engine)。
你的目標是最大化【淨利潤】，而非營收。

{alert_context}

【當前策略參數】
{json.dumps(current_params, indent=2, ensure_ascii=False)}

【當前表現 (Anti-Gaming Metrics)】
- 健康分數: {performance.get('health_score', 0):.2f} (目標: {performance.get('target_score', 50)})
- 週營收: ${performance.get('revenue', 0)}
- 利潤率: {performance.get('margin', 0)*100:.1f}%
- 淨利潤: ${performance.get('profit', 0)}
- 訂單數: {performance.get('order_count', 0)}
- 趨勢: {performance.get('trend', 'unknown')} ({performance.get('trend_pct', 0):+.1f}%)
- 警報: {alerts}

【最近的進化記錄】
{json.dumps(evolution_log, indent=2, ensure_ascii=False) if evolution_log else '無'}

【任務】
1. 分析為什麼【淨利潤】不足
2. 如果利潤率低，請提高價格或強調價值
3. 如果營收低，考慮更積極的行銷語氣
4. 生成新的策略參數

【可調參數】
- strategy_mode: "profit_maximization" | "volume_growth" | "market_penetration" | "premium_positioning"
- tone: 語氣風格 (例如: "urgent and exclusive", "friendly and educational", "professional and persuasive")
- risk_tolerance: "low" | "medium" | "high"
- price_step: 價格調整幅度 (0.01 - 0.20)

請回傳 JSON 格式：
```json
{{
    "strategy_mode": "...",
    "tone": "...",
    "risk_tolerance": "...",
    "price_step": 0.xx,
    "reasoning": "為什麼這個改變會提高淨利潤"
}}
```
"""
        
        system_prompt = "你是一個 Profit-First Optimization Engine。你的目標是淨利潤，不是營收。只回傳 JSON。"
        
        response = call_llm_api(mutation_prompt, system_prompt)
        
        try:
            # Extract JSON from response
            if "```json" in response:
                json_str = response.split("```json")[-1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                # Try to find JSON directly
                start = response.find("{")
                end = response.rfind("}") + 1
                json_str = response[start:end] if start >= 0 else response
            
            new_params = json.loads(json_str)
            print(f"   🦋 New parameters generated:")
            print(f"      Mode: {new_params.get('strategy_mode', 'unchanged')}")
            print(f"      Tone: {new_params.get('tone', 'unchanged')}")
            print(f"      Reasoning: {new_params.get('reasoning', 'N/A')[:100]}...")
            
            return new_params
            
        except json.JSONDecodeError as e:
            print(f"   ❌ Failed to parse LLM response: {e}")
            print(f"   Raw response: {response[:200]}...")
            return None
    
    def apply_mutation(self, new_params: Dict, performance: Dict) -> bool:
        """
        Apply mutation to config.json (The actual self-modification).
        """
        print("\n🔧 [RSI] Applying Mutation...")
        
        # Extract reasoning (not part of strategy_parameters)
        reasoning = new_params.pop("reasoning", "No reasoning provided")
        
        # Preserve fields not in mutation
        current_params = self.config.get("strategy_parameters", {})
        for key in current_params:
            if key not in new_params:
                new_params[key] = current_params[key]
        
        # Update config
        old_params = self.config["strategy_parameters"].copy()
        self.config["strategy_parameters"] = new_params
        
        # Update meta
        self.config["meta"]["last_evolution"] = datetime.now().isoformat()
        self.config["meta"]["evolution_count"] = self.config["meta"].get("evolution_count", 0) + 1
        
        # Log evolution
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "trigger": {
                "revenue": performance.get("revenue", 0),
                "trend": performance.get("trend", "unknown")
            },
            "old_params": old_params,
            "new_params": new_params,
            "reasoning": reasoning
        }
        self.config["evolution_log"].append(log_entry)
        
        # Keep only last 20 evolution logs
        if len(self.config["evolution_log"]) > 20:
            self.config["evolution_log"] = self.config["evolution_log"][-20:]
        
        # Save
        self._save_config(self.config)
        
        print(f"   ✅ Evolution #{self.config['meta']['evolution_count']} complete!")
        print(f"   📝 Reasoning: {reasoning[:150]}...")
        
        return True
    
    def evolve(self) -> bool:
        """
        Execute the RSI evolution cycle.
        
        1. Evaluate performance (Reward)
        2. Decide if evolution needed
        3. Generate mutation (Action)
        4. Apply mutation (Self-modification)
        
        Returns True if evolution occurred.
        """
        print("\n" + "=" * 60)
        print("🧬 [RSI EVOLVER] Starting Evolution Cycle")
        print(f"   Config: {CONFIG_PATH}")
        print(f"   Evolution Count: {self.config['meta'].get('evolution_count', 0)}")
        print("=" * 60)
        
        # 1. Evaluate
        performance = self.evaluate_performance(days=7)
        
        # 2. Decide
        if not self.should_evolve(performance):
            print("\n🏁 [RSI] No evolution needed. Cycle complete.")
            return False
        
        # 3. Generate
        new_params = self.generate_mutation(performance)
        if not new_params:
            print("\n❌ [RSI] Mutation generation failed.")
            self.consecutive_failures += 1
            return False
        
        # 4. Apply
        success = self.apply_mutation(new_params, performance)
        
        if success:
            self.consecutive_failures = 0
            print("\n🏁 [RSI] Evolution cycle complete. New DNA active!")
        
        return success
    
    def get_current_strategy(self) -> Dict:
        """Return current strategy parameters for decision_engine."""
        return self.config.get("strategy_parameters", {})
    
    def get_system_prompt(self) -> str:
        """Build system prompt from template and current parameters."""
        template = self.config.get("system_prompt_template", "")
        params = self.config.get("strategy_parameters", {})
        
        try:
            return template.format(**params)
        except KeyError:
            return template


# ═══════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    evolver = RSI_Evolver()
    
    if "--evaluate" in sys.argv:
        # Just evaluate, don't evolve
        evolver.evaluate_performance(days=7)
        
    elif "--force" in sys.argv:
        # Force evolution regardless of performance
        print("⚠️ Forcing evolution...")
        performance = evolver.evaluate_performance(days=7)
        new_params = evolver.generate_mutation(performance)
        if new_params:
            evolver.apply_mutation(new_params, performance)
        
    elif "--status" in sys.argv:
        # Show current config status
        config = evolver.config
        print("=" * 60)
        print("YEDAN AGI - RSI Status")
        print("=" * 60)
        print(f"Evolution Count: {config['meta'].get('evolution_count', 0)}")
        print(f"Last Evolution: {config['meta'].get('last_evolution', 'Never')}")
        print(f"\nCurrent Strategy:")
        for k, v in config.get("strategy_parameters", {}).items():
            print(f"   {k}: {v}")
        
    else:
        # Normal evolution cycle
        evolver.evolve()
