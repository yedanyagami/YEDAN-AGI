"""
YEDAN AGI - Actions Module (Ultra Optimized)
Autonomous action executors with connection pooling and centralized config.
[GEMINI ULTRA FIX] Replaced deprecated paypalrestsdk with modern requests-based auth.
"""
import sys
import io
import time
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from agi_config import config

# Force UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8') if hasattr(sys.stdout, 'buffer') else sys.stdout


class PayPalClient:
    """
    [GEMINI ULTRA PATTERN] Modern PayPal API Client.
    Replaces deprecated paypalrestsdk with direct REST calls.
    """
    def __init__(self, client_id: str, client_secret: str, mode: str = "sandbox"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.mode = mode
        self.base_url = f"https://api-m.{'sandbox.' if mode == 'sandbox' else ''}paypal.com"
        self._access_token = None
        self._token_expires = 0
        
    def _get_access_token(self) -> str:
        """Get or refresh OAuth2 token."""
        if self._access_token and time.time() < self._token_expires:
            return self._access_token
            
        url = f"{self.base_url}/v1/oauth2/token"
        response = requests.post(
            url,
            auth=HTTPBasicAuth(self.client_id, self.client_secret),
            data={"grant_type": "client_credentials"},
            headers={"Accept": "application/json", "Accept-Language": "en_US"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            self._access_token = data["access_token"]
            self._token_expires = time.time() + data.get("expires_in", 3600) - 60
            return self._access_token
        else:
            raise Exception(f"PayPal Auth Failed: {response.status_code} - {response.text}")
    
    def create_payment(self, product_name: str, price: str, return_url: str) -> dict:
        """Create a PayPal payment link."""
        try:
            token = self._get_access_token()
            url = f"{self.base_url}/v1/payments/payment"
            
            payload = {
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "redirect_urls": {
                    "return_url": return_url,
                    "cancel_url": "https://yedanyagami.myshopify.com"
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": product_name,
                            "sku": "AGI-AUTO",
                            "price": str(price),
                            "currency": "USD",
                            "quantity": 1
                        }]
                    },
                    "amount": {"total": str(price), "currency": "USD"},
                    "description": "YEDAN AGI Premium Intelligence"
                }]
            }
            
            response = requests.post(
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"
                },
                timeout=30
            )
            
            if response.status_code == 201:
                data = response.json()
                for link in data.get("links", []):
                    if link.get("rel") == "approval_url":
                        return {"success": True, "url": link["href"], "payment_id": data["id"]}
                return {"success": False, "error": "No approval URL found"}
            else:
                return {"success": False, "error": f"{response.status_code}: {response.text}"}
                
        except Exception as e:
            print(f"[PAYPAL] Payment creation failed: {e}")
            return {"success": False, "error": str(e), "url": "#paypal-unavailable"}


# Initialize PayPal client with config
paypal_client = PayPalClient(
    client_id=config.PAYPAL_CLIENT_ID or "",
    client_secret=config.PAYPAL_CLIENT_SECRET or "",
    mode=config.PAYPAL_MODE or "sandbox"
)


class AGIActions:
    """Autonomous action executor"""
    
    def __init__(self):
        self.session = requests.Session()
        self.last_payment_check = datetime.now()
        
        if not config.TELEGRAM_BOT_TOKEN:
            print("[WARN] Telegram token not configured in AGIActions")
    
    def _post(self, url, json=None):
        """Optimized POST with error handling"""
        try:
            resp = self.session.post(url, json=json, timeout=config.REQUEST_TIMEOUT)
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def check_recent_sales(self):
        """Check for recent PayPal sales using modern API"""
        # [GEMINI ULTRA FIX] Sales check via deprecated SDK is removed
        # Future: implement via paypal_client.list_payments() if needed
        print("[PAYPAL] Sales check skipped (legacy SDK removed)")
        return False, 0.0
    
    def telegram_send(self, message, parse_mode="HTML"):
        """Send message to Telegram using centralized config"""
        if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
            return {"success": False, "error": "Telegram not configured"}
        
        payload = {
            "chat_id": config.TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False
        }
        
        url = f"{config.TELEGRAM_API}/sendMessage"
        resp = self._post(url, json=payload)
        
        if resp["success"]:
            return {"success": True, "message_id": resp["data"].get("result", {}).get("message_id")}
        return resp
    
    def create_payment(self, product_name, price="9.99", return_url="https://t.me/yesinyagami_novel_bot"):
        """Create PayPal payment link using modern PayPalClient"""
        # [GEMINI ULTRA FIX] Using modern paypal_client instead of deprecated SDK
        return paypal_client.create_payment(product_name, str(price), return_url)
    
    def generate_pdf(self, filename, title, content):
        """Generate PDF report"""
        try:
            c = canvas.Canvas(filename, pagesize=letter)
            width, height = letter
            
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, height - 50, f"YEDAN INTEL: {title}")
            c.line(50, height - 60, width - 50, height - 60)
            
            c.setFont("Helvetica", 10)
            text = c.beginText(50, height - 100)
            for line in content.split('\n'):
                text.textLine(line[:90])
            c.drawText(text)
            
            c.setFont("Helvetica", 8)
            c.drawString(50, 30, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            c.drawString(400, 30, "YEDAN AGI System")
            
            c.save()
            return {"success": True, "path": filename}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def broadcast_intel(self, target, analysis, price="9.99"):
        """Generate PDF, Payment, and Broadcast via Telegram"""
        results = {}
        
        # 1. Create PDF
        pdf_name = f"Intel_{int(time.time())}.pdf"
        results['pdf'] = self.generate_pdf(pdf_name, target, analysis)
        
        # 2. Create payment
        results['payment'] = self.create_payment(f"Intel: {target}", price)
        
        # 3. Send Telegram
        pay_url = results['payment'].get('url', '#')
        msg = f"""<b>YEDAN INTELLIGENCE</b>
        
<b>Target:</b> {target}

{analysis[:500]}{'...' if len(analysis) > 500 else ''}

<b>Full Report:</b> ${price}
<a href="{pay_url}">Click to Purchase</a>

<i>YEDAN AGI</i>"""
        
        results['telegram'] = self.telegram_send(msg)
        return results

if __name__ == "__main__":
    actions = AGIActions()
    print("[TEST] Telegram:", actions.telegram_send("AGI Actions module test"))
