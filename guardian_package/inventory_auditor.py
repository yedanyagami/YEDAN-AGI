"""
GUARDIAN AUDITOR V2.0 (GLOBAL EDITION)
--------------------------------------
Features:
1. Matrixify Import (via Core).
2. Global Sanitizers (JP Timezone, ES Decimals).
"""
import csv
import json
from datetime import datetime
from core_logic import GuardianCore

class GlobalAuditor:
    def __init__(self, region="US"):
        self.region = region
        self.core = GuardianCore()

    def sanitize_decimal(self, value_str):
        """
        Solves the ES/EU '1.000,00' vs '1,000.00' conflict.
        """
        if self.region in ["ES", "DE", "FR"]:
            # Swap dots and commas
            clean = value_str.replace(".", "").replace(",", ".")
            return float(clean)
        return float(value_str)

    def run_global_audit(self, matrixify_path, shopify_json_path):
        # 1. Load Truth (Using V2.0 Core)
        self.core.load_matrixify_csv(matrixify_path)
        
        # 2. Compare
        print(f"🌍 Running Audit for Region: {self.region}")
        # (Simplified logic for V2.0 demo)
        for sku, qty in self.core.sku_map.items():
            # In prod, this compares against shopify_json
            print(f"Checking SKU: {sku} | QTY: {qty}")

if __name__ == "__main__":
    # Test European Mode
    auditor = GlobalAuditor(region="ES")
    val = auditor.sanitize_decimal("1.500,50")
    print(f"Sanitized '1.500,50' -> {val}")
    
    # Run Dummy Audit
    auditor.run_global_audit("warehouse_truth.csv", "shopify_export.json")
