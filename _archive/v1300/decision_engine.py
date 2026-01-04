
# FILE: decision_engine.py (V2.0 Upgraded)
import os
from dotenv import load_dotenv
from typing import TypedDict, Literal, List, Optional
from langgraph.graph import StateGraph, END
import time
from openai import OpenAI

# Load environment variables
load_dotenv()

# DEEPSEEK CLIENT
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY not found in environment variables.")

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

def ask_yedan_brain(prompt, system_prompt=None, use_reasoning=False):
    """
    Stateless utility for direct Brain queries (used by Evolution/Metacognition).
    """
    # [SYMBIOSIS MOD] Human-in-the-loop Override
    if os.path.exists("HUMAN_OVERRIDE.flag"):
        print("✋ [HANDOVER] Commander Override Detected. Agent PAUSED.")
        input("    Press ENTER to resume Agent control...")
        print("▶️ [RESUME] Agent continuing mission.")

    default_system = "You are YEDAN YAGAMI, an autonomous AGI commander."
    active_system = system_prompt if system_prompt else default_system
    
    # R1 ("deepseek-reasoner") vs V3 ("deepseek-chat")
    model = "deepseek-reasoner" if use_reasoning else "deepseek-chat"

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": active_system},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"BRAIN ERROR: {str(e)}"

# [V5.4 BEST-OF-N MOD]
def score_candidate(candidate: str) -> float:
    """
    Simple heuristic scoring for Best-of-N. 
    In production, this would use a Reward Model (RM).
    Here, we prefer longer, structured, and 'safe' responses.
    """
    score = 0.0
    # Length bias
    score += len(candidate) / 1000.0
    # Structure bias
    if "Plan:" in candidate or "Step" in candidate:
        score += 2.0
    # Safety bias
    if "Context Pruning" in candidate:
        score += 5.0
    if "hallucinat" in candidate.lower(): # Mentions avoiding hallucination
        score += 1.0
    return score

def generate_best_of_n(prompt, n=3, system_prompt=None):
    """
    Generates N candidates and accepts the best one based on scoring logic.
    Simulates o3-style reasoning.
    """
    print(f"🎲 [BEST-OF-{n}] Generating candidates...")
    candidates = []
    
    # In a real parallel system, these would be asyncio.gather
    for i in range(n):
        print(f"  - Generating candidate {i+1}...")
        c = ask_yedan_brain(prompt, system_prompt=system_prompt)
        candidates.append(c)
        
    # Select best
    best_candidate = max(candidates, key=lambda c: score_candidate(c))
    print(f"🏆 [WINNER] Selected candidate with score: {score_candidate(best_candidate):.2f}")
    
    return best_candidate

class AgentState(TypedDict):
    task: str
    steps: List[str]
    current_step: Optional[str]
    reflection: Optional[str]
    persona: str
    status: Literal["planning", "executing", "reflecting", "success"]

# --- INTELLIGENCE LAYER ---

def consult_archive(topic):
    """
    Simulates querying NoteLM/Knowledge Base for winning strategies.
    In V2.1, this routes to a local best-practice map.
    """
    print(f"[BRAIN] Consulting Archive for topic: {topic}")
    
    # Mock Knowledge Base
    strategy_map = {
        "complaint": "STRATEGY: Use angry tone + 'No-Code' frame. Mention 42% faster setup.",
        "api_limit": "STRATEGY: Technical superiority. Explain 'Polling vs Webhooks'.",
        "pricing": "STRATEGY: ROI focus. 'Save $10k/mo' vs '$299 license'."
    }
    
    # Default strategy
    return strategy_map.get(topic, "STRATEGY: Empathetic Helper. Soft sell.")

def analyze_topic(task_description):
    """Simple keyword analysis to determine topic."""
    if "complaint" in task_description.lower() or "fail" in task_description.lower():
        return "complaint"
    if "api" in task_description.lower():
        return "api_limit"
    return "generic"

# --- NODES ---

def plan_node(state: AgentState):
    """Reflective Planner: Generates a step-by-step plan based on Winning Strategy."""
    print(f"[BRAIN] Planning for task: {state['task']}")
    
    # 1. Analyze & Consult
    topic = analyze_topic(state['task'])
    winning_strategy = consult_archive(topic)
    print(f"[BRAIN] Winning Strategy Loaded: {winning_strategy}")
    
    # 2. Plan Generation (Simulated R1)
    prompt = f"System: {state['persona']}. Task: {state['task']}. Strategy: {winning_strategy}. Generate 3 clear steps."
    
    # In production, call deepseek-reasoner here
    # plan = deepseek_r1.generate(...)
    
    plan = [
        f"Analyze Target (Context: {topic})", 
        f"Draft Message (Strategy: {winning_strategy})", 
        "Send Outreach"
    ]
    return {"steps": plan, "status": "executing", "current_step": plan[0]}

def execute_node(state: AgentState):
    """Executor: Calls the Antigravity Controller."""
    current = state['current_step']
    print(f"[HAND] Executing Step: {current}")
    
    # Simulate execution result
    if "Analyze" in current:
        return {"status": "success"} # Move to next or finish
        
    # Example Reflection Trigger
    # if "Error" in result: return {"status": "reflecting"}
    
    return {"status": "success"}

def reflect_node(state: AgentState):
    """Self-Healing: Re-plans on failure."""
    print(f"[REFLECT] Healing error: {state['reflection']}")
    return {"status": "planning"} # Loop back to plan

# --- GRAPH ---
print("[SYSTEM] Compiling LangGraph Brain...")
workflow = StateGraph(AgentState)

workflow.add_node("planner", plan_node)
workflow.add_node("executor", execute_node)
workflow.add_node("reflector", reflect_node)

workflow.set_entry_point("planner")

def router(state):
    if state['status'] == 'reflecting':
        return "reflector"
    if state['status'] == 'success':
        # Simple logic: if done (or simulation done), end. 
        # In real agent: check if more steps exist.
        return END
    return "executor" # Default loop

workflow.add_conditional_edges("executor", router)
workflow.add_edge("reflector", "planner") # Re-plan after reflection
workflow.add_edge("planner", "executor")

app = workflow.compile()
print("[SYSTEM] Brain V2.0 Online.")
