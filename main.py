import datetime
import logic_core
from yedan_guardian import Guardian
from yedan_wallet import Wallet

def run_agi_system():
    # 1. 初始化系統
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    brain = Guardian()
    wallet = Wallet()
    
    print(f"🤖 [AGI] 正在喚醒... 時間: {time_now}")

    # 2. 大腦檢查 (Guardian)
    # 模擬檢查一個錯誤代碼，確保大腦在運作
    allow_run, guard_msg = brain.check_error_history("SYSTEM_STARTUP")
    print(f"🧠 [BRAIN] {guard_msg}")
    
    # 3. 錢包檢查 (Wallet)
    revenue, order_count = wallet.check_balance()
    print(f"💰 [WALLET] 當前營收: ${revenue} (訂單: {order_count})")

    # 4. 視覺掃描 (Eyes)
    market_data = logic_core.fetch_market_data()

    # 5. 生成全知戰報 (HTML)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>YEDAN AGI: OMEGA</title>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="300">
        <style>
            body {{ background-color: #000; color: #0f0; font-family: 'Courier New', monospace; padding: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; }}
            .card {{ border: 1px solid #333; padding: 15px; margin-bottom: 15px; background: #0a0a0a; }}
            h1 {{ border-bottom: 2px solid #0f0; padding-bottom: 10px; }}
            h3 {{ margin-top: 0; color: #fff; }}
            .highlight {{ color: #0ff; font-weight: bold; }}
            .warn {{ color: #ff0; }}
            .money {{ color: #ffd700; font-size: 1.2em; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>👁️ YEDAN AGI: OMEGA</h1>
            <p>最後同步: {time_now}</p>

            <div class="card">
                <h3>💰 現金流 (Wallet)</h3>
                <p>總營收: <span class="money">${revenue}</span></p>
                <p>總訂單: {order_count} 筆</p>
                <small>來源: Gumroad, Ko-fi Webhooks</small>
            </div>

            <div class="card">
                <h3>🧠 元認知 (Guardian)</h3>
                <p>系統狀態: <span class="highlight">{guard_msg}</span></p>
                <p>學習模式: <span class="warn">Active (Error Prevention Protocol)</span></p>
            </div>

            <div class="card">
                <h3>📈 市場洞察 (Nexus Eyes)</h3>
                <p>Bitcoin: <span class="highlight">{market_data['BTC']}</span></p>
                <p>Solana: <span class="highlight">{market_data['SOL']}</span></p>
                <small>數據源: CoinGecko (via Proxy)</small>
            </div>
            
            <div class="card">
                <h3>⚙️ 系統架構</h3>
                <p>Core: Python 3.9 (Logic + SQLite)</p>
                <p>Deploy: GitHub Actions (Serverless)</p>
            </div>
        </div>
    </body>
    </html>
    """

    with open("index.html", "w", encoding='utf-8') as f:
        f.write(html_content)
    print("✅ 全知戰報生成完畢")

if __name__ == "__main__":
    run_agi_system()
