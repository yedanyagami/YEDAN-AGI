#!/usr/bin/env python3
"""
YEDAN AGI - Memory Consolidator (Deep Sleep Module)
Implements memory consolidation like human sleep.

Truth #1: Forget the noise, remember the wisdom.

Process:
1. READ short-term memory (sales_history.csv)
2. EXTRACT business wisdom via LLM
3. WRITE to long-term memory (knowledge_base.md)
4. ARCHIVE raw data (optional)
"""

import os
import sys
import io
import pandas as pd
from datetime import datetime
from typing import Optional

# Fix Windows console encoding
if sys.platform == 'win32' and __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sales_history.csv")
KNOWLEDGE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "knowledge_base.md")
ARCHIVE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "archive")

# Minimum transactions required before consolidation
MIN_TRANSACTIONS_FOR_CONSOLIDATION = 10


def call_llm_api(prompt: str, system_prompt: str) -> str:
    """Call LLM for wisdom extraction."""
    try:
        import google.generativeai as genai
        from agi_config import config
        
        genai.configure(api_key=config.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-001')
        
        full_prompt = f"{system_prompt}\n\n{prompt}"
        response = model.generate_content(full_prompt)
        return response.text
        
    except Exception as e:
        print(f"⚠️ LLM API Error: {e}")
        return "- Unable to extract insights at this time."


class MemoryConsolidator:
    """
    The Deep Sleep Module.
    
    Like human sleep consolidates memories, this module:
    - Extracts patterns from raw transaction data
    - Summarizes into actionable business rules
    - Stores wisdom for future decision-making
    - Optionally archives old data
    """
    
    def __init__(self):
        # Ensure directories exist
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(KNOWLEDGE_PATH), exist_ok=True)
    
    def consolidate(self, force: bool = False) -> bool:
        """
        Execute memory consolidation cycle.
        
        Args:
            force: If True, consolidate even with few transactions
            
        Returns:
            True if consolidation occurred
        """
        print("\n" + "=" * 60)
        print("🧠 [MEMORY CONSOLIDATOR] Starting Deep Sleep Cycle")
        print(f"   Time: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # ═══════════════════════════════════════════════════════════
        # 1. READ SHORT-TERM MEMORY
        # ═══════════════════════════════════════════════════════════
        if not os.path.exists(DATA_PATH):
            print("\n   ⚠️ No short-term memory found (sales_history.csv missing)")
            return False
        
        try:
            df = pd.read_csv(DATA_PATH)
        except Exception as e:
            print(f"\n   ❌ Error reading CSV: {e}")
            return False
        
        transaction_count = len(df)
        print(f"\n📊 [Memory Scan] Found {transaction_count} transactions")
        
        # Check minimum threshold
        if transaction_count < MIN_TRANSACTIONS_FOR_CONSOLIDATION and not force:
            print(f"   ⏳ Not enough experiences ({transaction_count}/{MIN_TRANSACTIONS_FOR_CONSOLIDATION}) to generalize yet.")
            return False
        
        # ═══════════════════════════════════════════════════════════
        # 2. PREPARE DATA SUMMARY (Token-efficient)
        # ═══════════════════════════════════════════════════════════
        print("\n📈 [Preparing Summary]")
        
        # Financial metrics
        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)
            total_revenue = float(df['amount'].sum())
            avg_order = total_revenue / transaction_count if transaction_count > 0 else 0
            max_order = float(df['amount'].max())
            min_order = float(df['amount'].min())
        else:
            total_revenue = avg_order = max_order = min_order = 0
        
        # Platform breakdown
        if 'platform' in df.columns:
            platform_stats = df['platform'].value_counts().to_dict()
            top_platform = df['platform'].mode()[0] if not df['platform'].empty else "Unknown"
        else:
            platform_stats = {}
            top_platform = "Unknown"
        
        # Time analysis
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            # Day of week analysis
            df['day_of_week'] = df['timestamp'].dt.day_name()
            day_stats = df['day_of_week'].value_counts().to_dict()
            best_day = df['day_of_week'].mode()[0] if not df['day_of_week'].isna().all() else "Unknown"
        else:
            day_stats = {}
            best_day = "Unknown"
        
        # Sample recent transactions
        sample_data = df.tail(10).to_string() if len(df) > 0 else "No data"
        
        print(f"   💰 Total Revenue: ${total_revenue:.2f}")
        print(f"   📦 Avg Order: ${avg_order:.2f}")
        print(f"   🏆 Top Platform: {top_platform}")
        print(f"   📅 Best Day: {best_day}")
        
        # ═══════════════════════════════════════════════════════════
        # 3. DREAM - LLM Wisdom Extraction
        # ═══════════════════════════════════════════════════════════
        print("\n💭 [Dreaming] Extracting business wisdom...")
        
        extraction_prompt = f"""
[Role]: You are the Chief Strategy Officer consolidating business intelligence.

[Data Period Stats]:
- Total Transactions: {transaction_count}
- Total Revenue: ${total_revenue:.2f}
- Average Order Value: ${avg_order:.2f}
- Max Order: ${max_order:.2f}
- Min Order: ${min_order:.2f}

[Platform Performance]:
{platform_stats}

[Day of Week Distribution]:
{day_stats}

[Best Performing]:
- Platform: {top_platform}
- Day: {best_day}

[Recent Transactions Sample]:
{sample_data}

[Task]:
Analyze this data and extract 2-4 "Immutable Business Laws" that will guide future decisions.
Focus on:
1. What patterns indicate success?
2. What conditions lead to higher order values?
3. What should be avoided?

[Output Format]:
Return insights as Markdown bullets. Be specific and actionable.
Example:
- **Insight**: High-ticket items ($50+) perform 3x better on Gumroad than Shopify.
- **Rule**: Prioritize Friday-Sunday for promotional campaigns.
- **Warning**: Orders under $10 often indicate price-sensitive customers with low LTV.
"""
        
        system_prompt = """You are an expert Business Intelligence Analyst.
Extract only insights that are ACTIONABLE and SUPPORTED by the data.
Do not hallucinate patterns that don't exist.
If data is insufficient, say so."""
        
        insights = call_llm_api(extraction_prompt, system_prompt)
        
        # ═══════════════════════════════════════════════════════════
        # 4. WRITE TO LONG-TERM MEMORY
        # ═══════════════════════════════════════════════════════════
        print("\n💾 [Storing Wisdom] Writing to knowledge_base.md...")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"""

---

### 📅 Consolidated on {timestamp}
**Data Period**: {transaction_count} transactions, ${total_revenue:.2f} total revenue

{insights}

"""
        
        # Initialize knowledge base if doesn't exist
        if not os.path.exists(KNOWLEDGE_PATH):
            with open(KNOWLEDGE_PATH, "w", encoding="utf-8") as f:
                f.write("# YEDAN AGI - Knowledge Base\n\n")
                f.write("> Long-term business wisdom extracted from experience.\n")
                f.write("> This file is read by the Decision Engine before every decision.\n")
        
        # Append new entry
        with open(KNOWLEDGE_PATH, "a", encoding="utf-8") as f:
            f.write(entry)
        
        print(f"   ✅ Wisdom stored successfully")
        print(f"\n📝 [Extracted Insights]:")
        print("-" * 40)
        print(insights[:500] + "..." if len(insights) > 500 else insights)
        print("-" * 40)
        
        # ═══════════════════════════════════════════════════════════
        # 5. ARCHIVE RAW DATA (Optional - commented for safety)
        # ═══════════════════════════════════════════════════════════
        # Uncomment these lines when ready to enable automatic archiving
        
        # archive_filename = f"sales_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        # archive_path = os.path.join(ARCHIVE_DIR, archive_filename)
        # df.to_csv(archive_path, index=False)
        # 
        # # Clear main CSV (keep only header)
        # df.iloc[0:0].to_csv(DATA_PATH, index=False)
        # print(f"\n🗑️ [Archiving] Raw data moved to {archive_filename}")
        
        print("\n🏁 [DEEP SLEEP COMPLETE] Memory consolidation finished.")
        return True
    
    def get_knowledge_summary(self, max_chars: int = 2000) -> str:
        """
        Read long-term memory for injection into decision engine.
        
        Args:
            max_chars: Maximum characters to return (token control)
            
        Returns:
            Recent wisdom from knowledge base
        """
        if not os.path.exists(KNOWLEDGE_PATH):
            return "No prior wisdom available. This is a fresh start."
        
        try:
            with open(KNOWLEDGE_PATH, "r", encoding="utf-8") as f:
                content = f.read()
                
            if len(content) <= max_chars:
                return content
            
            # Return most recent entries (end of file)
            return "...[truncated older entries]...\n\n" + content[-max_chars:]
            
        except Exception as e:
            return f"Error reading long-term memory: {e}"


# ═══════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    consolidator = MemoryConsolidator()
    
    if "--force" in sys.argv:
        # Force consolidation even with few transactions
        print("⚠️ Forcing consolidation...")
        consolidator.consolidate(force=True)
        
    elif "--read" in sys.argv:
        # Read current knowledge base
        print("=" * 60)
        print("YEDAN AGI - Knowledge Base Contents")
        print("=" * 60)
        print(consolidator.get_knowledge_summary(max_chars=5000))
        
    else:
        # Normal consolidation
        consolidator.consolidate()
