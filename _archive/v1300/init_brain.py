import sqlite3
import os

DB_NAME = "yedan_memory.db"

# 您提取的 10% 黃金架構
SCHEMA = """
-- YEDAN Error Learning System (Extracted from Asset)
CREATE TABLE IF NOT EXISTS error_learning (
  error_id TEXT PRIMARY KEY,
  error_type TEXT NOT NULL,
  error_code TEXT,
  root_cause TEXT,
  solution TEXT,
  occurrence_count INTEGER DEFAULT 1,
  last_occurred_at INTEGER,
  severity TEXT DEFAULT 'medium'
);

CREATE TABLE IF NOT EXISTS deployment_plans (
  plan_id TEXT PRIMARY KEY,
  feature_name TEXT NOT NULL,
  plan_type TEXT NOT NULL,
  status TEXT DEFAULT 'draft',
  risk_level TEXT DEFAULT 'medium'
);

-- 初始化已知錯誤 (來自您的 SQL)
INSERT OR IGNORE INTO error_learning (error_id, error_type, error_code, root_cause, solution, occurrence_count, severity)
VALUES 
('err_002', 'deployment', 'FILE_CORRUPTION', 'PowerShell -replace corruption', 'Use python script instead', 1, 'critical');
"""

def wake_up():
    print(f"🧠 [BRAIN] 正在初始化神經元: {DB_NAME}...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 注入靈魂 (Schema)
    cursor.executescript(SCHEMA)
    
    # 驗證記憶
    cursor.execute("SELECT count(*) FROM error_learning")
    err_count = cursor.fetchone()[0]
    
    conn.commit()
    conn.close()
    
    print(f"✅ [BRAIN] 大腦覺醒完畢。")
    print(f"📚 [MEMORY] 當前已索引錯誤知識: {err_count} 條")
    print(f"🛡️ [GUARD] '同樣錯誤不犯第三次' 協議已啟動。")

if __name__ == "__main__":
    wake_up()
