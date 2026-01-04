"""
YEDAN AGI - Strategy Engine
Persona-based ad copy generation with mutation logic
"""
import random

# Strategy Personas (System Prompts)
STRATEGIES = {
    "FOMO_DEGEN": {
        "name": "FOMO Degen",
        "prompt": "You are a crypto degen with insider alpha. Use heavy emoji, extreme urgency. Make them feel they'll miss the pump if they don't buy NOW. Short, punchy, viral.",
        "style": "emoji-heavy, urgent, viral"
    },
    "WALLSTREET_PRO": {
        "name": "Wall Street Pro", 
        "prompt": "You are a Goldman Sachs quant analyst. Cold, data-driven, professional. Cite risk/reward ratios. Build institutional trust. No emoji. Sophisticated language.",
        "style": "professional, data-driven, institutional"
    },
    "INSIDER_LEAK": {
        "name": "Insider Leak",
        "prompt": "You act like a mysterious insider. Hint that institutions are accumulating. Create intrigue and curiosity. Use phrases like 'I shouldn't be sharing this' and 'sources close to the matter'.",
        "style": "mysterious, exclusive, FOMO-inducing"
    }
}


class StrategyEngine:
    """Selects and applies trading persona strategies"""
    
    def __init__(self, genetic_memory=None):
        self.strategies = STRATEGIES
        self.genetic_memory = genetic_memory
    
    def select_strategy(self, exploit_ratio=0.8):
        """
        Select a strategy using genetic mutation logic.
        80% exploit (use best), 20% explore (random mutation)
        """
        if self.genetic_memory and random.random() < exploit_ratio:
            # Exploit: use best performing strategy
            best = self.genetic_memory.get_best_strategy()
            return best, "exploit"
        else:
            # Explore: random mutation
            choice = random.choice(list(self.strategies.keys()))
            return choice, "explore"
    
    def get_prompt(self, strategy_name):
        """Get the system prompt for a strategy"""
        if strategy_name in self.strategies:
            return self.strategies[strategy_name]["prompt"]
        return self.strategies["FOMO_DEGEN"]["prompt"]
    
    def get_style(self, strategy_name):
        """Get the style description for a strategy"""
        if strategy_name in self.strategies:
            return self.strategies[strategy_name]["style"]
        return "default"
    
    def list_strategies(self):
        """List all available strategies"""
        return list(self.strategies.keys())
    
    def generate_ad_copy(self, target, strategy_name, ai_client=None):
        """
        Generate ad copy using the selected strategy.
        Uses provided AI client or returns template.
        """
        prompt = self.get_prompt(strategy_name)
        
        if ai_client:
            try:
                # Try Cerebras/OpenAI-compatible client
                completion = ai_client.chat.completions.create(
                    model="llama-3.3-70b",  # Cerebras model
                    messages=[
                        {"role": "system", "content": f"{prompt}\n\nYour goal is to make users click and pay. Write a 50-word max ultra-compelling ad copy."},
                        {"role": "user", "content": f"Create ad copy for: {target} Analysis Report ($9.99)"}
                    ],
                    max_tokens=150
                )
                return completion.choices[0].message.content
            except Exception as e:
                print(f"[STRATEGY] AI generation failed: {e}")
        
        # Fallback templates
        templates = {
            "FOMO_DEGEN": f"🚨🔥 {target} ABOUT TO EXPLODE 🔥🚨\n\nWhales are loading bags RIGHT NOW. Don't be exit liquidity.\n\n⏰ This alpha expires in 24h ⏰",
            "WALLSTREET_PRO": f"Institutional Analysis: {target}\n\nRisk/Reward: 3.2x | Confidence: High\nTechnical confluence with macro tailwinds.\n\nProfessional-grade intel.",
            "INSIDER_LEAK": f"I probably shouldn't share this...\n\n{target} - sources indicate major accumulation by smart money.\n\nThis info won't stay private for long."
        }
        return templates.get(strategy_name, templates["FOMO_DEGEN"])


if __name__ == "__main__":
    # Test
    engine = StrategyEngine()
    strategy, mode = engine.select_strategy()
    print(f"Selected: {strategy} ({mode})")
    print(f"Prompt: {engine.get_prompt(strategy)[:100]}...")
    print(f"Ad Copy: {engine.generate_ad_copy('SOL', strategy)}")
