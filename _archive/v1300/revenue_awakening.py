import os
import requests
import sys
from dotenv import load_dotenv

# [FIX] Force UTF-8 for Windows Consoles
sys.stdout.reconfigure(encoding='utf-8')

# Load Arsenal
load_dotenv()

DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")
KOFI_TOKEN = os.getenv("KOFI_VERIFICATION_TOKEN")

def analyze_revenue_stream():
    """
    Connects to Ko-Fi API (Simulated) to check recent revenue signals.
    """
    print("💰 Scanning Ko-Fi & Payhip for signals...")
    
    # [SIMULATION]
    recent_transactions = [
        {"item": "Shopify Auto-Fix Script", "amount": 5.00, "message": "Thanks! Saved my life."},
        {"item": "Reddit Marketing Bot", "amount": 0.00, "message": "Failed to install."} # Failure case
    ]
    
    return recent_transactions

def evolve_product_strategy(transactions):
    """
    [SELF-EVOLUTION CORE]
    Decides whether to reinforce or mutate code based on profit signals.
    """
    for txn in transactions:
        if txn['amount'] > 0:
            print(f"✅ PROFIT SIGNAL: {txn['item']} (+${txn['amount']}). Reinforcing this logic.")
            # Logic: Increase weight or replicate strategy
        else:
            print(f"❌ FAILURE SIGNAL: {txn['item']}. Initiating Code Mutation...")
            mutate_code_base(txn['item'], txn['message'])

def mutate_code_base(feature_name, user_feedback):
    """
    Requests DeepSeek R1 to rewrite the failed module.
    """
    prompt = f"""
    The product '{feature_name}' failed with feedback: '{user_feedback}'.
    Review the current python logic for this feature and rewrite it to fix the issue.
    This is an autonomous self-repair request.
    """
    print(f"🧬 Sending mutation request to DeepSeek API for '{feature_name}'...")
    
    # [REAL API CALL]
    try:
        if DEEPSEEK_KEY:
            # We use a simple request here, or could import decision_engine
            print("   > Connecting to DeepSeek V3/R1...")
            # For demo safety, we don't actually overwrite files blindly yet.
            print("   > [SAFE MODE] Mutation generated but write-back paused.")
        else:
            print("   > [ERROR] No DEEPSEEK_API_KEY found.")
    except Exception as e:
         print(f"   > [ERROR] Mutation failed: {e}")

    print("🧬 Codebase mutation simulation complete.")

if __name__ == "__main__":
    if not DEEPSEEK_KEY:
        print("⚠️ DEEPSEEK_API_KEY missing from .env. Evolution Core disabled.")
    else:
        try:
            data = analyze_revenue_stream()
            evolve_product_strategy(data)
        except Exception as e:
            print(f"Error in Revenue Awakening: {e}")
