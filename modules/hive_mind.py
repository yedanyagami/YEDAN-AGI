"""
YEDAN V1300 - Hive Mind Orchestrator
Coordinates the Tri-Core Neuro-Stack: Crawl4AI, Browser-Use, PydanticAI.
"""
import logging
import random
from typing import Optional
from modules.pydantic_models import HiveAction, MimicryConfig, PricingStrategy

logger = logging.getLogger('hive_mind')

class HiveMind:
    def __init__(self, reasoner):
        self.reasoner = reasoner
        self.personas = {
            "alpha": "Aggressive Growth Hacker. Focus on ROI, speed, and domination. Uses short, punchy sentences.",
            "beta": "Risk Manager. Focus on safety, sustainability, and protecting downside. Cautious tone.",
            "gamma": "Visionary Architect. Focus on long-term brand, aesthetics, and 'vibes'. Poetic tone."
        }
    
    def swarm_debate(self, user_input: str, context_platform: str) -> str:
        """
        Simulates a debate between 3 agents to find the best angle.
        Returns the synthesized best response.
        """
        logger.info(f"🐝 [HIVE] Activating Swarm Logic for: {user_input[:40]}...")
        
        # Phase 1: Calculate panic score
        panic_score = self._calculate_panic_score(user_input)
        logger.info(f"🐝 [HIVE] Panic Score: {panic_score}/10")
        
        # Phase 2: Select persona based on urgency
        if panic_score >= 7:
            winner = "alpha"
        elif panic_score >= 4:
            winner = "beta"
        else:
            winner = "gamma"
        
        logger.info(f"🐝 [HIVE] Selected Agent: {winner.upper()}")
        
        # Phase 3: Generate response with selected persona
        response_text = self.reasoner.generate_response(
            f"[PERSONA: {self.personas[winner]}]\n\n{user_input}",
            platform=context_platform
        )
        
        return response_text

    def create_hive_action(
        self, 
        target_thread: str, 
        user_input: str,
        platform: str = "reddit"
    ) -> HiveAction:
        """
        Creates a fully validated HiveAction output.
        Uses PydanticAI for structured validation.
        """
        panic_score = self._calculate_panic_score(user_input)
        response = self.swarm_debate(user_input, platform)
        
        # Determine if pricing strategy applies
        pricing = None
        if any(kw in user_input.lower() for kw in ["audit", "compliance", "legal", "gdpr"]):
            pricing = PricingStrategy(
                price=199.99,
                rationale="Compliance risk detected - premium positioning",
                compliance_flag=True
            )
        elif any(kw in user_input.lower() for kw in ["tool", "app", "plugin"]):
            pricing = PricingStrategy(
                price=49.99,
                rationale="General tool request - standard positioning",
                compliance_flag=False
            )
        
        # Create mimicry config based on urgency
        if panic_score >= 7:
            mimicry = MimicryConfig(
                typing_delay_sec=0.08,  # Faster for urgent
                cognitive_delay_sec=15.0,
                typo_injected=False  # No mistakes on critical
            )
        else:
            mimicry = MimicryConfig(
                typing_delay_sec=0.15,
                cognitive_delay_sec=random.uniform(20.0, 35.0),
                typo_injected=random.random() < 0.2
            )
        
        return HiveAction(
            tool_used="Simulation",
            target_thread=target_thread,
            panic_score=panic_score,
            pricing_strategy=pricing,
            mimicry_config=mimicry,
            generated_reply=response or "[No response generated]",
            platform=platform,
            simulation_mode=True
        )

    def apply_stealth_pulse(self, text: str) -> str:
        """
        Humanizes text with micro-imperfections to bypass AI detectors.
        """
        if not text:
            return text
            
        # 1. Lowercase random start
        if random.random() < 0.3 and len(text) > 0:
            text = text[0].lower() + text[1:]
            
        # 2. Remove trailing period sometimes
        if text.endswith(".") and random.random() < 0.4:
            text = text[:-1]
        
        # 3. Add casual filler sometimes
        if random.random() < 0.15:
            fillers = ["honestly, ", "tbh ", "yeah so "]
            text = random.choice(fillers) + text
            
        return text
    
    def _calculate_panic_score(self, text: str) -> int:
        """
        Analyzes text for anxiety indicators.
        Returns score 1-10.
        """
        panic_keywords = {
            10: ["emergency", "urgent", "immediately", "lost everything", "快"],
            8: ["help!", "broken", "stopped working", "zero sales", "crashed"],
            6: ["struggling", "confused", "not working", "frustrating", "annoying"],
            4: ["advice", "tips", "best way", "recommend", "thoughts"],
            2: ["curious", "wondering", "anyone tried", "opinions"],
        }
        
        text_lower = text.lower()
        for score, keywords in sorted(panic_keywords.items(), reverse=True):
            if any(kw in text_lower for kw in keywords):
                return score
        
        return 3  # Default moderate score
