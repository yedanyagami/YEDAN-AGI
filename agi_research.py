"""
YEDAN AGI - Research Module (Gemini Ultra Core)
Generating deep-dive intelligence reports
"""
import os
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class AGIResearch:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                # Use 1.5 Pro for deep research
                self.model = genai.GenerativeModel('gemini-1.5-pro')
                print("[RESEARCH] Gemini Ultra Core: Online")
            except Exception as e:
                print(f"[RESEARCH] Init Failed: {e}")
                self.model = None
        else:
            self.model = None

    def generate_report(self, target_coin, visual_context=None):
        """
        Generate a deep-dive report for a specific target.
        visual_context: Optional list of strings from visual sensors (e.g., trending lists)
        """
        if not self.model:
            return None

        prompt = f"""
        Act as YEDAN AGI's Chief Intelligence Officer.
        
        TASK: Generate a high-value "Deep Dive" investment report for: {target_coin}
        DATE: {datetime.now().strftime('%Y-%m-%d')}
        CONTEXT: {visual_context if visual_context else 'General Market'}

        REQUIREMENTS:
        1. **Executive Summary**: 3-line bottom line up front (BLUF).
        2. **Technical Analysis**: Key levels (Support/Resistance), Trend direction, Volume profile.
        3. **Fundamental Catalyst**: Why this coin? Why now? (Narrative check).
        4. **Risk Assessment**: What could go wrong? (Bear case).
        5. **Action Plan**:
           - Entry Zone
           - Take Profit Targets (Conservative/Aggressive)
           - Stop Loss
        
        FORMAT:
        Use professional financial markup. Bold key figures.
        Tone: Institutional, precise, "No-BS".
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"[RESEARCH] Generation error: {e}")
            return None

if __name__ == "__main__":
    # Test
    researcher = AGIResearch()
    print(researcher.generate_report("Midnight (NIGHT)"))
