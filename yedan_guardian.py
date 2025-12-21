import sqlite3
import uuid
import time

DB_NAME = "yedan_memory.db"

class Guardian:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()

    def check_error_history(self, error_code):
        """檢查某個錯誤是否已經犯過太多次"""
        self.cursor.execute("SELECT occurrence_count, solution FROM error_learning WHERE error_code = ?", (error_code,))
        row = self.cursor.fetchone()
        
        if row:
            count, solution = row
            if count >= 2:
                return False, f"⛔ [BLOCK] 此錯誤已發生 {count} 次! 系統拒絕執行以防止崩潰。解決方案: {solution}"
            else:
                return True, f"⚠️ [WARN] 此錯誤曾發生過 {count} 次。請小心。"
        return True, "✅ [SAFE] 無相關錯誤記錄。"

    def log_new_error(self, error_type, error_code, cause):
        """學習新錯誤"""
        error_id = f"err_{int(time.time())}"
        print(f"📝 [LEARN] 正在記錄新錯誤: {error_code}")
        
        # 嘗試更新現有錯誤
        self.cursor.execute("UPDATE error_learning SET occurrence_count = occurrence_count + 1, last_occurred_at = ? WHERE error_code = ?", (int(time.time()), error_code))
        
        if self.cursor.rowcount == 0:
            # 如果是新錯誤，插入
            self.cursor.execute("INSERT INTO error_learning (error_id, error_type, error_code, root_cause, occurrence_count, last_occurred_at) VALUES (?, ?, ?, ?, 1, ?)", 
                                (error_id, error_type, error_code, cause, int(time.time())))
        
        self.conn.commit()

# 測試守護者
if __name__ == "__main__":
    g = Guardian()
    
    # 測試 1: 模擬一個已知的高風險操作
    print("--- 測試 1: 執行 PowerShell 替換 ---")
    allow, msg = g.check_error_history("FILE_CORRUPTION")
    print(msg)
    
    # 測試 2: 模擬一個新錯誤
    print("\n--- 測試 2: 發生 API 超時 ---")
    g.log_new_error("runtime", "API_TIMEOUT", "Network latency > 5000ms")
    
    # 測試 3: 再次發生同樣錯誤 (模擬學習)
    g.log_new_error("runtime", "API_TIMEOUT", "Network latency again")
    allow, msg = g.check_error_history("API_TIMEOUT")
    print(f"檢查結果: {msg}")

