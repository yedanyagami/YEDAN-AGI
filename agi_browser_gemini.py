"""
YEDAN AGI - Browser-Based Gemini Interface (Perpetual Engine)
Uses Playwright to interact with Gemini Web directly, bypassing API limits.
"""
from playwright.sync_api import sync_playwright
import time
import json
import re

class BrowserGemini:
    """Interfaces with Gemini via browser automation (FREE & UNLIMITED)"""
    
    def __init__(self, headless=True):
        self.headless = headless
        self.browser = None
        self.page = None
        self.gemini_url = "https://gemini.google.com"
        print("[BROWSER_GEMINI] Perpetual Engine: Ready")
    
    def _ensure_browser(self):
        """Ensures browser is running, starts if not"""
        if self.browser is None:
            print("[BROWSER_GEMINI] Starting Browser...")
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            print("[BROWSER_GEMINI] Browser Started")
    
    def prompt(self, text, wait_time=30):
        """
        Send a prompt to Gemini Web and retrieve the response.
        This is the core "free Ultra" interaction.
        """
        self._ensure_browser()
        
        try:
            # Navigate if not already on Gemini
            if "gemini.google.com" not in self.page.url:
                print(f"[BROWSER_GEMINI] Navigating to {self.gemini_url}...")
                self.page.goto(self.gemini_url, timeout=60000)
                self.page.wait_for_load_state("networkidle")
                time.sleep(3)  # Wait for dynamic content
            
            # Find and click input area
            # Using a robust selector for the Gemini textarea
            input_selector = "div.ql-editor, textarea, [contenteditable='true']"
            self.page.click(input_selector, timeout=10000)
            
            # Type the prompt
            print(f"[BROWSER_GEMINI] Sending prompt ({len(text)} chars)...")
            self.page.keyboard.type(text, delay=5)  # Slight delay for stability
            
            # Submit (Enter or click send button)
            # Try send button first
            try:
                send_button = self.page.locator("button[aria-label*='Send'], button.send-button, button[data-test-id='send-button']").first
                if send_button.is_visible():
                    send_button.click()
                else:
                    self.page.keyboard.press("Enter")
            except:
                self.page.keyboard.press("Enter")
            
            # Wait for response
            print(f"[BROWSER_GEMINI] Waiting {wait_time}s for response...")
            time.sleep(wait_time)
            
            # Extract response text
            # Gemini response is typically in a specific container
            response_selector = "message-content, .response-container, .model-response"
            try:
                response_elements = self.page.locator(response_selector).all_text_contents()
                if response_elements:
                    response = "\n".join(response_elements)
                else:
                    # Fallback: get all visible text from main content area
                    response = self.page.locator("main").inner_text()
            except:
                response = self.page.content()  # Last resort: raw HTML
            
            print(f"[BROWSER_GEMINI] Response received ({len(response)} chars)")
            return response
            
        except Exception as e:
            print(f"[BROWSER_GEMINI] Error: {e}")
            return None
    
    def generate_content_matrix(self, target, context=None):
        """
        High-value factory method: Generates multi-channel content.
        """
        prompt = f"""
        Act as YEDAN PRIME Content Factory.
        Target Asset: {target}
        Context: {context or 'Crypto Market Analysis'}
        
        Generate a complete Content Matrix as a JSON object with these exact keys:
        - telegram: Short, punchy sales pitch (max 200 chars)
        - twitter_thread: Array of 5 tweet strings
        - email_subject: Newsletter subject line
        - email_body: 2-paragraph newsletter body
        
        Output ONLY the JSON, no markdown, no explanation.
        """
        
        raw_response = self.prompt(prompt)
        
        # Try to parse JSON from response
        if raw_response:
            # Find JSON in response
            json_match = re.search(r'\{[\s\S]*\}', raw_response)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
        
        return {"telegram": raw_response[:500] if raw_response else "Generation failed"}
    
    def close(self):
        """Clean up browser resources"""
        if self.browser:
            self.browser.close()
            self.playwright.stop()
            print("[BROWSER_GEMINI] Browser Closed")

if __name__ == "__main__":
    # Test
    gemini = BrowserGemini(headless=False)  # Visible for testing
    result = gemini.generate_content_matrix("Midnight (NIGHT)", "Privacy narrative is trending")
    print(json.dumps(result, indent=2))
    gemini.close()
