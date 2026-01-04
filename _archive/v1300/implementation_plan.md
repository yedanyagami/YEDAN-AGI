# [Architecture] SaaS Implementation Plan V2.0 (The 10k Consensus)

**Goal**: Upgrade Guardian Codebase to match the "10k Developer Consensus" found in widespread research.

## User Review Required
> [!IMPORTANT]
> **Architecture Shift**: We are moving from "File Comparison" to "SKU-First Webhook Architecture". This is a significant rewrite but ensures scalability.

## Proposed Changes

### 1. `guardian_package/core_logic.py` (New File)
Implement the **SKU-First** logic.
-   **Class**: `GuardianCore`
-   **Logic**:
    -   All operations key off `SKU` (String), never `Product ID` (Int).
    -   **Matrixify Loader**: Native support for loading `inventory_export.csv` from Matrixify.

### 2. `guardian_package/kill_switch.py` (V2.0)
Upgrade to **Webhook-Only** trigger.
-   **Remove**: Any polling loops.
-   **Add**: `FastAPI` endpoint `/webhook/orders/create`.
-   **Logic**:
    1.  Receive Webhook.
    2.  Extract SKU.
    3.  Check CoreDB for "Safety Buffer" breach.
    4.  If Breach -> Trigger Alert.

### 3. `guardian_package/inventory_auditor.py` (V2.0)
Add **Global Sanitizers**.
-   **Input**: `warehouse_truth.csv`.
-   **Sanitization**:
    -   `detect_decimal_separator`: Auto-switch between `.` and `,` (ES/EU support).
    -   `apply_jst_offset`: If `config.REGION == 'JP'`, add 32400s to timestamps.

## Verification Plan

### Automated Verification
-   Create `test_matrixify_load.py`: Ensure we can parse a real Matrixify export file.
-   Create `test_eu_decimal.py`: Ensure `1.000,00` becomes `1000.0` float.

### Manual Verification
-   Review code against the "10k Consensus" signals (SKU usage, No polling).
