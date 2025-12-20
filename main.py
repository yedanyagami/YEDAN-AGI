import datetime
import requests
import os

def generate_report():
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # 獲取數據
    btc_price = "Loading..."
    sol_price = "Loading..."
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,solana&vs_currencies=usd"
        data = requests.get(url, timeout=10).json()
        btc_price = f"${data['bitcoin']['usd']:,}"
        sol_price = f"${data['solana']['usd']:,}"
    except:
        pass

    # 生成 HTML (這就是 Cloudflare 要顯示的內容)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>YEDAN AGI INTELLIGENCE</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="refresh" content="1800"> <style>
            body {{ background-color: #000; color: #0f0; font-family: monospace; padding: 20px; }}
            h1 {{ border-bottom: 2px solid #0f0; padding-bottom: 10px; }}
            .card {{ border: 1px solid #0f0; padding: 15px; margin: 10px 0; }}
            .time {{ color: #888; font-size: 0.8em; }}
        </style>
    </head>
    <body>
        <h1>👁️ YEDAN AGI 監控中心</h1>
        <div class="time">最後更新: {time_now}</div>
        
        <div class="card">
            <h3>💰 市場資產監控</h3>
            <p>Bitcoin (BTC): <strong>{btc_price}</strong></p>
            <p>Solana (SOL): <strong>{sol_price}</strong></p>
        </div>

        <div class="card">
            <h3>🤖 系統狀態</h3>
            <p>狀態: <span style="color: #0f0;">ONLINE</span></p>
            <p>託管: GitHub Actions + Cloudflare</p>
        </div>
    </body>
    </html>
    """

    # 寫入檔案
    with open("public/index.html", "w", encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 戰報已生成: {time_now}")

if __name__ == "__main__":
    generate_report()
