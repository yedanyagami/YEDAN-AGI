"""
YEDAN AGI - Dashboard Generator
Creates a visual HTML dashboard from Echo Analytics data
"""
import json
from datetime import datetime
from modules.echo_analytics import EchoAnalytics
from modules.config import Config

class DashboardGenerator:
    def __init__(self):
        self.echo = EchoAnalytics()
        
    def generate(self, output_file="dashboard.html"):
        print("[Dashboard] Gathering intelligence...")
        
        # Fetch Data
        synapse = self.echo.get_synapse_revenue(days=30)
        shopify = self.echo.get_shopify_stats()
        paypal = self.echo.get_paypal_balance()
        
        # Process Data for Chart
        revenue_data = synapse.get("revenue", [])
        # Sort by date just in case
        revenue_data.sort(key=lambda x: x.get("date", ""))
        
        dates = [d.get("date") for d in revenue_data]
        values = [d.get("revenue", 0) for d in revenue_data]
        
        # Status checks
        status_synapse = "Online" if dates else "Offline (No Data)"
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YEDAN AGI | ROI Command Center</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ background-color: #0f172a; color: #e2e8f0; font-family: 'Inter', sans-serif; }}
        .glass {{ background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); }}
    </style>
</head>
<body class="p-6">
    <div class="max-w-7xl mx-auto space-y-6">
        
        <!-- Header -->
        <div class="flex justify-between items-center">
            <div>
                <h1 class="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
                    YEDAN V2.0 ENGINE
                </h1>
                <p class="text-gray-400 text-sm">Autonomous Revenue Architecture</p>
            </div>
            <div class="text-right">
                <p class="text-sm text-gray-400">Last Updated</p>
                <p class="font-mono text-emerald-400">{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>

        <!-- KPI Grid -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <!-- Revenue -->
            <div class="glass rounded-xl p-6">
                <h3 class="text-gray-400 text-sm font-medium">Total Revenue (Lifetime)</h3>
                <p class="text-3xl font-bold mt-2 text-white">${shopify['total_revenue']:.2f}</p>
                <p class="text-xs text-emerald-400 mt-1">Shopify Live</p>
            </div>
            
            <!-- Cash -->
            <div class="glass rounded-xl p-6">
                <h3 class="text-gray-400 text-sm font-medium">Liquid Cash</h3>
                <p class="text-3xl font-bold mt-2 text-white">${paypal:.2f}</p>
                <p class="text-xs text-blue-400 mt-1">PayPal Balance</p>
            </div>
            
            <!-- Inventory -->
            <div class="glass rounded-xl p-6">
                <h3 class="text-gray-400 text-sm font-medium">Digital Assets</h3>
                <p class="text-3xl font-bold mt-2 text-white">{shopify['products']}</p>
                <p class="text-xs text-purple-400 mt-1">Active Products</p>
            </div>
            
            <!-- Orders -->
            <div class="glass rounded-xl p-6">
                <h3 class="text-gray-400 text-sm font-medium">Total Conversions</h3>
                <p class="text-3xl font-bold mt-2 text-white">{shopify['orders']}</p>
                <p class="text-xs text-orange-400 mt-1">Completed Sales</p>
            </div>
        </div>

        <!-- Main Chart -->
        <div class="glass rounded-xl p-6">
            <h3 class="text-gray-400 text-sm font-medium mb-4">Revenue Trend (30 Days)</h3>
            <canvas id="revenueChart" height="100"></canvas>
        </div>

        <!-- System Status -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="glass rounded-xl p-6">
                <h3 class="text-gray-400 text-sm font-medium mb-4">Core Reactor Status</h3>
                <div class="space-y-3">
                    <div class="flex justify-between">
                        <span class="text-gray-300">Synapse (Brain)</span>
                        <span class="px-2 py-1 rounded text-xs bg-emerald-500/20 text-emerald-400">{status_synapse}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-300">Shopify Store</span>
                        <span class="px-2 py-1 rounded text-xs bg-emerald-500/20 text-emerald-400">Online</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-300">Cloud Social</span>
                        <span class="px-2 py-1 rounded text-xs bg-blue-500/20 text-blue-400">{'Active' if Config.SAFETY_MODE else 'Aggressive'}</span>
                    </div>
                </div>
            </div>
            
            <div class="glass rounded-xl p-6">
                <h3 class="text-gray-400 text-sm font-medium mb-4">Latest Logs</h3>
                <div class="font-mono text-xs text-gray-400 space-y-1 h-32 overflow-y-auto bg-black/20 p-2 rounded">
                    <!-- Placeholder logs, normally read from reactor.log -->
                    <p>> [INFO] System Initialized</p>
                    <p>> [INFO] Mining Operation Started</p>
                    <p>> [INFO] Checking Finance Pulse...</p>
                    <p>> [WARN] No Opal content found</p>
                    <p>> [INFO] Traffic Operation: Scan Complete</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        const ctx = document.getElementById('revenueChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(dates)},
                datasets: [{{
                    label: 'Daily Revenue ($)',
                    data: {json.dumps(values)},
                    borderColor: '#34d399',
                    backgroundColor: 'rgba(52, 211, 153, 0.1)',
                    tension: 0.4,
                    fill: true
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
                        ticks: {{ color: '#94a3b8' }}
                    }},
                    x: {{
                        grid: {{ display: false }},
                        ticks: {{ color: '#94a3b8' }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)
        
        print(f"[Dashboard] Generated: {output_file}")

if __name__ == "__main__":
    gen = DashboardGenerator()
    gen.generate()
