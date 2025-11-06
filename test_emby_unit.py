#!/usr/bin/env python3
"""
EmbyConnect Unit Tests
Basic unit tests for the EmbyConnect class
"""
import unittest
import sys
import os

# Add the plexpy directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plexpy'))

from env_config import get_emby_config


class TestEmbyConnect(unittest.TestCase):
    """Unit tests for EmbyConnect class"""
    
    def setUp(self):
        """Set up test environment"""
        self.config = get_emby_config()
        
        # Skip tests if API key is not configured
        if not self.config['api_key'] or self.config['api_key'] == 'your_api_key_here':
            self.skipTest("API key not configured")
    
    def test_config_loading(self):
        """Test that configuration loads correctly"""
        self.assertIsNotNone(self.config['url'])
        self.assertIsNotNone(self.config['api_key'])
        self.assertIsInstance(self.config['timeout'], int)
        self.assertIsInstance(self.config['ssl_verify'], bool)
    
    def test_server_connectivity(self):
        """Test basic server connectivity"""
        import requests
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        
        if not self.config['ssl_verify']:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        
        # Test public endpoint (no auth needed)
        response = requests.get(
            f"{self.config['url']}/System/Info/Public",
            timeout=self.config['timeout'],
            verify=self.config['ssl_verify']
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('ServerName', data)
        self.assertIn('Version', data)
    
    def test_api_authentication(self):
        """Test API authentication"""
        import requests
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        
        if not self.config['ssl_verify']:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        
        headers = {'X-Emby-Token': self.config['api_key']}
        
        response = requests.get(
            f"{self.config['url']}/System/Info",
            headers=headers,
            timeout=self.config['timeout'],
            verify=self.config['ssl_verify']
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('ServerName', data)
        self.assertIn('Version', data)
    
    def test_sessions_endpoint(self):
        """Test sessions endpoint"""
        import requests
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        
        if not self.config['ssl_verify']:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        
        headers = {'X-Emby-Token': self.config['api_key']}
        
        response = requests.get(
            f"{self.config['url']}/Sessions",
            headers=headers,
            timeout=self.config['timeout'],
            verify=self.config['ssl_verify']
        )
        
        self.assertEqual(response.status_code, 200)
        sessions = response.json()
        self.assertIsInstance(sessions, list)


if __name__ == '__main__':
    # Create a test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEmbyConnect)
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    print("="*60)