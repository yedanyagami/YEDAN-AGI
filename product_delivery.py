import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
import datetime

# 🚨 實戰模式：開關已解除
# 如果環境變數裡有密碼，就嘗試發信；否則回退到模擬模式以防崩潰
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_PASS = os.environ.get("GMAIL_PASS")
MOCK_MODE = False if (GMAIL_USER and GMAIL_PASS) else True

class DigitalDelivery:
    def __init__(self):
        self.inventory = {
            "YEDAN SEO Auditor": "seo-autopilot.js",
            "Shopify SEO Autopilot": "seo-autopilot.js"
        }
        self.user = GMAIL_USER
        self.password = GMAIL_PASS

    def deliver_product(self, email, product_name):
        print(f"📦 [DELIVERY] 正在處理訂單: {product_name} -> {email}")
        
        filename = self.inventory.get(product_name)
        if not filename or not os.path.exists(filename):
            return False, f"庫存錯誤: 找不到商品 {product_name}"

        # 準備真實郵件
        msg = MIMEMultipart()
        msg['Subject'] = f"【YEDAN发货】您的訂單: {product_name}"
        msg['From'] = self.user if self.user else "ai-sales@yesinyagami.com"
        msg['To'] = email

        body = """
        感謝您的購買！
        
        這是您購買的 Shopify SEO Autopilot 插件。
        
        [安裝說明]
        1. 下載附件的 .js 檔案。
        2. 上傳到您的 Shopify Theme Assets。
        3. 在 theme.liquid 中引入即可。
        
        Best,
        YEDAN AGI System
        """
        msg.attach(MIMEText(body, 'plain'))

        with open(filename, 'rb') as f:
            part = MIMEApplication(f.read(), Name=filename)
            part['Content-Disposition'] = f'attachment; filename="{filename}"'
            msg.attach(part)

        # 判斷是演習還是實戰
        if MOCK_MODE:
            print(f"⚠️ [WARN] 缺少 GMAIL 帳密，僅執行模擬發送。")
            return True, "發送成功 (Mock - No Credentials)"
        else:
            try:
                print(f"🚀 [LIVE] 正在連線 Gmail SMTP 伺服器...")
                # 使用 Gmail SSL 端口 465
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(self.user, self.password)
                    smtp.send_message(msg)
                print(f"✅ [SUCCESS] 真實郵件已發送至 {email}")
                return True, "發送成功 (LIVE)"
            except Exception as e:
                print(f"❌ [ERROR] 發送失敗: {str(e)}")
                return False, f"SMTP Error: {str(e)}"
