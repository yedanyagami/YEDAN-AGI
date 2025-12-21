ASSETS = {
    "CORE": "yedanyagami/yedan-core",         # 核心演算法 (Evolution V6)
    "SALES": "yedanyagami/yedan-sales-engine", # 支付與變現接口 (Wrangler/Ko-fi)
    "XOXO": "yedanyagami/yedan-xoxo",         # 實驗性功能與測試
    "AGI": "yedanyagami/YEDAN-AGI"            # 當前指揮中樞
}

def get_asset_status():
    for name, path in ASSETS.items():
        print(f"📡 [AGI] 已連線至資產庫 [{name}]: {path}")

if __name__ == "__main__":
    get_asset_status()
