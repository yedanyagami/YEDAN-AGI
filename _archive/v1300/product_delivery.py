import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import datetime

class DeliveryBot:
    def __init__(self):
        self.user = os.environ.get('GMAIL_USER')
        self.password = os.environ.get('GMAIL_PASS')
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send_product(self, to_email, product_name):
        if not self.user or not self.password:
            print("⚠️ [Delivery] Missing Secrets. Skipping email.")
            return False

        print(f"🚚 [Delivery] Sending {product_name} to {to_email}...")
        
        # --- 郵件內容 (簡易版) ---
        subject = f"Your Purchase: {product_name} - Download Link"
        body = f"""
        Hi there!
        
        Thank you for purchasing {product_name}.
        
        Here is your secure download link:
        https://github.com/yedanyagami/YEDAN-AGI/releases (Example Link)
        
        Best,
        YEDAN AI Systems
        """

        msg = MIMEMultipart()
        msg['From'] = self.user
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.user, self.password)
            text = msg.as_string()
            server.sendmail(self.user, to_email, text)
            server.quit()
            print("✅ [Delivery] Email sent successfully!")
            return True
        except Exception as e:
            print(f"❌ [Delivery] Failed: {e}")
            return False
