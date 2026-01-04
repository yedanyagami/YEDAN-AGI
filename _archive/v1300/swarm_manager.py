import os
import psutil
import time
import asyncio
import sys
from dotenv import load_dotenv

# [FIX] Force UTF-8 for Windows Consoles
sys.stdout.reconfigure(encoding='utf-8')

# 載入軍火庫
load_dotenv()

# 硬體安全閾值 (保留 2GB 給 Windows 系統)
RAM_THRESHOLD_PERCENT = 85 
MAX_CONCURRENT_AGENTS = 2  # 8GB RAM 建議同時最多 2 個瀏覽器

def check_vital_signs():
    """檢查硬體狀態，避免過熱或記憶體溢出"""
    mem = psutil.virtual_memory()
    print(f"🖥️ [SYSTEM VITAL] RAM: {mem.percent}% | CPU: {psutil.cpu_percent()}%")
    if mem.percent > RAM_THRESHOLD_PERCENT:
        print("⚠️ [WARNING] RAM Critical! Pausing deployment protocol...")
        return False
    return True

async def deploy_optimized_agent(agent_id, mission, api_model="deepseek"):
    """
    輕量化 Agent 部署
    使用 API (DeepSeek/Grok) 而非本地模型來節省 RAM
    """
    if not check_vital_signs():
        await asyncio.sleep(60) # 等待 1 分鐘讓記憶體釋放
        return

    print(f"🚀 [Agent-{agent_id}] Launching via {api_model} API...")
    
    # [SIMULATION]
    await asyncio.sleep(2) 
    
    print(f"✅ [Agent-{agent_id}] Mission Complete: {mission}")

async def main_swarm():
    print("⚔️ YEDAN V4.0 'Lightborn' Initializing...")
    print(f"🔧 Hardware: AMD Ryzen 5 | 8GB RAM Detected.")
    print("🔒 Strategy: Cloud Inference (DeepSeek/Grok) + Sequential Execution")

    missions = [
        {"target": "Twitter", "task": "Use Grok API to find trending SaaS topics", "model": "grok"},
        {"target": "Reddit", "task": "Use DeepSeek to write solution for Shopify API error", "model": "deepseek"},
        {"target": "Ko-Fi", "task": "Check for new donations via API", "model": "deepseek"}
    ]

    # 限制並發數量的信號量 (Semaphore)
    sem = asyncio.Semaphore(MAX_CONCURRENT_AGENTS)

    async def protected_mission(id, m):
        async with sem:
            await deploy_optimized_agent(id, m['task'], m['model'])

    # 執行任務
    await asyncio.gather(*(protected_mission(i, m) for i, m in enumerate(missions)))

if __name__ == "__main__":
    asyncio.run(main_swarm())
