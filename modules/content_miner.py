"""
Open Content Miner (The Infinite Source)
Harvests content from TRULY OPEN sources (ArXiv, Wikipedia, GitHub) 
that do not require anti-bot evasion.
"""
import requests
import xml.etree.ElementTree as ET
import logging
from urllib.parse import quote

logger = logging.getLogger('content_miner')

class OpenContentMiner:
    def __init__(self):
        self.sources = {
            "arxiv": "http://export.arxiv.org/api/query",
            "wikipedia": "https://en.wikipedia.org/w/api.php",
            "hackernews": "https://hacker-news.firebaseio.com/v0",
            "github": "https://api.github.com"
        }

    def harvest_arxiv(self, query="artificial intelligence", max_results=5):
        """
        Harvests research papers from ArXiv (Zero Anti-Bot, Open API).
        Perfect for 'Deep Dive' or 'Future Tech' ebooks.
        """
        logger.info(f"⛏️ Mining ArXiv for: {query}")
        
        url = (
            f"{self.sources['arxiv']}?search_query=all:{quote(query)}"
            f"&start=0&max_results={max_results}"
        )
        
        try:
            response = requests.get(url, timeout=20)
            if response.status_code != 200:
                logger.error(f"ArXiv Error: {response.status_code}")
                return []
                
            root = ET.fromstring(response.content)
            # Namespace for Atom
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            papers = []
            for entry in root.findall('atom:entry', ns):
                title = entry.find('atom:title', ns).text.strip().replace('\n', ' ')
                summary = entry.find('atom:summary', ns).text.strip().replace('\n', ' ')
                published = entry.find('atom:published', ns).text
                link = entry.find('atom:id', ns).text
                
                papers.append({
                    "source": "arxiv",
                    "title": title,
                    "summary": summary,
                    "published": published,
                    "url": link,
                    "raw_text": f"{title}\n\n{summary}"
                })
                
            logger.info(f"✅ Harvested {len(papers)} papers.")
            return papers
            
        except Exception as e:
            logger.error(f"Mining Failed: {e}")
            return []

    def harvest_wikipedia(self, query="Generative artificial intelligence"):
        """
        Harvests summaries from Wikipedia (Open API).
        Good for foundational content.
        """
        logger.info(f"⛏️ Mining Wikipedia for: {query}")
        
        params = {
            "action": "query",
            "format": "json",
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "titles": query
        }
        
        try:
            response = requests.get(self.sources["wikipedia"], params=params, timeout=10)
            data = response.json()
            
            pages = data['query']['pages']
            results = []
            
            for page_id, page_data in pages.items():
                if page_id == "-1": continue
                
                results.append({
                    "source": "wikipedia",
                    "title": page_data['title'],
                    "summary": page_data['extract'],
                    "url": f"https://en.wikipedia.org/wiki/{quote(page_data['title'])}",
                    "raw_text": f"{page_data['title']}\n\n{page_data['extract']}"
                })
                
            return results
        except Exception as e:
            logger.error(f"Wiki Mining Failed: {e}")
            return []

    def harvest_hackernews(self, max_results=10):
        """
        Harvests top stories from HackerNews (Open Firebase API, Zero Anti-Bot).
        Great for trending tech content.
        """
        logger.info("Mining HackerNews top stories...")
        
        try:
            # Get top story IDs
            r = requests.get(f"{self.sources['hackernews']}/topstories.json", timeout=10)
            if r.status_code != 200:
                return []
            
            story_ids = r.json()[:max_results]
            stories = []
            
            for sid in story_ids:
                story_r = requests.get(f"{self.sources['hackernews']}/item/{sid}.json", timeout=5)
                if story_r.status_code == 200:
                    story = story_r.json()
                    if story and story.get('title'):
                        stories.append({
                            "source": "hackernews",
                            "title": story.get('title', ''),
                            "url": story.get('url', f"https://news.ycombinator.com/item?id={sid}"),
                            "score": story.get('score', 0),
                            "raw_text": f"{story.get('title', '')} (Score: {story.get('score', 0)})"
                        })
            
            logger.info(f"Harvested {len(stories)} HN stories.")
            return stories
            
        except Exception as e:
            logger.error(f"HN Mining Failed: {e}")
            return []

    def harvest_github_trending(self, language="python"):
        """
        Harvests trending GitHub repos via search API (Rate limited but open).
        """
        logger.info(f"Mining GitHub trending for: {language}")
        
        try:
            headers = {"Accept": "application/vnd.github.v3+json"}
            params = {
                "q": f"language:{language}",
                "sort": "stars",
                "order": "desc",
                "per_page": 10
            }
            r = requests.get(f"{self.sources['github']}/search/repositories", 
                           headers=headers, params=params, timeout=10)
            
            if r.status_code != 200:
                logger.error(f"GitHub API error: {r.status_code}")
                return []
            
            repos = []
            for item in r.json().get('items', []):
                repos.append({
                    "source": "github",
                    "title": item.get('full_name', ''),
                    "description": item.get('description', ''),
                    "url": item.get('html_url', ''),
                    "stars": item.get('stargazers_count', 0),
                    "raw_text": f"{item.get('full_name', '')}: {item.get('description', '')}"
                })
            
            logger.info(f"Harvested {len(repos)} GitHub repos.")
            return repos
            
        except Exception as e:
            logger.error(f"GitHub Mining Failed: {e}")
            return []

if __name__ == "__main__":
    # Test Run
    miner = OpenContentMiner()
    
    print("\n=== ArXiv ===")
    papers = miner.harvest_arxiv("Language Models", max_results=2)
    for p in papers:
        print(f"[Paper] {p['title'][:50]}...")
    
    print("\n=== HackerNews ===")
    stories = miner.harvest_hackernews(max_results=3)
    for s in stories:
        print(f"[HN] {s['title'][:50]}... (Score: {s.get('score', 0)})")
    
    print("\n=== GitHub Trending ===")
    repos = miner.harvest_github_trending("python")
    for r in repos[:3]:
        print(f"[GH] {r['title']} ({r.get('stars', 0)} stars)")
