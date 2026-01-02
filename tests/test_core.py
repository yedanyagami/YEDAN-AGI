"""
YEDAN Test Suite
Basic tests to verify module imports and initialization.
"""
import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all modules can be imported"""
    from modules.safety_guard import SafetyGuard
    from modules.pydantic_models import HiveAction, SensorResult
    assert SafetyGuard is not None
    assert HiveAction is not None

def test_safety_guard_init():
    """Test SafetyGuard V1700 initialization"""
    from modules.safety_guard import SafetyGuard
    guard = SafetyGuard()
    assert guard.promo_count == 0
    assert guard.value_post_count == 1  # V1700 starts at 1

def test_safety_guard_self_healing():
    """Test SafetyGuard auto-recovery at 50% ratio"""
    from modules.safety_guard import SafetyGuard
    guard = SafetyGuard()
    
    # Simulate high promo ratio
    guard.promo_count = 10
    guard.value_post_count = 1
    
    # Should self-heal
    result = guard.validate_promo_ratio()
    assert result == True  # V1700 always returns True after self-heal
    assert guard.value_post_count > 1  # Should have added value posts

def test_pydantic_models():
    """Test Pydantic model creation"""
    from modules.pydantic_models import SensorResult, HiveAction, MimicryConfig
    
    result = SensorResult(
        thread_id="test_123",
        title="Test Post",
        body_markdown="Test body",
        author="TestUser",
        panic_score=5,
        keywords_matched=["test"]
    )
    assert result.thread_id == "test_123"
    assert result.panic_score == 5

def test_config_loading():
    """Test config file exists and is valid JSON"""
    import json
    with open("config/keywords.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    assert "reddit" in config or "twitter" in config
