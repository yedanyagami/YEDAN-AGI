import os
import logging
from imap_tools import MailBox, AND

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("YEDAN-WALLET")

def check_funds():
    username = os.getenv("GMAIL_USERNAME")
    password = os.getenv("GMAIL_PASSWORD")

    if not username or not password:
        logger.error("❌ 錢包錯誤: 找不到 Gmail 帳密。請檢查 GitHub Secrets。")
        return

    try:
        logger.info(f"正在嘗試登入 Gmail: {username} ...")
        with MailBox('imap.gmail.com').login(username, password) as mailbox:
            logger.info("✅ 登入成功！視覺神經已連接。")
            
            # 搜尋未讀信件作為測試
            unread_count = 0
            for msg in mailbox.fetch(limit=3, reverse=True):
                logger.info(f"📩 掃描信件: {msg.subject} | From: {msg.from_}")
                unread_count += 1
            
            logger.info(f"💰 掃描完成。目前系統運作正常。")

    except Exception as e:
        logger.error(f"❌ 登入失敗 (失明): {e}")

if __name__ == "__main__":
    check_funds()
