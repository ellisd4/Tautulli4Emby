#!/usr/bin/env python3
"""
Test EmbyConnect Class
Tests the new EmbyConnect class methods and compatibility with existing Tautulli infrastructure
"""
import sys
import os
import json

# Add the plexpy directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plexpy'))

from embyconnect import EmbyConnect
from env_config import get_emby_config


def test_emby_connect():
    """Test EmbyConnect class functionality"""
    print("="*80)
    print("EMBY CONNECT CLASS TEST")
    print("="*80)
    
    # Load configuration
    config = get_emby_config()
    
    print(f"Testing EmbyConnect with server: {config['url']}")
    print("-"*80)
    
    # Initialize EmbyConnect
    emby = EmbyConnect()
    
    # Test 1: Server Information
    print("Test 1: Server Information")
    try:
        server_info = emby.get_server_info(output_format='dict')
        print(f"✅ Server Info Retrieved:")
        print(f"   Server Name: {server_info.get('ServerName', 'Unknown')}")
        print(f"   Version: {server_info.get('Version', 'Unknown')}")
        print(f"   Operating System: {server_info.get('OperatingSystem', 'Unknown')}")
    except Exception as e:
        print(f"❌ Server Info Error: {e}")
    
    print()
    
    # Test 2: Server Identity (compatibility method)
    print("Test 2: Server Identity (Compatibility)")
    try:
        identity = emby.get_server_identity()
        print(f"✅ Server Identity Retrieved:")
        print(f"   Machine ID: {identity.get('machine_identifier', 'Unknown')}")
        print(f"   Server Name: {identity.get('server_name', 'Unknown')}")
        print(f"   Version: {identity.get('version', 'Unknown')}")
        print(f"   Product: {identity.get('product_name', 'Unknown')}")
    except Exception as e:
        print(f"❌ Server Identity Error: {e}")
    
    print()
    
    # Test 3: Sessions
    print("Test 3: Active Sessions")
    try:
        sessions = emby.get_sessions(output_format='dict')
        print(f"✅ Sessions Retrieved: {len(sessions)} total sessions")
        
        # Count active playback sessions
        active_count = len([s for s in sessions if s.get('NowPlayingItem')])
        print(f"   Active Playback Sessions: {active_count}")
        
        if active_count > 0:
            print("   Active Sessions:")
            for session in sessions:
                if session.get('NowPlayingItem'):
                    user = session.get('UserName', 'Unknown')
                    client = session.get('Client', 'Unknown')
                    device = session.get('DeviceName', 'Unknown')
                    item = session.get('NowPlayingItem', {})
                    title = item.get('Name', 'Unknown')
                    print(f"     • {user} on {client} ({device}) - {title}")
        
    except Exception as e:
        print(f"❌ Sessions Error: {e}")
    
    print()
    
    # Test 4: Current Activity (Tautulli format)
    print("Test 4: Current Activity (Tautulli Format)")
    try:
        activity = emby.get_current_activity()
        stream_count = activity.get('stream_count', '0')
        sessions_list = activity.get('sessions', [])
        
        print(f"✅ Current Activity Retrieved:")
        print(f"   Stream Count: {stream_count}")
        print(f"   Sessions: {len(sessions_list)}")
        
        if int(stream_count) > 0:
            print("   Active Sessions (Tautulli Format):")
            for session in sessions_list[:3]:  # Show first 3
                print(f"     • Session data available: {bool(session)}")
                
    except Exception as e:
        print(f"❌ Current Activity Error: {e}")
    
    print()
    
    # Test 5: Users List
    print("Test 5: Users List")
    try:
        users = emby.get_users_list(output_format='dict')
        print(f"✅ Users Retrieved: {len(users.get('Items', []))} users")
        
        for user in users.get('Items', [])[:5]:  # Show first 5 users
            name = user.get('Name', 'Unknown')
            user_id = user.get('Id', 'Unknown')
            print(f"   • {name} (ID: {user_id})")
            
    except Exception as e:
        print(f"❌ Users List Error: {e}")
    
    print()
    
    # Test 6: Libraries List
    print("Test 6: Libraries List")
    try:
        libraries = emby.get_libraries_list(output_format='dict')
        print(f"✅ Libraries Retrieved: {len(libraries)} libraries")
        
        for library in libraries[:5]:  # Show first 5 libraries
            name = library.get('Name', 'Unknown')
            library_type = library.get('CollectionType', 'Unknown')
            print(f"   • {name} (Type: {library_type})")
            
    except Exception as e:
        print(f"❌ Libraries List Error: {e}")
    
    print()
    
    # Test 7: Server Friendly Name
    print("Test 7: Server Friendly Name")
    try:
        friendly_name = emby.get_server_friendly_name()
        print(f"✅ Server Friendly Name: {friendly_name}")
    except Exception as e:
        print(f"❌ Server Friendly Name Error: {e}")
    
    print()
    print("="*80)
    print("EMBY CONNECT CLASS TEST COMPLETE")
    print("="*80)


if __name__ == "__main__":
    test_emby_connect()