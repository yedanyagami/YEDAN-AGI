"""
YEDAN AGI - Central Configuration
Eliminates magic strings and centralizes environment management.
"""
import os
from dotenv import load_dotenv

# Load environment variables once
load_dotenv()

class Config:
    # --- IDENTITY ---
    AGENT_NAME = "YEDAN PRIME"
    VERSION = "2.1.0 (Ultra)"
    
    # --- API KEYS ---
    # Core
    # GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") # Leaked/Dead
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") # Load from env (Self-Healed or Manual)
    # GEMINI_API_KEY = None # Force Web Mode (Disabled for self-healing test)
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    # Cloud
    CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
    
    # Optional / Fallback
    GROK_API_KEY = os.getenv("GROK_API_KEY")
    PPLX_API_KEY = os.getenv("PPLX_API_KEY")
    CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
    
    # --- FINANCE ---
    PAYPAL_MODE = os.getenv("PAYPAL_MODE", "live")
    PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
    PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
    
    # --- ENDPOINTS ---
    # Workers
    SYNAPSE_URL = "https://synapse.yagami8095.workers.dev"
    SCAM_GUARD_URL = "https://scam-guard.yagami8095.workers.dev"
    PAYHIP_MOCK_URL = "https://payhip-notifier.yagami8095.workers.dev"
    
    # External APIs
    COINGECKO_API = "https://api.coingecko.com/api/v3"
    TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
    
    # --- SYSTEM SETTINGS ---
    CYCLE_INTERVAL = 300  # 5 minutes
    REQUEST_TIMEOUT = 10
    MAX_RETRIES = 3
    
    # --- TRADING SAFETY ---
    MAX_TRADE_USD = 100.0
    STOP_LOSS_PERCENT = 10.0
    
    @classmethod
    def _setup_gcp_auth(cls):
        """Auto-configure Google ADC if available"""
        if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
            # 1. Check for specific Core Key (Priority)
            local_key = os.path.join(os.getcwd(), "yedan-core.json")
            if os.path.exists(local_key):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = local_key
                return True

            # 2. Check standard Windows ADC path
            appdata = os.getenv("APPDATA")
            if appdata:
                adc_path = os.path.join(appdata, "gcloud", "application_default_credentials.json")
                if os.path.exists(adc_path):
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = adc_path
                    return True
        return False

    @classmethod
    def validate(cls):
        """Self-diagnostic check"""
        cls._setup_gcp_auth()  # Try to set up GCP auth
        
        missing = []
        if not cls.GEMINI_API_KEY: missing.append("GEMINI_API_KEY")
        if not cls.TELEGRAM_BOT_TOKEN: missing.append("TELEGRAM_BOT_TOKEN")
        
        if missing:
            print(f"[CRITICAL] Missing keys: {', '.join(missing)}")
            return False
        return True

    @classmethod
    def update_key(cls, key_name: str, new_value: str):
        """
        [SELF-HEAL] Writes a new key to the .env file and updates runtime config.
        """
        # 1. Update Runtime
        if hasattr(cls, key_name):
            setattr(cls, key_name, new_value)
            
        # 2. Update .env file
        env_path = ".env"
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                lines = f.readlines()
        
        # Check if key exists
        found = False
        new_line = f"{key_name}={new_value}\n"
        
        for i, line in enumerate(lines):
            if line.startswith(f"{key_name}="):
                lines[i] = new_line
                found = True
                break
        
        if not found:
            lines.append(new_line)
            
        with open(env_path, "w") as f:
            f.writelines(lines)
            
        print(f"[CONFIG] Updated {key_name} in .env")


# Global instance
config = Config()
