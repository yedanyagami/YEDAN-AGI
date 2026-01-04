#!/usr/bin/env python3
"""
YEDAN AGI - ECOM Decision Engine (System 2 Slow Thinking)
Implements Chain-of-Thought reasoning with real LLM integration.

Design Philosophy: "Think Before You Act"
- Input: Sales data + trigger event
- Process: LLM reasoning with <think> tags
- Output: Action Plan JSON for bridge execution
"""

import os
import sys
import io
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional

# Fix Windows console encoding for emojis
if sys.platform == 'win32' and __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ═══════════════════════════════════════════════════════════════
# LLM INTERFACE (Real Gemini API)
# ═══════════════════════════════════════════════════════════════

def call_llm_api(prompt: str, system_prompt: str) -> str:
    """
    Real LLM API call using Gemini.
    Falls back to mock response if API unavailable.
    """
    try:
        import google.generativeai as genai
        from agi_config import config
        
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-001')
        
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        print(f"\n🧠 [AGI THINKING] Processing with Gemini...")
        response = model.generate_content(full_prompt)
        
        return response.text
        
    except Exception as e:
        print(f"⚠️ Gemini API Error: {e}")
        print("📋 Using fallback mock response...")
        
        # Fallback mock response for testing
        return """
<think>
1. 分析現狀：當前銷售數據顯示需要優化。
2. 策略評估：
   A. 調整價格 (風險：利潤下降)
   B. 優化文案 (風險：低，收益：中等)
   C. 維持現狀 (風險：錯失機會)
3. 決策：選擇低風險策略 B，優化文案增加轉換率。
</think>
{
    "decision": "OPTIMIZE_COPY",
    "parameters": {
        "target": "product_description",
        "action": "add_urgency"
    },
    "reasoning": "低風險高回報的優化策略",
    "confidence_score": 0.75
}
"""


class ECOMDecisionEngine:
    """
    ECOM Decision Engine with System 2 reasoning.
    Reads sales data, analyzes with LLM, outputs action plan.
    
    Now reads dynamic config from config.json for RSI integration.
    """
    
    def __init__(self, sales_data_path: str = "data/sales_history.csv"):
        self.data_path = sales_data_path
        self.config = self._load_config()
        self.system_prompt = self._build_system_prompt()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load dynamic configuration from config.json."""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading config.json: {e}")
        
        # Default fallback config
        return {
            "strategy_parameters": {
                "strategy_mode": "balanced",
                "tone": "professional",
                "personality": "data-driven",
                "risk_tolerance": "medium"
            }
        }
    
    def _build_system_prompt(self) -> str:
        """Build system prompt from config template and parameters."""
        # Get template and parameters
        template = self.config.get("system_prompt_template", "")
        params = self.config.get("strategy_parameters", {})
        
        # Build dynamic prompt
        if template:
            try:
                dynamic_part = template.format(**params)
            except KeyError:
                dynamic_part = template
        else:
            dynamic_part = f"策略模式：{params.get('strategy_mode', 'balanced')}。語氣：{params.get('tone', 'professional')}。"
        
        # Combine with base instructions
        base_instructions = """
在做出任何決定前，你必須嚴格遵循以下步驟：

1. [PERCEIVE] 分析當前的市場狀態和 KPI
2. [THINK] 在 <think> 標籤內進行多步驟推理：
   - 列出所有可能的策略選項
   - 評估每個策略的預期收益和風險
   - 進行自我辯論，考慮反面論點
3. [SIMULATE] 預測最佳策略的預期結果
4. [DECIDE] 輸出最終決策的 JSON 格式

JSON 輸出格式：
{
    "decision": "MODIFY_COPY|ADJUST_PRICE|UPDATE_PRICE|RETARGET|HOLD",
    "parameters": {
        "platform": "gumroad|shopify",
        "product_id": "產品ID",
        ...其他參數...
    },
    "reasoning": "決策理由",
    "confidence_score": 0.0-1.0
}

