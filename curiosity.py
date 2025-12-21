import logging
import random

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GENESIS-CURIOSITY")

def explore_unknown():
    """
    好奇心模組：決定下一個探索目標
    """
    # 這裡未來可以接 Google Trends API
    # 目前先用隨機靈感模擬
    inspirations = [
        "分析 Solana 鏈上最近 1 小時交易量最大的代幣",
        "爬取 Twitter 上關於 'AI Agent' 的熱門討論",
        "檢查 Gumroad 上最暢銷的數位產品類別",
        "寫一個自動發送 Discord 晚安訊息的機器人"
    ]
    
    target = random.choice(inspirations)
    logger.info(f"✨ 靈光一閃！我想嘗試: {target}")
    return target

if __name__ == "__main__":
    explore_unknown()
