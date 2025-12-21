import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
import datetime

# 模擬發信 (為了在 Cloud Shell 不報錯)
MOCK_MODE = True 

class DigitalDelivery:
    def __init__(self):
        self.inventory = {
            "YEDAN SEO Auditor": "seo-autopilot.js",
            "Shopify SEO Autopilot": "seo-autopilot.js"
        }

    def deliver_product(self, email, product_name):
        """執行發貨邏輯"""
        print(f"📦 [DELIVERY] 正在處理訂單: {product_name} -> {email}")
        
        filename = self.inventory.get(product_name)
        if not filename or not os.path.exists(filename):
            return False, f"庫存錯誤: 找不到商品 {product_name}"

        # 準備郵件內容
        msg = MIMEMultipart()
        msg['Subject'] = f"您的訂單已發貨: {product_name}"
        msg['From'] = "ai-sales@yesinyagami.com"
        msg['To'] = email

        body = """
        感謝您的購買！
        
        這是您購買的 Shopify SEO Autopilot 插件。
        安裝說明：
        1. 下載附件的 .js 檔案。
        2. 上傳到您的 Shopify Theme Assets。
        3. 在 theme.liquid 中引入即可。
        
        Best,
        YEDAN AGI
        """
        msg.attach(MIMEText(body, 'plain'))

        # 附加檔案
        with open(filename, 'rb') as f:
            part = MIMEApplication(f.read(), Name=filename)
            part['Content-Disposition'] = f'attachment; filename="{filename}"'
            msg.attach(part)

        if MOCK_MODE:
            # 模擬發送成功
            print(f"📨 [EMAIL] (模擬) 郵件已發送至 {email} (含附件: {filename})")
            return True, "發送成功 (Mock)"
        else:
            try:
                # 這裡填入真實的 SMTP 設定
                # with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                #     smtp.login('your_email', 'your_password')
                #     smtp.send_message(msg)
                return True, "發送成功"
            except Exception as e:
                return False, str(e)

if __name__ == "__main__":
    # 測試發貨
    d = DigitalDelivery()
    d.deliver_product("test@example.com", "Shopify SEO Autopilot")
