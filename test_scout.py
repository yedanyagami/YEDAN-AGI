"""
Test Scout Agent
Verifies lightweight scanning capabilities.
"""
from modules.scout_agent import ScoutAgent

def test_scout():
    print("="*60)
    print("Scout Agent (Low Token Mode)")
    print("="*60)
    
    scout = ScoutAgent()
    
    # Test on a real e-com site (or a safe target)
    # Using a generic tech site or documentation as proxy
    target_url = "https://www.python.org/" 
    
    print(f"[Target] {target_url}")
    
    result = scout.quick_scan_url(target_url)
    
    print(f"\n[Result] Title: {result.get('title')}")
    print(f"[Result] Desc: {result.get('description')}")
    print(f"[Result] Headers: {result.get('top_headers')}")
    print(f"[Result] Cost: ${result.get('token_cost')}")
    print("="*60)

if __name__ == "__main__":
    test_scout()
