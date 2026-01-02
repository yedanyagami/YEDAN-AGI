import logging
import time
from textblob import TextBlob
from modules.utils import check_pause_flag

logger = logging.getLogger('safety_guard')

class SafetyGuard:
    def __init__(self):
        self.promo_count = 0
        self.value_post_count = 0
        self.last_reply_times = {} # user_id -> timestamp

    def check_sentiment(self, text):
        """
        Returns False if text is too negative/aggressive (likely a rant/troll).
        """
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity # -1 to 1
        
        # If extremely negative interaction, skip it
        if sentiment < -0.6:
            logger.warning(f"Sentiment check failed: {sentiment:.2f}")
            return False
            
        return True

    def validate_promo_ratio(self):
        """
        Ensures we don't exceed 10% self-promotion ratio.
        """
        total = self.promo_count + self.value_post_count
        if total == 0:
            return True
            
        ratio = self.promo_count / total
        if ratio > 0.15: # Allow slight buffer, strict target is 0.10
            logger.warning(f"Promo ratio too high: {ratio:.2f}. Limit self-promotion.")
            return False
            
        return True

    def check_duplicate_user(self, user_id):
        """
        Prevent spamming the same user multiple times in 48 hours.
        """
        now = time.time()
        last_time = self.last_reply_times.get(user_id)
        
        if last_time and (now - last_time) < 172800: # 48 hours
            logger.info(f"Skipping duplicate user {user_id}")
            return False
            
        return True

    def record_action(self, user_id, is_promo=False):
        self.last_reply_times[user_id] = time.time()
        if is_promo:
            self.promo_count += 1
        else:
            self.value_post_count += 1

    def is_safe_to_post(self, user_id, content_text):
        if check_pause_flag():
            return False
            
        if not self.check_sentiment(content_text):
            return False
            
        if not self.check_duplicate_user(user_id):
            return False
        
        # If current response is promo, check ratio
        # (This logic implies we know if *this* pending post is promo. 
        # For now, we assume all automated tool-linking posts are promo)
        if not self.validate_promo_ratio():
             # If ratio bad, maybe we should post without link? 
             # For now, just block to be safe.
             return False

        return True
