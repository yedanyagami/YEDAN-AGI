import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger('analytics')

LOG_FILE = "logs/interactions.jsonl"

class Analytics:
    def __init__(self):
        pass

    def generate_daily_report(self):
        """
        Parses the JSONL log and calculates simple metrics for the last 24h.
        """
        now = datetime.utcnow()
        yesterday = now - timedelta(hours=24)
        
        metrics = {
            "total_interactions": 0,
            "reddit_count": 0,
            "twitter_count": 0,
            "errors": 0
        }
        
        try:
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        record = json.loads(line)
                        ts = datetime.fromisoformat(record["timestamp"])
                        
                        if ts > yesterday:
                            metrics["total_interactions"] += 1
                            if record["platform"] == "reddit":
                                metrics["reddit_count"] += 1
                            elif record["platform"] == "twitter":
                                metrics["twitter_count"] += 1
                                
                    except (ValueError, KeyError):
                        continue
                        
        except FileNotFoundError:
            logger.warning("No interaction logs found.")
            return

        report = f"""
        [DAILY REPORT]
        Total Interactions: {metrics['total_interactions']}
        Reddit: {metrics['reddit_count']}
        Twitter: {metrics['twitter_count']}
        """
        logger.info(report)
        return metrics
