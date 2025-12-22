"""
YEDAN AGI - Actions Module
Autonomous action executors for Telegram, PayPal, PDF, etc.
"""
import os
import sys
import io
import time
import requests
import paypalrestsdk
from datetime import datetime
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Force UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8') if hasattr(sys.stdout, 'buffer') else sys.stdout

load_dotenv()

# PayPal config
paypalrestsdk.configure({
    "mode": os.getenv("PAYPAL_MODE", "live"),
    "client_id": os.getenv("PAYPAL_CLIENT_ID"),
    "client_secret": os.getenv("PAYPAL_CLIENT_SECRET")
})

class AGIActions:
    """Autonomous action executor"""
    
    def __init__(self):
        self.tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.tg_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    def telegram_send(self, message, parse_mode="HTML"):
        """Send message to Telegram"""
        if not self.tg_token or not self.tg_chat_id:
            return {"success": False, "error": "Telegram not configured"}
        
        url = f"https://api.telegram.org/bot{self.tg_token}/sendMessage"
        payload = {
            "chat_id": self.tg_chat_id,
            "text": message,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False
        }
        
        try:
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                return {"success": True, "message_id": resp.json().get("result", {}).get("message_id")}
            else:
                return {"success": False, "error": resp.text}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_payment(self, product_name, price="9.99", return_url="https://t.me/yesinyagami_novel_bot"):
        """Create PayPal payment link"""
        payment = paypalrestsdk.Payment({
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
        })

        if payment.create():
            for link in payment.links:
                if link.rel == "approval_url":
                    return {"success": True, "url": link.href, "payment_id": payment.id}
        return {"success": False, "error": str(payment.error)}
    
    def generate_pdf(self, filename, title, content):
        """Generate PDF report"""
        try:
            c = canvas.Canvas(filename, pagesize=letter)
            width, height = letter
            
            # Header
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, height - 50, f"YEDAN INTEL: {title}")
            c.line(50, height - 60, width - 50, height - 60)
            
            # Content
            c.setFont("Helvetica", 10)
            text = c.beginText(50, height - 100)
            for line in content.split('\n'):
                text.textLine(line[:90])
            c.drawText(text)
            
            # Footer
            c.setFont("Helvetica", 8)
            c.drawString(50, 30, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            c.drawString(400, 30, "YEDAN AGI System")
            
            c.save()
            return {"success": True, "path": filename}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def broadcast_intel(self, target, analysis, price="9.99"):
        """Full broadcast: Generate PDF + Payment + Telegram"""
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
    print("[TEST] Payment:", actions.create_payment("Test Product", "0.01"))
