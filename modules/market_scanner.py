"""
YEDAN AGI - Market Scanner (Competitor Intelligence)
Scrapes competitor sites to benchmark pricing and keywords.
"""
import requests
import re
from collections import Counter
from urllib.parse import urlparse
from modules.config import setup_logging

logger = setup_logging('market_scanner')

class MarketScanner:
    def __init__(self):
        # Top Dropshipping/SaaS competitors (Placeholders)
        self.competitors = [
            "https://inspireuplift.com",
            "https://www.odditymall.com",
            "https://soaestheticshop.com"
        ]
        
    def scan_competitors(self) -> dict:
        """Scan top competitors for pricing and keywords"""
        logger.info("Starting Competitor Scan...")
        report = {}
        
        for url in self.competitors:
            domain = urlparse(url).netloc
            try:
                r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                if r.status_code == 200:
                    html = r.text.lower()
                    
                    # 1. Extract Prices
                    # Regex to find $XX.XX patterns
                    prices = re.findall(r'\$\d+\.\d{2}', html)
                    prices = [float(p.replace('$','')) for p in prices]
                    avg_price = sum(prices)/len(prices) if prices else 0
                    
                    # 2. Extract Keywords (Meta Keywords or Title)
                    title_match = re.search(r'<title>(.*?)</title>', html)
                    title = title_match.group(1) if title_match else "Unknown"
                    
                    logger.info(f"Scanned {domain}: Avg Price ${avg_price:.2f}")
                    
                    report[domain] = {
                        "avg_price": avg_price,
                        "title_keywords": title,
                        "status": "active"
                    }
                else:
                    report[domain] = {"status": "unreachable"}
                    
            except Exception as e:
                logger.error(f"Failed to scan {domain}: {e}")
                report[domain] = {"status": "error", "error": str(e)}
                
        return report

    async def monitor_pricing(self):
        """Async wrapper for continous monitoring"""
        import asyncio
        logger.info("⚡ Rapid Response: Starting Async Price Monitor...")
        # Run the blocking scan in a thread
        report = await asyncio.to_thread(self.scan_competitors)
        
        # Here we would implement "Instant Price Match" logic
        # For now, we just log the findings
        for domain, data in report.items():
            if data.get("status") == "active":
                logger.info(f"   -> [Realtime] {domain}: ${data['avg_price']:.2f}")

if __name__ == "__main__":
    import asyncio
    scanner = MarketScanner()
    # Test Async
    asyncio.run(scanner.monitor_pricing())
    # Test Sync
    # results = scanner.scan_competitors()
    print("\n🕵️ COMPETITOR INTEL REPORT")
    print("="*40)
    for domain, data in results.items():
        if data.get("status") == "active":
            print(f"Domain: {domain}")
            print(f"   -> Avg Detectable Price: ${data['avg_price']:.2f}")
            print(f"   -> Site Title: {data['title_keywords'][:60]}...")
        else:
            print(f"Domain: {domain} (Offline/Blocked)")
    print("="*40)
