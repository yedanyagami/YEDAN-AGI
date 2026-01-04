"""
Writer Agent (Content Copilot)
Specialized agent for generating high-ROI content from user inputs.
Uses DeepSeek R1 to analyze pain points and craft empathetic, solution-oriented responses.
"""
import logging
import json
from .r1_reasoner import DeepSeekReasoner

logger = logging.getLogger('writer_agent')

class WriterAgent:
    def __init__(self):
        self.brain = DeepSeekReasoner()
        
    def generate_reply(self, user_input: str, platform: str = "reddit") -> dict:
        """
        Generates a structured reply to a user post.
        Returns:
            dict: {
                "scan_analysis": "Pain point identified...",
                "reply_content": "Hey, I saw your post...",
                "confidence_score": 8.5
            }
        """
        # 1. Analyze the input (Implicit in R1's reasoning, but we can structure prompts)
        # For now, we rely on R1's generate_response to do the heavy lifting.
        
        reply = self.brain.generate_response(user_input, platform)
        
        # 2. Simple confidence scoring (mock logic for now, r1 doesn't return score yet)
        # If reply is long enough, assume higher confidence
        confidence = min(9.5, len(reply) / 100) if reply else 0.0
        
        return {
            "reply_content": reply,
            "confidence_score": round(confidence, 1),
            "model_used": self.brain.model if not self.brain.simulation_mode else "simulation"
        }

    def generate_post(self, topic: str, angle: str = "value_first") -> str:
        """
        Generates a new top-level post based on a topic.
        """
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
        
        Args:
            product_info: dict with keys 'title', 'current_description', 'keywords'
            
        Returns:
            dict: {
                "optimized_title": "...",
                "optimized_description_html": "...",
                "seo_score": 9.0
            }
        """
        title = product_info.get('title', '')
        desc = product_info.get('current_description', '')
        keywords = product_info.get('keywords', [])
        
        prompt = f"""
        Act as a Shopify SEO Expert. Optimize this product for Google Search.
        
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
