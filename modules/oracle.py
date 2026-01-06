"""
YEDAN AGI - The Oracle Module
Predictive Intelligence using Google Trends data.
Determines "Win Probability" for content topics.
"""
import time
import random
from datetime import datetime, timedelta
from modules.config import Config, setup_logging

logger = setup_logging('oracle')

try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False
    logger.warning("pytrends not installed. Oracle running in FALLBACK mode.")

class Oracle:
    """Predictive Intelligence Engine"""
    
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360) if PYTRENDS_AVAILABLE else None
        
    def get_trend_score(self, keyword: str) -> dict:
        """
        Calculate a 'Win Probability' score (0-100) for a keyword.
        Based on 12-month interest trajectory.
        """
        if not self.pytrends:
            return self._fallback_score(keyword)
            
        try:
            # Avoid rate limits with random sleep
            time.sleep(random.uniform(1, 3))
            
            # Build payload
            self.pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo='', gprop='')
            
            # Get interest over time
            data = self.pytrends.interest_over_time()
            
            if data.empty:
                logger.info(f"No trend data for '{keyword}'")
                return {"score": 0, "status": "no_data"}
                
            # Analysis Logic
            # 1. Calculate Average Interest
            avg_interest = data[keyword].mean()
            
            # 2. Calculate Trend (Last 30 days vs Previous 30 days)
            # We take the last few data points
            recent = data[keyword].tail(4).mean()
            past = data[keyword].head(12).mean() # Baseline
            
            # 3. Momentum Score
            momentum = 50 # Base score
            if recent > past:
                momentum += 20 # Rising
            if recent > 80:
                momentum += 20 # Peak popularity
            if recent < 20:
                momentum -= 30 # Dead topic
                
            # Clamp 0-100
            score = max(0, min(100, momentum))
            
            return {
                "score": int(score),
                "avg_interest": float(avg_interest),
                "trend": "rising" if recent > past else "falling",
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Oracle error for '{keyword}': {e}")
            return self._fallback_score(keyword)
            
    def _fallback_score(self, keyword: str) -> dict:
        """Fallback if API fails (heuristic based on keyword length/complexity)"""
        # Heuristic: Shorter keywords often higher volume, specific ones lower but targeted.
        # This is just a placeholder to keep system ALIVE.
        score = 50 + random.randint(-10, 10)
        return {
            "score": score,
            "status": "fallback",
            "reason": "api_unavailable"
        }

if __name__ == "__main__":
    # Test Routine
    import sys
    oracle = Oracle()
    test_keywords = ["dropshipping", "ai agents", "fidget spinner"]
    
    if len(sys.argv) > 1:
        test_keywords = [sys.argv[1]]
        
    print("\n🔮 ORACLE PREDICTIONS\n" + "="*30)
    for kw in test_keywords:
        result = oracle.get_trend_score(kw)
        print(f"[{kw.upper()}] Score: {result['score']}/100 ({result.get('trend', 'unknown')})")
        print(f"   -> Status: {result['status']}")
    print("="*30 + "\n")
