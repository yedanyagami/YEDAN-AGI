import datetime
import logic_core
from yedan_guardian import Guardian
from yedan_wallet import Wallet
from product_delivery import DigitalDelivery

def run_agi_system():
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # 初始化模組
    brain = Guardian()
    wallet = Wallet()
    logistics = DigitalDelivery()
    
    print(f"🤖 [AGI OMEGA] 系統啟動... {time_now}")

    # 1. 檢查系統安全
    allow, guard_msg = brain.check_error_history("SYSTEM_STARTUP")
    print(f"🧠 [BRAIN] {guard_msg}")

    # 2. 處理未完成訂單 (模擬邏輯：這裡我們假設每次啟動都檢查最新的一筆模擬訂單)
    # 在真實資料庫中，我們會加上 'fulfilled' 欄位來判斷
    print("🚚 [LOGISTICS] 正在掃描待出貨訂單...")
    
    # 模擬從錢包抓取一筆最新交易
    last_order = {
        "email": "customer_vip@gmail.com", 
        "product": "Shopify SEO Autopilot", 
        "price": 27.0
    }
    
    # 執行發貨
    success, delivery_msg = logistics.deliver_product(last_order['email'], last_order['product'])
    
    # 3. 獲取財務報表
    revenue, order_count = wallet.check_balance()

    # 4. 掃描市場
    market_data = logic_core.fetch_market_data()

    # 5. 生成最終戰報
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>YEDAN AGI: OMEGA COMPLETE</title>
        <meta charset="UTF-8">
        <style>
            body {{ background-color: #050505; color: #00ff00; font-family: monospace; padding: 20px; }}
            .box {{ border: 1px solid #333; padding: 15px; margin-bottom: 10px; background: #111; }}
            h1 {{ color: #fff; border-bottom: 1px solid #333; }}
            .stat {{ font-size: 1.5em; color: #fff; }}
            .success {{ color: #0f0; }}
        </style>
    </head>
    <body>
        <h1>👁️ YEDAN AGI: OMEGA (Live)</h1>
        <p>Sync Time: {time_now}</p>

        <div class="box">
            <h3>📦 自動履約 (Fulfillment)</h3>
            <p>最新訂單: {last_order['product']} (${last_order['price']})</p>
            <p>客戶: {last_order['email']}</p>
            <p>狀態: <span class="success">{delivery_msg}</span></p>
        </div>

        <div class="box">
            <h3>💰 財務狀況 (Wallet)</h3>
            <p>總營收: <span class="stat">${revenue}</span></p>
            <p>總訂單數: {order_count}</p>
        </div>

        <div class="box">
            <h3>📈 市場監控 (Eyes)</h3>
            <p>BTC: {market_data['BTC']} | SOL: {market_data['SOL']}</p>
        </div>
        
        <div class="box">
            <h3>🧠 元認知 (Guardian)</h3>
            <p>{guard_msg}</p>
        </div>
    </body>
    </html>
    """

    with open("index.html", "w", encoding='utf-8') as f:
        f.write(html_content)
    print("✅ 全知戰報生成完畢 (index.html)")

if __name__ == "__main__":
    run_agi_system()
