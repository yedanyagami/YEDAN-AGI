"""
YEDAN AGI - Cloud Social Agent
Uses Browserless.io for headless browser automation in the cloud
Enables 24/7 social media interaction without local computer
"""
import sys
import json
import requests
from datetime import datetime
from typing import Optional
from modules.config import Config, setup_logging

logger = setup_logging('cloud_social')

class CloudSocialAgent:
    """Cloud-based social media automation using Browserless"""
    
    def __init__(self):
        self.token = Config.BROWSERLESS_TOKEN
        self.reddit_user = Config.REDDIT_USERNAME
        self.reddit_pass = Config.REDDIT_PASSWORD
        self.twitter_user = Config.TWITTER_USERNAME
        self.twitter_pass = Config.TWITTER_PASSWORD
        
    def _run_script(self, script: str) -> dict:
        """Execute Puppeteer script on Browserless"""
        if not self.token:
            return {"success": False, "error": "No Browserless token"}
        
        try:
            r = requests.post(
                f"{Config.BROWSERLESS_URL}/function?token={self.token}",
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
            r = requests.post(
                f"{Config.BROWSERLESS_URL}/screenshot?token={self.token}",
                headers={"Content-Type": "application/json"},
                json={"url": "about:blank", "options": {"type": "png"}},
                timeout=15
            )
            if r.status_code == 200:
                return {"available": True, "status": "online"}
            else:
                return {"available": False, "error": f"API returned {r.status_code}"}
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def reddit_comment(self, post_url: str, comment: str) -> dict:
        """Post a comment on Reddit using cloud browser"""
        logger.info(f"Posting comment to {post_url}...")
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
    
    def reddit_search_and_engage(self, subreddit: str, keyword: str) -> dict:
        """Search Reddit for keyword and return posts"""
        script = f'''
module.exports = async ({{ page }}) => {{
    const results = [];
    await page.goto('https://www.reddit.com/r/{subreddit}/search/?q={keyword}&restrict_sr=1&sort=new', 
        {{ waitUntil: 'networkidle0' }});
    
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
                f"{Config.BROWSERLESS_URL}/screenshot?token={self.token}",
                headers={"Content-Type": "application/json"},
                json={
                    "url": url,
                    "options": {"fullPage": True, "type": "png"}
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


class CloudSocialOrchestrator:
    """Orchestrates cloud social media actions"""
    
    def __init__(self):
        self.agent = CloudSocialAgent()
        self.synapse_url = Config.SYNAPSE_URL
        
    def fetch_pending_tasks(self) -> list:
        """Get pending social tasks from Synapse"""
        try:
            r = requests.get(f"{self.synapse_url}/task/pending", timeout=10)
            if r.status_code == 200:
                tasks = r.json().get("tasks", [])
                return [t for t in tasks if t.get("type") == "social_post"]
        except Exception as e:
            logger.error(f"Error fetching tasks: {e}")
        return []
    
    def complete_task(self, task_id: str, result: dict):
        """Mark task as complete"""
        try:
            requests.post(
                f"{self.synapse_url}/task/complete",
                json={"task_id": task_id, "result": result},
                timeout=10
            )
        except Exception as e:
            logger.error(f"Error completing task: {e}")
    
    def run_cycle(self):
        """Process pending social tasks"""
        logger.info("Starting CloudSocial cycle")
        
        status = self.agent.check_browserless_status()
        if not status.get("available"):
            logger.warning("Browserless unavailable")
            return
        
        tasks = self.fetch_pending_tasks()
        logger.info(f"Found {len(tasks)} pending tasks")
        
        for task in tasks:
            task_id = task.get("task_id")
            data = task.get("data", {})
            platform = data.get("platform", "reddit")
            content = data.get("content", "")
            post_url = data.get("post_url", "") # If commenting
            
            logger.info(f"Processing task {task_id} for {platform}")
            
            if platform == "reddit":
                if Config.SAFETY_MODE:
                    logger.info(f"[SAFETY MODE] Would post: {content[:50]}...")
                    result = {"status": "safety_mode_blocked", "content": content}
                else:
                    if post_url:
                        result = self.agent.reddit_comment(post_url, content)
                    else:
                        # If no post_url, we need logic to find where to post
                        # For now, we assume it's a comment task
                        result = {"status": "failed", "error": "No post_url provided"}
            else:
                result = {"status": "unsupported_platform"}
            
            self.complete_task(task_id, result)
        
        logger.info("CloudSocial cycle complete")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--status":
        agent = CloudSocialAgent()
        print(f"Status: {json.dumps(agent.check_browserless_status(), indent=2)}")
    else:
        orchestrator = CloudSocialOrchestrator()
        orchestrator.run_cycle()
