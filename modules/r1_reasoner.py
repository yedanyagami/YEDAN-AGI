import os
import logging
import random
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.reactor")

logger = logging.getLogger('r1_reasoner')

class DeepSeekReasoner:
    def __init__(self):
        self.simulation_mode = False
        api_key = os.getenv("DEEPSEEK_API_KEY")
        
        # Detect missing or placeholder keys
        if not api_key or "your_" in api_key or "placeholder" in api_key.lower():
            logger.warning("DEEPSEEK_API_KEY missing or placeholder. Enabling SIMULATION MODE.")
            self.simulation_mode = True
            self.client = None
        else:
            try:
                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.deepseek.com/v1" 
                )
                self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-reasoner")
            except Exception as e:
                logger.error(f"Failed to init DeepSeek client: {e}")
                self.simulation_mode = True
                self.client = None

    def generate_response(self, user_problem, platform="reddit"):
        """
        Generates a technical solution using DeepSeek R1.
        Falls back to simulation if API is unavailable.
        """
        # Simulation Mode - Return mock response
        if self.simulation_mode or self.client is None:
            return self._generate_mock_response(user_problem, platform)
        
        system_prompt = """You are a senior Shopify Data Architect and Developer.
Your goal is to help users solve complex technical problems with empathy and precision.
You do NOT sound like a generic AI. You sound like a tired but helpful senior engineer.

Methodology:
1. deep_think: Analyze the root cause. Valid technical issue? Or user error?
2. empathy: Briefly validate their frustration (1 sentence).
3. solution: Provide the exact code, Liquid tag, or API call to fix it.
4. format: Use markdown code blocks.
5. tone: Professional, concise, "StackOverflow" style but nicer.

CRITICAL: Do not include the disclosure footer yourself. The system will append it.
"""
        
        user_msg = f"""
        User Post ({platform}): 
        {user_problem}
        
        Task:
        - Diagnose the issue.
        - Write a response that solves it.
        - If it's a known API limit or bug, explain exactly why it's happening.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ]
            )
            content = response.choices[0].message.content
            return content

        except Exception as e:
            logger.error(f"DeepSeek generation failed: {e}")
            # Fallback to simulation on error
            return self._generate_mock_response(user_problem, platform)
    
    def _generate_mock_response(self, user_problem, platform):
        """
        Generates a simulated response for offline testing.
        Uses keyword analysis to provide contextual mock replies.
        """
        logger.info("[SIMULATION] Generating mock response...")
        
        problem_lower = user_problem.lower()
        
        # Anxiety-driven response templates
        if any(kw in problem_lower for kw in ["roas", "ads", "facebook", "meta"]):
            templates = [
                "Been there. The key is to check your pixel events first - most ROAS drops come from misconfigured purchase events. Run `Meta Pixel Helper` extension and verify your `Purchase` event fires on order confirmation.",
                "Classic. Meta changed their attribution window silently. Go to Events Manager > Settings and check if you're on 7-day click or 1-day view. The numbers will look different but conversions might still be there."
            ]
        elif any(kw in problem_lower for kw in ["shopify", "store", "theme"]):
            templates = [
                "Quick check - did you recently update your theme? Shopify's 2.0 themes handle sections differently. Try reverting to a backup and see if the issue persists. If yes, it's your customizations.",
                "This is usually a caching issue. Clear your theme cache (Online Store > Actions > Edit code, then save any file). Also check if you have any app conflicts in the theme.liquid."
            ]
        elif any(kw in problem_lower for kw in ["dropship", "supplier", "shipping"]):
            templates = [
                "The supplier game is rough. I'd recommend DSers or CJDropshipping for reliability. AliExpress direct is a coinflip. Also, set customer expectations upfront with 15-25 day shipping notices.",
                "Biggest mistake I see: not having a backup supplier. When one fails, your whole store goes down. Always 2x source your top 3 products."
            ]
        else:
            templates = [
                "Interesting problem. Could you share more details? Specifically: 1) When did this start? 2) Any recent changes to your setup? 3) What have you already tried?",
                "I've seen similar issues before. The root cause is usually one of three things: API rate limits, app conflicts, or theme code issues. Let me know which applies and I can dig deeper."
            ]
        
        return random.choice(templates)
