#!/usr/bin/env python3
"""
YEDAN AGI - Regime Oracle CLI
Tipping Point Project: Manual MVT for "YEDAN Regime Signals"

Usage:
    python regime_oracle.py              # Full report
    python regime_oracle.py --quick      # One-liner for copy-paste
    python regime_oracle.py --export     # Export for Twitter/Telegram
"""

import sys
import os
import io

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from agi_math import FractalMath

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION - Adjust as needed
# ═══════════════════════════════════════════════════════════════
PAIR = "BTC/USDT"
TIMEFRAME = "5m"
HURST_WINDOW = 100

# Alpha Thresholds (from Gemini Ultra)
ALPHA_TREND_MIN = 0.60   # α ≥ 0.60 = TREND
ALPHA_REV_MAX = 0.40     # α ≤ 0.40 = REVERSION
# 0.40 < α < 0.60 = NOISE (Sleep)


def fetch_btc_data() -> list:
    """
    Fetch BTC/USDT OHLCV data from Binance.
    Returns list of close prices.
    """
    try:
        import ccxt
        exchange = ccxt.binance({'options': {'defaultType': 'future'}})
        ohlcv = exchange.fetch_ohlcv(PAIR, TIMEFRAME, limit=HURST_WINDOW + 50)
        closes = [candle[4] for candle in ohlcv]  # Close price
        return closes[-HURST_WINDOW:]
    except ImportError:
        print("[!] ccxt not installed. Run: pip install ccxt")
        print("[!] Using DEMO data for testing...")
        import random
        return [40000 + random.uniform(-500, 500) for _ in range(HURST_WINDOW)]
    except Exception as e:
        print(f"[!] Binance error: {e}")
        print("[!] Using DEMO data for testing...")
        import random
        return [40000 + random.uniform(-500, 500) for _ in range(HURST_WINDOW)]


def calculate_regime(alpha: float) -> tuple:
    """
    Determine market regime from Alpha exponent.
    Returns: (regime_name, emoji, action, color_code)
    """
    if alpha >= ALPHA_TREND_MIN:
        return ("TREND", "🟢", "Momentum: Follow the move", "\033[92m")
    elif alpha <= ALPHA_REV_MAX:
        return ("REVERSION", "🔵", "Mean Reversion: Scalp ranges", "\033[94m")
    else:
        return ("NOISE", "🟡", "Cash is a position. SLEEP.", "\033[93m")


def print_full_report(alpha: float, regime: tuple):
    """Print detailed regime report for analysis."""
    name, emoji, action, color = regime
    reset = "\033[0m"
    
    print("\n" + "═" * 60)
    print(f"  YEDAN REGIME ORACLE | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("═" * 60)
    print(f"  Asset: {PAIR} | Timeframe: {TIMEFRAME} | Window: {HURST_WINDOW}")
    print("-" * 60)
    print(f"  DFA Alpha: {color}{alpha:.4f}{reset}")
    print(f"  Regime:    {color}{emoji} {name}{reset}")
    print(f"  Action:    {action}")
    print("-" * 60)
    print("  Thresholds:")
    print(f"    α ≥ {ALPHA_TREND_MIN:.2f} → TREND (Momentum)")
    print(f"    α ≤ {ALPHA_REV_MAX:.2f} → REVERSION (Scalp)")
    print(f"    else   → NOISE (Sleep)")
    print("═" * 60)


def print_quick(alpha: float, regime: tuple):
    """One-liner for quick terminal check."""
    name, emoji, action, color = regime
    reset = "\033[0m"
    print(f"{emoji} {name} | α={alpha:.4f} | {action}")


def export_for_social(alpha: float, regime: tuple):
    """Generate copy-paste ready text for Twitter/Telegram."""
    name, emoji, action, _ = regime
    timestamp = datetime.now().strftime('%H:%M UTC+8')
    
    twitter_text = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━
🔮 YEDAN REGIME SIGNAL | {timestamp}
━━━━━━━━━━━━━━━━━━━━━━━━━

📊 {PAIR} | {TIMEFRAME}
📈 DFA Alpha: {alpha:.4f}

{emoji} REGIME: **{name}**

💡 {action}

━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ Statistical analysis only. Not financial advice.
#BTC #Trading #DFA #HurstExponent
━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    telegram_text = f"""
🔮 **YEDAN REGIME SIGNAL** | {timestamp}

📊 {PAIR} | {TIMEFRAME}
📈 DFA Alpha: `{alpha:.4f}`

{emoji} **REGIME: {name}**

💡 {action}

⚠️ _Statistical analysis only. Not financial advice._
"""
    
    print("\n" + "=" * 50)
    print("📱 TWITTER COPY:")
    print("=" * 50)
    print(twitter_text)
    
    print("\n" + "=" * 50)
    print("📱 TELEGRAM COPY:")
    print("=" * 50)
    print(telegram_text)


def main():
    # Parse args
    quick_mode = "--quick" in sys.argv
    export_mode = "--export" in sys.argv
    
    # Fetch data
    if not quick_mode:
        print(f"[*] Fetching {PAIR} data from Binance...")
    
    closes = fetch_btc_data()
    
    # Calculate Alpha
    alpha = FractalMath.calculate_dfa_alpha(closes)
    regime = calculate_regime(alpha)
    
    # Output based on mode
    if quick_mode:
        print_quick(alpha, regime)
    elif export_mode:
        print_full_report(alpha, regime)
        export_for_social(alpha, regime)
    else:
        print_full_report(alpha, regime)


if __name__ == "__main__":
    main()
