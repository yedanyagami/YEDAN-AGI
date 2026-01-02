import os
import sys
import time
import random
import json
import logging
from datetime import datetime

# Windows Unicode Fix
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Setup logging with both file and console handlers
def setup_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # File handler (UTF-8)
        file_handler = logging.FileHandler('logs/reactor.log', encoding='utf-8')
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(file_handler)
        
        # Console handler (with error replacement for Windows)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        # Use custom filter to sanitize emojis on Windows
        if sys.platform == 'win32':
            class UnicodeFilter(logging.Filter):
                def filter(self, record):
                    try:
                        record.msg = record.msg.encode('cp950', errors='replace').decode('cp950')
                    except:
                        pass
                    return True
            console_handler.addFilter(UnicodeFilter())
        logger.addHandler(console_handler)
    
    return logger

# Initialize root logging
logging.basicConfig(
    filename='logs/reactor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

logger = setup_logger('utils')

def add_random_delay(min_seconds=3.2, max_seconds=14.5):
    """
    Adds a random float delay to simulate organic timing and avoid rate limits.
    """
    delay = random.uniform(min_seconds, max_seconds)
    logger.info(f"Sleeping for {delay:.2f} seconds...")
    time.sleep(delay)

def calculate_reading_time(text, wpm=200):
    """
    Calculates estimated reading time for a post to simulate reading behavior.
    """
    word_count = len(text.split())
    reading_seconds = (word_count / wpm) * 60
    actual_wait = random.uniform(reading_seconds * 0.8, reading_seconds * 1.2)
    return max(5.0, actual_wait)

def check_pause_flag():
    """
    Checks for the existence of PAUSE.flag. If present, halts execution loop.
    """
    if os.path.exists("PAUSE.flag"):
        logger.warning("PAUSE.flag detected. System entering standby mode.")
        return True
    return False

def log_interaction(platform, post_id, response_content, meta=None):
    """
    Logs an interaction to the append-only JSONL file for analytics.
    """
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "platform": platform,
        "post_id": post_id,
        "response_length": len(response_content),
        "meta": meta or {}
    }
    
    try:
        with open("logs/interactions.jsonl", "a", encoding='utf-8') as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        logger.error(f"Failed to write interaction log: {e}")

def create_pause_flag():
    """Sets the emergency stop flag"""
    with open("PAUSE.flag", "w") as f:
        f.write("STOP")

def clear_pause_flag():
    """Clears the emergency stop flag"""
    if os.path.exists("PAUSE.flag"):
        os.remove("PAUSE.flag")
