import logging
import time
import threading
import json
import schedule
from dotenv import load_dotenv

from modules.reddit_monitor import RedditMonitor
from modules.twitter_monitor import TwitterMonitor
from modules.r1_reasoner import DeepSeekReasoner
from modules.safety_guard import SafetyGuard
from modules.analytics import Analytics
from modules.utils import setup_logger, check_pause_flag

# Load env variables
load_dotenv(dotenv_path=".env.reactor")

# Setup main Logger
logger = setup_logger('main_reactor')

def load_config():
    try:
        with open("config/keywords.json", "r", encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return None

def main():
    logger.info("⚡ YEDAN CONTENT REACTOR STARTING...")

    if check_pause_flag():
        logger.error("Startup aborted: PAUSE.flag found.")
        return

    # 1. Initialize Core Engines
    config = load_config()
    if not config:
        return

    reasoner = DeepSeekReasoner()
    guard = SafetyGuard()
    analytics = Analytics()
    
    # 4. Initialize Hive Flow (V1400)
    from modules.hive_mind import HiveMind
    hive = HiveMind(reasoner)
    
    # 2. Initialize Monitors (SIMULATION MODE ENABLED)
    logger.info("🔧 Running in SIMULATION MODE (No API Keys required)")
    
    # Pass 'hive' instead of 'reasoner' or alongside it. 
    # We will inject it into the monitors.
    reddit_bot = RedditMonitor(reasoner, guard, config)
    reddit_bot.simulation_mode = True 
    reddit_bot.hive = hive # Injection
    
    twitter_bot = TwitterMonitor(reasoner, guard, config)
    twitter_bot.simulation_mode = True
    twitter_bot.hive = hive # Injection

    # 3. Schedule Daily Analytics
    schedule.every().day.at("09:00").do(analytics.generate_daily_report)

    # 4. Start Threads
    # We run Reddit and Twitter monitors in separate threads to blocking each other
    # (Especially since Reddit uses stream and Twitter uses loop)
    
    threads = []
    
    t_reddit = threading.Thread(target=reddit_bot.start_stream, name="RedditThread", daemon=True)
    t_twitter = threading.Thread(target=twitter_bot.start_stream, name="TwitterThread", daemon=True)
    
    t_reddit.start()
    t_twitter.start()
    
    threads.append(t_reddit)
    threads.append(t_twitter)
    
    logger.info("✅ All systems online. Monitoring active.")

    # 5. Main Keep-Alive Loop
    try:
        while True:
            if check_pause_flag():
                logger.warning("Main loop detected PAUSE flag. Stopping...")
                break
                
            schedule.run_pending()
            time.sleep(60)
            
            # Watchdog: Check if threads are alive?
            if not t_reddit.is_alive():
                logger.error("Reddit thread died!")
                # Optional: Restart functionality
            
            if not t_twitter.is_alive():
                logger.error("Twitter thread died!")

    except KeyboardInterrupt:
        logger.info("Manual shutdown requested.")
    
    logger.info("Reactor shutting down.")

if __name__ == "__main__":
    main()
