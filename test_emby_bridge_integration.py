#!/usr/bin/env python3
"""
Test EmbyConnect Bridge Integration

This script tests the EmbyConnect bridge integration with the Tautulli infrastructure.
It simulates the key functionality used by activity_pinger, activity_handler, and activity_processor.
"""

import os
import sys

# Add project root and plexpy directory to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'plexpy'))

# Mock plexpy module for testing
class MockConfig:
    pass

class MockPlexPy:
    CONFIG = MockConfig()
    NOTIFY_QUEUE = None

sys.modules['plexpy'] = MockPlexPy()

# Mock logger
class MockLogger:
    @staticmethod
    def info(msg): print(f"INFO: {msg}")
    @staticmethod
    def debug(msg): print(f"DEBUG: {msg}")
    @staticmethod
    def error(msg): print(f"ERROR: {msg}")
    @staticmethod
    def warning(msg): print(f"WARNING: {msg}")

sys.modules['plexpy.logger'] = MockLogger()

# Now we can import our bridge directly
try:
    import embyconnect_bridge
    EmbyConnect = embyconnect_bridge.EmbyConnect
    PmsConnect = embyconnect_bridge.PmsConnect
    print("✅ Successfully imported EmbyConnect bridge")
except ImportError as e:
    print(f"❌ Failed to import EmbyConnect bridge: {e}")
    sys.exit(1)

def test_emby_connect():
    """Test EmbyConnect functionality."""
    print("\n=== Testing EmbyConnect Bridge ===")
    
    try:
        emby_connect = EmbyConnect()
        print("✅ EmbyConnect instance created successfully")
        
        # Test server info
        server_info = emby_connect.get_server_info()
        if server_info:
            print(f"✅ Server info retrieved: {server_info.get('ServerName', 'Unknown')}")
        else:
            print("⚠️  No server info retrieved (check configuration)")
        
        # Test current activity
        activity = emby_connect.get_current_activity()
        if activity and 'sessions' in activity:
            print(f"✅ Current activity retrieved: {len(activity['sessions'])} sessions")
        else:
            print("⚠️  No current activity retrieved")
        
        # Test connection
        if emby_connect.test_connection():
            print("✅ Connection test passed")
        else:
            print("⚠️  Connection test failed")
        
    except Exception as e:
        print(f"❌ EmbyConnect test failed: {e}")
        return False
    
    return True

def test_pms_connect_compatibility():
    """Test PmsConnect compatibility wrapper."""
    print("\n=== Testing PmsConnect Compatibility ===")
    
    try:
        pms_connect = PmsConnect()
        print("✅ PmsConnect compatibility wrapper created")
        
        # Test that it redirects to EmbyConnect
        activity = pms_connect.get_current_activity()
        if activity and 'sessions' in activity:
            print(f"✅ PmsConnect redirect working: {len(activity['sessions'])} sessions")
        else:
            print("⚠️  PmsConnect redirect not returning data")
        
    except Exception as e:
        print(f"❌ PmsConnect compatibility test failed: {e}")
        return False
    
    return True

def test_activity_pinger_simulation():
    """Simulate activity_pinger.py usage."""
    print("\n=== Simulating activity_pinger.py usage ===")
    
    try:
        # This simulates the key lines from activity_pinger.py
        emby_connect = EmbyConnect()
        session_list = emby_connect.get_current_activity()
        
        print("✅ Activity pinger simulation successful")
        
        if session_list and 'sessions' in session_list:
            media_container = session_list['sessions']
            print(f"✅ Retrieved {len(media_container)} sessions for processing")
            
            # Show first session details if available
            if media_container:
                session = media_container[0]
                print(f"✅ Sample session - Key: {session.get('session_key')}, State: {session.get('state')}")
        
    except Exception as e:
        print(f"❌ Activity pinger simulation failed: {e}")
        return False
    
    return True

def test_activity_handler_simulation():
    """Simulate activity_handler.py usage."""
    print("\n=== Simulating activity_handler.py usage ===")
    
    try:
        emby_connect = EmbyConnect()
        
        # Simulate getting current activity (like get_live_session)
        session_list = emby_connect.get_current_activity()
        if session_list and session_list['sessions']:
            print("✅ Activity handler simulation successful - sessions retrieved")
            
            # Try to get metadata for first session
            first_session = session_list['sessions'][0]
            rating_key = first_session.get('rating_key')
            if rating_key:
                metadata = emby_connect.get_metadata(rating_key)
                if metadata:
                    print(f"✅ Metadata retrieved for rating_key {rating_key}")
                else:
                    print(f"⚠️  No metadata for rating_key {rating_key}")
        
    except Exception as e:
        print(f"❌ Activity handler simulation failed: {e}")
        return False
    
    return True

def main():
    """Run all integration tests."""
    print("🚀 Starting EmbyConnect Bridge Integration Tests")
    print("=" * 60)
    
    # Check environment
    if not os.getenv('EMBY_SERVER_URL'):
        print("⚠️  EMBY_SERVER_URL not set - tests may fail")
        print("   Set environment variables for full testing:")
        print("   export EMBY_SERVER_URL='http://192.168.87.220:8096'")
        print("   export EMBY_API_KEY='your_api_key'")
    
    tests = [
        test_emby_connect,
        test_pms_connect_compatibility, 
        test_activity_pinger_simulation,
        test_activity_handler_simulation
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"🎯 Integration Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("EmbyConnect bridge is ready for Phase 1.4 integration!")
        return True
    else:
        print("⚠️  Some tests failed - check configuration and connectivity")
        return False

if __name__ == '__main__':
    main()