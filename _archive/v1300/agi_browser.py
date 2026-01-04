import os
import asyncio
import logging
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from typing import Optional, List, Dict

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AGIBrowser")

class AGIBrowser:
    """
    'The Eye': Handles Lateral Brainstorming via Web.
    Uses Playwright with Persistent Context to maintain 'Memory' (Cookies/Login).
    """
    def __init__(self, user_data_dir: str = None):
        if user_data_dir is None:
            # Default to a safe subdirectory in .gemini to avoid polluting workspace
            base_dir = os.path.join(os.path.expanduser("~"), ".gemini", "browser_context")
            self.user_data_dir = base_dir
        else:
            self.user_data_dir = user_data_dir
        
        if not os.path.exists(self.user_data_dir):
            os.makedirs(self.user_data_dir)
            
        self.playwright = None
        self.browser_context = None
        self.page = None

    async def start(self, headless: bool = True):
        """Launches the persistent browser context."""
        logger.info(f"Launching AGIBrowser (Headless: {headless})...")
        self.playwright = await async_playwright().start()
        
        # Use launch_persistent_context to keep cookies/login states
        self.browser_context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.user_data_dir,
            headless=headless,
            viewport={"width": 1280, "height": 720},
            args=["--disable-blink-features=AutomationControlled"] # Basic anti-detect
        )
        
        pages = self.browser_context.pages
        self.page = pages[0] if pages else await self.browser_context.new_page()
        logger.info("Browser launched successfully.")

    async def stop(self):
        """Closes the browser."""
        if self.browser_context:
            await self.browser_context.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser stopped.")

    async def lateral_brainstorm(self, query: str, domain: str = "google", timeout: int = 30000) -> str:
        """
        Conducts a 'Lateral Brainstorming' session.
        Navigates to the domain, inputs the query, and extracts high-level reasoning.
        """
        if not self.page:
            await self.start()

        try:
            logger.info(f"Brainstorming on {domain}: {query[:50]}...")
            
            if "gemini" in domain.lower():
                await self._navigate_to_gemini()
                response = await self._interact_with_gemini(query, timeout)
            else:
                await self._navigate_to_google(query)
                response = await self._extract_google_results()

            return response

        except Exception as e:
            logger.error(f"Brainstorming failed: {e}")
            return f"Error during brainstorming: {str(e)}"

    async def _navigate_to_gemini(self):
        """Navigates to Google Gemini."""
        await self.page.goto("https://gemini.google.com/app")
        # Wait for input area (robust selector)
        try:
            await self.page.wait_for_selector(".ql-editor", timeout=10000)
        except PlaywrightTimeout:
            logger.warning("Gemini Input not found. Might need login.")
            # We assume user is logged in via persistent context. 
            # If not, this is a limitation we notify.

    async def _interact_with_gemini(self, prompt: str, timeout: int) -> str:
        """Inputs prompt into Gemini and waits for response."""
        # 1. Clear and Type Prompt
        await self.page.click(".ql-editor")
        await self.page.keyboard.type(prompt)
        await self.page.keyboard.press("Enter")
        
        # 2. Wait for Response
        # Heuristic: Wait for the 'Stop' button to disappear or 'Copy' icon to appear
        # This is tricky. Simplified approach: Wait fixed time + Polling
        logger.info("Waiting for Gemini response...")
        await self.page.wait_for_timeout(5000) # Initial wait
        
        # Wait for the last message to stabilize (no 'typing' indicator)
        # For now, simplistic wait. In production, check DOM mutation.
        await self.page.wait_for_timeout(10000) 
        
        # 3. Extract Text
        # Select all message content divs
        elements = await self.page.query_selector_all(".message-content")
        if elements:
            last_response = await elements[-1].inner_text()
            return last_response
        return "No response extracted."

    async def _navigate_to_google(self, query: str):
        """Performs a Google Search."""
        await self.page.goto("https://www.google.com")
        await self.page.fill("textarea[name='q']", query)
        await self.page.keyboard.press("Enter")
        await self.page.wait_for_load_state("networkidle")

    async def _extract_google_results(self) -> str:
        """Extracts search results."""
        raw_text = await self.page.inner_text("#search")
        return self._sanitize_for_llm(raw_text)
    
    def _sanitize_for_llm(self, text: str) -> str:
        """
        [SECURITY] DOM Sanitization to prevent Indirect Prompt Injection.
        Strips instructional language that could hijack the LLM's executive function.
        Pattern recommended by Gemini Ultra.
        """
        import re
        
        # Remove common injection patterns
        injection_patterns = [
            r"ignore\s+(all\s+)?previous\s+instructions?",
            r"disregard\s+(all\s+)?previous",
            r"forget\s+everything",
            r"you\s+are\s+now\s+a",
            r"new\s+instructions?:",
            r"system\s*:\s*",
            r"assistant\s*:\s*",
            r"\[INST\]",
            r"\[/INST\]",
            r"<\|im_start\|>",
            r"<\|im_end\|>",
        ]
        
        sanitized = text
        for pattern in injection_patterns:
            sanitized = re.sub(pattern, "[SANITIZED]", sanitized, flags=re.IGNORECASE)
        
        return sanitized

    async def generate_gemini_key(self) -> str:
        """
        [SELF-HEALING] Automates the creation of a new Gemini API Key via AI Studio.
        Pre-requisite: Browser context must be logged in to Google.
        This method is designed to be robust and allow for manual intervention if needed.
        """
        if not self.page:
            await self.start(headless=False) # Force visible for complex actions/auth checks
        
        key = ""
        try:
            logger.info("[SELF-HEAL] Navigating to Google AI Studio...")
            await self.page.goto("https://aistudio.google.com/app/apikey", wait_until="networkidle")
            
            # Allow time for potential login redirect or page load
            await self.page.wait_for_timeout(3000)
            
            # Check if we are on the key page or a login page
            current_url = self.page.url
            if "accounts.google.com" in current_url:
                logger.warning("[SELF-HEAL] Login Required! Please log in manually in the browser window. Waiting 60s...")
                await self.page.wait_for_timeout(60000) # Wait for manual login
                await self.page.goto("https://aistudio.google.com/app/apikey", wait_until="networkidle")
                await self.page.wait_for_timeout(3000)

            # 1. Click "Create API key" button
            logger.info("[SELF-HEAL] Looking for 'Create API key' button...")
            try:
                # Wait for the button to appear
                create_btn = self.page.get_by_role("button", name="Create API key")
                await create_btn.first.wait_for(state="visible", timeout=10000)
                await create_btn.first.click()
                logger.info("[SELF-HEAL] Clicked 'Create API key'.")
            except Exception as e:
                logger.error(f"[SELF-HEAL] Could not find 'Create API key' button: {e}")
                return "" # Give up if main button not found

            # 2. Handle potential project selection modal
            await self.page.wait_for_timeout(2000) # Wait for modal to appear
            try:
                new_proj_btn = self.page.get_by_text("Create API key in new project")
                if await new_proj_btn.count() > 0:
                    await new_proj_btn.first.click()
                    logger.info("[SELF-HEAL] Selected 'Create API key in new project'.")
            except Exception:
                logger.info("[SELF-HEAL] 'New Project' option not found/clicked. Proceeding...")

            # 3. Wait for Key to be generated and displayed
            logger.info("[SELF-HEAL] Waiting for key to be generated (may take up to 30s)...")
            try:
                # The key is displayed in a modal with a copy button. Wait for it.
                await self.page.wait_for_selector("button[aria-label='Copy API key']", timeout=30000)
                logger.info("[SELF-HEAL] Key generation modal detected.")

                # 4. Extract Key from the modal
                # The key is inside a `mat-dialog-container` or similar. Find the text.
                modal = self.page.locator("mat-dialog-container")
                modal_text = await modal.inner_text(timeout=5000)
                
                import re
                match = re.search(r"AIza[0-9A-Za-z-_]{35}", modal_text)
                if match:
                    key = match.group(0)
                    logger.info(f"[SELF-HEAL] SUCCESS! Key Extracted: {key[:10]}...")
                else:
                    logger.warning("[SELF-HEAL] Key pattern not found in modal text.")
                    
            except Exception as e:
                logger.error(f"[SELF-HEAL] Key Generation/Extraction Failed: {e}")

        except Exception as e:
            logger.error(f"[SELF-HEAL] Critical failure in generate_gemini_key: {e}")
        finally:
            # Do NOT stop browser here - let the caller handle it
            pass
            
        return key

# Self-Test
if __name__ == "__main__":
    async def main():
        browser = AGIBrowser()
        try:
            await browser.start(headless=False)
            res = await browser.lateral_brainstorm("What is the Fractal Dimension of Bitcoin?", "gemini")
            print("RESULT:", res[:500])
        except Exception as e:
            print(f"Test Failed: {e}")
        finally:
            await browser.stop()

    asyncio.run(main())
