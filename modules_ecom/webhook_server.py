#!/usr/bin/env python3
"""
YEDAN AGI - Commerce Nerve Center (Webhook Server)
The "Nervous System" that receives external payment signals.

Supports:
- Shopify Orders
- Gumroad Sales

Data is logged to sales_history.csv for RLVR training.
"""

import os
import csv
import json
import hmac
import hashlib
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Header
from pydantic import BaseModel
from typing import Optional

# 初始化 FastAPI 應用
app = FastAPI(title="YEDAN AGI Commerce Nerve Center")

# --- 設定與常數 ---
SHOPIFY_SECRET = os.getenv("SHOPIFY_WEBHOOK_SECRET", "your_shopify_secret_here")
GUMROAD_SECRET = os.getenv("GUMROAD_WEBHOOK_SECRET", "your_gumroad_secret_here")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DATA_FILE = os.path.join(DATA_DIR, "sales_history.csv")

# 確保數據儲存目錄存在
os.makedirs(DATA_DIR, exist_ok=True)

# 初始化 CSV 文件 (如果不存在，寫入標題)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # 這些欄位是 AGI 計算 ROAS 和 PnL 的關鍵
        writer.writerow([
            "timestamp", "platform", "event_type", "order_id", 
            "product_name", "amount", "currency", "customer_email"
        ])


# --- 輔助函數 ---
def log_event(platform: str, event_type: str, order_id: str, 
              product_name: str, amount: str, currency: str, email: str):
    """
    將交易事件寫入長期記憶 (CSV)，供 RSI 引擎回測使用
    """
    log_entry = [
        datetime.now().isoformat(),
        platform,
        event_type,
        order_id,
        product_name,
        amount,
        currency,
        email
    ]
    
    with open(DATA_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(log_entry)
    
    print(f"✅ [AGI MEMORY] Recorded {platform} sale: {amount} {currency} - {product_name}")
    return log_entry


# --- 驗證邏輯 (Security) ---
async def verify_shopify_hmac(body: bytes, hmac_header: str) -> bool:
    """驗證請求是否真的來自 Shopify (防止偽造數據攻擊 AGI)"""
    import base64
    if not hmac_header:
        return False
    hash_calc = hmac.new(
        SHOPIFY_SECRET.encode('utf-8'), 
        body, 
        hashlib.sha256
    ).digest()
    expected = base64.b64encode(hash_calc).decode('utf-8')
    return hmac.compare_digest(expected, hmac_header)


# --- Endpoints (神經觸手) ---

@app.get("/")
def health_check():
    """Health check endpoint"""
    return {
        "status": "active", 
        "system": "YEDAN AGI Commerce Nerve Center",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/stats")
def get_stats():
    """Get sales statistics"""
    try:
        if not os.path.exists(DATA_FILE):
            return {"total_sales": 0, "total_revenue": 0}
        
        with open(DATA_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
        total_sales = len(rows)
        total_revenue = sum(float(r.get("amount", 0) or 0) for r in rows)
        
        return {
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "last_sale": rows[-1] if rows else None
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/webhook/shopify/orders/create")
async def shopify_order_webhook(
    request: Request, 
    x_shopify_hmac_sha256: Optional[str] = Header(None)
):
    """
    接收 Shopify 訂單創建事件
    """
    body_bytes = await request.body()
    
    # 1. 安全驗證 (MVP 階段可跳過)
    # if SHOPIFY_SECRET != "your_shopify_secret_here":
    #     if not await verify_shopify_hmac(body_bytes, x_shopify_hmac_sha256):
    #         raise HTTPException(status_code=401, detail="Invalid HMAC")

    try:
        payload = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    # 2. 提取 AGI 需要的關鍵數據
    try:
        order_id = str(payload.get("id", ""))
        total_price = str(payload.get("total_price", "0"))
        currency = payload.get("currency", "USD")
        email = payload.get("email", "")
        
        # 取得第一個商品的名稱 (簡化版)
        line_items = payload.get("line_items", [])
        product_name = line_items[0].get("name") if line_items else "Unknown Product"

        # 3. 寫入記憶
        log_event("Shopify", "order_created", order_id, product_name, total_price, currency, email)
        
        return {"status": "received", "order_id": order_id}
        
    except Exception as e:
        print(f"⚠️ Error parsing Shopify payload: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/webhook/gumroad/sale")
async def gumroad_sale_webhook(request: Request):
    """
    接收 Gumroad 銷售事件
    Gumroad 通常發送 application/x-www-form-urlencoded
    """
    try:
        # Try form data first (Gumroad's default)
        content_type = request.headers.get("content-type", "")
        
        if "form" in content_type:
            form_data = await request.form()
            product_name = form_data.get("product_name", "Unknown")
            price = form_data.get("price", "0")
            currency = form_data.get("currency", "USD")
            email = form_data.get("email", "")
            order_id = form_data.get("sale_id", str(datetime.now().timestamp()))
        else:
            # JSON fallback
            payload = await request.json()
            product_name = payload.get("product_name", "Unknown")
            price = str(payload.get("price", "0"))
            currency = payload.get("currency", "USD")
            email = payload.get("email", "")
            order_id = payload.get("sale_id", str(datetime.now().timestamp()))

        # 寫入記憶
        log_event("Gumroad", "sale", order_id, product_name, price, currency, email)
        
        return {"status": "received", "order_id": order_id}

    except Exception as e:
        print(f"⚠️ Error parsing Gumroad payload: {e}")
        return {"status": "error", "message": str(e)}


@app.post("/webhook/payhip/sale")
async def payhip_sale_webhook(request: Request):
    """
    接收 Payhip 銷售事件
    """
    try:
        payload = await request.json()
        
        product_name = payload.get("product_name", "Unknown")
        price = str(payload.get("amount", "0"))
        currency = payload.get("currency", "USD")
        email = payload.get("buyer_email", "")
        order_id = payload.get("order_id", str(datetime.now().timestamp()))

        # 寫入記憶
        log_event("Payhip", "sale", order_id, product_name, price, currency, email)
        
        return {"status": "received", "order_id": order_id}

    except Exception as e:
        print(f"⚠️ Error parsing Payhip payload: {e}")
        return {"status": "error", "message": str(e)}


# --- 啟動指令 ---
# uvicorn modules_ecom.webhook_server:app --reload --port 8000

if __name__ == "__main__":
    import uvicorn
    print("Starting YEDAN AGI Commerce Nerve Center...")
    print("Endpoints:")
    print("  GET  /              - Health check")
    print("  GET  /stats         - Sales statistics")
    print("  POST /webhook/shopify/orders/create")
    print("  POST /webhook/gumroad/sale")
    print("  POST /webhook/payhip/sale")
    uvicorn.run(app, host="0.0.0.0", port=8000)
