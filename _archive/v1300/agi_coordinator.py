import time
import mmap
import struct
import os
import logging
import asyncio
from typing import Optional, Dict

# Internal Imports
from agi_config import config
from agi_evolution import AGIEvolution

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BrainCoordinator")

class MmapBridge:
    """
    Zero-Copy Bridge using Memory Mapped Files.
    Safe for Windows (No resource_tracker bugs).
    Structure: [Float: Trigger Price] [Float: Risk Factor] [Byte: Signal (0=None, 1=Buy, 2=Sell)]
    """
    def __init__(self, filename="yedan_bridge.dat", size=1024):
        self.filename = filename
        self.size = size
        self.mm = None
        self._setup_backing_file()

    def _setup_backing_file(self):
        if not os.path.exists(self.filename):
            with open(self.filename, "wb") as f:
                f.seek(self.size - 1)
                f.write(b'\0')

    def open(self):
        if not self.mm:
            with open(self.filename, "r+b") as f:
                self.mm = mmap.mmap(f.fileno(), self.size, tagname="Global\\YedanBridge")

    def close(self):
        if self.mm:
            self.mm.close()
            self.mm = None

    def write_strategy_params(self, trigger: float, risk: float):
        if not self.mm: self.open()
        try:
            self.mm.seek(0)
            # Pack 2 floats (8 bytes)
            self.mm.write(struct.pack('ff', trigger, risk))
        except Exception as e:
            logger.error(f"Bridge Write Error: {e}")

    def read_fast_state(self) -> Dict[str, float]:
        if not self.mm: self.open()
        try:
            self.mm.seek(0)
            data = self.mm.read(8)
            trigger, risk = struct.unpack('ff', data)
            return {"trigger": trigger, "risk": risk}
        except Exception as e:
            logger.error(f"Bridge Read Error: {e}")
            return {"trigger": 0.0, "risk": 0.0}

class BrainCoordinator:
    """
    Orchestrates the Fast and Slow Brains.
    Uses MmapBridge for microsecond communication.
    """
    def __init__(self):
        self.evolution = AGIEvolution()
        self.bridge = MmapBridge()
        self.running = False

    async def run_cycle(self):
        """
        The Main Loop.
        """
        logger.info("Starting Brain Coordinator...")
        self.running = True
        self.bridge.open()
        
        # Example Cycle
        while self.running:
            # 1. Fast Brain: Read Bridge (Simulated here)
            params = self.bridge.read_fast_state()
            
            # 2. Slow Brain: Evolution Check (Every 100 ticks or 1 sec)
            # In real system, this runs in separate process/thread
            # For this prototype, we just check survival
            
            # Mock Data for testing
            current_pnl = 0.0 # Placeholder
            current_vol = 0.01
            price_history = [100, 101, 102] * 20 # Placeholder
            
            alive = self.evolution.check_survival(current_pnl, current_vol, price_history)
            
            if not alive:
                logger.info("Brain Dead. Triggering Re-write...")
                # self.evolution.evolve("Fix me")
                
            await asyncio.sleep(1) # Slow Brain Tick

    def stop(self):
        self.running = False
        self.bridge.close()
