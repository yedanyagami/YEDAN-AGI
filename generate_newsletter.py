"""
YEDAN AGI - AI Newsletter Generator
Automated newsletter content generation for vertical niches
Target: Real Estate Professionals
"""
import sys
import io
import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

load_dotenv(dotenv_path=".env.reactor")

from modules.content_miner import OpenContentMiner
from modules.writer_agent import WriterAgent


class NewsletterGenerator:
    """Generates niche-specific AI newsletters"""
    
    def __init__(self, niche: str = "Real Estate"):
        self.niche = niche
        self.miner = OpenContentMiner()
        self.writer = WriterAgent()
        self.output_dir = "newsletters"
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
    
    def mine_relevant_content(self, topic: str = None) -> list:
        """Mine AI research relevant to the niche"""
        queries = {
            "Real Estate": [
                "AI property valuation machine learning",
                "Large language models real estate",
                "Computer vision property analysis",
                "AI mortgage underwriting automation"
            ],
            "E-commerce": [
                "AI product recommendation systems",
                "Machine learning inventory optimization",
                "AI customer behavior prediction"
            ]
        }
        
        niche_queries = queries.get(self.niche, queries["Real Estate"])
        query = topic or niche_queries[datetime.now().day % len(niche_queries)]
        
        print(f"[Newsletter] Mining content for: {query}")
        papers = self.miner.harvest_arxiv(query=query, max_results=3)
        
        if not papers:
            print("[Newsletter] Falling back to Wikipedia...")
            papers = self.miner.harvest_wikipedia(query=f"Artificial intelligence {self.niche.lower()}")
        
        return papers
    
    def generate_newsletter_issue(self, issue_number: int, topic: str = None) -> dict:
        """Generate a complete newsletter issue"""
        
        # Mine content
        papers = self.mine_relevant_content(topic)
        
        if not papers:
            return {"error": "No content found"}
        
        # Prepare context
        research_summary = "\n\n".join([
            f"**{p.get('title', 'Research')}**\n{p.get('raw_text', '')[:500]}..."
            for p in papers[:3]
        ])
        
        # Generate newsletter content
        prompt = f"""You are writing a newsletter for {self.niche} professionals about AI.

Today's research to cover:
{research_summary}

Write a newsletter issue with:

1. **HEADLINE** - Catchy, benefit-focused (e.g., "3 AI Tools That Could Save You 10 Hours This Week")

2. **HOOK** (2-3 sentences) - Why this matters to {self.niche} professionals RIGHT NOW

3. **THE INSIGHT** (Main content, 200-300 words)
   - Explain the AI development in simple terms
   - Give ONE specific, actionable way to apply this
   - Include a real-world example or use case

4. **QUICK WINS** (Bullet points)
   - 3 tools or tactics readers can try TODAY
   - Be specific with tool names or techniques

5. **THE BOTTOM LINE** (1-2 sentences)
   - Key takeaway they should remember

Format: Use markdown. Keep it scannable. Sound like a helpful expert, not a professor.
Total length: 400-500 words.

DO NOT include any sign-off, subscription links, or promotional content."""

        print(f"[Newsletter] Generating Issue #{issue_number}...")
        
        response = self.writer.brain.generate_response(prompt, platform="newsletter")
        
        if isinstance(response, dict):
            content = response.get("content", str(response))
        else:
            content = str(response)
        
        # Create issue object
        issue = {
            "issue_number": issue_number,
            "niche": self.niche,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "topic": topic or "AI Trends",
            "content": content,
            "sources": [p.get("title", "Research") for p in papers[:3]],
            "generated_at": datetime.now().isoformat()
        }
        
        # Save to file
        filename = f"{self.output_dir}/issue_{issue_number:03d}_{datetime.now().strftime('%Y%m%d')}.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# AI Insider for {self.niche} - Issue #{issue_number}\n\n")
            f.write(f"*{datetime.now().strftime('%B %d, %Y')}*\n\n")
            f.write("---\n\n")
            f.write(content)
            f.write("\n\n---\n\n")
            f.write("*This newsletter is powered by YEDAN AI.*\n")
        
        print(f"[Newsletter] Saved to {filename}")
        
        return issue
    
    def generate_batch(self, count: int = 5) -> list:
        """Generate multiple newsletter issues"""
        
        topics = [
            "AI property valuation and appraisal automation",
            "Virtual staging and AI-powered home visualization",
            "AI chatbots for real estate lead qualification",
            "Predictive analytics for property market trends",
            "AI-powered contract analysis and document automation"
        ]
        
        issues = []
        for i in range(count):
            topic = topics[i % len(topics)]
            issue = self.generate_newsletter_issue(i + 1, topic)
            issues.append(issue)
            print(f"[Newsletter] Completed {i + 1}/{count}")
        
        return issues
    
    def generate_welcome_email(self) -> str:
        """Generate welcome email for new subscribers"""
        
        prompt = f"""Write a welcome email for new subscribers to "AI Insider for {self.niche}".

The email should:
1. Thank them for subscribing (1 sentence)
2. Explain what they'll get (AI insights for {self.niche} professionals, delivered weekly)
3. Set expectations (every Tuesday, actionable insights, no fluff)
4. Give them ONE quick win they can try TODAY
5. Ask them to reply with their biggest AI question

Tone: Friendly, professional, helpful. Like a knowledgeable colleague.
Length: 150-200 words.
Format: Plain text (for email)."""

        response = self.writer.brain.generate_response(prompt, platform="email")
        
        if isinstance(response, dict):
            return response.get("content", str(response))
        return str(response)


def main():
    """Generate first batch of newsletters"""
    print("=" * 60)
    print("YEDAN Newsletter Generator - Real Estate Edition")
    print("=" * 60)
    
    generator = NewsletterGenerator(niche="Real Estate")
    
    # Generate 5 issues
    print("\n[Phase 1] Generating 5 newsletter issues...")
    issues = generator.generate_batch(count=5)
    
    # Generate welcome email
    print("\n[Phase 2] Generating welcome email...")
    welcome = generator.generate_welcome_email()
    
    with open("newsletters/welcome_email.txt", "w", encoding="utf-8") as f:
        f.write(welcome)
    
    print("\n" + "=" * 60)
    print("GENERATION COMPLETE")
    print("=" * 60)
    print(f"Issues generated: {len(issues)}")
    print(f"Output directory: newsletters/")
    print("\nFiles created:")
    for f in os.listdir("newsletters"):
        print(f"  - {f}")
    
    return issues


if __name__ == "__main__":
    main()
