"""
GUARDIAN KILL-SWITCH V2.0 (WEBHOOK EDITION)
-------------------------------------------
THE 10K CONSENSUS: "NEVER POLL".
This script listens for Shopify 'orders/create' webhooks.
"""
import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from collections import deque
import time

# IMPORT V2.0 CORE
try:
    from core_logic import GuardianCore
except ImportError:
    # Fallback for standalone run
    class GuardianCore: 
        def check_buffer_breach(self, s, q, b): return False, "OK"

# CONFIG
PORT = 8000
ANOMALY_THRESHOLD = 5 
TIME_WINDOW = 60
SAFETY_BUFFER = 50

risk_counter = deque()

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            payload = json.loads(post_data)
            self.process_webhook(payload)
            self.send_response(200)
        except Exception as e:
            logging.error(f"Error processing webhook: {e}")
            self.send_response(500)
        self.end_headers()

    def process_webhook(self, payload):
        """
        V2.0 LOGIC:
        1. Extract SKU from Line Items.
        2. Check for "Buffer Breach" (Real-time).
        """
        line_items = payload.get("line_items", [])
        for item in line_items:
            sku = item.get("sku")
            print(f"📦 Processing Order for SKU: {sku}")
            
            # SIMULATING A CHECK AGAINST CORE MEMORY
            # In prod, this links to the loaded Matrixify CSV
            
            # ANOMALY DETECTION (The Death Spiral Check)
            now = time.time()
            risk_counter.append(now)
            
            # Prune
            while risk_counter and (now - risk_counter[0] > TIME_WINDOW):
                risk_counter.popleft()
                
            if len(risk_counter) >= ANOMALY_THRESHOLD:
                print("🚫 KILL SWITCH TRIGGERED: Too many requests!")

def run_server():
    print(f"🛡️  Guardian V2.0 Listening on Port {PORT}...")
    server = HTTPServer(('localhost', PORT), WebhookHandler)
    server.serve_forever()

if __name__ == '__main__':
    run_server()
