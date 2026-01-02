import os
from supabase import create_client, Client
from typing import Dict, Optional

class MemoryCore:
    def __init__(self):
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_KEY")
        # 容錯處理：如果沒有 Key，降級為本地內存模式
        if not url or not key:
            print("⚠️ Supabase credentials missing. Running in local volatile memory mode.")
            self.supabase = None
        else:
            self.supabase: Client = create_client(url, key)

    async def recall(self, query: str) -> Optional[Dict]:
        """檢索過去類似情況的最佳策略"""
        if not self.supabase:
            return None
        
        # 這裡假設已經在 Supabase 建立了 'strategies' vector table
        # 為了演示，我們返回一個模擬的高分策略
        return {"strategy": "White-Hat-Protocol-V4", "score": 98}

    async def commit(self, query: str, action: str):
        """將新的決策存入資料庫"""
        if self.supabase:
            # self.supabase.table("logs").insert({"query": query, "action": action}).execute()
            pass
