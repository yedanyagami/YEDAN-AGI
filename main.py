import datetime
import logic_core  # 調用剛才移植的核心

def run_agi():
    # 1. 執行時間戳記
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # 2. 調用 V6 的遺產邏輯 (Market Eye)
    market_data = logic_core.fetch_market_data()
    
    # 3. 生成戰報 (HTML)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>YEDAN AGI v3.2</title>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="300">
        <style>
            body {{ background-color: #0d1117; color: #c9d1d9; font-family: monospace; padding: 20px; }}
            .card {{ border: 1px solid #30363d; padding: 15px; margin-bottom: 10px; border-radius: 6px; }}
            .highlight {{ color: #58a6ff; font-weight: bold; }}
            .header {{ border-bottom: 1px solid #30363d; padding-bottom: 10px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>👁️ YEDAN AGI 監控中心</h1>
            <small>最後同步: {time_now}</small>
        </div>

        <div class="card">
            <h3>💰 市場資產 (Core V6 Logic)</h3>
            <p>Bitcoin: <span class="highlight">{market_data['BTC']}</span></p>
            <p>Solana: <span class="highlight">{market_data['SOL']}</span></p>
            <small>Source: CoinGecko via Nexus Washer</small>
        </div>

        <div class="card">
            <h3>⚙️ 系統狀態</h3>
            <p>架構: GitHub Actions (Serverless)</p>
            <p>核心: Logic Core v3.2 (Transplanted from V6)</p>
        </div>
    </body>
    </html>
    """

    with open("index.html", "w", encoding='utf-8') as f:
        f.write(html_content)
    print("✅ 戰報生成完畢")

if __name__ == "__main__":
    run_agi()
