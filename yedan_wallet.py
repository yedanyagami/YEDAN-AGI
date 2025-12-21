import sqlite3
import json
import datetime
import uuid

DB_NAME = "yedan_memory.db"

class Wallet:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()
        self._init_ledger()

    def _init_ledger(self):
        """初始化帳本 (對應 Sales Engine 的 D1 結構)"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id TEXT PRIMARY KEY,
                source TEXT,
                product TEXT,
                price REAL,
                email TEXT,
                created_at TEXT
            )
        """)
        self.conn.commit()

    def process_webhook(self, source, data):
        """處理來自 Gumroad 或 Ko-fi 的訂單"""
        sale_data = {}
        
        try:
            if source == 'gumroad':
                # 模擬 Gumroad 格式解析
                sale_data = {
                    'id': data.get('sale_id', f"G_{int(datetime.datetime.now().timestamp())}"),
                    'price': float(data.get('price', 0)),
                    'product': data.get('product_name', 'unknown'),
                    'email': data.get('email', 'anon'),
                    'created_at': datetime.datetime.now().isoformat()
                }
            elif source == 'kofi':
                # 模擬 Ko-fi 格式解析 (Level 1)
                # Ko-fi 傳來的是 JSON string，這裡假設已經 loads
                sale_data = {
                    'id': data.get('message_id', f"K_{int(datetime.datetime.now().timestamp())}"),
                    'price': float(data.get('amount', 0)),
                    'product': 'Ko-fi Donation',
                    'email': data.get('email', 'anon'),
                    'created_at': data.get('timestamp', datetime.datetime.now().isoformat())
                }
            
            # 存入金庫
            print(f"💰 [WALLET] 收到 {source} 款項: ${sale_data['price']} ({sale_data['product']})")
            self.cursor.execute(
                "INSERT OR IGNORE INTO sales (id, source, product, price, email, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (sale_data['id'], source, sale_data['product'], sale_data['price'], sale_data['email'], sale_data['created_at'])
            )
            self.conn.commit()
            return True, f"收據已開立: {sale_data['id']}"

        except Exception as e:
            return False, f"交易失敗: {str(e)}"

    def check_balance(self):
        """查詢總營收"""
        self.cursor.execute("SELECT SUM(price), COUNT(*) FROM sales")
        total, count = self.cursor.fetchone()
        return total or 0, count

# 測試收銀機
if __name__ == "__main__":
    w = Wallet()
    
    # 測試 1: 模擬有人在 Gumroad 買了 SEO Auditor ($27)
    print("--- 測試 1: Gumroad 購買 ---")
    w.process_webhook('gumroad', {
        'sale_id': str(uuid.uuid4()),
        'price': '27.00',
        'product_name': 'YEDAN SEO Auditor',
        'email': 'customer@example.com'
    })
    
    # 測試 2: 模擬有人在 Ko-fi 斗內 ($5)
    print("\n--- 測試 2: Ko-fi 斗內 ---")
    w.process_webhook('kofi', {
        'message_id': str(uuid.uuid4()),
        'amount': '5.00',
        'email': 'fan@example.com'
    })
    
    # 結算
    total, count = w.check_balance()
    print(f"\n📊 [REPORT] 總營收: ${total} (共 {count} 筆訂單)")
