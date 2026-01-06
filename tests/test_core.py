import unittest
import os
import sys
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.config import Config
from modules.watchdog import Watchdog
from modules.cloud_social import CloudSocialAgent

class TestCoreSystem(unittest.TestCase):
    
    def test_config_loading(self):
        """Test if Config loads sensitive variables (mocked if missing)"""
        # We assume .env.reactor exists in the user's environment or is loaded
        # Even if empty, attributes should exist on the class
        self.assertTrue(hasattr(Config, 'SYNAPSE_URL'))
        self.assertTrue(hasattr(Config, 'SHOPIFY_ADMIN_TOKEN'))
        print(f"\n[Test] Config Loaded. Synapse URL: {Config.SYNAPSE_URL}")

    @patch('requests.post')
    def test_watchdog_synapse_check(self, mock_post):
        """Test Watchdog's ability to check Synapse"""
        mock_post.return_value.status_code = 200
        dog = Watchdog()
        alive, msg = dog.check_synapse()
        self.assertTrue(alive)
        self.assertEqual(msg, "Online")

    def test_cloud_social_instantiation(self):
        """Test CloudSocialAgent init"""
        agent = CloudSocialAgent()
        self.assertIsNotNone(agent.token)
        # We don't call external APIs here, just check setup

if __name__ == '__main__':
    unittest.main()