重要：永遠先在 <think></think> 標籤內展示完整推理過程，再輸出 JSON。
"""
        
        return f"{dynamic_part}\n{base_instructions}"
    
    def get_strategy_params(self) -> Dict[str, Any]:
        """Return current strategy parameters for external access."""
        return self.config.get("strategy_parameters", {})
    
    def _read_long_term_memory(self, max_chars: int = 2000) -> str:
        """
        Read wisdom from knowledge_base.md (Long-term Memory).
        
        This is injected into the system prompt so the AGI can learn
        from past successes and failures.
        
        Args:
            max_chars: Maximum characters to return (token control)
            
        Returns:
            Wisdom from knowledge base or default message
        """
        kb_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "knowledge_base.md")
        
        if not os.path.exists(kb_path):
            return "No prior wisdom available. This is a fresh start - proceed with caution."
        
        try:
            with open(kb_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            if not content.strip():
                return "Knowledge base is empty. No prior experience to draw from."
            
            # Return most recent entries if content is too long
            if len(content) > max_chars:
                return "...[older entries truncated]...\n\n" + content[-max_chars:]
            
            return content
            
        except Exception as e:
            return f"Error reading long-term memory: {e}"
    
    def _read_market_state(self) -> Dict[str, Any]:
        """
        讀取銷售數據，計算當前市場狀態 (KPIs)
        """
        if not os.path.exists(self.data_path):
            return {
                "conversion_rate": 0.0, 
                "total_revenue": 0.0,
                "total_orders": 0,
                "data_available": False
            }
        
        try:
            df = pd.read_csv(self.data_path)
            
            if df.empty:
                return {
                    "conversion_rate": 0.0,
                    "total_revenue": 0.0,
                    "total_orders": 0,
                    "data_available": False
                }
            
            # Calculate KPIs
            total_orders = len(df)
            
            # Convert amount to float safely
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
            total_revenue = df['amount'].sum()
            
            # Platform breakdown
            platform_counts = df['platform'].value_counts().to_dict()
            
            # Recent orders (last 24h)
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            recent = df[df['timestamp'] > datetime.now() - pd.Timedelta(days=1)]
            recent_orders = len(recent)
            recent_revenue = recent['amount'].sum()
            
            # Mock traffic for CVR calculation (replace with real data)
            mock_traffic = max(total_orders * 20, 100)
            conversion_rate = total_orders / mock_traffic
            
            return {
                "conversion_rate": round(conversion_rate, 4),
                "total_revenue": round(total_revenue, 2),
                "total_orders": total_orders,
                "recent_orders_24h": recent_orders,
                "recent_revenue_24h": round(recent_revenue, 2),
                "platforms": platform_counts,
                "last_order": df.iloc[-1].to_dict() if not df.empty else None,
                "data_available": True
            }
            
        except Exception as e:
            print(f"⚠️ Error reading sales data: {e}")
            return {"error": str(e), "data_available": False}
    
    
    
    def _arbitrate_conflict(self, market_opportunity_score: float, roas_health: float) -> bool:
        """
        [實作結果] 數位鐵三角仲裁算法 (Triangle Arbitration)
        根據當前 Risk Level，動態調整「設計師(增長)」與「財務官(安全)」的權重。
        """
        # 1. 讀取當前風險偏好 (由 RSI 進化決定)
        params = self.config.get('strategy_parameters', {})
        current_risk = params.get('risk_tolerance', 'medium').lower() # Map to user's "risk_level"
        
        # 2. 設定動態權重 (這是 NotebookLLM 給不出的核心參數)
        if current_risk in ['high', 'aggressive']:
            # 激進模式：設計師(增長)權重 70%，財務官(安全)權重 30%
            w_growth = 0.7
            w_safety = 0.3
        else:
            # 防禦模式：設計師(增長)權重 30%，財務官(安全)權重 70%
            w_growth = 0.3
            w_safety = 0.7

        # 3. 計算加權決策分數 (0.0 - 1.0)
        # market_opportunity_score: LLM 對市場熱度的評分 (0-1)
        # roas_health: 當前 ROAS (e.g., 1.2). Normalize: ROAS 2.0 = 1.0 score.
        
        # 歸一化 ROAS
        roas_score = min(roas_health / 2.0, 1.0) 
        
        final_score = (market_opportunity_score * w_growth) + (roas_score * w_safety)
        
        print(f"⚖️ [ARBITRATION] Growth({w_growth}) vs Safety({w_safety})")
        print(f"   -> Market Opp: {market_opportunity_score:.2f} | ROAS: {roas_health:.2f} (Score: {roas_score:.2f})")
        print(f"   -> Final Weighted Score: {final_score:.2f}")

        # 4. 輸出硬性裁決
        # 分數 > 0.6 才允許行動，否則否決
        return final_score > 0.6

    def analyze_and_decide(self, trigger_event: str) -> Optional[Dict]:
        """
        [ULTRA UPGRADE] 遞迴批判決策迴圈 (Recursive Critic Loop)
        
        Truth #2: AI 透過多步驟思考 (Think Harder) 來超越人類直覺。
        This trades 3x token cost for exponentially better decisions.
        
        Step 1: Proposal (Draft 1) - Generate initial plan
        Step 2: Critic - Attack the plan's weaknesses
        Step 3: Synthesis - Combine insights into final decision
        """
        print("=" * 60)
        print(f"🎯 [ECOM DECISION ENGINE] Trigger: {trigger_event}")
        print("=" * 60)
        
        # Reload config to get latest RSI mutations
        self.config = self._load_config()
        settings = self.config.get('strategy_parameters', {}).copy()
        
        # Inject root config keys needed for template
        settings['system_identity'] = self.config.get('system_identity', 'YEDAN AGI')

        
        # 1. PERCEIVE - Read market state
        state = self._read_market_state()
        print(f"\n📊 [Current State]")
        print(f"   CVR: {state.get('conversion_rate', 0)*100:.2f}%")
        print(f"   Total Revenue: ${state.get('total_revenue', 0)}")
        print(f"   Orders (24h): {state.get('recent_orders_24h', 0)}")
        
        # ═══════════════════════════════════════════════════════════
        # [HGM LOGIC] TRIANGLE ARBITRATION
        # Digital Iron Triangle: Design vs Finance
        # ═══════════════════════════════════════════════════════════
        
        # [SIMULATION] Get Input Data (As requested by user)
        # Ideally, market_opp comes from System 2 perception (e.g., trend analysis)
        market_opp = 0.8  # Strong market signal
        
        # Ideally, current_roas comes from RSI Evolver (real-time financial health)
        current_roas = 1.2 # Weak ROAS (Burn Rate)
        
        # Execute Arbitration
        is_approved = self._arbitrate_conflict(market_opp, current_roas)
        
        if not is_approved:
            print("🚫 [VETO] Arbitration rejected the action. Financial risk outweighs market opportunity.")
            # Return a PASS decision to skip expensive thinking
            return {
                "decision": "PASS", 
                "reasoning": "Vetoed by Iron Triangle Logic (Financial Risk > Market Opp)",
                "confidence_score": 1.0 # Certain veto
            }
        
        print(f"\n🧠 [Deep Thinking] Initiating 3-Step Recursive Loop...")
        
        # ═══════════════════════════════════════════════════════════
        # STEP 1: PROPOSAL (The Draft Plan)
        # ═══════════════════════════════════════════════════════════
        # [ULTRA UPGRADE] Read Long-term Memory
        # This injects past wisdom into decision-making
        # ═══════════════════════════════════════════════════════════
        wisdom = self._read_long_term_memory(max_chars=1500)
        
        proposer_system = f"""
{self.config.get('system_prompt_template', 'You are a sales AI.').format(**settings)}

