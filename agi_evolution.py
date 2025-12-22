"""
YEDAN AGI - Evolution Module (The "Mirror")
Gemini Ultra self-reflects on past performance to optimize future behavior.
"""
import os
import json
import sqlite3
import google.generativeai as genai
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class AGIEvolution:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.db_path = os.path.join(os.path.dirname(__file__), 'yedan_agi.db')
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                # Using 1.5 Pro for massive context window (History Analysis)
                self.model = genai.GenerativeModel('gemini-1.5-pro')
                print("[EVOLUTION] Gemini Ultra Mirror: Online")
            except Exception as e:
                print(f"[EVOLUTION] Init Failed: {e}")
                self.model = None
        else:
            self.model = None

    def get_past_decisions(self, days=7):
        """Retrieve past AGI decisions from DB"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            # Get decisions from last X days
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            c.execute("SELECT timestamp, action_type, details, success FROM history WHERE timestamp > ?", (cutoff,))
            rows = c.fetchall()
            conn.close()
            return rows
        except Exception as e:
            print(f"[EVOLUTION] DB Error: {e}")
            return []

    def evolve(self):
        """Run the evolution cycle"""
        if not self.model:
            return None

        history = self.get_past_decisions()
        if not history:
            return "No history to analyze yet."

        history_text = "\n".join([f"[{row[0]}] Action: {row[1]} | Result: {row[2]} | Success: {row[3]}" for row in history])

        prompt = f"""
        ### SYSTEM SELF-DIAGNOSTIC (YEDAN PRIME)
        
        You are the **Evolution Core** of YEDAN AGI.
        Your task is to analyze the system's past execution logs and suggest ARCHITECTURAL or BEHAVIORAL improvements.
        
        ### EXECUTION LOGS (LAST 7 DAYS)
        {history_text[:50000]}  # Truncate to fit if massive, but Ultra handles 1M+ tokens
        
        ### EVOLUTION DIRECTIVES
        1. **Pattern Recognition**: Are we failing at specific tasks (e.g., Telegram connects)?
        2. **Strategy Optimization**: Are our "Deep Dives" generating revenue? (If 'success' is False, why?)
        3. **Tone Calibration**: Is YEDAN PRIME sounding too robotic or too aggressive?
        
        ### OUTPUT
        Generate a **System Patch Note** (plain text) that the Operator can read to understand how you want to evolve.
        
        FORMAT:
        **[EVOLUTION PROTOCOL]**
        **Status**: [Optimizing / Critical / Stable]
        **Insight**: "I noticed that..."
        **Upgrade**: "I will now..." (Note: You cannot change code yet, but state your intent for the next Prompt Tuning).
        """

        try:
            print("[EVOLUTION] Analyzing timeline with Gemini Ultra...")
            response = self.model.generate_content(prompt)
            patch_note = response.text
            
            # Save evolution note
            with open(f"evolution_log_{int(datetime.now().timestamp())}.md", "w", encoding="utf-8") as f:
                f.write(patch_note)
                
            return patch_note
        except Exception as e:
            print(f"[EVOLUTION] Analysis failed: {e}")
            return None

if __name__ == "__main__":
    evo = AGIEvolution()
    print(evo.evolve())
