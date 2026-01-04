# YEDAN AGI - Regime Bot Configuration
# Used by market_oracle.py, execution_agent.py, and regime_oracle.py

# ═══════════════════════════════════════════════════════════════
# TRADING PARAMETERS
# ═══════════════════════════════════════════════════════════════
PAIR = "BTC/USDT"
TIMEFRAME = "5m"
HURST_WINDOW = 100

# Alpha Thresholds (from Gemini Ultra)
ALPHA_TREND_MIN = 0.60   # α ≥ 0.60 = TREND (Momentum)
ALPHA_REV_MAX = 0.40     # α ≤ 0.40 = REVERSION (Mean Reversion)
# 0.40 < α < 0.60 = NOISE (Sleep/Cash)

# ═══════════════════════════════════════════════════════════════
# TIMING
# ═══════════════════════════════════════════════════════════════
ORACLE_UPDATE_INTERVAL = 300  # 5 minutes
AGENT_POLL_INTERVAL = 1       # 1 second

# ═══════════════════════════════════════════════════════════════
# MMAP BRIDGE
# ═══════════════════════════════════════════════════════════════
MMAP_REGIME_FILE = "yedan_regime.dat"
MMAP_SIZE = 64

# Regime States
STATE_NOISE = 0
STATE_TREND = 1
STATE_REVERSION = 2

# ═══════════════════════════════════════════════════════════════
# EMA / BOLLINGER BANDS (for future trade execution)
# ═══════════════════════════════════════════════════════════════
EMA_PERIOD = 20
BB_PERIOD = 20
BB_STD = 2.0

# ═══════════════════════════════════════════════════════════════
# RISK MANAGEMENT
# ═══════════════════════════════════════════════════════════════
MAX_POSITION_SIZE = 0.1  # 10% of capital per trade
STOP_LOSS_PCT = 0.02     # 2% stop loss
TAKE_PROFIT_PCT = 0.04   # 4% take profit (2:1 RR)
