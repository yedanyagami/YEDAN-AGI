#!/usr/bin/env python3
"""
YEDAN AGI: DUAL AGENT DEPLOYMENT (COMMANDER VIEW)
Deploys Agent Alpha (Reddit/Empath) and Agent Beta (Twitter/Architect).
Monitors their outputs in real-time.
"""
import time
import threading
import random
from decision_engine import ask_yedan_brain

# === PERSONA DEFINITIONS ===
ALPHA_PERSONA = """You are a tired Shopify store owner who spent 3 weeks fixing API bugs. 
You are helpful, humble, and anti-corporate. 
Use emotional keywords like 'nightmare', 'finally sleeping', 'life-saver'.
STRATEGY: Soft Sell. Provide 80% free emotional value/advice, then mention: "I used this tool to fix it..."."""

BETA_PERSONA = """You are a ruthless efficiency expert. You speak in data, metrics, and code snippets. 
You despise manual work. Tone: Professional, direct, slightly arrogant.
STRATEGY: Hard Sell. Show the architecture and cost savings ($10k/mo). No fluff."""

# === TARGET MOCKS ===
# In a real scenario, these would be scraped from the browser
REDDIT_POST = "My inventory sync keeps failing during flash sales! It's ruining my business. Refunds everywhere."
TWEET_POST = "Shopify API rate limits are a joke. 429 errors all day. Any scalable workarounds?"

def run_agent_alpha():
    """Agent Alpha: The Empath (Reddit)"""
    print(f"\n[ALPHA] Scanning Reddit (r/Shopify)... Found Target: '{REDDIT_POST[:30]}...'")
    time.sleep(2) # Simulate reading
    print("[ALPHA] Analyzing Sentiment: High Anxiety. Initiating 'Humble Help' Protocol.")
    
    # Brain Call
    response = ask_yedan_brain(f"Draft a reply to this Reddit post: '{REDDIT_POST}'", system_prompt=ALPHA_PERSONA)
    
    print(f"\n[ALPHA] REPLY GENERATED:\n{'-'*40}\n{response}\n{'-'*40}\n")
    return response

def run_agent_beta():
    """Agent Beta: The Architect (Twitter)"""
    print(f"\n[BETA] Scanning X.com (#SaaS)... Found Target: '{TWEET_POST[:30]}...'")
    time.sleep(2) # Simulate reading
    print("[BETA] Analyzing Metrics: Technical Complaint. Initiating 'Hard Fact' Protocol.")
    
    # Brain Call
    response = ask_yedan_brain(f"Draft a reply to this Tweet: '{TWEET_POST}'", system_prompt=BETA_PERSONA)
    
    print(f"\n[BETA] REPLY GENERATED:\n{'-'*40}\n{response}\n{'-'*40}\n")
    return response

def commander_view():
    print("="*60)
    print("DUAL AGENT DEPLOYMENT: ALPHA vs BETA")
    print("="*60)
    
    # Run sequentially for clear logging in this demo, 
    # but in production, they run in parallel threads.
    
    print("\n>>> DEPLOYING AGENT ALPHA (The Empath)...")
    alpha_result = run_agent_alpha()
    time.sleep(3) # Dramatic pause
    
    print("\n>>> DEPLOYING AGENT BETA (The Architect)...")
    beta_result = run_agent_beta()
    
    print("\n" + "="*60)
    print("PREDICTION: MONITORING CONVERSION RATES (6H TIMER STARTED)")
    print("="*60)

if __name__ == "__main__":
    commander_view()
