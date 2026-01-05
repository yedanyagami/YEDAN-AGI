"""
YEDAN AGI - n8n Workflow Integration
Connects YEDAN to n8n for complete workflow automation
Supports triggering workflows, monitoring status, and receiving webhooks
"""
import sys
import io
import os
import json
import requests
from datetime import datetime
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Fix Windows console encoding
# Encoding fix moved to __main__ or handled by caller

load_dotenv(dotenv_path=".env.reactor")


class N8nBridge:
    """Bridge between YEDAN and n8n workflow automation"""
    
    def __init__(self, base_url: str = None):
        self.api_token = os.getenv("N8N_API_TOKEN")
        # n8n cloud or self-hosted URL
        self.base_url = base_url or os.getenv("N8N_BASE_URL", "https://yedanyagami.app.n8n.cloud/api/v1")
        self.headers = {
            "X-N8N-API-KEY": self.api_token,
            "Content-Type": "application/json"
        }
        
    def is_configured(self) -> bool:
        """Check if n8n is properly configured"""
        return bool(self.api_token)
    
    def get_workflows(self) -> List[Dict]:
        """List all workflows"""
        if not self.is_configured():
            return []
        
        try:
            r = requests.get(
                f"{self.base_url}/workflows",
                headers=self.headers,
                timeout=30
            )
            if r.status_code == 200:
                return r.json().get("data", [])
            else:
                print(f"[n8n] Error: {r.status_code} - {r.text}")
        except Exception as e:
            print(f"[n8n] Connection error: {e}")
        return []
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict]:
        """Get specific workflow details"""
        try:
            r = requests.get(
                f"{self.base_url}/workflows/{workflow_id}",
                headers=self.headers,
                timeout=30
            )
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            print(f"[n8n] Error getting workflow: {e}")
        return None
    
    def execute_workflow(self, workflow_id: str, data: Dict = None) -> Optional[Dict]:
        """Execute a workflow with optional data"""
        try:
            payload = {"workflowData": data} if data else {}
            r = requests.post(
                f"{self.base_url}/workflows/{workflow_id}/run",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            if r.status_code in [200, 201]:
                return r.json()
            else:
                print(f"[n8n] Execution error: {r.status_code} - {r.text}")
        except Exception as e:
            print(f"[n8n] Error executing workflow: {e}")
        return None
    
    def get_executions(self, workflow_id: str = None, limit: int = 10) -> List[Dict]:
        """Get workflow execution history"""
        try:
            params = {"limit": limit}
            if workflow_id:
                params["workflowId"] = workflow_id
            
            r = requests.get(
                f"{self.base_url}/executions",
                headers=self.headers,
                params=params,
                timeout=30
            )
            if r.status_code == 200:
                return r.json().get("data", [])
        except Exception as e:
            print(f"[n8n] Error getting executions: {e}")
        return []
    
    def create_webhook_node(self) -> Dict:
        """Template for creating a webhook node in n8n"""
        return {
            "name": "YEDAN Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 1,
            "position": [250, 300],
            "webhookId": "yedan-trigger",
            "parameters": {
                "httpMethod": "POST",
                "path": "yedan-trigger",
                "responseMode": "onReceived",
                "responseData": "",
            }
        }
    
    def create_shopify_workflow_template(self) -> Dict:
        """Template for YEDAN ROI Shopify workflow"""
        return {
            "name": "YEDAN ROI - Shopify Automation",
            "nodes": [
                {
                    "name": "Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "position": [250, 300],
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "yedan-shopify"
                    }
                },
                {
                    "name": "Create Product",
                    "type": "n8n-nodes-base.shopify",
                    "position": [500, 300],
                    "parameters": {
                        "operation": "create",
                        "resource": "product"
                    }
                },
                {
                    "name": "Telegram Notify",
                    "type": "n8n-nodes-base.telegram",
                    "position": [750, 300],
                    "parameters": {
                        "operation": "sendMessage",
                        "chatId": os.getenv("TELEGRAM_CHAT_ID", "")
                    }
                }
            ],
            "connections": {
                "Webhook": {"main": [[{"node": "Create Product", "type": "main", "index": 0}]]},
                "Create Product": {"main": [[{"node": "Telegram Notify", "type": "main", "index": 0}]]}
            }
        }
    
    def trigger_webhook(self, webhook_url: str, data: Dict) -> bool:
        """Trigger an n8n webhook"""
        try:
            r = requests.post(webhook_url, json=data, timeout=30)
            return r.status_code in [200, 201]
        except Exception as e:
            print(f"[n8n] Webhook error: {e}")
            return False
    
    def status_check(self) -> Dict:
        """Check n8n connection status"""
        result = {
            "configured": self.is_configured(),
            "connected": False,
            "workflows": 0,
            "error": None
        }
        
        if not result["configured"]:
            result["error"] = "N8N_API_TOKEN not set"
            return result
        
        try:
            workflows = self.get_workflows()
            result["connected"] = True
            result["workflows"] = len(workflows)
        except Exception as e:
            result["error"] = str(e)
        
        return result


class N8nSynapseIntegration:
    """Integration layer between n8n and Synapse"""
    
    def __init__(self):
        self.n8n = N8nBridge()
        self.synapse_url = "https://synapse.yagami8095.workers.dev"
    
    def sync_roi_metrics(self):
        """Sync ROI metrics from n8n to Synapse"""
        executions = self.n8n.get_executions(limit=20)
        
        success_count = sum(1 for e in executions if e.get("finished") and not e.get("stoppedAt"))
        error_count = sum(1 for e in executions if e.get("stoppedAt"))
        
        metrics = {
            "n8n_executions_today": len(executions),
            "success_rate": success_count / len(executions) if executions else 0,
            "errors": error_count,
            "last_sync": datetime.now().isoformat()
        }
        
        try:
            requests.post(
                f"{self.synapse_url}/roi/metrics",
                json=metrics,
                timeout=10
            )
            print(f"[n8n] Synced metrics: {metrics}")
        except Exception as e:
            print(f"[n8n] Sync error: {e}")
    
    def register_webhook_with_synapse(self, webhook_path: str):
        """Store n8n webhook URL in Synapse for reference"""
        try:
            requests.post(
                f"{self.synapse_url}/set/n8n_webhook",
                json={"value": webhook_path},
                timeout=10
            )
        except:
            pass


def main():
    """Test n8n connection"""
    print("=" * 60)
    print("[n8n Bridge] Testing connection...")
    print("=" * 60)
    
    bridge = N8nBridge()
    status = bridge.status_check()
    
    print(f"Configured: {status['configured']}")
    print(f"Connected: {status['connected']}")
    print(f"Workflows: {status['workflows']}")
    
    if status['error']:
        print(f"Error: {status['error']}")
    
    if status['connected']:
        print("\nWorkflows:")
        for wf in bridge.get_workflows():
            print(f"  - {wf.get('name')} (ID: {wf.get('id')})")
    
    return status


if __name__ == "__main__":
    main()
