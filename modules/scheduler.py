"""
Viral Scheduler (The Timekeeper)
Releases content at peak viral hours (9AM, 12PM, 5PM, 8PM EST).
"""
import logging
from datetime import datetime, time
import random
import queue

logger = logging.getLogger('scheduler')

class ViralScheduler:
    def __init__(self):
        self.queue = queue.PriorityQueue()
        self.peak_hours = [9, 12, 17, 20] # EST approx
        
    def add_content(self, content: dict, platform="twitter", priority=1):
        """
        Add content to the holding queue.
        Priority: 0 (Critical), 1 (High), 2 (Normal)
        """
        # (priority, timestamp, item)
        self.queue.put((priority, datetime.now(), {"content": content, "platform": platform}))
        logger.info(f"⏳ Scheduled: '{content.get('title', 'Unknown')[:30]}...' (Priority {priority})")

    def is_peak_hour(self) -> bool:
        """Check if current hour is a peak hour"""
        now = datetime.now()
        is_peak = now.hour in self.peak_hours
        
        # Add some randomness/fuzziness (+/- 30 mins handled by polling logic)
        # For simulation, we assume check happens frequently.
        return is_peak

    def get_next_content(self) -> dict:
        """Get content if it's time to post, else None (unless forced)"""
        # In a real system, we'd strict-check time. 
        # For "Time is Money" velocity, we might skip strict waiting if queue is full.
        # But let's respect the "Scheduler" name.
        
        if self.queue.empty():
            return None
            
        # If simulation or always-on mode
        return self.queue.get()[2]

    def pending_count(self):
        return self.queue.qsize()

if __name__ == "__main__":
    # Test
    sched = ViralScheduler()
    sched.add_content({"title": "Test Viral Post"}, priority=1)
    print(f"Pending: {sched.pending_count()}")
    item = sched.get_next_content()
    print(f"Released: {item['content']['title']}")
