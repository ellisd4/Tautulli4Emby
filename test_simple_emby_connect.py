#!/usr/bin/env python3
"""
Simple EmbyConnect Test
Tests the EmbyConnect class with minimal dependencies
"""
import sys
import os
import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Add the plexpy directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plexpy'))

from env_config import get_emby_config


class SimpleHTTPHandler:
    """Simplified HTTP handler for testing"""
    
    def __init__(self, base_url, api_key, timeout=30, ssl_verify=True):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.ssl_verify = ssl_verify
        
        if not ssl_verify:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    
    def make_request(self, uri, request_type='GET', output_format='dict', data=None, return_response=False):
        """Make HTTP request to Emby server"""
        url = f"{self.base_url}{uri}"
        
        headers = {
            'X-Emby-Token': self.api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            if request_type.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=self.timeout, verify=self.ssl_verify)
            elif request_type.upper() == 'POST':
                response = requests.post(url, headers=headers, data=data, timeout=self.timeout, verify=self.ssl_verify)
            else:
                raise ValueError(f"Unsupported request type: {request_type}")
            
            if return_response:
                return response
            
            if response.status_code == 200:
                if output_format == 'dict':
                    return response.json()
                elif output_format == 'json':
                    return response.text
                else:
                    return response.content
            else:
                print(f"HTTP Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"Request Error: {e}")
            return None


class SimpleEmbyConnect:
    """Simplified EmbyConnect for testing"""
    
    def __init__(self):
        config = get_emby_config()
        self.request_handler = SimpleHTTPHandler(
            base_url=config['url'],
            api_key=config['api_key'],
            timeout=config['timeout'],
            ssl_verify=config['ssl_verify']
        )
    
    def get_sessions(self, output_format='dict'):
        """Get active sessions"""
        return self.request_handler.make_request('/Sessions', output_format=output_format)
    
    def get_server_info(self, output_format='dict'):
        """Get server information"""
        return self.request_handler.make_request('/System/Info', output_format=output_format)
    
    def get_server_info_public(self, output_format='dict'):
        """Get public server information"""
        return self.request_handler.make_request('/System/Info/Public', output_format=output_format)
    
    def get_users_list(self, output_format='dict'):
        """Get users list"""
        return self.request_handler.make_request('/Users/Query', output_format=output_format)
    
    def get_libraries_list(self, output_format='dict'):
        """Get libraries list"""
        return self.request_handler.make_request('/Library/VirtualFolders', output_format=output_format)
    
    def get_current_activity(self):
        """Get current activity in Tautulli format"""
        sessions = self.get_sessions()
        if not sessions:
            return {'stream_count': '0', 'sessions': []}
        
        # Filter only active playback sessions
        active_sessions = [s for s in sessions if s.get('NowPlayingItem')]
        
        return {
            'stream_count': str(len(active_sessions)),
            'sessions': active_sessions  # Simplified - would normally transform data
        }


def test_simple_emby_connect():
    """Test simplified EmbyConnect"""
    print("="*80)
    print("SIMPLE EMBY CONNECT TEST")
    print("="*80)
    
    emby = SimpleEmbyConnect()
    
    # Test 1: Server Info
    print("Test 1: Server Information")
    try:
        server_info = emby.get_server_info()
        if server_info:
            print(f"✅ Server Name: {server_info.get('ServerName', 'Unknown')}")
            print(f"   Version: {server_info.get('Version', 'Unknown')}")
            print(f"   OS: {server_info.get('OperatingSystem', 'Unknown')}")
        else:
            print("❌ Failed to get server info")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 2: Public Server Info
    print("Test 2: Public Server Information")
    try:
        public_info = emby.get_server_info_public()
        if public_info:
            print(f"✅ Public Server Name: {public_info.get('ServerName', 'Unknown')}")
            print(f"   Product: {public_info.get('ProductName', 'Unknown')}")
            print(f"   Version: {public_info.get('Version', 'Unknown')}")
        else:
            print("❌ Failed to get public server info")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 3: Active Sessions
    print("Test 3: Active Sessions")
    try:
        sessions = emby.get_sessions()
        if sessions:
            active_sessions = [s for s in sessions if s.get('NowPlayingItem')]
            print(f"✅ Total Sessions: {len(sessions)}")
            print(f"   Active Playback: {len(active_sessions)}")
            
            for session in active_sessions[:3]:  # Show first 3
                user = session.get('UserName', 'Unknown')
                client = session.get('Client', 'Unknown')
                device = session.get('DeviceName', 'Unknown')
                item = session.get('NowPlayingItem', {})
                title = item.get('Name', 'Unknown')
                media_type = item.get('Type', 'Unknown')
                print(f"   • {user} on {client} ({device})")
                print(f"     Playing: {title} ({media_type})")
        else:
            print("❌ Failed to get sessions")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 4: Current Activity (Tautulli Format)
    print("Test 4: Current Activity (Tautulli Format)")
    try:
        activity = emby.get_current_activity()
        print(f"✅ Stream Count: {activity['stream_count']}")
        print(f"   Sessions: {len(activity['sessions'])}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 5: Users
    print("Test 5: Users List")
    try:
        users_data = emby.get_users_list()
        if users_data:
            users = users_data.get('Items', [])
            print(f"✅ Users Found: {len(users)}")
            for user in users[:5]:  # Show first 5
                name = user.get('Name', 'Unknown')
                user_id = user.get('Id', 'Unknown')[:8] + '...'  # Truncate ID
                is_admin = user.get('Policy', {}).get('IsAdministrator', False)
                print(f"   • {name} (ID: {user_id}) {'[Admin]' if is_admin else ''}")
        else:
            print("❌ Failed to get users")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 6: Libraries
    print("Test 6: Libraries List")
    try:
        libraries = emby.get_libraries_list()
        if libraries:
            print(f"✅ Libraries Found: {len(libraries)}")
            for library in libraries[:5]:  # Show first 5
                name = library.get('Name', 'Unknown')
                lib_type = library.get('CollectionType', 'mixed')
                item_id = library.get('ItemId', 'Unknown')[:8] + '..'
                print(f"   • {name} (Type: {lib_type}, ID: {item_id})")
        else:
            print("❌ Failed to get libraries")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("="*80)
    print("✅ SIMPLE EMBY CONNECT TEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    test_simple_emby_connect()