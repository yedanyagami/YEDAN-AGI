"""
YEDAN AGI - Cloud Social Agent
Uses Browserless.io for headless browser automation in the cloud
Enables 24/7 social media interaction without local computer
"""
import sys
import io
import os
import json
import requests
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Fix Windows console encoding
# Encoding fix moved to __main__ or handled by caller

load_dotenv(dotenv_path=".env.reactor")

BROWSERLESS_TOKEN = os.getenv("BROWSERLESS_TOKEN")
BROWSERLESS_URL = f"https://chrome.browserless.io"


class CloudSocialAgent:
    """Cloud-based social media automation using Browserless"""
    
    def __init__(self):
        self.token = BROWSERLESS_TOKEN
        self.reddit_user = os.getenv("REDDIT_USERNAME")
        self.reddit_pass = os.getenv("REDDIT_PASSWORD")
        self.twitter_user = os.getenv("TWITTER_USERNAME")
        self.twitter_pass = os.getenv("TWITTER_PASSWORD")
        
    def _run_script(self, script: str) -> dict:
        """Execute Puppeteer script on Browserless"""
        if not self.token:
            return {"success": False, "error": "No Browserless token"}
        
        try:
            r = requests.post(
                f"{BROWSERLESS_URL}/function?token={self.token}",
                headers={"Content-Type": "application/javascript"},
                data=script,
                timeout=60
            )
            if r.status_code == 200:
                return {"success": True, "result": r.json()}
            else:
                return {"success": False, "error": r.text}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_browserless_status(self) -> dict:
        """Check if Browserless is available"""
        if not self.token:
            return {"available": False, "error": "No token configured"}
        
        try:
            r = requests.get(
                f"{BROWSERLESS_URL}/pressure?token={self.token}",
                timeout=10
            )
            if r.status_code == 200:
                data = r.json()
                return {
                    "available": True,
                    "cpu": data.get("cpu"),
                    "memory": data.get("memory"),
                    "queued": data.get("queued", 0)
                }
        except Exception as e:
            return {"available": False, "error": str(e)}
        return {"available": False}
    
    def reddit_comment(self, post_url: str, comment: str) -> dict:
        """Post a comment on Reddit using cloud browser"""
        script = f'''
module.exports = async ({{ page }}) => {{
    await page.goto('https://www.reddit.com/login', {{ waitUntil: 'networkidle0' }});
    
    // Login
    await page.type('#loginUsername', '{self.reddit_user}');
    await page.type('#loginPassword', '{self.reddit_pass}');
    await page.click('button[type="submit"]');
    await page.waitForNavigation({{ waitUntil: 'networkidle0' }});
    
    // Navigate to post
    await page.goto('{post_url}', {{ waitUntil: 'networkidle0' }});
    
    // Find comment box and post
    const commentBox = await page.$('div[data-test-id="comment-submission-form-richtext"] div[contenteditable="true"]');
    if (commentBox) {{
        await commentBox.click();
        await page.keyboard.type(`{comment}`);
        
        const submitBtn = await page.$('button[type="submit"]');
        if (submitBtn) {{
            await submitBtn.click();
            await page.waitForTimeout(3000);
            return {{ success: true, message: 'Comment posted' }};
        }}
    }}
    
    return {{ success: false, message: 'Could not find comment box' }};
}};
'''
        return self._run_script(script)
    
    def reddit_search_and_engage(self, subreddit: str, keyword: str, response_template: str) -> dict:
        """Search Reddit for keyword and auto-engage"""
        script = f'''
module.exports = async ({{ page }}) => {{
    const results = [];
    
    // Search subreddit
    await page.goto('https://www.reddit.com/r/{subreddit}/search/?q={keyword}&restrict_sr=1&sort=new', 
        {{ waitUntil: 'networkidle0' }});
    
    // Get post titles and links
    const posts = await page.$$eval('a[data-click-id="body"]', links => 
        links.slice(0, 5).map(link => ({{
            title: link.textContent,
            url: link.href
        }}))
    );
    
    return {{ success: true, posts: posts }};
}};
'''
        return self._run_script(script)
    
    def take_screenshot(self, url: str, filename: str) -> dict:
        """Take screenshot of a URL"""
        try:
            r = requests.post(
                f"{BROWSERLESS_URL}/screenshot?token={self.token}",
                headers={"Content-Type": "application/json"},
                json={
                    "url": url,
                    "options": {
                        "fullPage": True,
                        "type": "png"
                    }
                },
                timeout=30
            )
            if r.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(r.content)
                return {"success": True, "file": filename}
        except Exception as e:
            return {"success": False, "error": str(e)}
        return {"success": False}
    
    def scrape_page(self, url: str, selector: str) -> dict:
        """Scrape content from a page"""
        try:
            r = requests.post(
                f"{BROWSERLESS_URL}/scrape?token={self.token}",
                headers={"Content-Type": "application/json"},
                json={
                    "url": url,
                    "elements": [{"selector": selector}]
                },
                timeout=30
            )
            if r.status_code == 200:
                return {"success": True, "data": r.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
        return {"success": False}


class CloudSocialOrchestrator:
    """Orchestrates cloud social media actions"""
    
    def __init__(self):
        self.agent = CloudSocialAgent()
        self.synapse_url = "https://synapse.yagami8095.workers.dev"
        
    def fetch_pending_tasks(self) -> list:
        """Get pending social tasks from Synapse"""
        try:
            r = requests.get(f"{self.synapse_url}/task/pending", timeout=10)
            if r.status_code == 200:
                tasks = r.json().get("tasks", [])
                return [t for t in tasks if t.get("type") == "social_post"]
        except:
            pass
        return []
    
    def complete_task(self, task_id: str, result: dict):
        """Mark task as complete"""
        try:
            requests.post(
                f"{self.synapse_url}/task/complete",
                json={"task_id": task_id, "result": result},
                timeout=10
            )
        except:
            pass
    
    def run_cycle(self):
        """Process pending social tasks"""
        print("=" * 60)
        print("[CloudSocial] Starting cloud social cycle")
        print("=" * 60)
        
        # Check Browserless status
        status = self.agent.check_browserless_status()
        print(f"[CloudSocial] Browserless: {status}")
        
        if not status.get("available"):
            print("[CloudSocial] Browserless not available, skipping")
            return
        
        # Fetch and process tasks
        tasks = self.fetch_pending_tasks()
        print(f"[CloudSocial] Found {len(tasks)} pending social tasks")
        
        for task in tasks:
            task_id = task.get("task_id")
            data = task.get("data", {})
            platform = data.get("platform", "reddit")
            content = data.get("content", "")
            
            print(f"[CloudSocial] Processing task {task_id} for {platform}")
            
            # Execute based on platform
            if platform == "reddit":
                # For now, just log - real implementation would post
                result = {"status": "simulated", "platform": platform}
            else:
                result = {"status": "unsupported_platform"}
            
            self.complete_task(task_id, result)
        
        print("[CloudSocial] Cycle complete")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        agent = CloudSocialAgent()
        status = agent.check_browserless_status()
        print(f"Browserless Status: {json.dumps(status, indent=2)}")
    elif len(sys.argv) > 1 and sys.argv[1] == "--screenshot":
        agent = CloudSocialAgent()
        url = sys.argv[2] if len(sys.argv) > 2 else "https://google.com"
        result = agent.take_screenshot(url, "screenshot.png")
        print(f"Screenshot: {result}")
    else:
        orchestrator = CloudSocialOrchestrator()
        orchestrator.run_cycle()
