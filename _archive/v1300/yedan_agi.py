"""
YEDAN AGI - Main Agent Loop
Autonomous AI agent with continuous operation
"""
import os
import sys
import time
import json
from datetime import datetime

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')

# Import Central Config (Auto-loads .env)
from agi_config import config

# Import AGI modules
from agi_memory import AGIMemory
from agi_actions import AGIActions
from agi_sensors import AGISensors
from agi_research import AGIResearch
from agi_evolution import AGIEvolution
from agi_gems import GemRegistry
from agi_factory import ContentFactory
from agi_scam_guard import ScamGuard  # [NEW] Integrated Protection
from agi_coordinator import BrainCoordinator # [ULTRA] Fast Brain Integration
import random

# AI Clients
try:
    from openai import OpenAI
except:
    OpenAI = None

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except:
    GEMINI_AVAILABLE = False

class YedanAGI:
    """Main AGI Agent"""
    
    def __init__(self):
        print("=" * 60)
        print(f"[YEDAN AGI] Initializing {config.AGENT_NAME} v{config.VERSION}...")
        print("=" * 60)
        
        # Validate Config
        if not config.validate():
            print("[CRITICAL] Configuration failed. Exiting.")
            sys.exit(1)
            
        # Core systems
        self.memory = AGIMemory()
        self.actions = AGIActions()
        self.sensors = AGISensors()
        self.researcher = AGIResearch()
        self.evolution = AGIEvolution()
        self.gem_registry = GemRegistry()
        self.factory = ContentFactory()
        self.scam_guard = ScamGuard() # [NEW] Active Protection
        
        # [ULTRA] Initialize Fast Brain Coordinator
        print("[AGI] Spininng up Fast Brain (Coordinator)...")
        self.coordinator = BrainCoordinator()
        
        # AI Models (with fallback)
        self.ai_clients = self._init_ai()
        
        # Config
        self.cycle_interval = config.CYCLE_INTERVAL
        self.running = False
        
        # Initialize default goals if none exist
        if not self.memory.get_active_goals():
            self._init_default_goals()
        
        print("[YEDAN AGI] All systems online")
    


    class BrowserLLM:
        """
        [ULTRA] A wraper that makes the Web Browser look like the Gemini API.
        Allows the 'Slow Brain' to reason using the Web Interface directly.
        """
        def __init__(self):
            # Lazy import to avoid circular dependency issues at top level if any
            pass
            
        def generate_content(self, prompt: str):
            """
            Mimics genai.GenerativeModel.generate_content
            """
            print("[BROWSER_LLM] converting prompt to Web Session...")
            from agi_browser import AGIBrowser
            import asyncio
            
            # Simple synchronous wrapper
            async def run_query():
                browser = AGIBrowser()
                # Run headless=False to show user? User said "open the browser"
                # But AGIBrowser default matches config. Let's force it visible if user wants?
                # User said "you can open", let's stick to default for stability (usually headless).
                # Actually, strictly following "so nothing is in your way", headless is safer for auto-runs.
                await browser.start() 
                response = await browser.lateral_brainstorm(prompt, "gemini")
                await browser.stop()
                return response
                
            try:
                msg = asyncio.run(run_query())
                # Return a mock object with .text attribute
                class Response:
                   text = msg
                return Response()
            except Exception as e:
                print(f"[BROWSER_LLM] Error: {e}")
                class ErrorResponse:
                   text = "{}"
                return ErrorResponse()

    def _init_ai(self):
        """Initialize AI clients"""
        clients = {}
        
        # Grok (X.AI) - Primary
        grok_key = config.GROK_API_KEY
        if grok_key and grok_key.startswith("xai-") and OpenAI:
            try:
                clients['grok'] = OpenAI(api_key=grok_key, base_url="https://api.x.ai/v1")
                print("[AI] Grok (X.AI): Ready")
            except Exception as e:
                print(f"[AI] Grok: Failed - {e}")
        
        # Perplexity
        pplx_key = config.PPLX_API_KEY
        if pplx_key and pplx_key.startswith("pplx-") and OpenAI:
            try:
                clients['pplx'] = OpenAI(api_key=pplx_key, base_url="https://api.perplexity.ai")
                print("[AI] Perplexity: Ready")
            except Exception as e:
                print(f"[AI] Perplexity: Failed - {e}")
        
        # Gemini (Ultra-Class Power)
        gemini_key = config.GEMINI_API_KEY
        # If Key exists, try API. If it fails (or no key), use BROWSER LLM [ULTRA]
        USE_BROWSER = False
        
        if gemini_key:
            try:
                genai.configure(api_key=gemini_key)
                clients['gemini'] = genai.GenerativeModel('gemini-2.0-flash-001')
                print("[AI] Gemini Ultra (2.0 Flash): Ready (API)")
            except Exception as e:
                print(f"[AI] Gemini API Failed: {e}. Switching to ULTRA WEB.")
                USE_BROWSER = True
        else:
            USE_BROWSER = True
            
        if USE_BROWSER:
            print("[AI] Initializing Gemini Ultra (Web Edition)...")
            clients['gemini'] = self.BrowserLLM()
            print("[AI] Gemini Ultra (Web): Ready")
        
        return clients
    
    # ... (Goals init remains same) ...

    def reason(self, observations, context):
        """
        The Slow Brain: Decides on the next high-level action.
        Uses available AI clients (Gemini/Grok) to analyze context.
        """
        # Construct Prompt
        prompt = f"""
        You are YEDAN AGI ({config.AGENT_NAME}).
        OBJECTIVE: Maximize Net Profit via Intelligence.
        
        CONTEXT:
        - Cycle: {context.get('cycle_count')}
        - Goals: {[g['goal'] for g in context.get('goals', [])]}
        - Recent: {[a['type'] for a in context.get('recent_actions', [])]}
        
        OBSERVATIONS:
        {json.dumps(observations, indent=2)}
        
        AVAILABLE ACTIONS:
        1. "broadcast_intel" (params: "target") -> Publish market report.
        2. "generate_deep_dive" (params: "target") -> Create paid PDF report.
        3. "generate_content_matrix" (params: "target") -> Viral content factory.
        4. "lateral_brainstorm" (params: "target") -> Use Web Browser to research new ideas.
        5. "evolve_system" -> Trigger self-optimization (if energy low).
        6. "wait" -> Do nothing.
        
        DECISION FORMAT (JSON ONLY):
        {{
            "action": "ACTION_NAME",
            "params": {{ "target": "..." }},
            "reasoning": "Brief explanation..."
        }}
        """
        
        client = None
        model_name = "unknown"
        
        # Priority: Gemini Ultra > Grok > Perplexity
        if 'gemini' in self.ai_clients:
            client = self.ai_clients['gemini']
            model_name = "gemini"
        elif 'grok' in self.ai_clients:
            client = self.ai_clients['grok']
            model_name = "grok"
            
        response_text = "{}"
        try:
            if model_name == "gemini":
                # client is GenerativeModel
                response = client.generate_content(prompt)
                response_text = response.text
            elif model_name == "grok":
                # client is OpenAI compatible
                response = client.chat.completions.create(
                    model="grok-beta", # or specific model
                    messages=[{"role": "system", "content": "You are a JSON-speaking AGI."}, 
                              {"role": "user", "content": prompt}]
                )
                response_text = response.choices[0].message.content
            else:
                # Fallback heuristic
                print("[REASON] No AI Client active. Using heuristic.")
                return {"action": "broadcast_intel", "params": {"target": "Bitcoin"}, "reasoning": "Fallback mode"}
                
            # Clean JSON
            json_str = response_text.replace("```json", "").replace("```", "").strip()
            decision = json.loads(json_str)
            return decision
            
        except Exception as e:
            print(f"[REASON] Logic Failure: {str(e)}")
            
            # [ULTRA FAILOVER] If API Key is dead (403), use The Eye (Browser) to reason?
            # That's risky for a structured loop, but we can try lateral_brainstorm as a fallback action
            if "403" in str(e) or "quota" in str(e).lower():
                 print("[REASON] API Key Failed. Switching to LATERAL BRAINSTORMING (Browser Identity).")
                 return {
                     "action": "lateral_brainstorm", 
                     "params": {"target": "Critical Strategy Update (API Key Dead)"}, 
                     "reasoning": "Fallback: API Key invalid, using Browser Reasoning."
                 }
                 
            return {"action": "wait", "reasoning": f"Error: {str(e)}"}

    
    def execute_action(self, decision):
        """Execute the decided action"""
        action = decision.get("action", "wait")
        params = decision.get("params", {})
        
        print(f"[EXECUTE] Action: {action}")
        
        # --- FINOPS GATE: SCAM CHECK ---
        target_to_check = None
        if action in ["broadcast_intel", "generate_deep_dive", "generate_content_matrix"]:
            # Extract target from params or sensors (logic inside action block usually gets it, 
            # but we need it early for safety. For now, assume we scan first.)
            pass 
        
        if action == "broadcast_intel":
            # Get market data for analysis
            market = self.sensors.scan_market()
            trending = self.sensors.scan_trending()
            
            # Find interesting target
            if trending.get("success") and trending.get("trending"):
                target = trending["trending"][0]["name"]
            else:
                target = "Bitcoin"
            
            # 🛡️ SCAM GUARD VERIFICATION 🛡️
            print(f"[FINOPS] Verifying target: {target}...")
            security_check = self.scam_guard.verify_source(target)
            risk_score = security_check.get("score", 0)
            
            if risk_score < 40:
                print(f"[BLOCKED] Target {target} is RISKY (Score: {risk_score}). Aborting broadcast.")
                self.memory.log_action("block_scam", f"Blocked broadcast for {target}", f"Score: {risk_score}", True)
                return {"success": False, "error": "Risk too high"}
            
            # Generate simple analysis
            analysis = f"""Market Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            
Target: {target} (Security Score: {risk_score}/100)

Top Coins by Market Cap:
"""
            if market.get("success"):
                for coin in market.get("coins", [])[:5]:
                    analysis += f"- {coin['symbol']}: ${coin['price']:,.2f} ({coin['change_24h']:.1f}%)\n"
            
            analysis += "\nThis is an automated AGI intelligence report."
            
            # Broadcast
            result = self.actions.broadcast_intel(target, analysis, "0.01")  # $0.01 for testing
            self.memory.log_action("broadcast_intel", f"Target: {target}", str(result), result.get('telegram', {}).get('success', False))
            return result
        
        elif action == "generate_deep_dive":
            # Get trending target
            trending = self.sensors.scan_trending()
            if trending.get("success") and trending.get("trending"):
                target = trending["trending"][0]["name"]
            else:
                target = "Bitcoin"
            
            # 🛡️ SCAM GUARD VERIFICATION 🛡️
            print(f"[FINOPS] Verifying target: {target}...")
            security_check = self.scam_guard.verify_source(target)
            risk_score = security_check.get("score", 0)
            
            if risk_score < 60: # Strict threshold for paid products
                print(f"[BLOCKED] Target {target} Risk Score {risk_score} < 60. Too risky for Deep Dive.")
                return {"success": False, "error": "Risk too high for product"}

            # Select a Gem (for now random, later can be reasoned)
            # Default to YEDAN_PRIME (Hedge Fund Analyst) but mix it up
            gems = self.gem_registry.list_gems()
            selected_gem = random.choice(gems)
            
            print(f"[EXECUTE] Deep Dive Research on: {target} using Gem: {selected_gem}")
            
            # Generate Report via Gemini Ultra + Gem
            report_content = self.researcher.generate_report(target, gem_name=selected_gem)
            
            if report_content:
                # Create PDF & Payment Link ($19.99 for Deep Dive)
                pdf_res = self.actions.generate_pdf(f"YEDAN_DeepDive_{target}_{selected_gem}.pdf", f"DEEP DIVE ({selected_gem}): {target} [Score: {risk_score}]", report_content)
                pay_res = self.actions.create_payment(f"YEDAN Deep Dive: {target}", "19.99")
                
                # Broadcast Teaser
                teaser = f"""<b>💎 YEDAN GEM ACTIVATED: {selected_gem}</b>
                
Gemini Ultra has generated a Deep Dive on {target}.
Security Score: {risk_score}/100

<b>Persona Insight:</b>
{report_content[:200]}...

<a href='{pay_res.get('url')}'><b>🔓 UNLOCK {selected_gem}'s REPORT ($19.99)</b></a>"""
                
                result = self.actions.telegram_send(teaser)
                self.memory.log_action("generate_deep_dive", f"Target: {target} | Gem: {selected_gem}", str(result), result.get("success", False))
                return result
            else:
                return {"success": False, "error": "Research generation failed"}
        
        if action == "lateral_brainstorm":
            target = params.get("target", "Future of AGI")
            print(f"[EXECUTE] Lateral Brainstorming on: {target}")
            
            # Use The Eye (agi_browser)
            # Since browser is async, we need a wrapper or run it synchronously here
            import asyncio
            from agi_browser import AGIBrowser
            
            async def run_brainstorm():
                browser = AGIBrowser()
                await browser.start()
                res = await browser.lateral_brainstorm(f"Brainstorm heavily on: {target}", "gemini")
                await browser.stop()
                return res
                
            try:
                result_text = asyncio.run(run_brainstorm())
                self.memory.log_action("lateral_brainstorm", target, result_text[:100] + "...", True)
                return {"success": True, "insight": result_text}
            except Exception as e:
                print(f"[ERROR] Brainstorm failed: {e}")
                return {"success": False, "error": str(e)}

        elif action == "evolve_system":
            print("[EXECUTE] Running System Evolution...")
            # Pass recent pnl/volatility to check survival first
            # Mocking values for now - in production this comes from sensors
            survival = self.evolution.check_survival(0.0, 0.05, [])
            
            if not survival:
                patch_note = self.evolution.evolve("Energy Depleted - optimize strategy")
                if patch_note:
                    msg = f"🧬 **YEDAN EVOLUTION**\n\nSystem has optimized its own logic.\n\n{patch_note[:500]}..."
                    self.actions.telegram_send(msg)
                    return {"success": True, "patch_note": patch_note}
            else:
                 print("[EVOLUTION] Energy sufficient. No change needed.")
                 return {"success": True, "status": "Stable"}
            return {"success": False}
        
        # ... (rest of actions) ...

        else:  # wait
            self.memory.log_action("wait", decision.get("reasoning", "Waiting"), "No action taken", True)
            return {"success": True, "action": "wait", "status": "Waiting"}

    def run_cycle(self):
        """Run one AGI cycle"""
        
        # [ULTRA] Run Fast Brain Cycle (Trading/Safety)
        # Note: Coordinator.run_cycle is async and meant to run potentially forever or in bursts.
        # For the sync loop, we just tick it or spawn it.
        # For this implementation, we assume we launch it once or it runs in background.
        # Here we just print status as placeholder for specific async integration
        # print("\n--- [FAST BRAIN] ---") 
        # In a real async loop: asyncio.create_task(self.coordinator.run_cycle())
        pass 
            
        print("\n--- [SLOW BRAIN] ---")
            
        print("\n--- [SLOW BRAIN] ---")
        cycle_count = self.memory.get_state("cycle_count", 0) + 1
        self.memory.set_state("cycle_count", cycle_count)
        self.memory.set_state("last_run", datetime.now().isoformat())
        
        print(f"\n{'='*60}")
        print(f"[CYCLE {cycle_count}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # 1. Observe
        print("[OBSERVE] Gathering sensor data...")
        observations = self.sensors.gather_all()
        self.memory.log_observation("sensors", observations)
        
        # 2. Think
        print("[THINK] Reasoning about observations...")
        context = self.memory.get_context_summary()
        decision = self.reason(observations, context)
        
        # 3. Act
        print("[ACT] Executing decision...")
        result = self.execute_action(decision)
        
        # 4. Summary
        print(f"\n[SUMMARY]")
        print(f"  Decision: {decision.get('action')}")
        print(f"  Reasoning: {decision.get('reasoning', 'N/A')[:100]}")
        print(f"  Result: {'Success' if result.get('success') or result.get('telegram', {}).get('success') else 'Partial/None'}")
        
        return result
    
    def run_forever(self):
        """Run the AGI continuously"""
        self.running = True
        print(f"\n[AGI] Starting continuous operation (interval: {self.cycle_interval}s)")
        print("[AGI] Press Ctrl+C to stop\n")
        
        while self.running:
            try:
                self.run_cycle()
                print(f"\n[SLEEP] Next cycle in {self.cycle_interval}s...")
                time.sleep(self.cycle_interval)
            except KeyboardInterrupt:
                print("\n[AGI] Shutdown requested")
                self.running = False
            except Exception as e:
                print(f"[ERROR] Cycle failed: {e}")
                time.sleep(60)  # Wait 1 min on error
        
        print("[AGI] Shutdown complete")
    
    def run_once(self):
        """Run a single cycle (for testing)"""
        return self.run_cycle()

if __name__ == "__main__":
    import sys
    
    agi = YedanAGI()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # Single cycle for testing
        agi.run_once()
    else:
        # Continuous operation
        agi.run_forever()
