"""
Money Dashboard Generator
Creates a real-time HTML dashboard for YEDAN Revenue.
Auto-refreshes every 30 seconds.
"""
import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from modules.echo_analytics import EchoAnalytics
from modules.config import Config

DASHBOARD_PATH = "dashboard.html"

def generate_dashboard():
    echo = EchoAnalytics()
    data = echo.quick_status()
    
    # Read n8n status from cache
    n8n_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "n8n_status.json")
    try:
        if os.path.exists(n8n_path):
            with open(n8n_path, "r") as f:
                n8n_data = json.load(f)
        else:
            n8n_data = {"connected": False, "workflows": 0}
    except:
        n8n_data = {"connected": False, "workflows": 0}

    n8n_status_html = f"<span style='color: #00ff00'>ONLINE ({n8n_data.get('workflows', 0)} Workflows)</span>" if n8n_data.get('connected') else "<span style='color: #ff0000'>OFFLINE</span>"
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="refresh" content="30">
        <title>YEDAN AGI | Mission Control ☁️</title>
        <style>
            body {{ font-family: 'Courier New', monospace; background-color: #0a0a0a; color: #00ff00; margin: 0; padding: 20px; }}
            .container {{ max-width: 800px; margin: 0 auto; border: 2px solid #00ff00; padding: 20px; }}
            h1 {{ text-align: center; text-transform: uppercase; border-bottom: 1px solid #00ff00; padding-bottom: 10px; }}
            .metric-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 20px; }}
            .metric-card {{ background: #111; padding: 20px; border: 1px solid #333; text-align: center; }}
            .metric-value {{ font-size: 2.5em; font-weight: bold; margin: 10px 0; }}
            .metric-label {{ color: #888; text-transform: uppercase; font-size: 0.8em; }}
            .status-bar {{ margin-top: 30px; font-size: 0.9em; color: #666; text-align: center; }}
            .cloud-status {{ margin-top: 20px; padding: 10px; border: 1px dashed #444; text-align: center; }}
            .blink {{ animation: blinker 1.5s linear infinite; }}
            @keyframes blinker {{ 50% {{ opacity: 0; }} }}
            .live-indicator {{ color: #ff0000; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>YEDAN AGI <span class="live-indicator blink">● LIVE</span></h1>
            
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">Today's Revenue</div>
                    <div class="metric-value">${data['today_revenue']:.2f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Sales Count</div>
                    <div class="metric-value">{data['today_sales']}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">PayPal Balance</div>
                    <div class="metric-value">${data['paypal_balance']:.2f}</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">Cloud Brain (n8n)</div>
                    <div class="metric-value" style="font-size: 1.5em">{n8n_status_html}</div>
                </div>
            </div>
            
            <div class="cloud-status">
                SYSTEM MODE: <strong>ULTRA (ECO)</strong> | SYNAPSE: <strong>ONLINE</strong>
            </div>
            
            <div class="status-bar">
                LAST UPDATED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} <br>
                NEXT REFRESH IN 30s
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(DASHBOARD_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"[Dashboard] Dashboard updated: {os.path.abspath(DASHBOARD_PATH)}")

if __name__ == "__main__":
    generate_dashboard()
