#!/usr/bin/env python3
"""
Direct EmbyConnect Bridge Functionality Test

Tests the bridge by directly using the transformed methods from our standalone EmbyConnect.
This simulates what the bridge does internally.
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import standalone EmbyConnect directly
from embyconnect_standalone import EmbyConnect

def test_bridge_functionality():
    """Test the core bridge functionality using standalone EmbyConnect."""
    print("🚀 Testing EmbyConnect Bridge Functionality")
    print("=" * 60)
    
    try:
        # Initialize EmbyConnect (what bridge does)
        emby_connect = EmbyConnect()
        print("✅ EmbyConnect initialized")
        
        # Test server connection
        server_info = emby_connect.get_server_info()
        if server_info:
            server_name = server_info.get('ServerName', 'Unknown')
            version = server_info.get('Version', 'Unknown')
            print(f"✅ Connected to: {server_name} v{version}")
        else:
            print("❌ Could not connect to server")
            return False
        
        # Test get_current_activity equivalent (activity_pinger.py pattern)
        print("\n=== Testing activity_pinger.py pattern ===")
        raw_sessions = emby_connect.get_sessions()
        
        if raw_sessions:
            # Transform sessions (what bridge does)
            transformed_sessions = []
            active_sessions = []
            
            for session in raw_sessions:
                try:
                    transformed = emby_connect.transform_session_data(session)
                    if transformed:
                        transformed_sessions.append(transformed)
                        if transformed.get('session_key') and transformed.get('rating_key'):
                            active_sessions.append(transformed)
                except Exception as e:
                    print(f"   Warning: Failed to transform session: {e}")
                    continue
            
            # This is what activity_pinger.py expects:
            session_list = {'sessions': transformed_sessions}
            media_container = session_list['sessions']
            
            print(f"✅ Raw sessions: {len(raw_sessions)}")
            print(f"✅ Transformed sessions: {len(transformed_sessions)}")
            print(f"✅ Active sessions: {len(active_sessions)}")
            
            # Show active session details (what activity_pinger.py processes)
            for session in active_sessions[:3]:
                session_key = session.get('session_key', 'None')[:12]
                rating_key = session.get('rating_key', 'None')
                state = session.get('state', 'unknown')
                user = session.get('user', 'Unknown')
                title = session.get('title', 'Unknown')
                print(f"   [{session_key}...] {user} - {state} - {title}")
        
        # Test metadata retrieval (activity_handler.py pattern)
        print("\n=== Testing activity_handler.py pattern ===")
        if active_sessions:
            test_session = active_sessions[0]
            rating_key = test_session['rating_key']
            
            metadata = emby_connect.get_item_details(rating_key)
            if metadata:
                transformed_metadata = emby_connect.transform_metadata(metadata)
                title = transformed_metadata.get('title', 'Unknown')
                media_type = transformed_metadata.get('media_type', 'Unknown')
                print(f"✅ Metadata retrieval works: {title} ({media_type})")
            else:
                print(f"⚠️  Could not get metadata for rating_key: {rating_key}")
        
        # Test user retrieval (activity_processor.py pattern)
        print("\n=== Testing activity_processor.py pattern ===")
        raw_users = emby_connect.get_users_list()
        if raw_users:
            transformed_users = []
            for user in raw_users:
                try:
                    transformed = emby_connect.transform_user_data(user)
                    if transformed:
                        transformed_users.append(transformed)
                except Exception as e:
                    print(f"   Warning: Failed to transform user: {e}")
                    continue
            
            print(f"✅ User retrieval works: {len(transformed_users)} users")
        
        print("\n" + "=" * 60)
        print("🎉 BRIDGE FUNCTIONALITY VALIDATION COMPLETE!")
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"   Server: {server_name} v{version}")
        print(f"   Active Sessions: {len(active_sessions)}")
        print(f"   Users: {len(transformed_users) if 'transformed_users' in locals() else 'N/A'}")
        print(f"   Metadata: {'✅ Working' if metadata else '⚠️  Issue'}")
        
        return len(active_sessions) > 0
        
    except Exception as e:
        print(f"❌ Bridge functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the bridge functionality test."""
    success = test_bridge_functionality()
    
    if success:
        print("\n🎯 RESULT: EmbyConnect bridge is ready for integration!")
        print("✅ Phase 1.4 can proceed with confidence")
        return True
    else:
        print("\n⚠️  RESULT: Bridge needs attention before integration")
        return False

if __name__ == '__main__':
    main()