"""
YEDAN AGI - Neural Bridge (Redis Synapse)
Connects Slow Brain (Antigravity + Gemini) with Fast Brain (Cloud Run + Jito)
"""
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import requests
except ImportError:
    requests = None


class NeuralBridge:
    """
    The nervous system connecting two brains:
    - Slow Brain: Antigravity + Gemini (strategy, news, charts)
    - Fast Brain: Cloud Run + Jito (execution, sniping, defense)
    """
    
    # Redis channel keys
    KEYS = {
        "strategy": "yedan:strategy",           # Current trading strategy
        "task_queue": "yedan:task:queue",       # Tasks for slow brain
        "task_result": "yedan:task:result",     # Results from slow brain
        "heartbeat": "yedan:heartbeat:slow",    # Slow brain heartbeat
        "alert": "yedan:alert",                 # Urgent alerts
        "mode": "yedan:mode",                   # System mode (normal/safe/panic)
        "price_cache": "yedan:price:cache"      # Latest price data
    }
    
    # Trading strategies slow brain can set
    STRATEGIES = {
        "ACCUMULATE_DIP": "Buy on small dips, bullish bias",
        "SELL_RALLY": "Sell on small pumps, bearish bias", 
        "NEUTRAL": "No directional bias, range trade only",
        "FULL_RISK_ON": "Maximum long exposure",
        "FULL_RISK_OFF": "Exit all positions, cash only",
        "SNIPE_MODE": "Watch for new token launches"
    }
    
    # Safety modes
    MODES = {
        "NORMAL": "Full autonomous operation",
        "SAFE": "Only sell, no new buys",
        "PANIC": "Emergency liquidation",
        "MANUAL": "Human override required"
    }
    
    def __init__(self):
        self.redis = None
        self.last_heartbeat = None
        self.watchdog_timeout = 180  # 3 minutes
        
        # Connect to Redis
        redis_url = os.getenv("REDIS_URL") or os.getenv("UPSTASH_REDIS_REST_URL")
        if redis_url and REDIS_AVAILABLE:
            try:
                if "upstash" in redis_url:
                    # Upstash REST API mode
                    self.redis_mode = "upstash"
                    self.upstash_url = redis_url
                    self.upstash_token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
                else:
                    # Standard Redis
                    self.redis = redis.from_url(redis_url)
                    self.redis.ping()
                    self.redis_mode = "standard"
                print("[BRIDGE] Neural Bridge connected to Redis")
            except Exception as e:
                print(f"[BRIDGE] Redis connection failed: {e}")
                self.redis_mode = None
        else:
            self.redis_mode = None
            print("[BRIDGE] Running in simulation mode (no Redis)")
    
    def _redis_get(self, key: str) -> str:
        """Get value from Redis (handles both modes)"""
        if self.redis_mode == "standard":
            val = self.redis.get(key)
            return val.decode() if val else None
        elif self.redis_mode == "upstash" and requests:
            try:
                resp = requests.get(
                    f"{self.upstash_url}/get/{key}",
                    headers={"Authorization": f"Bearer {self.upstash_token}"},
                    timeout=5
                )
                data = resp.json()
                return data.get("result")
            except:
                return None
        return None
    
    def _redis_set(self, key: str, value: str, ex: int = None):
        """Set value in Redis (handles both modes)"""
        if self.redis_mode == "standard":
            if ex:
                self.redis.setex(key, ex, value)
            else:
                self.redis.set(key, value)
        elif self.redis_mode == "upstash" and requests:
            try:
                cmd = f"/set/{key}/{value}"
                if ex:
                    cmd += f"?EX={ex}"
                requests.get(
                    f"{self.upstash_url}{cmd}",
                    headers={"Authorization": f"Bearer {self.upstash_token}"},
                    timeout=5
                )
            except:
                pass
    
    # === SLOW BRAIN INTERFACE ===
    
    def set_strategy(self, strategy: str, reasoning: str = ""):
        """Slow brain sets trading strategy"""
        if strategy not in self.STRATEGIES:
            return {"success": False, "error": f"Unknown strategy: {strategy}"}
        
        payload = {
            "strategy": strategy,
            "reasoning": reasoning,
            "set_by": "slow_brain",
            "timestamp": datetime.now().isoformat()
        }
        
        self._redis_set(self.KEYS["strategy"], json.dumps(payload))
        print(f"[BRIDGE] Strategy set: {strategy}")
        return {"success": True, "strategy": strategy}
    
    def submit_task_result(self, task_id: str, result: dict):
        """Slow brain submits result for a task"""
        payload = {
            "task_id": task_id,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        self._redis_set(f"{self.KEYS['task_result']}:{task_id}", json.dumps(payload), ex=300)
        return {"success": True}
    
    def send_heartbeat(self):
        """Slow brain sends heartbeat (must call every 60s)"""
        self._redis_set(self.KEYS["heartbeat"], datetime.now().isoformat(), ex=120)
        return {"success": True}
    
    # === FAST BRAIN INTERFACE ===
    
    def get_strategy(self) -> dict:
        """Fast brain reads current strategy"""
        data = self._redis_get(self.KEYS["strategy"])
        if data:
            return json.loads(data)
        return {"strategy": "NEUTRAL", "reasoning": "Default"}
    
    def request_analysis(self, task_type: str, data: dict) -> str:
        """Fast brain requests analysis from slow brain"""
        task_id = f"task_{int(time.time()*1000)}"
        
        payload = {
            "task_id": task_id,
            "type": task_type,  # "news_check", "chart_analysis", "sentiment"
            "data": data,
            "requested_at": datetime.now().isoformat()
        }
        
        self._redis_set(f"{self.KEYS['task_queue']}:{task_id}", json.dumps(payload), ex=300)
        print(f"[BRIDGE] Task requested: {task_type} ({task_id})")
        return task_id
    
    def get_task_result(self, task_id: str, timeout: int = 30) -> dict:
        """Fast brain waits for slow brain's response"""
        start = time.time()
        while time.time() - start < timeout:
            data = self._redis_get(f"{self.KEYS['task_result']}:{task_id}")
            if data:
                return json.loads(data)
            time.sleep(1)
        return {"error": "timeout", "task_id": task_id}
    
    def send_alert(self, alert_type: str, message: str, priority: str = "normal"):
        """Fast brain sends urgent alert"""
        payload = {
            "type": alert_type,
            "message": message,
            "priority": priority,
            "timestamp": datetime.now().isoformat()
        }
        self._redis_set(self.KEYS["alert"], json.dumps(payload), ex=60)
        print(f"[BRIDGE] Alert sent: {alert_type}")
    
    # === WATCHDOG ===
    
    def check_slow_brain_alive(self) -> bool:
        """Check if slow brain is responsive"""
        heartbeat = self._redis_get(self.KEYS["heartbeat"])
        if not heartbeat:
            return False
        
        try:
            last = datetime.fromisoformat(heartbeat)
            age = (datetime.now() - last).total_seconds()
            return age < self.watchdog_timeout
        except:
            return False
    
    def get_mode(self) -> str:
        """Get current system mode"""
        mode = self._redis_get(self.KEYS["mode"])
        return mode if mode else "NORMAL"
    
    def set_mode(self, mode: str):
        """Set system mode"""
        if mode not in self.MODES:
            return {"success": False, "error": f"Unknown mode: {mode}"}
        self._redis_set(self.KEYS["mode"], mode)
        print(f"[BRIDGE] Mode set: {mode}")
        return {"success": True, "mode": mode}
    
    def watchdog_check(self) -> dict:
        """Run watchdog check - auto-switch to SAFE mode if brain offline"""
        alive = self.check_slow_brain_alive()
        current_mode = self.get_mode()
        
        if not alive and current_mode == "NORMAL":
            print("[WATCHDOG] Slow brain offline! Switching to SAFE mode")
            self.set_mode("SAFE")
            self.send_alert("BRAIN_OFFLINE", "Slow brain disconnected, switching to SAFE mode", "high")
            return {"alive": False, "action": "switched_to_safe"}
        
        return {"alive": alive, "mode": current_mode}


class FastBrain:
    """
    The fast execution brain (runs on Cloud Run).
    Reacts in milliseconds, doesn't think, just executes.
    """
    
    def __init__(self, bridge: NeuralBridge):
        self.bridge = bridge
        self.safety_stop_loss = 0.10  # 10% hard stop
        
    def execute_strategy(self, price_data: dict) -> dict:
        """Execute based on current strategy"""
        # Check watchdog first
        watchdog = self.bridge.watchdog_check()
        mode = self.bridge.get_mode()
        
        if mode == "PANIC":
            return self._panic_sell()
        elif mode == "SAFE":
            return self._safe_mode_only_sell(price_data)
        elif mode == "MANUAL":
            return {"action": "none", "reason": "manual_override"}
        
        # Normal operation - follow slow brain's strategy
        strategy = self.bridge.get_strategy()
        strategy_name = strategy.get("strategy", "NEUTRAL")
        
        if strategy_name == "ACCUMULATE_DIP":
            return self._accumulate_dip(price_data)
        elif strategy_name == "SELL_RALLY":
            return self._sell_rally(price_data)
        elif strategy_name == "FULL_RISK_OFF":
            return self._exit_all()
        else:
            return {"action": "none", "strategy": strategy_name}
    
    def _panic_sell(self) -> dict:
        """Emergency liquidation"""
        return {
            "action": "PANIC_SELL",
            "message": "Emergency liquidation triggered",
            "execute_immediately": True
        }
    
    def _safe_mode_only_sell(self, price_data: dict) -> dict:
        """Safe mode - only close positions, no new entries"""
        return {
            "action": "SAFE_MODE",
            "message": "Only selling allowed, brain offline",
            "can_buy": False,
            "can_sell": True
        }
    
    def _accumulate_dip(self, price_data: dict) -> dict:
        """Buy on dips strategy"""
        change = price_data.get("change_5m", 0)
        
        if change < -2:  # 2% dip
            return {
                "action": "BUY",
                "reason": f"Dip detected: {change:.1f}%",
                "size": "small"
            }
        return {"action": "wait", "reason": "No dip detected"}
    
    def _sell_rally(self, price_data: dict) -> dict:
        """Sell on rallies strategy"""
        change = price_data.get("change_5m", 0)
        
        if change > 3:  # 3% pump
            return {
                "action": "SELL",
                "reason": f"Rally detected: {change:.1f}%",
                "size": "partial"
            }
        return {"action": "wait", "reason": "No rally detected"}
    
    def _exit_all(self) -> dict:
        """Exit all positions"""
        return {
            "action": "EXIT_ALL",
            "message": "Full risk-off requested by slow brain"
        }


if __name__ == "__main__":
    bridge = NeuralBridge()
    
    print("\n=== Neural Bridge Test ===")
    
    # Test strategy setting (what slow brain would do)
    print("\n[SLOW BRAIN] Setting strategy...")
    result = bridge.set_strategy("ACCUMULATE_DIP", "Market oversold, expect bounce")
    print(f"  Result: {result}")
    
    # Test strategy reading (what fast brain would do)
    print("\n[FAST BRAIN] Reading strategy...")
    strategy = bridge.get_strategy()
    print(f"  Strategy: {strategy}")
    
    # Test watchdog
    print("\n[WATCHDOG] Checking slow brain...")
    watchdog = bridge.watchdog_check()
    print(f"  Result: {watchdog}")
    
    # Test fast brain execution
    print("\n[FAST BRAIN] Executing strategy...")
    fast_brain = FastBrain(bridge)
    action = fast_brain.execute_strategy({"change_5m": -3.5})
    print(f"  Action: {action}")
