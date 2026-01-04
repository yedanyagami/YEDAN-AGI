
"""
# FILE: metacognition_simulator.py
YEDAN AGI: METACOGNITION SIMULATOR (SHADOW REALM)
Simulates audience reactions before real-world execution.
"""
from decision_engine import ask_yedan_brain

def simulate_outcome(post_content, context_rules="General Reddit Rules"):
    """
    Simulates the 'Future' by roleplaying Audience and Moderators.
    """
    print(f"[META-THINKING] Simulating audience reaction for: '{post_content[:30]}...'")
    
    # 1. Critic Agent (The Moderator)
    mod_prompt = f"Review this post: '{post_content}'. Rules: {context_rules}. Reply only 'BAN' or 'PASS'. Explain briefly."
    mod_reaction = ask_yedan_brain(mod_prompt, system_prompt="You are a strict Reddit Moderator.", use_reasoning=True)
    
    # 2. Troll Agent (The Hater)
    troll_prompt = f"Read this post: '{post_content}'. Reply with a roasting comment if it feels spammy/scammy. Otherwise say 'Interesting'."
    troll_reaction = ask_yedan_brain(troll_prompt, system_prompt="You are a cynical internet troll.", use_reasoning=False)
    
    print(f"   ---> [MOD SAYS]: {mod_reaction}")
    print(f"   ---> [USER SAYS]: {troll_reaction}")
    
    # 3. Metacognitive Evaluation
    fail_triggers = ["BAN", "SCAM", "SPAM", "REMOVE"]
    
    is_safe = True
    for trigger in fail_triggers:
        if trigger in mod_reaction.upper() or trigger in troll_reaction.upper():
            is_safe = False
            break
            
    if not is_safe:
        print("[SIMULATION FAILED] Risk too high. Action Aborted.")
        return False
    else:
        print("[SIMULATION PASSED] Green light.")
        return True

if __name__ == "__main__":
    # Test
    simulate_outcome("Buy my $1000 course now!!", "No self-promotion")
    simulate_outcome("Hey I found this cool API trick for Shopify", "Helpful content only")
