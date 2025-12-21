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
        # 連接 Gmail IMAP
        with MailBox('imap.gmail.com').login(username, password) as mailbox:
            logger.info("✅ 登入成功！視覺神經已連接。")
            
            # 搜尋未讀的付款通知 (範例：來自 Gumroad 或 Ko-fi)
            # 這裡我們先搜尋所有未讀信件來測試
            unread_count = 0
            for msg in mailbox.fetch(AND(seen=False), limit=5):
                logger.info(f"📩 發現信件: {msg.subject} | From: {msg.from_}")
                unread_count += 1
            
            if unread_count == 0:
                logger.info("👀 信箱掃描完畢，暫無新訊號。系統待機中。")
            else:
                logger.info(f"💰 掃描到 {unread_count} 封新信件，準備分析...")

    except Exception as e:
        logger.error(f"❌ 登入失敗 (失明): {e}")

if __name__ == "__main__":
    check_funds()
