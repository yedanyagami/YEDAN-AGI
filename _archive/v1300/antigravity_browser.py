import os
import time
import logging
import random
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [ANTIGRAVITY] - %(message)s')
logger = logging.getLogger()

def stealth_browse(target_url):
    logger.info(f'🛸 啟動全自動瀏覽器，目標: {target_url}')
    with sync_playwright() as p:
        # 啟動隱形 Chrome
        browser = p.chromium.launch(headless=True)
        # 偽裝成最新款 MacBook Pro
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='en-US'
        )
        page = context.new_page()
        try:
            logger.info('👀 正在像真人一樣瀏覽...')
            page.goto(target_url, timeout=60000)
            time.sleep(random.uniform(3, 7)) 
            # 模擬人類滑鼠滾動
            page.mouse.wheel(0, 700)
            time.sleep(2)
            title = page.title()
            logger.info(f'✅ 成功獲取情報: {title}')
            logger.info('💾 數據已自動存檔，無需人工干預。')
        except Exception as e:
            logger.error(f'❌ 瀏覽失敗: {e}')
        finally:
            browser.close()

if __name__ == '__main__':
    stealth_browse('https://www.coingecko.com/')
