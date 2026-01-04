"""
GUARDIAN PACKAGE V2.0 - CORE LOGIC
----------------------------------
THE 10K CONSENSUS: SKU-FIRST ARCHITECTURE.
Drivers:
1. 'SKU' is the only reliable foreign key.
2. 'Matrixify' is the only reliable bulk format.
3. 'Webhooks' are the only safe trigger.
"""
import csv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [CORE] %(message)s')

class GuardianCore:
    def __init__(self):
        self.sku_map = {}

    def load_matrixify_csv(self, filepath):
        """
        Parses a standard Matrixify (Excelify) inventory export.
        Columns Expected: 'Variant SKU', 'Inventory Available: [Location]'
        """
        logging.info(f"📂 Loading Matrixify compatible file: {filepath}")
        count = 0
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # HEURISTIC: Find the 'Variant SKU' column
                    sku = row.get('Variant SKU') or row.get('SKU') or row.get('Handle')
                    
                    if not sku:
                        continue

                    # HEURISTIC: Find inventory column (often 'Inventory Available: ...')
                    qty = 0
                    for k, v in row.items():
                        if "Inventory Available" in k or "QTY" in k:
                            try:
                                qty = int(v)
                                break 
                            except:
                                pass
                    
                    self.sku_map[sku] = qty
                    count += 1
            
            logging.info(f"✅ Loaded {count} SKUs into Core Memory.")
            return True
        except Exception as e:
            logging.error(f"❌ Matrixify Load Failed: {e}")
            return False

    def check_buffer_breach(self, sku, current_qty, safety_buffer=50):
        """
        The 'Safety Buffer' Logic (Reddit Consensus).
        """
        if current_qty < safety_buffer:
            return True, f"⚠️ BREACH: Stock {current_qty} < Buffer {safety_buffer}"
        return False, "OK"
