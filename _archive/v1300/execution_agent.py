#!/usr/bin/env python3
"""
YEDAN AGI - Execution Agent
Listens to mmap regime state and executes actions.

This is the FAST BRAIN that reacts to regime changes.
"""

import sys
import os
import io
import time
import mmap
import struct
import logging
from datetime import datetime

# Fix Windows encoding (only at main entry)
if sys.platform == 'win32' and __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agi_actions import AGIActions

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
MMAP_FILE = "yedan_regime.dat"
MMAP_SIZE = 64
POLL_INTERVAL = 1  # Check every second

# Regime States
STATE_NOISE = 0
STATE_TREND = 1
STATE_REVERSION = 2

# [GEMINI ULTRA PATTERN] Heartbeat Safety
STALE_THRESHOLD = 600  # 10 minutes - halt if data older than this

logging.basicConfig(level=logging.INFO, format='%(asctime)s [AGENT] %(message)s')
logger = logging.getLogger("ExecutionAgent")


class RegimeListener:
    """Listens to regime mmap and triggers actions on change."""
    
    def __init__(self):
        self.actions = AGIActions()
        self.last_state = -1
        self.last_alpha = 0.0
        self.mm = None
        self.file = None
        self.stale_warned = False  # Prevent spam
    
    def _open_mmap(self):
        if not os.path.exists(MMAP_FILE):
            logger.warning(f"{MMAP_FILE} not found. Waiting for market_oracle...")
            return False
        
        if not self.mm:
            self.file = open(MMAP_FILE, "r+b")
            self.mm = mmap.mmap(self.file.fileno(), MMAP_SIZE)
        return True
    
    def _close_mmap(self):
        if self.mm:
            self.mm.close()
            self.file.close()
            self.mm = None
    
    def read_state(self) -> dict:
        """Read current state from mmap."""
        if not self._open_mmap():
            return None
        
        try:
            self.mm.seek(0)
            data = self.mm.read(13)
            alpha, state, timestamp = struct.unpack('<fBq', data)
            return {
                "alpha": alpha,
                "state": state,
                "timestamp": timestamp,
                "regime": ["NOISE", "TREND", "REVERSION"][state]
            }
        except Exception as e:
            logger.error(f"Read error: {e}")
            return None
    
    def on_regime_change(self, old_state: int, new_state: int, alpha: float):
        """Handle regime change event."""
        old_name = ["NOISE", "TREND", "REVERSION"][old_state] if old_state >= 0 else "INIT"
        new_name = ["NOISE", "TREND", "REVERSION"][new_state]
        emoji = ["🟡", "🟢", "🔵"][new_state]
        
        logger.info(f"🔔 REGIME CHANGE: {old_name} → {new_name} | α={alpha:.4f}")
        
        # Send Telegram notification
        message = f"""
{emoji} <b>REGIME CHANGE</b>

📊 BTC/USDT
📈 α = <code>{alpha:.4f}</code>
🎯 {old_name} → <b>{new_name}</b>

⏰ {datetime.now().strftime('%H:%M:%S')}
"""
        self.actions.telegram_send(message.strip())
        
        # Execute regime-specific action
        if new_state == STATE_TREND:
            self._on_trend_enter(alpha)
        elif new_state == STATE_REVERSION:
            self._on_reversion_enter(alpha)
        elif new_state == STATE_NOISE:
            self._on_noise_enter(alpha)
    
    def _on_trend_enter(self, alpha: float):
        """Enter TREND regime - momentum strategy."""
        logger.info("💹 TREND: Momentum mode activated")
        # TODO: Execute momentum entry via exchange API
    
    def _on_reversion_enter(self, alpha: float):
        """Enter REVERSION regime - mean reversion strategy."""
        logger.info("📉 REVERSION: Scalp mode activated")
        # TODO: Execute mean reversion setup
    
    def _on_noise_enter(self, alpha: float):
        """Enter NOISE regime - go to cash."""
        logger.info("💤 NOISE: Cash mode - all positions closed")
        # TODO: Close all positions
    
    def run(self):
        """Main listener loop."""
        logger.info("=" * 50)
        logger.info("YEDAN EXECUTION AGENT - Starting...")
        logger.info(f"Listening to: {MMAP_FILE}")
        logger.info("=" * 50)
        
        try:
            while True:
                state_data = self.read_state()
                
                if state_data:
                    current_state = state_data["state"]
                    current_alpha = state_data["alpha"]
                    data_timestamp = state_data["timestamp"]
                    
                    # [GEMINI ULTRA PATTERN] Heartbeat Safety Check
                    age = int(time.time()) - data_timestamp
                    if age > STALE_THRESHOLD:
                        if not self.stale_warned:
                            logger.warning(f"⚠️ STALE DATA: Last update {age}s ago. HALTING!")
                            self.actions.telegram_send(f"⚠️ <b>ORACLE STALE</b>\nData is {age}s old. Trading HALTED.")
                            self.stale_warned = True
                        time.sleep(POLL_INTERVAL)
                        continue  # Skip trading until fresh data
                    else:
                        if self.stale_warned:
                            logger.info("✅ Oracle data fresh again. Resuming...")
                            self.stale_warned = False
                    
                    # Detect regime change
                    if current_state != self.last_state:
                        self.on_regime_change(self.last_state, current_state, current_alpha)
                        self.last_state = current_state
                        self.last_alpha = current_alpha
                
                time.sleep(POLL_INTERVAL)
                
        except KeyboardInterrupt:
            logger.info("Agent stopped by user.")
        finally:
            self._close_mmap()


if __name__ == "__main__":
    agent = RegimeListener()
    agent.run()
