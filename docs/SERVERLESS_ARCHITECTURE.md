# YEDAN V2.0 Serverless Architecture (The Brain Transplant) ☁️🧠

**Objective**: Eliminate local `run_roi_loop.py`. Move 100% logic to Cloudflare + n8n.
**Cost**: ~$5/mo (Cloudflare Workers + n8n Basic).
**Uptime**: 99.99% (No PC required).

## 1. The New Core Loop (n8n)
Instead of a `while True` loop in Python, we use an **n8n Cron Trigger**.

*   **Trigger**: Cron (Every 10-30 mins)
*   **Step 1**: Call `Darwin Worker` (Cloudflare) -> Get `strategy` (e.g., "Sassy + Reddit").
*   **Step 2**: Switch (Strategy):
    *   **Case: Reddit Post**:
        *   Call `Content Miner` (n8n HTTP Request to NewsAPI/Reddit).
        *   Call `Writer Agent` (n8n AI Node / DeepSeek).
        *   Call `Cloud Social` (n8n HTTP Request to Browserless).
    *   **Case: Shopify Product**:
        *   Call `Opal` (n8n HTTP Request to Trends).
        *   Call `Shopify API` (Create Product).
*   **Step 3**: Feedback -> Call `Darwin Worker` (Report Win/Loss).

## 2. The Nueral Network (Cloudflare Workers)

We move the stateful logic to Cloudflare Workers.

### A. Darwin Worker (`/darwin`)
*   **Replaces**: `modules/darwin.py` + `data/prompts.json`.
*   **Storage**: Cloudflare KV (Key-Value Store).
*   **Endpoints**:
    *   `GET /strategy`: Returns the best strategy using Epsilon-Greedy.
    *   `POST /feedback`: Updates win/loss counts for a strategy.

### B. Synapse Worker (`/synapse`)
*   **Status**: Already Active (Relay).
*   **Update**: Will simply route heavy requests if needed.

## 3. Migration Checklist

| component | Local (Old) | Cloud (New) |
| :--- | :--- | :--- |
| **Orchestrator** | `run_roi_loop.py` | **n8n Workflow** (Cron + Switch) |
| **Strategy Brain** | `modules/darwin.py` | **Cloudflare Worker** (`darwin-worker`) |
| **Memory** | `data/prompts.json` | **Cloudflare KV** (`Darwin_Genes`) |
| **Trends** | `modules/oracle.py` | **n8n HTTP Request** (Google Trends API) |
| **Execution** | `cloud_social.py` | **n8n -> Browserless API** (Direct) |

## 4. Execution Plan

1.  **Deploy `darwin-worker`**: Upload the JS logic to `darwin.yagami8095.workers.dev`.
2.  **Import n8n Workflow**: Upload `yedan_core.json` to n8n instance.
3.  **Config**: Env vars in n8n (Service Account).
4.  **Launch**: Turn off the PC.
