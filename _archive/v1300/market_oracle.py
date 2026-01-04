#!/usr/bin/env python3
"""
YEDAN AGI - Market Oracle (Continuous Loop)
The "Always-On Eye" that monitors market regime and updates mmap bridge.

This is the AUTOMATED version of regime_oracle.py
Runs 24/7, writes to mmap for fast brain consumption.
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

from agi_math import FractalMath
from agi_config import config

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
PAIR = "BTC/USDT"
TIMEFRAME = "5m"
HURST_WINDOW = 100
UPDATE_INTERVAL = 300  # 5 minutes

# Alpha Thresholds
ALPHA_TREND_MIN = 0.60
ALPHA_REV_MAX = 0.40

# Regime States (for mmap)
STATE_NOISE = 0
STATE_TREND = 1
STATE_REVERSION = 2

# Mmap file
MMAP_FILE = "yedan_regime.dat"
MMAP_SIZE = 64  # bytes: [float alpha] [byte state] [long timestamp]

logging.basicConfig(level=logging.INFO, format='%(asctime)s [ORACLE] %(message)s')
logger = logging.getLogger("MarketOracle")


class RegimeBridge:
    """
    Zero-copy bridge for regime state.
    Structure: [float32 alpha] [uint8 state] [int64 timestamp]
    """
    def __init__(self, filename=MMAP_FILE, size=MMAP_SIZE):
        self.filename = filename
        self.size = size
        self.mm = None
        self._setup()
    
    def _setup(self):
        if not os.path.exists(self.filename):
            with open(self.filename, "wb") as f:
                f.write(b'\x00' * self.size)
    
    def open(self):
        if not self.mm:
            self.file = open(self.filename, "r+b")
            self.mm = mmap.mmap(self.file.fileno(), self.size)
    
    def close(self):
        if self.mm:
            self.mm.close()
            self.file.close()
            self.mm = None
    
    def write_state(self, alpha: float, state: int):
        """Write current regime state to mmap."""
        if not self.mm:
            self.open()
        try:
            timestamp = int(time.time())
            # Pack: float (4) + byte (1) + long (8) = 13 bytes
            data = struct.pack('<fBq', alpha, state, timestamp)
            self.mm.seek(0)
            self.mm.write(data)
            self.mm.flush()
        except Exception as e:
            logger.error(f"Bridge write error: {e}")
    
    def read_state(self) -> dict:
        """Read current regime state from mmap."""
        if not self.mm:
            self.open()
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
            logger.error(f"Bridge read error: {e}")
            return {"alpha": 0.5, "state": 0, "timestamp": 0, "regime": "NOISE"}


def fetch_btc_data() -> list:
    """Fetch BTC/USDT close prices from Binance."""
    try:
        import ccxt
        exchange = ccxt.binance({'options': {'defaultType': 'future'}})
        ohlcv = exchange.fetch_ohlcv(PAIR, TIMEFRAME, limit=HURST_WINDOW + 50)
        closes = [candle[4] for candle in ohlcv]
        return closes[-HURST_WINDOW:]
    except ImportError:
        logger.error("ccxt not installed. Run: pip install ccxt")
        return []
    except Exception as e:
        logger.error(f"Binance error: {e}")
        return []


def calculate_regime(alpha: float) -> int:
    """Map alpha to regime state."""
    if alpha >= ALPHA_TREND_MIN:
        return STATE_TREND
    elif alpha <= ALPHA_REV_MAX:
        return STATE_REVERSION
    else:
        return STATE_NOISE


def get_regime_emoji(state: int) -> str:
    """Get emoji for regime state."""
    return ["🟡", "🟢", "🔵"][state]


def run_oracle():
    """Main continuous loop."""
    logger.info("=" * 50)
    logger.info("YEDAN MARKET ORACLE - Starting...")
    logger.info(f"Pair: {PAIR} | Timeframe: {TIMEFRAME} | Window: {HURST_WINDOW}")
    logger.info(f"Update interval: {UPDATE_INTERVAL}s")
    logger.info("=" * 50)
    
    bridge = RegimeBridge()
    bridge.open()
    
    last_state = -1
    
    try:
        while True:
            # Fetch data
            closes = fetch_btc_data()
            if not closes:
                logger.warning("No data received, retrying in 60s...")
                time.sleep(60)
                continue
            
            # Calculate alpha
            alpha = FractalMath.calculate_dfa_alpha(closes)
            state = calculate_regime(alpha)
            emoji = get_regime_emoji(state)
            regime_name = ["NOISE", "TREND", "REVERSION"][state]
            
            # Write to mmap
            bridge.write_state(alpha, state)
            
            # Log (only on state change or every 5 ticks)
            if state != last_state:
                logger.info(f"{emoji} REGIME CHANGE: {regime_name} | α={alpha:.4f}")
                last_state = state
            else:
                logger.info(f"{emoji} {regime_name} | α={alpha:.4f}")
            
            # Wait for next tick
            time.sleep(UPDATE_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("Oracle stopped by user.")
    finally:
        bridge.close()


def read_current_state():
    """Read current state from mmap (for other processes)."""
    bridge = RegimeBridge()
    state = bridge.read_state()
    bridge.close()
    return state


if __name__ == "__main__":
    if "--read" in sys.argv:
        # Just read current state
        state = read_current_state()
        print(f"Current: {state['regime']} | α={state['alpha']:.4f}")
    else:
        # Run continuous loop
        run_oracle()
