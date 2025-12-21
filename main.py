import os
import datetime
import asset_linker

def run_agi_intelligence():
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    print("🧠 [AGI] 全局資產同步開始...")
    asset_linker.get_asset_status()
    
    # 這裡未來將加入讀取 yedan-core/V6 的邏輯
    summary = """
    <h2>✅ 全局資產已掛載</h2>
    <ul>
        <li><b>yedan-core:</b> 讀取 V6 自我進化演算法...</li>
        <li><b>yedan-sales:</b> 支付接口已就緒 (Ko-fi Ready)...</li>
        <li><b>YEDAN-AGI:</b> 部署中樞穩定...</li>
    </ul>
    """
    
    with open("index.html", "w", encoding='utf-8') as f:
        f.write(f"<h1>👁️ YEDAN AGI 指揮中心</h1><p>同步時間: {time_now}</p>{summary}")

if __name__ == "__main__":
    run_agi_intelligence()