你的目標是最大化長期利潤。請根據市場數據，提出一個具體的行動方案。
當前策略風格: {settings.get('tone', 'professional')}
風險偏好: {settings.get('risk_tolerance', 'medium')}

【長期商業智慧 (從過往經驗中學習，請勿忽略)】:
{wisdom}

請基於上述過往的成功/失敗經驗，結合當前數據進行決策。
"""
        
        proposer_prompt = f"""
[觸發事件]: {trigger_event}
[市場數據]: {json.dumps(state, indent=2, ensure_ascii=False, default=str)}

請給出你的初步行動計畫。說明你的理由，並解釋如何應用過往智慧。
可選行動：UPDATE_PRICE, MODIFY_COPY, HOLD
"""
        
        plan_v1 = call_llm_api(proposer_prompt, proposer_system)
        print(f"\n💡 [Step 1: Proposal] Draft Generated")
        print(f"   Preview: {plan_v1[:150].replace(chr(10), ' ')}...")
        
        # ═══════════════════════════════════════════════════════════
        # STEP 2: CRITIC (The Devil's Advocate)
        # ═══════════════════════════════════════════════════════════
        critic_system = """
你是一個嚴厲的風險控制專家與惡毒的批評家。
你的任務是找出計畫中的漏洞、風險和邏輯錯誤。
不要給面子，直接指出為什麼這個計畫可能會失敗或導致虧損。
考慮：品牌傷害、利潤下降、客戶流失、執行風險等。
"""
        
        critic_prompt = f"""
請審查以下行動計畫：

{plan_v1}

