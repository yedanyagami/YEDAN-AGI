import os
import google.generativeai as genai
from datetime import datetime

# 設定 API (從 GitHub Secrets 獲取)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def reflect():
    """
    AGI 自我反思迴路：
    1. 感知：讀取當前時間與檔案狀態
    2. 思考：(未來擴充) 呼叫 Gemini 分析 logs
    3. 行動：寫入 reflection_log.md
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if not GEMINI_API_KEY:
        print("Warning: No GEMINI_API_KEY found. Running in localized mode.")
        ai_thought = "I am awake, but I cannot see the outside world yet (No API Key)."
    else:
        # 這裡未來會接上真正的 Gemini 思考，目前先做自我狀態確認
        ai_thought = "System Check: Ouroboros cycle active. I have write access. I am ready to evolve."

    # 產生反思日誌
    log_entry = f"## Reflection at {timestamp}\n- Status: {ai_thought}\n- Action: Logged memory.\n\n"

    # 寫入長期記憶 (檔案)
    with open("reflection_log.md", "a") as f:
        f.write(log_entry)
    
    print(f"Reflection complete: {ai_thought}")

if __name__ == "__main__":
    reflect()
