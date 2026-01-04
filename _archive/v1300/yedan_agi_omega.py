"""
YEDAN AGI OMEGA - Self-Evolving Revenue Engine
Genetic mutation + Reinforcement learning + Cerebras speed
"""
import os
import sys
import time
import random
from datetime import datetime
from dotenv import load_dotenv

# Fix encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, errors='replace')

load_dotenv()

# Import evolution modules
from agi_genes import GeneticMemory
from agi_strategies import StrategyEngine
from agi_actions import AGIActions
from agi_sensors import AGISensors

# AI Clients
try:
    from cerebras.cloud.sdk import Cerebras
    CEREBRAS_AVAILABLE = True
except ImportError:
    CEREBRAS_AVAILABLE = False
    Cerebras = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class YedanOmega:
    """Self-evolving AGI with genetic memory and reinforcement learning"""
    
    def __init__(self):
        print("=" * 60)
        print("[YEDAN OMEGA] Initializing Self-Evolution Engine...")
        print("=" * 60)
        
        # Core systems
        self.genes = GeneticMemory()
        self.strategy_engine = StrategyEngine(self.genes)
        self.actions = AGIActions()
        self.sensors = AGISensors()
        
        # AI Clients
        self.ai_clients = self._init_ai()
        
        # Config
        self.cooldown = 60  # 1 minute between cycles
        self.feedback_wait = 30  # Wait 30s for market response
        
        print(f"[OMEGA] Generation: {self.genes.get_generation()}")
        print(f"[OMEGA] Best Strategy: {self.genes.get_best_strategy()}")
        print(f"[OMEGA] Total Revenue: ${self.genes.get_total_revenue():.2f}")
        print("[OMEGA] All systems online")
    
    def _init_ai(self):
        """Initialize AI clients with Cerebras priority"""
        clients = {}
        
        # Cerebras (PRIMARY - Ultra fast)
        cerebras_key = os.getenv("CEREBRAS_API_KEY")
        if cerebras_key and CEREBRAS_AVAILABLE:
            try:
                clients['cerebras'] = Cerebras(api_key=cerebras_key)
                print("[AI] Cerebras (llama-3.3-70b): Ready - ULTRA SPEED")
            except Exception as e:
                print(f"[AI] Cerebras failed: {e}")
        
        # Grok (Fallback)
        grok_key = os.getenv("GROK_API_KEY")
        if grok_key and grok_key.startswith("xai-") and OpenAI:
            try:
                clients['grok'] = OpenAI(api_key=grok_key, base_url="https://api.x.ai/v1")
                print("[AI] Grok: Ready")
            except Exception as e:
                print(f"[AI] Grok failed: {e}")
        
        return clients
    
    def get_ai_client(self):
        """Get best available AI client"""
        if 'cerebras' in self.ai_clients:
            return self.ai_clients['cerebras'], 'cerebras'
        if 'grok' in self.ai_clients:
            return self.ai_clients['grok'], 'grok'
        return None, None
    
    def evolve_cycle(self):
        """Run one evolution cycle"""
        gen = self.genes.get_generation()
        
        print(f"\n{'='*60}")
        print(f"[GENERATION {gen}] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # 1. MUTATION: Select strategy
        strategy, mode = self.strategy_engine.select_strategy()
        print(f"[MUTATE] Strategy: {strategy} ({mode})")
        
        # 2. OBSERVE: Get target
        trending = self.sensors.scan_trending()
        if trending.get("success") and trending.get("trending"):
            target = random.choice(trending["trending"][:5])["name"]
        else:
            target = random.choice(["SOL", "BTC", "ETH", "DOGE", "PEPE", "XRP"])
        print(f"[TARGET] {target}")
        
        # 3. GENERATE: Create ad copy
        client, client_name = self.get_ai_client()
        if client and client_name == 'cerebras':
            try:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b",
                    messages=[
                        {"role": "system", "content": f"{self.strategy_engine.get_prompt(strategy)}\n\nYour goal is to make users click and pay. Write a 50-word max ultra-compelling ad copy."},
                        {"role": "user", "content": f"Create ad copy for: {target} Analysis Report ($9.99)"}
                    ]
                )
                ad_copy = completion.choices[0].message.content
                print(f"[CEREBRAS] Generated ad copy")
            except Exception as e:
                print(f"[CEREBRAS] Error: {e}")
                ad_copy = self.strategy_engine.generate_ad_copy(target, strategy)
        else:
            ad_copy = self.strategy_engine.generate_ad_copy(target, strategy)
        
        # 4. MONETIZE: Create payment link
        pay_result = self.actions.create_payment(f"{target} Intel", "9.99")
        pay_url = pay_result.get("url", "#")
        
        # 5. BROADCAST: Send to Telegram
        msg = f"""<b>🧬 AGI Generation {gen}</b> | <i>{strategy}</i>

{ad_copy}

<a href="{pay_url}"><b>💰 UNLOCK REPORT ($9.99)</b></a>"""
        
        tg_result = self.actions.telegram_send(msg)
        if tg_result.get("success"):
            print(f"[BROADCAST] Sent (msg_id: {tg_result.get('message_id')})")
        else:
            print(f"[BROADCAST] Failed: {tg_result.get('error')}")
        
        # 6. WAIT: Allow market to respond
        print(f"[WAIT] Listening for {self.feedback_wait}s...")
        time.sleep(self.feedback_wait)
        
        # 7. FEEDBACK: Check for sales
        sold, revenue = self.actions.check_recent_sales()
        
        if sold:
            print(f"[SUCCESS] 💰 SOLD! Revenue: ${revenue:.2f}")
            self.actions.telegram_send(f"💰 <b>REVENUE ALERT!</b>\n\nGeneration {gen} sold using strategy: {strategy}\nRevenue: ${revenue:.2f}")
        else:
            print(f"[FAIL] No sale this cycle")
        
        # 8. EVOLVE: Update genetic scores
        new_gen = self.genes.record_outcome(strategy, target, sold, revenue)
        
        print(f"\n[EVOLUTION COMPLETE]")
        print(f"  Strategy Scores: {self.genes.get_strategy_scores()}")
        print(f"  Best Strategy: {self.genes.get_best_strategy()}")
        print(f"  Total Revenue: ${self.genes.get_total_revenue():.2f}")
        print(f"  Next Generation: {new_gen}")
        
        return {
            "generation": gen,
            "strategy": strategy,
            "target": target,
            "sold": sold,
            "revenue": revenue
        }
    
    def run_forever(self):
        """Run the evolution engine continuously"""
        print(f"\n[OMEGA] Starting perpetual evolution (cooldown: {self.cooldown}s)")
        print("[OMEGA] Press Ctrl+C to stop\n")
        
        while True:
            try:
                self.evolve_cycle()
                print(f"\n[COOLDOWN] Next cycle in {self.cooldown}s...")
                time.sleep(self.cooldown)
            except KeyboardInterrupt:
                print("\n[OMEGA] Shutdown requested")
                break
            except Exception as e:
                print(f"[ERROR] Cycle failed: {e}")
                time.sleep(10)
        
        print("[OMEGA] Evolution halted")
    
    def run_once(self):
        """Run a single evolution cycle (for testing)"""
        return self.evolve_cycle()


if __name__ == "__main__":
    import sys
    
    omega = YedanOmega()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        omega.run_once()
    else:
        omega.run_forever()
