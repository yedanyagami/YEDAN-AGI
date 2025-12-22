"""
YEDAN AGI - Content Factory (Ultra Maximalism)
Squeezes Gemini Ultra to generate a complete multi-channel content matrix from a single signal.
"""
import os
import json
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class ContentFactory:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-pro')
                print("[FACTORY] Gemini Ultra Content Matrix: Online")
            except Exception as e:
                print(f"[FACTORY] Init Failed: {e}")
                self.model = None
        else:
            self.model = None

    def generate_matrix(self, target, deep_dive_report):
        """
        Takes a deep dive report and "squeezes" it into a multi-channel content matrix.
        """
        if not self.model:
            return None
        
        prompt = f"""
        ### SYSTEM: ULTRA CONTENT MAXIMALIST
        **MISSION**: "DRAIN THE INTEL". Turn a single report into a media empire.
        
        ### INPUT INTEL
        TARGET: {target}
        REPORT:
        {deep_dive_report}
        
        ### MAXIMALIST OUTPUT DIRECTIVES
        Generate a JSON object containing optimized content for EVERY channel.
        Use specific psychological hooks for each platform.
        
        1. **TELEGRAM (Alpha/Sales)**:
           - Short, punchy, "Inside Info" vibe.
           - Direct call to action (Buy the PDF).
           
        2. **TWITTER/X (Viral Thread)**:
           - Hook line (0% clickbait, 100% curiosity).
           - 5-tweet thread structure summarizing the thesis.
           - Hashtags: #{target} #Crypto #Alpha
           
        3. **EMAIL NEWSLETTER (Storytelling)**:
           - Subject Line: High open rate focus.
           - Body: Narrative-driven (Hero's Journey of the coin).
           - Soft sell at the bottom.
           
        4. **TRADINGVIEW IDEA (Technical)**:
           - Pure chart analysis description.
           - Entry/Exit/Stop numbers clearly listed.
           
        ### JSON OUTPUT STRUCTURE (STRICT)
        {{
            "telegram": "string...",
            "twitter_thread": ["tweet1", "tweet2"...],
            "email_subject": "string...",
            "email_body": "string...",
            "tradingview": "string..."
        }}
        """
        
        try:
            print(f"[FACTORY] Squeezing Ultra for {target} content matrix...")
            response = self.model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
            return json.loads(response.text)
        except Exception as e:
            print(f"[FACTORY] Matrix Generation Failed: {e}")
            # Fallback for non-JSON response (rare with Ultra)
            return None

if __name__ == "__main__":
    # Test
    factory = ContentFactory()
    mock_report = "Midnight (NIGHT) is breaking out due to privacy narrative. Target $0.15."
    print(json.dumps(factory.generate_matrix("Midnight", mock_report), indent=2))
