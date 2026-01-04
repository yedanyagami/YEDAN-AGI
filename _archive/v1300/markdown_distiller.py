
"""
YEDAN AGI: THE EYES (MARKDOWN DISTILLER)
Converts raw, messy HTML/Text into clean, high-density Markdown for the Brain.
Architecture: Raw Data -> Distiller -> Brain Input
"""
import re

def distill_to_markdown(raw_content, source_type="generic"):
    """
    Clean raw content into specific markdown structures for Agentic/DeepSeek consumption.
    """
    if not raw_content:
        return ""

    distilled = raw_content

    # 1. Remove Excessive Whitespace
    distilled = re.sub(r'\n\s*\n', '\n\n', distilled)
    
    # 2. Source-Specific Cleaning
    if source_type == "reddit":
        distilled = _clean_reddit(distilled)
    elif source_type == "twitter":
        distilled = _clean_twitter(distilled)
    
    # 3. Token Optimization (Simple Truncation/Summary simulation)
    # In a real scenario, this might use a lightweight summarizer model
    
    header = f"--- DISTILLED INTEL (Source: {source_type.upper()}) ---\n"
    return header + distilled.strip()

def _clean_reddit(text):
    """Specific filters for Reddit threads"""
    # Example: Remove upvote counts if they appear as raw numbers alone
    # This is a mock implementation of the logic
    return text

def _clean_twitter(text):
    """Specific filters for Tweets"""
    # Example: Remove 'View conversation' type links
    return text

if __name__ == "__main__":
    # Test The Eyes
    raw_sample = """
    User123 [Score hidden] 5 hours ago
    
    
    My Shopify sync is broken again!
    
    reply  share
    """
    print(distill_to_markdown(raw_sample, "reddit"))
