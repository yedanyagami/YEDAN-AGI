import unittest
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestReactorDryRun(unittest.TestCase):
    def test_imports(self):
        """Simple test to ensure all modules can be imported without syntax errors"""
        try:
            from modules.reddit_monitor import RedditMonitor
            from modules.twitter_monitor import TwitterMonitor
            from modules.r1_reasoner import DeepSeekReasoner
            from modules.safety_guard import SafetyGuard
            from modules.analytics import Analytics
            from modules.utils import setup_logger
            print("\n✅ All modules imported successfully.")
        except ImportError as e:
            self.fail(f"Import failed: {e}")

    def test_config_load(self):
        """Test if config file is valid JSON"""
        import json
        try:
            with open("config/keywords.json", "r") as f:
                data = json.load(f)
            self.assertIn("reddit", data)
            self.assertIn("twitter", data)
            print("\n✅ Config file is valid JSON.")
        except Exception as e:
            self.fail(f"Config load failed: {e}")

if __name__ == '__main__':
    unittest.main()
