"""
Scout Agent (The Researcher)
Responsible for gathering intelligence with MINIMAL token usage.
Uses lightweight scraping (BeautifulSoup) instead of heavy LLM browsing where possible.
"""
import requests
import logging
import json
from bs4 import BeautifulSoup

logger = logging.getLogger('scout_agent')

class ScoutAgent:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def quick_scan_url(self, url: str) -> dict:
        """
        Scrapes a URL without using LLM tokens.
        Extracts title, headers, and meta description.
        """
        logger.info(f"🕵️ Scout scanning: {url}")
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                return {"error": f"Status {response.status_code}"}
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title = soup.title.string if soup.title else "No Title"
            
            # Extract Meta Description
            meta_desc = ""
            meta = soup.find('meta', attrs={'name': 'description'})
            if meta:
                meta_desc = meta.get('content', '')
                
            # Extract H1/H2 for structure
            headers = [h.get_text().strip() for h in soup.find_all(['h1', 'h2'])[:5]]
            
            return {
                "url": url,
                "title": title.strip(),
                "description": meta_desc.strip(),
                "top_headers": headers,
                "token_cost": 0 # $0.00 cost
            }
            
        except Exception as e:
            logger.error(f"Scout failed: {e}")
            return {"error": str(e)}

    def analyze_competitor_product(self, url: str) -> dict:
        """
        Analyzes a competitor's Shopify product page.
        Returns clear data for the Writer Agent to use.
        """
        scan = self.quick_scan_url(url)
        if "error" in scan:
            return scan
            
        # Basic heuristic analysis (No AI)
        quality_score = 0
        if len(scan['description']) > 100: quality_score += 2
        if len(scan['top_headers']) >= 3: quality_score += 2
        
        scan['quality_score'] = quality_score
        return scan
