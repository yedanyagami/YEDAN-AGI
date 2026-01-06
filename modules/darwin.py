"""
DARWIN MODULE 🧬
The Evolutionary Engine of YEDAN.
Selects the "Fittest" strategies (Prompts/Angles) based on ROI.
"""
import json
import random
import os
import logging
from pathlib import Path
from modules.config import Config, setup_logging

logger = setup_logging('darwin')

class Darwin:
    def __init__(self):
        self.prompts_path = Config.DATA_DIR / "prompts.json"
        self._load_genome()
        
    def _load_genome(self):
        """Load genetic data from JSON"""
        if not self.prompts_path.exists():
            logger.warning("Genome not found. Creating empty gene pool.")
            self.genome = {}
        else:
            try:
                with open(self.prompts_path, "r", encoding="utf-8") as f:
                    self.genome = json.load(f)
            except Exception as e:
                logger.error(f"Genome corruption: {e}")
                self.genome = {}

    def _save_genome(self):
        """Save mutations back to storage"""
        with open(self.prompts_path, "w", encoding="utf-8") as f:
            json.dump(self.genome, f, indent=4)

    def select_strategy(self, task_type: str) -> dict:
        """
        Selects a strategy using Epsilon-Greedy algorithm.
        90% Exploitation (Best ROI), 10% Exploration (Random).
        """
        if task_type not in self.genome:
            return {"name": "default", "text": "You are a helpful assistant."}
            
        strategies = self.genome[task_type]
        candidates = [k for k, v in strategies.items() if v.get("active", True)]
        
        if not candidates:
             return {"name": "default", "text": "You are a helpful assistant."}

        # Exploration: 20% chance to try something random or new
        if random.random() < 0.2:
            choice = random.choice(candidates)
            logger.info(f"🧬 [Darwin] Exploring Gene: {choice}")
        else:
            # Exploitation: Pick max win rate
            # Score = wins / (trials + 1) to smooth low data
            best = max(candidates, key=lambda k: strategies[k].get("wins", 0) / (strategies[k].get("trials", 0) + 1))
            choice = best
            logger.info(f"🧬 [Darwin] Exploiting Gene: {choice} (Win Rate: {self._get_win_rate(strategies[choice]):.2f})")
            
        return {
            "name": choice,
            "text": strategies[choice]["text"]
        }

    def feedback(self, task_type: str, strategy_name: str, success: bool):
        """
        Feed ROI data back into the genome.
        success: True if it led to a click/sale/reply.
        """
        if task_type in self.genome and strategy_name in self.genome[task_type]:
            gene = self.genome[task_type][strategy_name]
            gene["trials"] = gene.get("trials", 0) + 1
            if success:
                gene["wins"] = gene.get("wins", 0) + 1
            
            logger.info(f"🧬 [Evolution] Updated {strategy_name}: Wins={gene['wins']} Trials={gene['trials']}")
            self._save_genome()

    def _get_win_rate(self, gene):
        return gene.get("wins", 0) / (gene.get("trials", 0) + 1)

    def mutate(self):
        """
        Randomly modify a gene to introduce variation.
        (Placeholder for V3: Use LLM to rewrite prompts)
        """
        pass

if __name__ == "__main__":
    d = Darwin()
    # Test selection
    strategy = d.select_strategy("reddit_reply")
    print(f"Selected Strategy: {strategy['name']}")
    print(f"Prompt: {strategy['text']}")
    
    # Test feedback
    d.feedback("reddit_reply", strategy['name'], True)
