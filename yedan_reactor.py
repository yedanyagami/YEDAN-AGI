import logging
import time
import threading
import json
import schedule
from dotenv import load_dotenv

# V1500: Browser-Use based monitors (no API required)
from modules.reddit_browser_monitor import RedditBrowserMonitor
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
    
    # 2. Determine Operation Mode (SMART DETECTION)
    import os
    
    # Check if we have real API keys
    deepseek_key = os.getenv("DEEPSEEK_API_KEY", "")
    reddit_id = os.getenv("REDDIT_CLIENT_ID", "")
    twitter_token = os.getenv("TWITTER_BEARER_TOKEN", "")
    
    deepseek_live = deepseek_key and "your_" not in deepseek_key and len(deepseek_key) > 20
    reddit_live = reddit_id and "your_" not in reddit_id
    twitter_live = twitter_token and "your_" not in twitter_token
    
    if deepseek_live:
        logger.info("🧠 DeepSeek R1: LIVE MODE (Real reasoning enabled)")
    else:
        logger.info("🔧 DeepSeek R1: SIMULATION MODE (Mock responses)")
        
    if reddit_live:
        logger.info("🔴 Reddit: LIVE MODE (Real API)")
    else:
        logger.info("🔮 Reddit: SIMULATION MODE (Mock data)")
        
    if twitter_live:
        logger.info("🐦 Twitter: LIVE MODE (Real API)")
    else:
        logger.info("🔮 Twitter: SIMULATION MODE (Mock data)")
    
    # Pass 'hive' instead of 'reasoner' or alongside it. 
    # V1500: Reddit uses Browser-Use (no API required)
    reddit_bot = RedditBrowserMonitor(hive, guard, config)
    # simulation_mode is auto-detected in RedditBrowserMonitor
    
    twitter_bot = TwitterMonitor(reasoner, guard, config)
    twitter_bot.simulation_mode = not twitter_live
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

    # 5. Main Keep-Alive Loop (V1700 Self-Healing)
    restart_counts = {"reddit": 0, "twitter": 0}
    max_restarts = 5
    
    try:
        while True:
            if check_pause_flag():
                logger.warning("Main loop detected PAUSE flag. Stopping...")
                break
                
            schedule.run_pending()
            time.sleep(60)
            
            # V1700 Watchdog with Auto-Restart
            if not t_reddit.is_alive():
                restart_counts["reddit"] += 1
                if restart_counts["reddit"] <= max_restarts:
                    logger.warning(f"🔄 Reddit thread died - Restarting ({restart_counts['reddit']}/{max_restarts})...")
                    t_reddit = threading.Thread(target=reddit_bot.start_stream, name="RedditThread", daemon=True)
                    t_reddit.start()
                else:
                    logger.error("❌ Reddit exceeded max restarts. Stopping.")
            
            if not t_twitter.is_alive():
                restart_counts["twitter"] += 1
                if restart_counts["twitter"] <= max_restarts:
                    logger.warning(f"🔄 Twitter thread died - Restarting ({restart_counts['twitter']}/{max_restarts})...")
                    t_twitter = threading.Thread(target=twitter_bot.start_stream, name="TwitterThread", daemon=True)
                    t_twitter.start()
                else:
                    logger.error("❌ Twitter exceeded max restarts. Stopping.")

    except KeyboardInterrupt:
        logger.info("Manual shutdown requested.")
    
    logger.info("Reactor shutting down.")

if __name__ == "__main__":
    main()
