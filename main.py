import datetime
import os
import logic_core
from yedan_guardian import Guardian
from yedan_wallet import Wallet
from product_delivery import DigitalDelivery

def run_agi_system():
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # 初始化
    brain = Guardian()
    wallet = Wallet()
    logistics = DigitalDelivery()
    
    print(f"🤖 [AGI OMEGA] 啟動神經網路... {time_now}")

    # --- PHASE 1: 自我診斷與修正 (Ask Gemini) ---
    # 如果系統有之前的錯誤紀錄，詢問 Gemini 如何修正
    allow, guard_msg = brain.check_error_history("SYSTEM_HEALTH")
    ai_advice = "系統運轉正常，無需修正。"
    
    if "BLOCK" in guard_msg or "WARN" in guard_msg:
        print("⚠️ 偵測到系統異常，正在諮詢 Gemini...")
        prompt = f"我的 Python 自動化系統遇到這個錯誤: '{guard_msg}'。請用一句話告訴我如何修正或優化它。"
        ai_advice = logic_core.ask_gemini(prompt)
        print(f"💡 Gemini 建議: {ai_advice}")

    # --- PHASE 2: 執行業務 (Money Logic) ---
    try:
        new_orders = wallet.scan_for_payments()
        for order in new_orders:
            success, msg = logistics.deliver_product(order['email'], order['product'])
            if success:
                wallet.mark_as_done(order['id'])
                # 賺到錢了，讓 Gemini 寫一句慶祝詞
                celebration = logic_core.ask_gemini(f"我剛剛自動賺了 $27，寫一句簡短霸氣的慶祝語，要在戰報上顯示。")
                print(f"🎉 {celebration}")
    except Exception as e:
        print(f"❌ 業務執行錯誤: {e}")
        brain.log_error("RUNTIME_ERROR")

    # --- PHASE 3: 市場戰略分析 (Strategic Thinking) ---
    market_data = logic_core.fetch_market_data()
    # 讓 Gemini 分析當前價格並給出建議
    market_prompt = f"現在 BTC 價格是 {market_data.get('BTC')}，SOL 價格是 {market_data.get('SOL')}。請給出一句簡短的市場趨勢判斷（看漲/看跌/觀望）。"
    market_analysis = logic_core.ask_gemini(market_prompt)

    # --- PHASE 4: 獲取財務狀態 ---
    revenue, count = wallet.get_balance()

    # --- PHASE 5: 生成全知戰報 (包含 Gemini 的建議) ---
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>YEDAN AGI: NEURAL LINK</title>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="900">
        <style>
            body {{ background-color: #000; color: #0f0; font-family: monospace; padding: 20px; }}
            .box {{ border: 1px solid #333; padding: 15px; margin-bottom: 10px; background: #111; }}
            h1 {{ color: #fff; border-bottom: 1px solid #0f0; }}
            .ai-msg {{ color: #00ffff; font-style: italic; }}
            .money {{ color: gold; font-size: 1.5em; }}
        </style>
    </head>
    <body>
        <h1>🧠 YEDAN AGI: NEURAL LINK ACTIVE</h1>
        <p>Sync: {time_now}</p>

        <div class="box">
            <h3>💡 Gemini 戰略顧問 (AI Brain)</h3>
            <p>系統診斷: <span class="ai-msg">{ai_advice}</span></p>
            <p>市場分析: <span class="ai-msg">{market_analysis}</span></p>
        </div>

        <div class="box">
            <h3>💰 財務中樞 (Wallet)</h3>
            <p>總營收: <span class="money">${revenue}</span></p>
            <p>處理訂單: {count}</p>
        </div>

        <div class="box">
            <h3>📈 市場數據 (Eyes)</h3>
            <p>BTC: {market_data.get('BTC')}</p>
            <p>SOL: {market_data.get('SOL')}</p>
        </div>
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding='utf-8') as f:
        f.write(html_content)
    print("✅ 戰報更新完畢")

if __name__ == "__main__":
    run_agi_system()
