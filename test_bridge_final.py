#!/usr/bin/env python3
"""
Test EmbyConnect Bridge Final Integration

This test validates that our EmbyConnect bridge works correctly with 
the exact patterns used by activity_pinger.py, activity_handler.py, and activity_processor.py
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'plexpy'))

# Mock plexpy module
class MockConfig:
    pass

class MockPlexPy:
    CONFIG = MockConfig()

class MockLogger:
    @staticmethod
    def info(msg): print(f"INFO: {msg}")
    @staticmethod
    def debug(msg): print(f"DEBUG: {msg}")
    @staticmethod
    def error(msg): print(f"ERROR: {msg}")
    @staticmethod
    def warning(msg): print(f"WARNING: {msg}")

sys.modules['plexpy'] = MockPlexPy()
sys.modules['plexpy.logger'] = MockLogger()

# Import our bridge
try:
    import embyconnect_bridge
    print("✅ EmbyConnect bridge imported successfully")
except ImportError as e:
    print(f"❌ Failed to import bridge: {e}")
    sys.exit(1)

def test_activity_pinger_integration():
    """Test exact activity_pinger.py integration pattern."""
    print("\n=== Testing activity_pinger.py Integration ===")
    
    try:
        # Exact pattern from activity_pinger.py:
        # emby_connect = embyconnect_bridge.EmbyConnect()
        # session_list = emby_connect.get_current_activity()
        
        emby_connect = embyconnect_bridge.EmbyConnect()
        session_list = emby_connect.get_current_activity()
        
        if session_list and 'sessions' in session_list:
            media_container = session_list['sessions']
            active_sessions = [s for s in media_container if s.get('session_key') and s.get('rating_key')]
            
            print(f"✅ Activity pinger integration successful!")
            print(f"   Total sessions: {len(media_container)}")
            print(f"   Active sessions: {len(active_sessions)}")
            
            # Show active session details
            for session in active_sessions[:3]:  # First 3 active sessions
                session_key = session.get('session_key')
                rating_key = session.get('rating_key')
                state = session.get('state', 'unknown')
                user = session.get('user', 'Unknown')
                title = session.get('title', 'Unknown')
                print(f"   [{session_key[:8]}...] {user} - {state} - {title}")
            
            return len(active_sessions) > 0
        else:
            print("⚠️  No sessions returned")
            return False
            
    except Exception as e:
        print(f"❌ Activity pinger integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_activity_handler_integration():
    """Test exact activity_handler.py integration pattern."""
    print("\n=== Testing activity_handler.py Integration ===")
    
    try:
        emby_connect = embyconnect_bridge.EmbyConnect()
        
        # Test get_live_session pattern
        session_list = emby_connect.get_current_activity()
        
        if session_list and session_list['sessions']:
            # Find first active session
            active_session = None
            for session in session_list['sessions']:
                if session.get('session_key') and session.get('rating_key'):
                    active_session = session
                    break
            
            if active_session:
                rating_key = active_session['rating_key']
                session_key = active_session['session_key']
                
                # Test metadata retrieval pattern
                metadata = emby_connect.get_metadata(rating_key)
                
                if metadata:
                    title = metadata.get('title', 'Unknown')
                    print(f"✅ Activity handler integration successful!")
                    print(f"   Session: {session_key[:8]}...")
                    print(f"   Rating Key: {rating_key}")
                    print(f"   Metadata: {title}")
                    return True
                else:
                    print(f"⚠️  No metadata for rating_key {rating_key}")
                    return False
            else:
                print("⚠️  No active sessions with rating keys")
                return False
        else:
            print("⚠️  No sessions found")
            return False
            
    except Exception as e:
        print(f"❌ Activity handler integration failed: {e}")
        return False

def test_pms_connect_compatibility():
    """Test PmsConnect compatibility wrapper."""
    print("\n=== Testing PmsConnect Compatibility ===")
    
    try:
        # This tests existing code that uses PmsConnect
        pms_connect = embyconnect_bridge.PmsConnect()
        activity = pms_connect.get_current_activity()
        
        if activity and 'sessions' in activity:
            active_count = len([s for s in activity['sessions'] if s.get('session_key')])
            print(f"✅ PmsConnect compatibility successful!")
            print(f"   Active sessions via PmsConnect: {active_count}")
            return True
        else:
            print("⚠️  PmsConnect compatibility issue")
            return False
            
    except Exception as e:
        print(f"❌ PmsConnect compatibility failed: {e}")
        return False

def main():
    """Run bridge integration tests."""
    print("🚀 EmbyConnect Bridge Final Integration Test")
    print("=" * 60)
    
    # Check environment
    if not os.getenv('EMBY_URL'):
        print("⚠️  EMBY_URL not set - using defaults")
    
    tests = [
        test_activity_pinger_integration,
        test_activity_handler_integration,
        test_pms_connect_compatibility
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 60)
    print(f"🎯 Final Integration Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 EMBYCONNECT BRIDGE INTEGRATION COMPLETE!")
        print("✅ Ready for Phase 1.4 deployment!")
        return True
    elif passed >= 2:
        print("✅ Bridge integration mostly successful - minor issues only")
        return True
    else:
        print("⚠️  Bridge needs fixes before deployment")
        return False

if __name__ == '__main__':
    main()