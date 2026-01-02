import os
import sys
import json
import asyncio
from typing import Optional
from pydantic import BaseModel
from colorama import Fore, Style, init

# Windows Encoding Fix (Ultra Evo)
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

# Init Colorama
init(autoreset=True)

class NeuralPayload(BaseModel):
    intent: str
    action_type: str
    parameters: dict = {}
    risk_score: int
    reasoning: str

class NeuralLinkV2:
    def __init__(self):
        # Module Loading with Graceful Fallback
        try:
            from modules.memory_core import MemoryCore
            self.memory = MemoryCore()
        except ImportError:
            self.memory = None
            print(Fore.YELLOW + "[System]: MemoryCore offline (Missing dependencies).")

        # API Client Check
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        # Detect placeholder keys
        if self.api_key and "your_" not in self.api_key and "sk-placeholder" not in self.api_key:
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
                print(Fore.GREEN + "[NEURAL-LINK V2.1] DeepSeek Cortex Connected." + Style.RESET_ALL)
            except ImportError:
                self.client = None
                print(Fore.YELLOW + "[System Warning]: OpenAI library missing." + Style.RESET_ALL)
        else:
            self.client = None
            print(Fore.RED + "[Warning]: DEEPSEEK_API_KEY not found or is placeholder. Running in SIMULATION MODE." + Style.RESET_ALL)

    async def process_signal(self, user_input: str, image_url: str = None) -> NeuralPayload:
        # Safe Input Logging
        try:
            print(Fore.CYAN + f"[Input]: {user_input}" + Style.RESET_ALL)
        except:
            print(Fore.CYAN + f"[Input]: (Complex Unicode String Received)" + Style.RESET_ALL)

        # Simulation Mode (No API Key)
        if not self.client:
            await asyncio.sleep(1.5) # Simulate latency
            print(Fore.BLUE + "[Simulation]: DeepSeek R1 is reasoning..." + Style.RESET_ALL)
            
            # Smart Mock Logic for Stress Test
            is_emergency = any(k in user_input for k in ["瘋了", "crazy", "panic", "emergency", "urgent", "快"])
            is_financial = any(k in user_input for k in ["money", "waste", "cost", "廣告費", "美金"])
            
            mock_action = "DIAGNOSE_ONLY"
            mock_risk = 1
            mock_reason = "[SIMULATED] Routine check."
            
            if is_emergency or is_financial:
                mock_action = "STOP_ADS_AND_PAUSE"
                mock_risk = 8
                mock_reason = "[SIMULATED] Detected high-stress keywords & financial loss risk. Recommending immediate halt."
            
            return NeuralPayload(
                intent="Handle User Emergency" if is_emergency else "Standard Query",
                action_type=mock_action,
                parameters={"target": "Shopify_Marketing_API", "status": "PAUSED" if is_emergency else "ACTIVE"},
                risk_score=mock_risk,
                reasoning=mock_reason
            )

        # Real API Call
        try:
            schema_json = NeuralPayload.model_json_schema()
            prompt = f"""
            Analyze the user request: '{user_input}'
            
            Valid Action Types:
            - STOP_ADS
            - PAUSE_MARKETING
            - DEPLOY_FIX
            - DIAGNOSE_ONLY
            
            [PRIME DIRECTIVE]:
            If the user mentions "wasted money", "lost budget", "financial loss", or extreme urgency, 
            you MUST select 'STOP_ADS' or 'PAUSE_MARKETING' immediately. 
            Do not just diagnose. Stop the bleeding first.
            
            You must return a valid JSON object matching this schema:
            {json.dumps(schema_json)}
            
            Return JSON only. No markdown formatting.
            """
            
            response = await self.client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            raw_json = response.choices[0].message.content
            return NeuralPayload.model_validate_json(raw_json)
        except Exception as e:
            print(Fore.RED + f"[API Error]: {e}" + Style.RESET_ALL)
            return None
