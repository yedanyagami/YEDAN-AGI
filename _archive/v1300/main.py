#!/usr/bin/env python3
"""
YEDAN AGI - Life Center (main.py)
The heartbeat of the autonomous system.

This orchestrates all organs:
- Business Active Phase (Decision + Execution)
- Evolution Phase (RSI Self-Improvement)
- Rest Phase (Memory Consolidation)

Run with: python main.py
"""

import time
import sys
import os
import io
import logging
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import schedule (will be installed if missing)
try:
    import schedule
except ImportError:
    print("Installing 'schedule' package...")
    os.system(f"{sys.executable} -m pip install schedule")
    import schedule

# ═══════════════════════════════════════════════════════════════
# LOGGING CONFIGURATION
# ═══════════════════════════════════════════════════════════════
LOG_FILE = os.path.join(os.path.dirname(__file__), "agi_life.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [YEDAN LIFE LOOP] - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════
# ORGAN IMPORTS (Lazy loading to avoid circular imports)
# ═══════════════════════════════════════════════════════════════

def get_decision_engine():
    """Lazy load decision engine."""
    from core.decision_engine import ECOMDecisionEngine
    return ECOMDecisionEngine()

def get_executor():
    """Lazy load executor."""
    from core.ecom_executor import ECOMExecutor
    return ECOMExecutor()

def get_evolver():
    """Lazy load RSI Evolver."""
    from core.rsi_evolver import RSI_Evolver
    return RSI_Evolver()

def get_memory_consolidator():
    """Lazy load Memory Consolidator."""
    from core.memory_consolidator import MemoryConsolidator
    return MemoryConsolidator()

def get_router():
    """Lazy load MetaCognitive Router."""
    from core.router import MetaCognitiveRouter
    import json
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(config_path):
         with open(config_path, 'r', encoding='utf-8') as f:
             config = json.load(f)
    else:
        config = {}
    return MetaCognitiveRouter(config)


# ═══════════════════════════════════════════════════════════════
# LIFE CYCLE JOBS
# ═══════════════════════════════════════════════════════════════

def job_business_active():
    """
    [ACTIVE PHASE] Business Activity Cycle
    
    Frequency: High (e.g., every 30 minutes)
    Tasks: Perceive Market -> Think Strategy -> Execute (with Safety Valve)
    
    [SOFAI UPDATE] Now uses MetaCognitive Router to choose System 1 vs System 2.
    """
    logger.info("=" * 60)
    logger.info("⚡ [WAKE UP] Starting Business Activity Cycle...")
    logger.info("=" * 60)
    
    try:
        # 1. Initialize organs
        brain = get_decision_engine()
        hands = get_executor()
        router = get_router()
        
        # 2. [SOFAI] Metacognitive Routing
        # Context simulation (Connect to real sensors later)
        context = {
            "potential_revenue": 150.0, # High enough to matter (> $50)
            "data_quality_score": 0.4   # Low quality -> Low S1 confidence
        }
        
        route_decision = router.route_decision(context)
        
        if route_decision == "SYSTEM_1_EXECUTE":
            logger.info("⚡ [ROUTER] Selected System 1 (Fast). Executing Intuition...")
            logger.info("✅ System 1 Action: MAINTAIN_STATUS_QUO (Simulated)")
            return

        elif route_decision == "PASS":
            logger.info("🛑 [ROUTER] Decision skipped (Low confidence & Low value).")
            return
            
        # If SYSTEM_2_REASON, proceed to Deep Thinking
        logger.info("🧠 [ROUTER] Selected System 2 (Slow). Escalating to Brain...")

        # 3. Think (Recursive Critic Loop)
        logger.info("🧠 [THINKING] Analyzing market state...")
        decision = brain.analyze_and_decide(trigger_event="SCHEDULED_CYCLE")
        
        if decision is None:
            logger.info("🤷 No decision generated (might be HOLD or low data)")
            return
        
        # 4. Execute (with Safety Valve)
        logger.info("🤖 [EXECUTING] Passing decision to executor...")
        result = hands.run_cycle()
        
        if result:
            logger.info(f"✅ Business cycle completed. Result: {result}")
        else:
            logger.info("🛡️ Action aborted by Safety Valve or no action needed.")
        
        # 4. Log safety stats
        stats = hands.get_safety_stats()
        logger.info(f"📊 Safety Stats: {stats}")
        
    except Exception as e:
        logger.error(f"❌ Business cycle crashed: {e}")
        import traceback
        traceback.print_exc()


def job_evolution_review():
    """
    [REVIEW PHASE] Evolution Cycle (RSI Self-Improvement)
    
    Frequency: Medium (e.g., daily at 3 AM)
    Tasks: Calculate ROAS/Profit -> Modify config.json (Anti-Gaming + Truth #5)
    
    This is Bostrom's RSI in action.
    """
    logger.info("=" * 60)
    logger.info("🧬 [EVOLUTION] Starting RSI Self-Improvement Cycle...")
    logger.info("=" * 60)
    
    try:
        evolver = get_evolver()
        
        # 1. Evaluate performance with real costs
        logger.info("📊 Evaluating performance (ROAS-aware)...")
        performance = evolver.evaluate_performance(days=7)
        
        logger.info(f"   Health Score: {performance.get('health_score', 0)}")
        logger.info(f"   ROAS: {performance.get('roas', 0)}x")
        logger.info(f"   Alerts: {performance.get('alerts', [])}")
        
        # 2. Check if evolution needed
        if evolver.should_evolve(performance):
            logger.info("📉 Performance below target. Initiating mutation...")
            evolver.evolve()
        else:
            logger.info("✅ Performance healthy. No evolution needed.")
        
    except Exception as e:
        logger.error(f"❌ Evolution cycle crashed: {e}")
        import traceback
        traceback.print_exc()


def job_deep_sleep():
    """
    [REST PHASE] Memory Consolidation (Deep Sleep)
    
    Frequency: Low (e.g., weekly on Sunday at 4 AM)
    Tasks: Extract wisdom from CSV -> Write to knowledge_base.md (Truth #1)
    
    This is episodic memory consolidation.
    """
    logger.info("=" * 60)
    logger.info("💤 [SLEEP] Entering Deep Memory Consolidation...")
    logger.info("=" * 60)
    
    try:
        consolidator = get_memory_consolidator()
        success = consolidator.consolidate()
        
        if success:
            logger.info("✅ Memory consolidated. Wisdom stored in knowledge_base.md")
        else:
            logger.info("ℹ️ Not enough data to consolidate yet.")
        
    except Exception as e:
        logger.error(f"❌ Memory consolidation crashed: {e}")
        import traceback
        traceback.print_exc()


def job_health_check():
    """
    [MONITOR] System Health Check
    
    Frequency: Every 5 minutes
    Tasks: Check that all systems are responsive
    """
    try:
        # Quick config check
        import json
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.debug(f"💓 Heartbeat OK. Evolution count: {config.get('meta', {}).get('evolution_count', 0)}")
        else:
            logger.warning("⚠️ config.json missing!")
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")


# ═══════════════════════════════════════════════════════════════
# STARTUP SEQUENCE
# ═══════════════════════════════════════════════════════════════

def print_banner():
    """Print the startup banner."""
    banner = r"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   __  __________  ___    _   __   ___   ______  ____          ║
    ║   \ \/ / ____/  |/  /   / | / /  /   | / ____/ /  _/          ║
    ║    \  / __/ / /|_/ /   /  |/ /  / /| |/ / __   / /            ║
    ║    / / /___/ /  / /   / /|  /  / ___ / /_/ / _/ /             ║
    ║   /_/_____/_/  /_/   /_/ |_/  /_/  |_\____/ /___/             ║
    ║                                                               ║
    ║   [ULTRA EDITION] - Autonomous E-Commerce AGI                 ║
    ║   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ║
    ║   • Recursive Critic Loop (System 2)     ✅                   ║
    ║   • Confidence Safety Valve              ✅                   ║
    ║   • Anti-Gaming Protocol (ROAS)          ✅                   ║
    ║   • Memory Consolidation                 ✅                   ║
    ║   • Dynamic Cost Logic                   ✅                   ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def run_startup_sequence():
    """Run initial startup sequence."""
    logger.info("🚀 Running startup sequence...")
    
    # 1. Check configuration
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if not os.path.exists(config_path):
        logger.warning("⚠️ config.json not found. It will be created on first evolution.")
    else:
        logger.info("✅ config.json found.")
    
    # 2. Check data files
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    sales_path = os.path.join(data_dir, "sales_history.csv")
    if not os.path.exists(sales_path):
        logger.warning("⚠️ No sales_history.csv found. Creating empty file...")
        with open(sales_path, 'w', encoding='utf-8') as f:
            f.write("timestamp,platform,event_type,order_id,product_name,amount,currency,customer_email\n")
    else:
        logger.info("✅ sales_history.csv found.")
    
    # 3. Check marketing spend
    marketing_path = os.path.join(data_dir, "marketing_spend.json")
    if not os.path.exists(marketing_path):
        logger.warning("⚠️ No marketing_spend.json found. Creating default...")
        import json
        default_marketing = {
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "daily_ad_spend": [],
            "platform_fees": {
                "gumroad": {"percent": 0.10, "fixed": 0.30},
                "shopify": {"percent": 0.029, "fixed": 0.30}
            },
            "monthly_fixed_costs": {"shopify_subscription": 0, "other": 0}
        }
        with open(marketing_path, 'w', encoding='utf-8') as f:
            json.dump(default_marketing, f, indent=4)
    else:
        logger.info("✅ marketing_spend.json found.")
    
    logger.info("🏁 Startup sequence complete!")


def start_life_loop():
    """
    Start the YEDAN AGI life loop.
    
    This is the main entry point that:
    1. Schedules all jobs
    2. Runs initial business cycle
    3. Enters infinite loop
    """
    print_banner()
    
    logger.info("🤖 YEDAN AGI Logic Core Starting...")
    logger.info(f"📅 Time: {datetime.now().isoformat()}")
    
    # Run startup checks
    run_startup_sequence()
    
    # ═══════════════════════════════════════════════════════════
    # SCHEDULE CONFIGURATION
    # ═══════════════════════════════════════════════════════════
    
    # 1. Business Activity: Every 10 minutes (Turbo Mode)
    schedule.every(10).minutes.do(job_business_active)
    logger.info("📅 Scheduled: Business cycle every 10 minutes (Turbo)")
    
    # 2. Evolution Review: Every 1 Hour (Turbo Mode)
    schedule.every(1).hours.do(job_evolution_review)
    logger.info("📅 Scheduled: Evolution review every 1 hour (Turbo)")
    
    # 3. Deep Sleep: Sunday at 4 AM
    schedule.every().sunday.at("04:00").do(job_deep_sleep)
    logger.info("📅 Scheduled: Memory consolidation Sunday at 04:00")
    
    # 4. Health Check: Every 5 minutes (silent/debug)
    schedule.every(5).minutes.do(job_health_check)
    
    # ═══════════════════════════════════════════════════════════
    # INITIAL TRIGGER (For Development/Testing)
    # ═══════════════════════════════════════════════════════════
    logger.info("")
    logger.info("🚀 Triggering initial business cycle...")
    job_business_active()
    
    # ═══════════════════════════════════════════════════════════
    # INFINITE LOOP
    # ═══════════════════════════════════════════════════════════
    logger.info("")
    logger.info("🔄 Entering life loop. Press Ctrl+C to stop.")
    logger.info("=" * 60)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("")
        logger.info("🛑 System shut down by user.")
        logger.info("👋 YEDAN AGI going to sleep. Goodbye!")


# ═══════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="YEDAN AGI Life Center")
    parser.add_argument("--once", action="store_true", help="Run one business cycle and exit")
    parser.add_argument("--evolve", action="store_true", help="Run evolution cycle and exit")
    parser.add_argument("--sleep", action="store_true", help="Run memory consolidation and exit")
    parser.add_argument("--status", action="store_true", help="Show system status")
    
    args = parser.parse_args()
    
    if args.once:
        print_banner()
        job_business_active()
    elif args.evolve:
        print_banner()
        job_evolution_review()
    elif args.sleep:
        print_banner()
        job_deep_sleep()
    elif args.status:
        print_banner()
        print("\n📊 YEDAN AGI System Status")
        print("=" * 40)
        
        # Check config
        import json
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"Evolution Count: {config.get('meta', {}).get('evolution_count', 0)}")
            print(f"Last Evolution: {config.get('meta', {}).get('last_evolution', 'Never')}")
            print(f"Strategy Mode: {config.get('strategy_parameters', {}).get('strategy_mode', 'N/A')}")
        else:
            print("Config: Not found")
        
        # Check sales
        sales_path = os.path.join(os.path.dirname(__file__), "data", "sales_history.csv")
        if os.path.exists(sales_path):
            import pandas as pd
            df = pd.read_csv(sales_path)
            print(f"Total Sales Logged: {len(df)}")
            if not df.empty:
                print(f"Total Revenue: ${df['amount'].sum():.2f}")
        else:
            print("Sales: No data")
        
        # Check knowledge base
        kb_path = os.path.join(os.path.dirname(__file__), "data", "knowledge_base.md")
        if os.path.exists(kb_path):
            with open(kb_path, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
            print(f"Knowledge Base: {lines} lines")
        else:
            print("Knowledge Base: Empty")
        
        print("=" * 40)
    else:
        # Default: Start the life loop
        start_life_loop()