請列出 3 個潛在的致命風險或邏輯漏洞，以及每個風險的嚴重程度 (1-10)。
"""
        
        critique = call_llm_api(critic_prompt, critic_system)
        print(f"\n⚖️ [Step 2: Critic] Risks Identified")
        print(f"   Preview: {critique[:150].replace(chr(10), ' ')}...")
        
        # ═══════════════════════════════════════════════════════════
        # STEP 3: SYNTHESIS (The Final Arbiter)
        # ═══════════════════════════════════════════════════════════
        finalizer_system = f"""
你是一個完美主義的戰略家，也是最終決策者。
你需要綜合初始計畫與批評意見，生成一個「修正後」的最終決策。

如果風險過高，你有權決定 "decision": "HOLD" (不行動)。
如果風險可控，請採納計畫並加入風險緩解措施。

當前策略設定：
- 語氣: {settings.get('tone', 'professional')}
- 風險偏好: {settings.get('risk_tolerance', 'medium')}
- 價格步進: {settings.get('price_step', 0.05)}

你必須輸出純 JSON 格式，不要有其他文字。
"""
        
        finalizer_prompt = f"""
[初始計畫]:
{plan_v1}

[批評意見]:
{critique}

請修正計畫以規避上述風險，並生成最終決策。

輸出格式 (純 JSON):
{{
    "decision": "UPDATE_PRICE" | "MODIFY_COPY" | "HOLD",
    "parameters": {{
        "platform": "gumroad" | "shopify",
        "product_id": "產品ID (如果適用)",
        "new_price": 數字 (如果是價格調整),
        "content": "新文案內容 (如果是文案修改)"
    }},
    "confidence_score": 0.0-1.0,
    "reasoning": "最終採納的理由，包含如何緩解風險",
    "risks_mitigated": ["風險1的緩解方式", "風險2的緩解方式"]
}}
"""
        
        final_decision_raw = call_llm_api(finalizer_prompt, finalizer_system)
        print(f"\n🎯 [Step 3: Synthesis] Final Decision Generated")
        
        # ═══════════════════════════════════════════════════════════
        # PARSE FINAL JSON
        # ═══════════════════════════════════════════════════════════
        try:
            # Clean markdown artifacts
            json_str = final_decision_raw.replace("```json", "").replace("```", "").strip()
            
            # Find JSON object
            start = json_str.find("{")
            end = json_str.rfind("}") + 1
            
            if start >= 0 and end > start:
                json_str = json_str[start:end]
                decision = json.loads(json_str)
                
                # Add metadata
                decision["timestamp"] = datetime.now().isoformat()
                decision["trigger_event"] = trigger_event
                decision["market_state"] = state
                decision["recursive_loop"] = {
                    "proposal_length": len(plan_v1),
                    "critique_length": len(critique),
                    "steps_completed": 3
                }
                
                print(f"\n✅ [FINAL DECISION]")
                print(f"   Action: {decision.get('decision')}")
                print(f"   Confidence: {decision.get('confidence_score', 0):.0%}")
                print(f"   Reasoning: {decision.get('reasoning', 'N/A')[:100]}...")
                
                return decision
            else:
                print("❌ No valid JSON found in final response")
                return None
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parsing Failed: {e}")
            print(f"   Raw output: {final_decision_raw[:200]}...")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None
    
    def log_decision(self, decision: Dict, log_path: str = "data/decision_log.jsonl"):
        """Log decision for future RLVR training."""
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(decision, ensure_ascii=False, default=str) + "\n")
        print(f"📝 Decision logged to {log_path}")


# ═══════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    engine = ECOMDecisionEngine()
    
    # Default trigger event
    trigger = "daily_review"
    if len(sys.argv) > 1:
        trigger = sys.argv[1]
    
    print("\n" + "=" * 60)
    print("YEDAN AGI - ECOM Decision Engine")
    print("=" * 60)
    
    decision = engine.analyze_and_decide(trigger_event=trigger)
    
    if decision:
        print("\n" + "=" * 60)
        print("🚀 [FINAL DECISION]")
        print("=" * 60)
        print(f"Action: {decision['decision']}")
        print(f"Parameters: {json.dumps(decision.get('parameters', {}), indent=2)}")
        print(f"Reasoning: {decision.get('reasoning', 'N/A')}")
        print(f"Confidence: {decision.get('confidence_score', 0):.0%}")
        
        # Log for RLVR
        engine.log_decision(decision)
    else:
        print("\n❌ No decision could be made")
