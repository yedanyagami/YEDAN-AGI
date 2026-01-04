"""
YEDAN Iterative Optimization Cycle
Practical approach: Run → Measure → Optimize → Repeat
"""
import os
import time
from datetime import datetime
from dashboard import ROIDashboard
from modules.content_miner import OpenContentMiner
from modules.writer_agent import WriterAgent
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env.reactor")

class IterativeOptimizer:
    def __init__(self):
        self.dashboard = ROIDashboard()
        self.miner = OpenContentMiner()
        self.writer = WriterAgent()
        self.cycle_count = 0
        self.history = []
        
    def run_cycle(self):
        """Single optimization cycle: Measure -> Identify -> Act -> Record"""
        self.cycle_count += 1
        print(f"\n{'='*60}")
        print(f"OPTIMIZATION CYCLE #{self.cycle_count}")
        print(f"{'='*60}")
        
        # 1. MEASURE: Get current state
        print("\n[Step 1] MEASURE - Checking system state...")
        metrics = self.dashboard.check_all_systems()
        
        # 2. IDENTIFY: Find bottleneck
        print("\n[Step 2] IDENTIFY - Finding optimization target...")
        target = self._find_bottleneck(metrics)
        print(f"   Target: {target['dimension']} - {target['action']}")
        
        # 3. ACT: Execute improvement
        print("\n[Step 3] ACT - Executing improvement...")
        result = self._execute_action(target)
        print(f"   Result: {result}")
        
        # 4. RECORD: Log for iteration
        self.history.append({
            "cycle": self.cycle_count,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "target": target,
            "result": result
        })
        
        # 5. VISUALIZE: Show progress
        print("\n[Step 4] VISUALIZE - Rendering progress...")
        self._render_progress()
        
        return result
    
    def _find_bottleneck(self, metrics):
        """Identify the most impactful optimization target."""
        # Priority order: Revenue > Factory > Traffic > Mining
        
        if metrics["revenue"]["total_value"] < 100:
            return {"dimension": "revenue", "action": "add_product", "reason": "Total value under $100"}
        
        if metrics["factory"]["products_created"] < 5:
            return {"dimension": "factory", "action": "create_product", "reason": "Need more products"}
        
        if metrics["traffic"]["status"] != "OK":
            return {"dimension": "traffic", "action": "fix_browser", "reason": "Traffic engine offline"}
        
        if metrics["mining"]["latency_ms"] > 5000:
            return {"dimension": "mining", "action": "optimize_mining", "reason": "High latency"}
        
        return {"dimension": "none", "action": "maintain", "reason": "All systems optimal"}
    
    def _execute_action(self, target):
        """Execute the identified optimization action."""
        action = target["action"]
        
        if action == "create_product" or action == "add_product":
            return self._create_new_product()
        elif action == "fix_browser":
            return "Manual intervention required for Camoufox"
        elif action == "optimize_mining":
            return "Mining latency is network-dependent, consider caching"
        else:
            return "System maintained - no action needed"
    
    def _create_new_product(self):
        """Create a new digital product to boost revenue."""
        print("   -> Mining fresh content...")
        papers = self.miner.harvest_arxiv("machine learning applications", max_results=3)
        
        if not papers:
            return "FAILED: No content mined"
        
        print(f"   -> Mined {len(papers)} papers")
        
        # Generate product data
        today = datetime.now().strftime("%Y-%m-%d")
        title = f"AI Research Digest: {today}"
        
        # Simple description from papers
        content = "<h2>Today's AI Research Highlights</h2><ul>"
        for p in papers[:3]:
            content += f"<li><b>{p['title'][:60]}...</b><br>{p['summary'][:150]}...</li>"
        content += "</ul>"
        
        # Upload to Shopify
        store_url = os.getenv("SHOPIFY_STORE_URL", "")
        if store_url.startswith("https://"): store_url = store_url.replace("https://", "")
        access_token = os.getenv("SHOPIFY_ACCESS_TOKEN") or os.getenv("SHOPIFY_ADMIN_TOKEN")
        
        if not store_url or not access_token:
            return "FAILED: No Shopify credentials"
        
        product_data = {
            "product": {
                "title": title,
                "body_html": content,
                "vendor": "YEDAN Research",
                "product_type": "Digital Report",
                "variants": [{"price": "2.99", "requires_shipping": False}],
                "status": "active"
            }
        }
        
        try:
            headers = {"X-Shopify-Access-Token": access_token, "Content-Type": "application/json"}
            r = requests.post(f"https://{store_url}/admin/api/2024-01/products.json", 
                            json=product_data, headers=headers, timeout=15)
            if r.status_code == 201:
                return f"SUCCESS: Created '{title}' at $2.99"
            else:
                return f"FAILED: Shopify returned {r.status_code}"
        except Exception as e:
            return f"FAILED: {e}"
    
    def _render_progress(self):
        """Render optimization progress visualization."""
        print("\n" + "-"*60)
        print("OPTIMIZATION HISTORY:")
        print("-"*60)
        
        for h in self.history[-5:]:  # Last 5 cycles
            status = "OK" if "SUCCESS" in str(h["result"]) else "!!"
            print(f"  Cycle {h['cycle']:2d} | {h['target']['dimension']:10s} | [{status}] {h['result'][:40]}")
        
        print("-"*60)
        print(f"Total Cycles: {len(self.history)} | Success Rate: {sum(1 for h in self.history if 'SUCCESS' in str(h['result']))/max(1,len(self.history))*100:.0f}%")

def main():
    optimizer = IterativeOptimizer()
    
    # Run a single optimization cycle
    print("Starting Iterative Optimization...")
    result = optimizer.run_cycle()
    
    print("\n" + "="*60)
    print("CYCLE COMPLETE")
    print("="*60)
    print(f"Result: {result}")
    print("\nRun again to continue optimization cycle.")

if __name__ == "__main__":
    main()
