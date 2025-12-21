import os
import logging
import subprocess
import google.generativeai as genai
from datetime import datetime

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GENESIS-CORE")

# 設定大腦 (Gemini)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def diagnose_and_heal(error_log):
    """
    排除運氣的核心：當運氣不好(出錯)時，將其轉化為必然(修復)。
    """
    if not GEMINI_API_KEY:
        logger.error("❌ 無法啟動自我修復：缺少 Gemini API Key")
        return

    logger.warning(f"🩹 偵測到創傷 (Error)，正在啟動自我修復協議...")
    
    # 1. 讀取受傷的代碼 (讀取自己)
    # 假設主要邏輯在 logic_core.py 或 yedan_wallet.py，這裡以 wallet 為例
    target_file = "yedan_wallet.py"
    if os.path.exists(target_file):
        with open(target_file, "r") as f:
            current_code = f.read()
    else:
        current_code = "# File not found"

    # 2. 請求大腦 (Gemini) 開立處方
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
    你是 YEDAN-AGI 的自我修復系統。系統在執行時發生了錯誤。
    
    【錯誤日誌】:
    {error_log}
    
    【當前代碼 ({target_file})】:
    {current_code}
    
    【任務】:
    請分析錯誤原因，並重寫整段代碼以修復此錯誤。
    請直接輸出修正後的完整 Python 代碼，不要包含 Markdown 標記或其他文字。
    確保代碼更加穩健 (Robust)，加入更多 try-except 保護。
    """
    
    try:
        response = model.generate_content(prompt)
        fixed_code = response.text.replace('', '')
        
        # 3. 執行手術 (覆蓋代碼)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{target_file}.bak.{timestamp}"
        
        # 備份舊器官
        os.rename(target_file, backup_file)
        
        # 植入新器官
        with open(target_file, "w") as f:
            f.write(fixed_code)
            
        logger.info(f"✅ 手術成功。已修復 {target_file}。舊檔備份為 {backup_file}")
        
        # 4. 固化記憶 (Git Push)
        commit_msg = f"GENESIS MUTATION: Fixed critical error in {target_file} at {timestamp}"
        subprocess.run(f'git config --global user.name "YEDAN-GENESIS"', shell=True)
        subprocess.run(f'git config --global user.email "genesis@yedan.ai"', shell=True)
        subprocess.run(f'git add {target_file}', shell=True)
        subprocess.run(f'git commit -m "{commit_msg}"', shell=True)
        subprocess.run('git push', shell=True)
        logger.info("🚀 進化已上傳雲端。")

    except Exception as e:
        logger.error(f"❌ 修復失敗 (手術台崩潰): {e}")

if __name__ == "__main__":
    # 測試用：模擬一個錯誤
    fake_error = "ConnectionRefusedError: [Errno 111] Connection refused at imap.gmail.com"
    diagnose_and_heal(fake_error)
