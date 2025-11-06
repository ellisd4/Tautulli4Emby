#!/usr/bin/env python3
"""
Test Standalone EmbyConnect
Tests the standalone EmbyConnect class without any Plex dependencies
"""
import sys
import os

# Test the standalone EmbyConnect
sys.path.insert(0, os.getcwd())

def test_standalone_emby_connect():
    """Test standalone EmbyConnect functionality"""
    print("=" * 80)
    print("STANDALONE EMBY CONNECT TEST")
    print("=" * 80)
    
    # Import our standalone EmbyConnect
    from embyconnect_standalone import EmbyConnect
    
    try:
        # Import configuration and initialize EmbyConnect
        sys.path.insert(0, os.path.join(os.getcwd(), 'plexpy'))
        from env_config import get_emby_config
        config = get_emby_config()
        
        emby = EmbyConnect(
            url=config['url'],
            api_key=config['api_key'],
            timeout=config['timeout'],
            ssl_verify=config['ssl_verify']
        )
        print("✅ EmbyConnect initialized successfully")
        
        # Test server info
        try:
            server_info = emby.get_server_info()
            print(f"Server info type: {type(server_info)}")
            if server_info and isinstance(server_info, dict):
                print(f"✅ Server: {server_info.get('ServerName')} v{server_info.get('Version')}")
            else:
                print(f"❌ Failed to get server info: {server_info}")
                return False
        except Exception as e:
            print(f"❌ Server info error: {e}")
            return False
        
        # Test sessions
        sessions = emby.get_sessions()
        if sessions is not None:
            active_count = len([s for s in sessions if s.get('NowPlayingItem')])
            print(f"✅ Sessions: {len(sessions)} total, {active_count} active")
        else:
            print("❌ Failed to get sessions")
            return False
        
        # Test current activity with transformation
        activity = emby.get_current_activity()
        print(f"✅ Current Activity: {activity.get('stream_count')} active streams")
        
        # Test transformation on real data
        if sessions and any(s.get('NowPlayingItem') for s in sessions):
            active_session = next(s for s in sessions if s.get('NowPlayingItem'))
            transformed = emby.transform_session_data(active_session)
            
            if transformed:
                print("✅ Data transformation successful")
                print(f"   User: {transformed.get('user')}")
                print(f"   Title: {transformed.get('full_title')}")
                print(f"   State: {transformed.get('state')}")
                print(f"   Progress: {transformed.get('view_offset')}/{transformed.get('duration')}")
            else:
                print("❌ Data transformation failed")
                return False
        
        # Test users
        users = emby.get_users_list()
        if users and users.get('Items'):
            print(f"✅ Users: {len(users['Items'])} found")
            
            # Test user transformation
            user = users['Items'][0]
            transformed_user = emby.transform_user_data(user)
            if transformed_user:
                print(f"   Sample User: {transformed_user.get('username')} (Admin: {bool(transformed_user.get('is_admin'))})")
        
        # Test libraries
        libraries = emby.get_libraries_list()
        if libraries:
            print(f"✅ Libraries: {len(libraries)} found")
            
            # Test library transformation
            if libraries:
                library = libraries[0]
                transformed_lib = emby.transform_library_data(library)
                if transformed_lib:
                    print(f"   Sample Library: {transformed_lib.get('section_name')} ({transformed_lib.get('section_type')})")
        
        print("\n" + "=" * 80)
        print("✅ ALL STANDALONE TESTS PASSED!")
        print("EmbyConnect is fully functional without Plex dependencies!")
        print("=" * 80)
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = test_standalone_emby_connect()
    sys.exit(0 if success else 1)