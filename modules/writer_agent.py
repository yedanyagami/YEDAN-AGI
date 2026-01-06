"""
Writer Agent (Content Copilot)
Specialized agent for generating high-ROI content from user inputs.
Uses DeepSeek R1 to analyze pain points and craft empathetic, solution-oriented responses.
"""
import logging
import json
from .r1_reasoner import DeepSeekReasoner
from .darwin import Darwin

logger = logging.getLogger('writer_agent')

class WriterAgent:
    def __init__(self):
        self.brain = DeepSeekReasoner()
        self.darwin = Darwin()
        
    def generate_reply(self, user_input: str, platform: str = "reddit") -> dict:
        """
        Generates a structured reply to a user post.
        """
        # 1. Select Best Strategy via Darwin
        strategy = self.darwin.select_strategy("reddit_reply")
        logger.info(f"🧠 [Writer] Using Strategy: {strategy['name']}")
        
        # 2. Inject Strategy into Brain
        # We append the Darwin-selected persona to the prompt context
        context_input = f"{user_input}\n\n[Persona Instruction]: {strategy['text']}"
        
        reply = self.brain.generate_response(context_input, platform)
        
        # 3. Simple confidence scoring
        confidence = min(9.5, len(reply) / 100) if reply else 0.0
        
        return {
            "reply_content": reply,
            "confidence_score": round(confidence, 1),
            "model_used": self.brain.model if not self.brain.simulation_mode else "simulation",
            "strategy_used": strategy['name'] # Return this so we can log feedback later
        }

    def generate_post(self, topic: str, angle: str = None) -> str:
        """
        Generates a new top-level post based on a topic.
        """
        if not angle:
             # Let Darwin decide the angle if not specified
             # (Future: add 'reddit_post' gene to prompts.json)
             angle = "value_first"
             
        prompt = f"""
        Write a high-value Reddit post about: {topic}
        Angle: {angle}
        
        Requirements:
        - Hook: Catchy title (no clickbait).
        - Body: Provide actionable value, personal experience, or deep insight.
        - Call to Action: Subtle.
        - Format: Markdown.
        """
        return self.brain.generate_response(prompt, platform="reddit_post")

    def generate_seo_content(self, product_info: dict) -> dict:
        """
        Generates SEO-optimized title and description for a Shopify product.
        Implements logic from 'ShopifySeoChatGPT'.
        """
        # 1. Select Best Strategy via Darwin
        strategy = self.darwin.select_strategy("shopify_product_desc")
        logger.info(f"🧠 [Writer] Using Strategy: {strategy['name']}")

        title = product_info.get('title', '')
        desc = product_info.get('current_description', '')
        keywords = product_info.get('keywords', [])
        
        prompt = f"""
        Act as a Shopify SEO Expert. Optimize this product for Google Search.
        Style Guide: {strategy['text']}
        
        Product: {title}
        Current Desc: {desc}
        Target Keywords: {', '.join(keywords)}
        
        Task:
        1. Write a SEO-friendly Title (max 60 chars) that includes the main keyword.
        2. Write a converting HTML Description (Professional, clear, includes bullet points).
           - Use <h2> for section headers.
           - Highlight benefits over features.
        3. Output strict JSON format:
        {{
            "title": "...",
            "description_html": "..."
        }}
        """
        
        response = self.brain.generate_response(prompt, platform="shopify_seo")
        
        # Parse JSON from response (simple heuristic if model returns raw text)
        # In a real scenario, we'd use a parser or JSON mode. 
        # For now, we return the raw response if parsing fails.
        try:
            # Try to find JSON block
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
                data = json.loads(json_str)
            elif "{" in response and "}" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                data = json.loads(response[start:end])
            else:
                data = {"title": title + " [AI Optimized]", "description_html": response}
        except Exception:
            data = {"title": "Error Parsing AI", "description_html": response}

        return {
            "optimized_title": data.get("title", title),
            "optimized_description_html": data.get("description_html", desc),
            "seo_score": 9.5 # Mock score until we implement analysis
        }
