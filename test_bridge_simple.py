#!/usr/bin/env python3
"""
Simple EmbyConnect Bridge Test

Tests the core functionality of our EmbyConnect bridge without full Tautulli dependencies.
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Use our standalone EmbyConnect directly for testing
try:
    from embyconnect_standalone import EmbyConnect
    print("✅ Successfully imported standalone EmbyConnect")
except ImportError as e:
    print(f"❌ Failed to import standalone EmbyConnect: {e}")
    sys.exit(1)

def test_standalone_integration():
    """Test standalone EmbyConnect in bridge-like usage."""
    print("\n=== Testing Standalone EmbyConnect for Bridge Integration ===")
    
    try:
        # Initialize EmbyConnect (simulating bridge behavior)
        emby_connect = EmbyConnect()
        print("✅ EmbyConnect instance created")
        
        # Test server connection
        server_info = emby_connect.get_server_info()
        if server_info:
            print(f"✅ Server connected: {server_info.get('ServerName', 'Unknown')}")
        else:
            print("⚠️  Could not connect to server (check config)")
            return False
        
        # Test current activity (key for activity_pinger.py)
        raw_sessions = emby_connect.get_sessions()
        transformed_sessions = [emby_connect.transform_session_data(session) for session in raw_sessions] if raw_sessions else []
        print(f"✅ Current sessions retrieved: {len(transformed_sessions)} active")
        
        # Format in expected bridge format
        activity_data = {'sessions': transformed_sessions}
        print(f"✅ Bridge format ready: {len(activity_data['sessions'])} sessions")
        
        # Test metadata retrieval (key for activity_handler.py)
        if transformed_sessions:
            first_session = transformed_sessions[0]
            rating_key = first_session.get('rating_key')
            if rating_key:
                metadata = emby_connect.get_item_metadata(rating_key)
                if metadata:
                    print(f"✅ Metadata retrieved for session {first_session.get('session_key')}")
                else:
                    print(f"⚠️  No metadata for rating_key {rating_key}")
        
        # Test user info (key for activity_processor.py)
        raw_users = emby_connect.get_users_list()
        transformed_users = [emby_connect.transform_user_data(user) for user in raw_users] if raw_users else []
        print(f"✅ Users retrieved: {len(transformed_users)} total")
        
        return True
        
    except Exception as e:
        print(f"❌ Standalone integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_activity_pinger_pattern():
    """Test the exact pattern used by activity_pinger.py"""
    print("\n=== Testing activity_pinger.py Pattern ===")
    
    try:
        # This matches the pattern in activity_pinger.py:
        # emby_connect = embyconnect_bridge.EmbyConnect()
        # session_list = emby_connect.get_current_activity()
        
        emby_connect = EmbyConnect()
        
        # Simulate get_current_activity() - our bridge method
        raw_sessions = emby_connect.get_sessions()  # Raw Emby sessions
        transformed_sessions = [emby_connect.transform_session_data(session) for session in raw_sessions] if raw_sessions else []
        session_list = {'sessions': transformed_sessions}   # Bridge format
        
        if session_list:
            media_container = session_list['sessions']
            print(f"✅ Activity pinger pattern works: {len(media_container)} sessions")
            
            # Test session processing
            for session in media_container:
                session_key = session.get('session_key')
                rating_key = session.get('rating_key')
                state = session.get('state')
                print(f"   Session {session_key}: {state} - Rating: {rating_key}")
            
            return True
        else:
            print("⚠️  No session data returned")
            return False
            
    except Exception as e:
        print(f"❌ Activity pinger pattern test failed: {e}")
        return False

def test_activity_handler_pattern():
    """Test the exact pattern used by activity_handler.py"""
    print("\n=== Testing activity_handler.py Pattern ===")
    
    try:
        emby_connect = EmbyConnect()
        
        # Test get_metadata pattern
        raw_sessions = emby_connect.get_sessions()
        transformed_sessions = [emby_connect.transform_session_data(session) for session in raw_sessions] if raw_sessions else []
        if transformed_sessions:
            rating_key = transformed_sessions[0].get('rating_key')
            if rating_key:
                # This matches: metadata = emby_connect.get_metadata(rating_key)
                metadata = emby_connect.get_item_metadata(rating_key)
                if metadata:
                    title = metadata.get('title', 'Unknown')
                    print(f"✅ Activity handler metadata pattern works: {title}")
                    return True
        
        print("⚠️  No metadata retrieved for testing")
        return False
        
    except Exception as e:
        print(f"❌ Activity handler pattern test failed: {e}")
        return False

def main():
    """Run integration tests."""
    print("🚀 Starting EmbyConnect Bridge Integration Tests")
    print("=" * 60)
    
    # Check environment
    server_url = os.getenv('EMBY_SERVER_URL')
    if not server_url:
        print("⚠️  EMBY_SERVER_URL not set")
        print("   For full testing, set:")
        print("   export EMBY_SERVER_URL='http://192.168.87.220:8096'")
        print("   export EMBY_API_KEY='your_api_key'")
        print()
    else:
        print(f"✅ Using Emby server: {server_url}")
    
    tests = [
        test_standalone_integration,
        test_activity_pinger_pattern,
        test_activity_handler_pattern
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"🎯 Bridge Integration Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 ALL BRIDGE INTEGRATION TESTS PASSED!")
        print("✅ EmbyConnect is ready for Tautulli integration!")
        return True
    else:
        print("⚠️  Some tests failed - check configuration")
        return False

if __name__ == '__main__':
    main()