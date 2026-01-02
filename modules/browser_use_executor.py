"""
YEDAN V1300 - Browser-Use Executor (Hands)
Human-mimicking browser automation for stealth interactions.
Uses Bézier curves, typing delays, and typo injection.
"""
import logging
import random
import asyncio
import time
from typing import Optional
from modules.pydantic_models import MimicryConfig, ExecutorResult

logger = logging.getLogger('browser_use_executor')

# Attempt to import browser-use, fallback to simulation
try:
    from browser_use import Agent
    BROWSER_USE_AVAILABLE = True
except ImportError:
    BROWSER_USE_AVAILABLE = False
    logger.warning("[Browser-Use] Not installed. Running in SIMULATION MODE.")

class BrowserUseExecutor:
    """
    Human-mimicking browser executor using Browser-Use.
    Falls back to simulation when library unavailable.
    """
    def __init__(self, simulation_mode: bool = False):
        self.simulation_mode = simulation_mode or not BROWSER_USE_AVAILABLE
        self.agent = None
        
        if not self.simulation_mode:
            try:
                self.agent = Agent()
            except Exception as e:
                logger.error(f"Failed to init Browser-Use: {e}")
                self.simulation_mode = True
    
    async def execute_reply(
        self, 
        url: str, 
        message: str, 
        config: Optional[MimicryConfig] = None
    ) -> ExecutorResult:
        """
        Posts a reply to a thread with human-like behavior.
        """
        config = config or MimicryConfig()
        
        if self.simulation_mode:
            return await self._simulate_reply(url, message, config)
        
        # Real browser-use implementation
        try:
            # Apply cognitive delay before action
            await asyncio.sleep(config.cognitive_delay_sec)
            
            # Navigate and interact
            result = await self.agent.run(
                task=f"Navigate to {url}, click Reply button, type: {message}, click Submit",
                # Browser-use handles the actual Bézier mouse movements
            )
            
            return ExecutorResult(
                success=True,
                action_taken="reply",
                latency_ms=int(time.time() * 1000)
            )
            
        except Exception as e:
            logger.error(f"Browser-Use execution failed: {e}")
            return ExecutorResult(
                success=False,
                action_taken="error",
                latency_ms=0
            )
    
    async def _simulate_reply(
        self, 
        url: str, 
        message: str, 
        config: MimicryConfig
    ) -> ExecutorResult:
        """
        Simulates browser reply for offline testing.
        Logs all actions that would be taken.
        """
        logger.info(f"[SIMULATION] Browser-Use executing reply to: {url[:60]}...")
        
        # Simulate cognitive delay
        delay = random.uniform(config.cognitive_delay_sec * 0.8, config.cognitive_delay_sec * 1.2)
        logger.info(f"[SIMULATION] Cognitive delay: {delay:.1f}s (Human thinking)")
        await asyncio.sleep(min(delay, 3.0))  # Cap at 3s for testing
        
        # Simulate Bézier mouse movement
        logger.info(f"[SIMULATION] Mouse movement: {config.mouse_curve} curve to Reply button")
        await asyncio.sleep(0.5)
        
        # Simulate typing with optional typos
        typed_message = message
        if config.typo_injected and random.random() < 0.3:
            # Inject a typo and correction
            typo_pos = random.randint(5, min(20, len(message) - 5))
            typed_message = f"{message[:typo_pos]}x[BACKSPACE]{message[typo_pos:]}"
            logger.info(f"[SIMULATION] Typo injected at position {typo_pos}")
        
        # Calculate typing time
        typing_time = len(message) * config.typing_delay_sec
        logger.info(f"[SIMULATION] Typing {len(message)} chars @ {config.typing_delay_sec}s/char = {typing_time:.1f}s")
        await asyncio.sleep(min(typing_time, 2.0))  # Cap for testing
        
        # Log the reply content
        logger.info(f"[SIMULATION] Reply content ({len(message)} chars):")
        logger.info(f"   → {message[:100]}{'...' if len(message) > 100 else ''}")
        
        return ExecutorResult(
            success=True,
            action_taken="reply",
            latency_ms=int((delay + typing_time) * 1000)
        )
    
    async def simulate_scroll_and_read(self, duration_sec: float = 5.0):
        """
        Simulates human reading behavior - scrolling and pausing.
        """
        logger.info(f"[SIMULATION] Reading page for {duration_sec}s...")
        
        scroll_events = int(duration_sec / 1.5)
        for i in range(scroll_events):
            await asyncio.sleep(random.uniform(1.0, 2.0))
            logger.info(f"[SIMULATION] Scroll event {i+1}/{scroll_events}")
