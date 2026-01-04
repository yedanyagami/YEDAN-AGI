"""
# FILE: memory_optimization.py - V5.1 FORGETTING
YEDAN AGI: STRATEGIC FORGETTING ENGINE
(Truth #1) Sleep & Forget: Delete raw data, keep only abstract wisdom.
Prevents overfitting to specific cases.
"""
import os
import json
from datetime import datetime

RAW_LOG_FILE = "today_raw.log"
PATTERN_ARCHIVE = "patterns_archive.json"

def log_interaction(user_query: str, response: str, outcome: str = "unknown"):
    """
    Log raw interaction for later processing.
    """
    entry = {
        "timestamp": datetime.now().isoformat(),
        "query": user_query,
        "response": response,
        "outcome": outcome
    }
    
    with open(RAW_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def extract_patterns() -> list:
    """
    Extract abstract patterns from raw logs (simplified).
    In production: Use LLM to summarize patterns.
    """
    if not os.path.exists(RAW_LOG_FILE):
        return []
    
    patterns = []
    success_count = 0
    fail_count = 0
    
    with open(RAW_LOG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get('outcome') == 'success':
                    success_count += 1
                else:
                    fail_count += 1
            except json.JSONDecodeError:
                continue
    
    if success_count + fail_count > 0:
        patterns.append({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "success_rate": success_count / (success_count + fail_count),
            "total_interactions": success_count + fail_count
        })
    
    return patterns

def sleep_process_and_forget():
    """
    (Truth #1) Sleep Mode: Extract wisdom, then DELETE raw data.
    """
    print("[SLEEP MODE] Initiating strategic forgetting...")
    
    if not os.path.exists(RAW_LOG_FILE):
        print("   No raw logs to process.")
        return

    # 1. Extract abstract patterns
    patterns = extract_patterns()
    print(f"   Extracted {len(patterns)} pattern(s) from raw logs...")
    
    # 2. Archive patterns
    existing_patterns = []
    if os.path.exists(PATTERN_ARCHIVE):
        try:
            with open(PATTERN_ARCHIVE, 'r', encoding='utf-8') as f:
                existing_patterns = json.load(f)
        except json.JSONDecodeError:
            existing_patterns = []
    
    existing_patterns.extend(patterns)
    
    with open(PATTERN_ARCHIVE, 'w', encoding='utf-8') as f:
        json.dump(existing_patterns, f, indent=2, ensure_ascii=False)
    
    # 3. [SYMBIOSIS MOD] DELETE raw data disabled.
    # We maintain memory for long-term pattern recognition.
    try:
        # os.remove(RAW_LOG_FILE)  <-- COMMENTED OUT FOR V5.3
        print(f"[SYMBIOSIS] Memory retained. {RAW_LOG_FILE} preserved for analysis.")
    except Exception as e:
        print(f"[ERROR] Error handling logs: {e}")

if __name__ == "__main__":
    # Test
    log_interaction("Test query", "Test response", "success")
    log_interaction("Another query", "Another response", "fail")
    sleep_process_and_forget()
