"""
YEDAN AGI - Genetic Memory Module
Persists and evolves strategy scores across generations
"""
import os
import json
from datetime import datetime

GENES_FILE = "agi_genes.json"

class GeneticMemory:
    """Manages AGI genetic evolution state"""
    
    def __init__(self):
        self.genes = self.load()
    
    def load(self):
        """Load genetic memory from disk"""
        if os.path.exists(GENES_FILE):
            try:
                with open(GENES_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # Genesis state
        return {
            "generation": 1,
            "total_revenue": 0.0,
            "best_strategy": "FOMO_DEGEN",
            "strategy_scores": {
                "FOMO_DEGEN": 0,
                "WALLSTREET_PRO": 0,
                "INSIDER_LEAK": 0
            },
            "history": []
        }
    
    def save(self):
        """Persist genetic memory to disk"""
        with open(GENES_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.genes, f, indent=4, ensure_ascii=False)
    
    def get_generation(self):
        """Get current generation number"""
        return self.genes["generation"]
    
    def get_best_strategy(self):
        """Get highest scoring strategy"""
        scores = self.genes["strategy_scores"]
        return max(scores, key=scores.get)
    
    def get_strategy_scores(self):
        """Get all strategy scores"""
        return self.genes["strategy_scores"]
    
    def record_outcome(self, strategy_name, target, sold, revenue=0.0):
        """Record evolution cycle outcome"""
        # Update scores
        if sold:
            self.genes["strategy_scores"][strategy_name] += 10  # Big reward
            self.genes["total_revenue"] += revenue
        else:
            self.genes["strategy_scores"][strategy_name] -= 1  # Small penalty
        
        # Update best strategy
        self.genes["best_strategy"] = self.get_best_strategy()
        
        # Record history
        self.genes["history"].append({
            "gen": self.genes["generation"],
            "strategy": strategy_name,
            "target": target,
            "sold": sold,
            "revenue": revenue,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep history bounded (last 100 entries)
        if len(self.genes["history"]) > 100:
            self.genes["history"] = self.genes["history"][-100:]
        
        # Increment generation
        self.genes["generation"] += 1
        
        # Persist
        self.save()
        
        return self.genes["generation"]
    
    def get_total_revenue(self):
        """Get total revenue earned"""
        return self.genes["total_revenue"]
    
    def get_recent_history(self, n=10):
        """Get last N evolution records"""
        return self.genes["history"][-n:]


if __name__ == "__main__":
    # Test
    gm = GeneticMemory()
    print(f"Generation: {gm.get_generation()}")
    print(f"Best Strategy: {gm.get_best_strategy()}")
    print(f"Scores: {gm.get_strategy_scores()}")
