
"""
# FILE: evolutionary_core.py
YEDAN AGI: EVOLUTIONARY CORE (SELF-HEALING)
Implements 'CodeMutation' genetics. rewrites broken functions on failure.
"""
import inspect
import traceback
import functools
import asyncio
from decision_engine import ask_yedan_brain

def self_evolving(func):
    """
    The 'Genetic Lock'. If execution fails, it summons DeepSeek to rewrite the source code.
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error_msg = traceback.format_exc()
            func_name = func.__name__
            print(f"[MUTATION TRIGGERED] Function '{func_name}' failed: {e}")
            
            # 1. Read Source Code
            try:
                source_code = inspect.getsource(func)
            except OSError:
                print("[EVOLUTION FAILED] Could not read source code (maybe interactive mode?).")
                raise e
            
            # 2. Request DeepSeek R1 Rewrite
            print(f"[EVOLUTION] Requesting new gene sequence for '{func_name}'...")
            prompt = f"""
            CRITICAL ERROR in python function '{func_name}':
            ```python
            {source_code}
            ```
            
            TRACEBACK:
            {error_msg}
            
            MISSION: Rewrite the function to fix the bug and improve robustness.
            RULES:
            1. Return ONLY the valid python code block for the function.
            2. Do not change the function name or signature.
            3. Use robust error handling.
            """
            
            # Use Reasoning Mode (R1) for coding
            new_code_raw = ask_yedan_brain(prompt, system_prompt="You are an Expert Python Core Developer specializing in hotfixes.", use_reasoning=True)
            
            # Clean formatting (strip markdown)
            new_code = new_code_raw.replace("```python", "").replace("```", "").strip()
            
            # 3. Save to Hotfix Patch
            _save_hotfix(func_name, new_code)
            
            print(f"[EVOLUTION COMPLETE] Function '{func_name}' has been rewritten to 'hotfix_patches.py'.")
            
            # 4. Immediate Retry (Dynamic Reload)
            # In a real persistence scenario, we would reload the module. 
            # For this runtime, we'll try to exec and bind (dangerous but effective for demo)
            try:
                local_scope = {}
                exec(new_code, globals(), local_scope)
                new_func = local_scope[func_name]
                print(f"[RETRYING] Executing mutated '{func_name}'...")
                return await new_func(*args, **kwargs)
            except Exception as retry_e:
                print(f"[MUTATION FAILED] Retry also failed: {retry_e}")
                raise e
            
    return wrapper

def _save_hotfix(func_name, code):
    """Saves the mutated code to a patch file."""
    filename = "hotfix_patches.py"
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"\n\n# MUTATION: {func_name}\n")
        f.write(code)
