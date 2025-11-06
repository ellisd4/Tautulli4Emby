#!/usr/bin/env python3
"""
Emby Server Connectivity Test
Tests basic connection and API access to Emby server
"""
import sys
import os
import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Add the plexpy directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plexpy'))

from env_config import get_emby_config


def test_emby_connection():
    """Test connection to Emby server and API functionality"""
    print("="*60)
    print("EMBY SERVER CONNECTIVITY TEST")
    print("="*60)
    
    # Load configuration
    config = get_emby_config()
    
    print(f"Testing connection to: {config['url']}")
    print(f"SSL Verification: {'Enabled' if config['ssl_verify'] else 'Disabled'}")
    print(f"Timeout: {config['timeout']}s")
    print("-"*60)
    
    # Disable SSL warnings if SSL verification is disabled
    if not config['ssl_verify']:
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    
    # Test 1: Basic connectivity
    print("Test 1: Basic Server Connectivity")
    try:
        response = requests.get(
            f"{config['url']}/System/Info/Public",
            timeout=config['timeout'],
            verify=config['ssl_verify']
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is reachable")
            print(f"   Server Name: {data.get('ServerName', 'Unknown')}")
            print(f"   Version: {data.get('Version', 'Unknown')}")
            print(f"   Product Name: {data.get('ProductName', 'Unknown')}")
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Connection timeout after {config['timeout']}s")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server at {config['url']}")
        print("   Check if the server is running and the URL is correct")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    print()
    
    # Test 2: API Key Authentication
    print("Test 2: API Key Authentication")
    
    if not config['api_key'] or config['api_key'] == 'your_api_key_here':
        print("❌ API key not configured")
        print("   Please add your API key to the .env file")
        print("   Generate one at: Settings → API Keys in Emby web interface")
        return False
    
    try:
        headers = {
            'X-Emby-Token': config['api_key']
        }
        
        response = requests.get(
            f"{config['url']}/System/Info",
            headers=headers,
            timeout=config['timeout'],
            verify=config['ssl_verify']
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API authentication successful")
            print(f"   Server Name: {data.get('ServerName', 'Unknown')}")
            print(f"   Operating System: {data.get('OperatingSystem', 'Unknown')}")
            print(f"   Has Pending Restart: {data.get('HasPendingRestart', False)}")
        elif response.status_code == 401:
            print("❌ API key authentication failed")
            print("   Check if the API key is correct and active")
            return False
        else:
            print(f"❌ API request failed with status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False
    
    print()
    
    # Test 3: Sessions Endpoint (Core functionality)
    print("Test 3: Sessions Endpoint Access")
    try:
        response = requests.get(
            f"{config['url']}/Sessions",
            headers={'X-Emby-Token': config['api_key']},
            timeout=config['timeout'],
            verify=config['ssl_verify']
        )
        
        if response.status_code == 200:
            sessions = response.json()
            print(f"✅ Sessions endpoint accessible")
            print(f"   Active sessions: {len(sessions)}")
            
            if sessions:
                print("   Current sessions:")
                for i, session in enumerate(sessions[:3]):  # Show first 3 sessions
                    user_name = session.get('UserName', 'Unknown')
                    client = session.get('Client', 'Unknown')
                    device = session.get('DeviceName', 'Unknown')
                    print(f"     {i+1}. {user_name} on {client} ({device})")
            else:
                print("   No active sessions")
        else:
            print(f"❌ Sessions endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Sessions test error: {e}")
        return False
    
    print()
    print("="*60)
    print("✅ ALL TESTS PASSED - Emby server is ready for development!")
    print("="*60)
    return True


if __name__ == "__main__":
    success = test_emby_connection()
    sys.exit(0 if success else 1)