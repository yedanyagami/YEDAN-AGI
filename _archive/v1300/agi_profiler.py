"""
YEDAN AGI - Profiler Module
Smart wallet identification and behavior tracking
"""
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

try:
    import requests
except ImportError:
    requests = None

# Try Redis import
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class WalletProfiler:
    """
    Profiles and tracks smart money wallets.
    The Profiler knows who's who on-chain.
    """
    
    def __init__(self, chain="solana"):
        self.chain = chain
        self.redis = None
        
        # Initialize Redis if available
        redis_url = os.getenv("REDIS_URL")
        if redis_url and REDIS_AVAILABLE:
            try:
                self.redis = redis.from_url(redis_url)
                self.redis.ping()
                print("[PROFILER] Connected to Redis")
            except:
                self.redis = None
                print("[PROFILER] Redis connection failed, using in-memory")
        
        # In-memory fallback
        self.profiles = {}
        
        # Known wallet labels
        self.known_wallets = {
            # CEX Hot Wallets
            "H8sMJSCQxfKiFTCfDR3DUMLPwcRbM61LGFJ8N4dK3WjS": {"label": "Coinbase", "type": "cex", "risk": "low"},
            "2AQdpHJ2JpcEgPiATUXjQxA8UA2ENqDLdP2Eqk5oC8w5": {"label": "Binance", "type": "cex", "risk": "low"},
            "9WzDXwBbmkg8ZTbNMqUxvQRAyrZzDsGYdLVL9zYtAWWM": {"label": "FTX", "type": "cex_dead", "risk": "high"},
            
            # Notable Traders
            "GJRs4FwHtemZ5ZE9x3FNvJ8TMwitKTh21yxdRPqn7npE": {"label": "SOL Whale #1", "type": "whale", "risk": "follow"},
            
            # DEV/Insider patterns (generic)
            "11111111111111111111111111111111": {"label": "System Program", "type": "system", "risk": "neutral"},
        }
        
        # Behavior patterns
        self.behavior_patterns = {
            "accumulator": {"min_buys": 5, "sell_ratio": 0.2, "description": "Buys and holds"},
            "trader": {"min_trades": 10, "win_rate": 0.6, "description": "Active trader"},
            "dev_insider": {"early_holder": True, "large_sells": True, "description": "Possible insider"},
            "sniper": {"first_block": True, "quick_flip": True, "description": "Token sniper"},
            "whale": {"min_balance_usd": 1000000, "description": "Large holder"}
        }
        
        print(f"[PROFILER] Initialized for {chain}")
    
    def _get_profile_key(self, address: str) -> str:
        """Generate Redis key for wallet profile"""
        return f"profile:{self.chain}:{address}"
    
    def get_profile(self, address: str) -> dict:
        """Get or create wallet profile"""
        # Check cache
        key = self._get_profile_key(address)
        
        if self.redis:
            try:
                cached = self.redis.get(key)
                if cached:
                    return json.loads(cached)
            except:
                pass
        elif address in self.profiles:
            return self.profiles[address]
        
        # Check known wallets
        if address in self.known_wallets:
            return {
                "address": address,
                **self.known_wallets[address],
                "known": True,
                "last_updated": datetime.now().isoformat()
            }
        
        # Create new profile
        profile = {
            "address": address,
            "label": None,
            "type": "unknown",
            "risk": "unknown",
            "known": False,
            "first_seen": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "stats": {
                "total_txs": 0,
                "buys": 0,
                "sells": 0,
                "win_rate": 0,
                "avg_hold_time": 0,
                "pnl_estimate": 0
            },
            "behavior": [],
            "tokens_traded": []
        }
        
        # Save to cache
        self._save_profile(address, profile)
        
        return profile
    
    def _save_profile(self, address: str, profile: dict):
        """Save profile to cache"""
        key = self._get_profile_key(address)
        profile["last_updated"] = datetime.now().isoformat()
        
        if self.redis:
            try:
                self.redis.setex(key, 86400 * 7, json.dumps(profile))  # 7 day expiry
            except:
                pass
        else:
            self.profiles[address] = profile
    
    def analyze_behavior(self, address: str, transactions: list) -> dict:
        """Analyze wallet behavior from transaction history"""
        profile = self.get_profile(address)
        
        if not transactions:
            return profile
        
        # Count behaviors
        buys = sum(1 for tx in transactions if tx.get("type") == "buy")
        sells = sum(1 for tx in transactions if tx.get("type") == "sell")
        total = len(transactions)
        
        profile["stats"]["total_txs"] = total
        profile["stats"]["buys"] = buys
        profile["stats"]["sells"] = sells
        
        # Classify behavior
        behaviors = []
        
        if buys >= 5 and sells / max(buys, 1) < 0.2:
            behaviors.append("accumulator")
        
        if total >= 10:
            behaviors.append("trader")
        
        # Check for sniper pattern (first block buyer)
        first_tx_block = transactions[0].get("block", 0) if transactions else 0
        token_launch_block = transactions[0].get("token_launch_block", 0) if transactions else 0
        if first_tx_block <= token_launch_block + 2:
            behaviors.append("sniper")
        
        profile["behavior"] = behaviors
        
        # Risk assessment
        if "sniper" in behaviors and sells > buys * 2:
            profile["risk"] = "high"
            profile["type"] = "potential_rugger"
        elif "accumulator" in behaviors:
            profile["risk"] = "follow"
            profile["type"] = "smart_money"
        else:
            profile["risk"] = "neutral"
        
        self._save_profile(address, profile)
        return profile
    
    def identify_wallet(self, address: str) -> dict:
        """Quick identification of wallet type"""
        profile = self.get_profile(address)
        
        return {
            "address": address,
            "label": profile.get("label", "Unknown"),
            "type": profile.get("type", "unknown"),
            "risk": profile.get("risk", "unknown"),
            "known": profile.get("known", False),
            "recommendation": self._get_recommendation(profile)
        }
    
    def _get_recommendation(self, profile: dict) -> str:
        """Generate trading recommendation based on profile"""
        risk = profile.get("risk", "unknown")
        wallet_type = profile.get("type", "unknown")
        
        if risk == "high":
            return "AVOID - High risk wallet, possible insider/rugger"
        elif risk == "follow":
            return "FOLLOW - Smart money, consider copy trading"
        elif wallet_type == "cex":
            return "NEUTRAL - CEX flow, large volume expected"
        elif wallet_type == "whale":
            return "WATCH - Whale activity may move market"
        else:
            return "UNKNOWN - Insufficient data"
    
    def track_copy_trade(self, target_address: str, our_address: str) -> dict:
        """Set up copy trading for a smart wallet"""
        profile = self.identify_wallet(target_address)
        
        if profile["risk"] == "high":
            return {
                "success": False,
                "error": "Cannot copy trade high-risk wallet"
            }
        
        copy_config = {
            "target": target_address,
            "follower": our_address,
            "enabled": True,
            "max_position": 100,  # Max USD per trade
            "delay_ms": 500,      # Delay before copying
            "created": datetime.now().isoformat()
        }
        
        # Save to Redis
        if self.redis:
            try:
                key = f"copytrade:{self.chain}:{target_address}"
                self.redis.set(key, json.dumps(copy_config))
            except:
                pass
        
        return {
            "success": True,
            "config": copy_config,
            "target_profile": profile
        }
    
    def get_leaderboard(self, limit: int = 10) -> list:
        """Get top performing wallets from database"""
        # Would query Redis for all profiles sorted by PnL
        # For now, return simulated data
        return [
            {"address": "Whale1...", "pnl_30d": 150000, "win_rate": 0.72},
            {"address": "Trader2...", "pnl_30d": 85000, "win_rate": 0.68},
            {"address": "Smart3...", "pnl_30d": 45000, "win_rate": 0.65},
        ][:limit]
    
    def flag_suspicious(self, address: str, reason: str):
        """Flag a wallet as suspicious"""
        profile = self.get_profile(address)
        profile["risk"] = "high"
        profile["flags"] = profile.get("flags", [])
        profile["flags"].append({
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        self._save_profile(address, profile)


if __name__ == "__main__":
    profiler = WalletProfiler(chain="solana")
    
    # Test known wallet
    print("Known Wallet Check:")
    known = profiler.identify_wallet("H8sMJSCQxfKiFTCfDR3DUMLPwcRbM61LGFJ8N4dK3WjS")
    print(f"  {known['label']}: {known['recommendation']}")
    
    # Test unknown wallet
    print("\nUnknown Wallet Check:")
    unknown = profiler.identify_wallet("RandomWallet123456789")
    print(f"  Type: {unknown['type']}")
    print(f"  Recommendation: {unknown['recommendation']}")
    
    # Test behavior analysis
    print("\nBehavior Analysis:")
    fake_txs = [
        {"type": "buy", "block": 100},
        {"type": "buy", "block": 101},
        {"type": "buy", "block": 102},
        {"type": "buy", "block": 105},
        {"type": "buy", "block": 110},
        {"type": "sell", "block": 200}
    ]
    profile = profiler.analyze_behavior("SmartMoney123", fake_txs)
    print(f"  Behaviors: {profile['behavior']}")
    print(f"  Risk: {profile['risk']}")
    
    # Test copy trade setup
    print("\nCopy Trade Setup:")
    copy = profiler.track_copy_trade("SmartMoney123", "MyWallet")
    print(f"  Success: {copy['success']}")
