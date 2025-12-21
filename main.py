import datetime
import os
import logic_core
from yedan_guardian import Guardian
from yedan_wallet import Wallet
from product_delivery import DigitalDelivery

def run_agi_system():
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # 1. 初始化 (全部連接 Redis)
    try:
        brain = Guardian()
        wallet = Wallet()
        logistics = DigitalDelivery()
        print(f"🤖 [AGI OMEGA] 雲端喚醒... {time_now}")
    except Exception as e:
        print(f"❌ 初始化失敗 (檢查 Redis 連線): {e}")
        return

    # 2. 自我診斷
    allow, guard_msg = brain.check_error_history("SYSTEM_CRASH")
    if not allow:
        print(guard_msg)
        return # 停止執行以保護系統

    # 3. 執行金流掃描 (Active Polling)
    try:
        print("🔍 [WALLET] 正在掃描 Gmail...")
        new_orders = wallet.scan_for_payments()
        
        for order in new_orders:
            # 執行發貨
            success, msg = logistics.deliver_product(order['email'], order['product'])
            if success:
                print(f"✅ [FULFILL] 訂單 {order['id']} 發貨成功")
                wallet.mark_as_done(order['id'])
            else:
                print(f"❌ [FAIL] 發貨失敗: {msg}")
                brain.log_error("DELIVERY_FAIL")
    except Exception as e:
        print(f"⚠️ 金流掃描異常: {e}")
        brain.log_error("GMAIL_SCAN_FAIL")

    # 4. 獲取狀態 (從 Redis)
    revenue, count = wallet.get_balance()
    market_data = logic_core.fetch_market_data()

    # 5. 生成戰報 (這是唯一需要 Git Push 的東西)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>YEDAN AGI: REDIS CORE</title>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="900">
        <style>
            body {{ background-color: #000; color: #0f0; font-family: monospace; padding: 20px; }}
            .card {{ border: 1px solid #333; padding: 15px; margin: 10px 0; background: #111; }}
            h1 {{ border-bottom: 2px solid #0f0; }}
            .money {{ color: gold; font-size: 1.5em; }}
        </style>
    </head>
    <body>
        <h1>👁️ YEDAN AGI (Serverless)</h1>
        <p>Sync: {time_now}</p>
        
        <div class="card">
            <h3>💰 財務中樞 (Redis)</h3>
            <p>總營收: <span class="money">${revenue}</span></p>
            <p>處理訂單: {count}</p>
        </div>

        <div class="card">
            <h3>📈 市場視角</h3>
            <p>BTC: {market_data.get('BTC')} | SOL: {market_data.get('SOL')}</p>
        </div>

        <div class="card">
            <h3>🧠 系統狀態</h3>
            <p>{guard_msg}</p>
        </div>
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding='utf-8') as f:
        f.write(html_content)
    print("✅ 戰報更新完畢")

if __name__ == "__main__":
    run_agi_system()
