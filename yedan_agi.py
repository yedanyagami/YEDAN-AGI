"""
YEDAN AGI - Main Agent Loop
Autonomous AI agent with continuous operation
"""
import os
import sys
import time
import json
from datetime import datetime
from dotenv import load_dotenv

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')

load_dotenv()

# Import AGI modules
from agi_memory import AGIMemory
from agi_actions import AGIActions
from agi_sensors import AGISensors
from agi_research import AGIResearch
from agi_evolution import AGIEvolution
from agi_gems import GemRegistry
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
        print("[YEDAN AGI] Initializing...")
        print("=" * 60)
        
        # Core systems
        self.memory = AGIMemory()
        self.actions = AGIActions()
        self.sensors = AGISensors()
        self.researcher = AGIResearch()
        self.evolution = AGIEvolution()
        self.gem_registry = GemRegistry()
        
        # AI Models (with fallback)
        self.ai_clients = self._init_ai()
        
        # Config
        self.cycle_interval = 300  # 5 minutes between cycles
        self.running = False
        
        # Initialize default goals if none exist
        if not self.memory.get_active_goals():
            self._init_default_goals()
        
        print("[YEDAN AGI] All systems online")
    
    def _init_ai(self):
        """Initialize AI clients"""
        clients = {}
        
        # Grok (X.AI) - Primary
        grok_key = os.getenv("GROK_API_KEY")
        if grok_key and grok_key.startswith("xai-") and OpenAI:
            try:
                clients['grok'] = OpenAI(api_key=grok_key, base_url="https://api.x.ai/v1")
                print("[AI] Grok (X.AI): Ready")
            except Exception as e:
                print(f"[AI] Grok: Failed - {e}")
        
        # Perplexity
        pplx_key = os.getenv("PPLX_API_KEY")
        if pplx_key and pplx_key.startswith("pplx-") and OpenAI:
            try:
                clients['pplx'] = OpenAI(api_key=pplx_key, base_url="https://api.perplexity.ai")
                print("[AI] Perplexity: Ready")
            except Exception as e:
                print(f"[AI] Perplexity: Failed - {e}")
        
        # Gemini (Ultra-Class Power)
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=gemini_key)
                # Upgrading to 1.5 Pro for maximum reasoning ("Ultra" power)
                clients['gemini'] = genai.GenerativeModel('gemini-1.5-pro')
                print("[AI] Gemini Ultra (1.5 Pro): Ready")
            except Exception as e:
                print(f"[AI] Gemini: Failed - {e}")
        
        return clients
    
    def _init_default_goals(self):
        """Set up default goals for the AGI"""
        self.memory.add_goal("Generate revenue through AI intelligence reports", priority=10)
        self.memory.add_goal("Monitor crypto market for alpha opportunities", priority=9)
        self.memory.add_goal("Build and engage Telegram audience", priority=8)
        self.memory.add_goal("Respond to customer inquiries", priority=7)
        print("[GOALS] Default goals initialized")
    
    def reason(self, observations, context):
        """Use AI to reason about observations and decide actions"""
        # Build reasoning prompt
        prompt = f"""You are YEDAN AGI, an autonomous AI agent operating in live mode.

CURRENT CONTEXT:
- Cycle Count: {context.get('cycle_count', 0)}
- Active Goals: {json.dumps(context.get('goals', []), indent=2)}
- Recent Actions: {json.dumps(context.get('recent_actions', [])[:3], indent=2)}

CURRENT OBSERVATIONS:
{json.dumps(observations, indent=2, default=str)[:2000]}

AVAILABLE ACTIONS:
1. broadcast_intel - Create and publish a simple market update
2. generate_deep_dive - EXPERIMENTAL: Generate a high-value Deep Dive Report ($19.99)
3. send_telegram - Send a message to the operator
4. wait - Take no action this cycle

Based on the observations and your goals, decide what action to take.
Respond in JSON format:
{{"action": "action_name", "params": {{}}, "reasoning": "brief explanation"}}"""

        # Try OpenAI-compatible clients first (Grok, Perplexity)
        for name, client in self.ai_clients.items():
            if name == 'gemini':
                continue
            try:
                model = "grok-2-latest" if name == "grok" else "llama-3.1-sonar-large-128k-online"
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are YEDAN AGI, a strategic AI agent focused on generating revenue through crypto intelligence."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500
                )
                result = response.choices[0].message.content
                print(f"[REASON] {name}: {result[:100]}...")
                
                try:
                    if "{" in result:
                        json_str = result[result.find("{"):result.rfind("}")+1]
                        return json.loads(json_str)
                except:
                    pass
                return {"action": "wait", "reasoning": result}
            except Exception as e:
                print(f"[REASON] {name} failed: {e}")
                continue
        
        # Try Gemini as fallback
        if 'gemini' in self.ai_clients:
            try:
                response = self.ai_clients['gemini'].generate_content(prompt)
                result = response.text
                print(f"[REASON] gemini: {result[:100]}...")
                
                try:
                    if "{" in result:
                        json_str = result[result.find("{"):result.rfind("}")+1]
                        return json.loads(json_str)
                except:
                    pass
                return {"action": "broadcast_intel", "reasoning": "Gemini decided to broadcast"}
            except Exception as e:
                print(f"[REASON] gemini failed: {e}")
        
        # Fallback if no AI available
        return {"action": "wait", "reasoning": "No AI available for reasoning"}
    
    def execute_action(self, decision):
        """Execute the decided action"""
        action = decision.get("action", "wait")
        params = decision.get("params", {})
        
        print(f"[EXECUTE] Action: {action}")
        
        if action == "broadcast_intel":
            # Get market data for analysis
            market = self.sensors.scan_market()
            trending = self.sensors.scan_trending()
            
            # Find interesting target
            if trending.get("success") and trending.get("trending"):
                target = trending["trending"][0]["name"]
            else:
                target = "Bitcoin Market Analysis"
            
            # Generate simple analysis
            analysis = f"""Market Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Target: {target}

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
        
        elif action == "send_telegram":
            message = params.get("message", "AGI Status Check")
            result = self.actions.telegram_send(message)
            self.memory.log_action("send_telegram", message, str(result), result.get("success", False))
            return result

        elif action == "generate_deep_dive":
            # Get trending target
            trending = self.sensors.scan_trending()
            if trending.get("success") and trending.get("trending"):
                target = trending["trending"][0]["name"]
            else:
                target = "Bitcoin"
            
            # Select a Gem (for now random, later can be reasoned)
            # Default to YEDAN_PRIME (Hedge Fund Analyst) but mix it up
            gems = self.gem_registry.list_gems()
            selected_gem = random.choice(gems)
            
            print(f"[EXECUTE] Deep Dive Research on: {target} using Gem: {selected_gem}")
            
            # Generate Report via Gemini Ultra + Gem
            report_content = self.researcher.generate_report(target, gem_name=selected_gem)
            
            if report_content:
                # Create PDF & Payment Link ($19.99 for Deep Dive)
                pdf_res = self.actions.generate_pdf(f"YEDAN_DeepDive_{target}_{selected_gem}.pdf", f"DEEP DIVE ({selected_gem}): {target}", report_content)
                pay_res = self.actions.create_payment(f"YEDAN Deep Dive: {target}", "19.99")
                
                # Broadcast Teaser
                teaser = f"""<b>💎 YEDAN GEM ACTIVATED: {selected_gem}</b>
                
Gemini Ultra has generated a Deep Dive on {target}.

<b>Persona Insight:</b>
{report_content[:200]}...

<a href='{pay_res.get('url')}'><b>🔓 UNLOCK {selected_gem}'s REPORT ($19.99)</b></a>"""
                
                result = self.actions.telegram_send(teaser)
                self.memory.log_action("generate_deep_dive", f"Target: {target} | Gem: {selected_gem}", str(result), result.get("success", False))
                return result
            else:
                return {"success": False, "error": "Research generation failed"}
        
            else:
                return {"success": False, "error": "Research generation failed"}
        
        elif action == "evolve_system":
            print("[EXECUTE] Running System Evolution...")
            patch_note = self.evolution.evolve()
            if patch_note:
                # Notify operator of evolution
                msg = f"🧬 **YEDAN EVOLUTION**\n\nSystem has optimized its own logic.\n\n{patch_note[:500]}..."
                self.actions.telegram_send(msg)
                return {"success": True, "patch_note": patch_note}
            return {"success": False}

        else:  # wait
            self.memory.log_action("wait", decision.get("reasoning", "Waiting"), "No action taken", True)
            return {"action": "wait"}
    
    def run_cycle(self):
        """Run one AGI cycle"""
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
