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
    DRY_RUN = False     # REAL MONEY/PRODUCT CREATION
    SAFETY_MODE = False # REAL TRAFFIC/POSTING
    ECO_MODE = True     # Optimize for Low RAM (Aggressive GC, Cloud-Only)
    
    # Paths
    ROOT_DIR = Path(__file__).parent.parent
    LOG_DIR = ROOT_DIR / "logs"
    DATA_DIR = ROOT_DIR / "data"

# Ensure directories exist
Config.LOG_DIR.mkdir(exist_ok=True)
Config.DATA_DIR.mkdir(exist_ok=True)


class RedactingFormatter(logging.Formatter):
    """Formatter that masks sensitive info from environment variables."""
    def __init__(self, orig_formatter):
        self.orig_formatter = orig_formatter
        self._secrets = []
        # Collect secrets from Config attributes that look sensitive
        for key in dir(Config):
            if key.isupper() and ("KEY" in key or "TOKEN" in key or "PASSWORD" in key or "SECRET" in key):
                val = getattr(Config, key)
                if val and len(val) > 4: # Don't mask short common words
                    self._secrets.append(str(val))

    def format(self, record):
        msg = self.orig_formatter.format(record)
        for secret in self._secrets:
            if secret in msg:
                msg = msg.replace(secret, "***REDACTED***")
        return msg

def setup_logging(name: str):
    """Standard logging setup with REDACTION"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Base formatter
    base_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Wrap in Redactor
    formatter = RedactingFormatter(base_formatter)
    
    # File Handler
    file_handler = logging.FileHandler(Config.LOG_DIR / "reactor.log", encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Console Handler (Fix Windows Encoding)
    console_handler = logging.StreamHandler(sys.stdout)
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    console_handler.setFormatter(formatter)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger
