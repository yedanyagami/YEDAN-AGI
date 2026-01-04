"""
Digital Product Generator (The Asset Factory)
Uses WriterAgent (DeepSeek) to generate sellable digital content.
"""
from modules.writer_agent import WriterAgent
import json

def generate_digital_product():
    print("="*60)
    print("Digital Product Generator")
    print("="*60)
    
    agent = WriterAgent()
    
    topic = "How to Use AI to Dominate Dropshipping in 2026"
    print(f"Generating E-book Content: {topic}...")
    
    # 1. Generate Outline & Content
    prompt = f"""
    Write a comprehensive 3-chapter Mini-Course (E-book) about: {topic}
    
    Structure:
    - Title Page
    - Chapter 1: The Death of Old Dropshipping (Pain)
    - Chapter 2: The AI Advantage (Solution)
    - Chapter 3: 3 Steps to Start Today (Action)
    
    Format: Markdown.
    Tone: High-Ticket, Authoritative, "Wall Street" style.
    """
    
    content = agent.brain.generate_response(prompt, platform="ebook_gen")
    
    print("\n[Content Generated] Saving to 'AI_Dropshipping_Mastery.md'...")
    
    with open("AI_Dropshipping_Mastery.md", "w", encoding="utf-8") as f:
        f.write("# " + topic + "\n\n")
        f.write(content)
        
    # 2. Generate Shopify Product Details
    print("\nGenerating Shopify Product Listing...")
    seo_data = agent.generate_seo_content({
        "title": "The 2026 AI Dropshipping Blueprint (E-book)",
        "current_description": "Learn how to use AI to scale.",
        "keywords": ["ai dropshipping", "ecommerce guide", "passive income"]
    })
    
    print(f"[Title] {seo_data['optimized_title']}")
    print(f"[Score] {seo_data['seo_score']}")
    
    return seo_data

if __name__ == "__main__":
    generate_digital_product()
