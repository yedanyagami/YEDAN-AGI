import os
import logging
import subprocess
import google.generativeai as genai
from datetime import datetime

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GENESIS-ARCHITECT")

# 設定 Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def create_new_skill(goal):
    """
    讓 AGI 自己寫代碼的核心函數。
    """
    logger.info(f"🧠 架構師正在思考如何達成目標: {goal} ...")
    
    model = genai.GenerativeModel('gemini-pro')
    
    # 這是給 LLM 的「元指令 (Meta-Prompt)」
    prompt = f"""
    你是 YEDAN-AGI 的首席架構師。你的任務是編寫一個獨立的 Python 腳本來達成以下目標：
    目標：{goal}
    
    要求：
    1. 腳本必須是完整的，包含所有 import。
    2. 必須包含錯誤處理 (try-except)。
    3. 檔案名稱必須是 'skill_{datetime.now().strftime("%H%M")}.py'。
    4. 直接輸出 Python 代碼，不要有 Markdown 格式。
    5. 如果需要額外安裝庫，請在註解中說明。
    """
    
    try:
        response = model.generate_content(prompt)
        code = response.text.replace('', '')
        
        # 產生檔案名稱
        filename = f"skill_generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        
        with open(filename, "w") as f:
            f.write(code)
            
        logger.info(f"🧬 新技能已生成: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"❌ 創造失敗: {e}")
        return None

if __name__ == "__main__":
    # 測試用：讓它自己寫一個簡單的 Hello World
    create_new_skill("寫一個腳本，打印出當前的 UTC 時間和一句激勵的話")
