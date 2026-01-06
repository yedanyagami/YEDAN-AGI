"""
YEDAN AGI - Central Configuration
Source of Truth for all modules. Eliminates hardcoded values.
"""
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.reactor"))

class Config:
    # Infrastructure
    SYNAPSE_URL = os.getenv("SYNAPSE_URL", "https://synapse.yagami8095.workers.dev")
    N8N_BASE_URL = os.getenv("N8N_BASE_URL", "https://yedanyagami.app.n8n.cloud/api/v1")
    BROWSERLESS_URL = "https://chrome.browserless.io"
    
    # Credentials
    SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")
    SHOPIFY_ADMIN_TOKEN = os.getenv("SHOPIFY_ADMIN_TOKEN")
    BROWSERLESS_TOKEN = os.getenv("BROWSERLESS_TOKEN")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    N8N_API_TOKEN = os.getenv("N8N_API_TOKEN")
    
    # Social Accounts
    REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
    REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
    TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")
    TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD")
    
    # Settings
    DRY_RUN = os.getenv("SHOPIFY_DRY_RUN", "true").lower() == "true"
    SAFETY_MODE = True  # Prevent spamming (monitor only) vs Action
    
    # Paths
    ROOT_DIR = Path(__file__).parent.parent
    LOG_DIR = ROOT_DIR / "logs"
    DATA_DIR = ROOT_DIR / "data"

# Ensure directories exist
Config.LOG_DIR.mkdir(exist_ok=True)
Config.DATA_DIR.mkdir(exist_ok=True)

def setup_logging(name: str):
    """Standard logging setup"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # File Handler
    file_handler = logging.FileHandler(Config.LOG_DIR / "reactor.log", encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Console Handler (Fix Windows Encoding)
    console_handler = logging.StreamHandler(sys.stdout)
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
