#!/usr/bin/env python3
"""
YEDAN AGI: THE REVENUE (SHOPIFY AGENT ARCHITECTURE) V2.0
Uses LangGraph Brain for decision-making.
Architecture: Webhook -> LangGraph Brain -> Auto-Action -> Shopify API
"""
import time
import os
import requests
from dotenv import load_dotenv
from decision_engine import app as brain

load_dotenv()
SHOPIFY_ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
SHOPIFY_STORE_URL = os.getenv("SHOPIFY_STORE_URL")

class RevenueAgent:
    def __init__(self):
        self.status = "LISTENING"
    
    def on_webhook_trigger(self, payload):
        """
        Simulates receiving a Webhook from Shopify (e.g., Inventory Level Low, Order Created).
        """
        print(f"[REVENUE] Webhook Received: {payload.get('event_type')}")
        
        # Use LangGraph Brain to decide action
        action_plan = self.generate_action_plan(payload)
        
        # Execute the action
        self.execute_shopify_action(action_plan)

    def generate_action_plan(self, payload):
        """
        Uses LangGraph Brain to generate an action plan.
        """
        initial_state = {
            "task": f"Handle Shopify event: {payload.get('event_type')}. Data: {payload.get('data')}",
            "persona": "Shopify Automation Bot. Be concise and action-oriented.",
            "steps": [],
            "current_step": None,
            "reflection": None,
            "status": "planning"
        }
        
        print("[REVENUE] Consulting LangGraph Brain...")
        final_state = brain.invoke(initial_state)
        
        # Extract the plan from final state
        return final_state.get('steps', ["No action generated"])

    def execute_shopify_action(self, action_plan):
        print(f"[ACTION] Executing Plan: {action_plan}")

if __name__ == "__main__":
    agent = RevenueAgent()
    
    # Simulation: Trigger
    test_payload = {
        "event_type": "INVENTORY_LEVEL_LOW",
        "data": "SKU-999 is at 0 stock. 10 orders pending."
    }
    
    agent.on_webhook_trigger(test_payload)
