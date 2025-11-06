#!/usr/bin/env python3
"""
Test EmbyConnect Data Transformations
Tests the data transformation methods for converting Emby data to Tautulli format
"""
import unittest
import sys
import os
import json

# Add the plexpy directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plexpy'))

from test_simple_emby_connect import SimpleEmbyConnect


class TestEmbyTransformations(unittest.TestCase):
    """Test data transformation methods"""
    
    def setUp(self):
        """Set up test environment"""
        self.emby = SimpleEmbyConnect()
        
        # Skip tests if we can't connect to Emby
        try:
            server_info = self.emby.get_server_info()
            if not server_info:
                self.skipTest("Cannot connect to Emby server")
        except Exception as e:
            self.skipTest(f"Cannot connect to Emby server: {e}")
    
    def test_session_data_transformation(self):
        """Test session data transformation"""
        # Get real session data from Emby
        sessions = self.emby.get_sessions()
        active_session = next((s for s in sessions if s.get('NowPlayingItem')), None)
        
        if not active_session:
            self.skipTest("No active sessions to test with")
        
        # Import the EmbyConnect class (simplified version for testing)
        from embyconnect import EmbyConnect
        emby_client = EmbyConnect()
        
        # Transform the session data
        transformed = emby_client.transform_session_data(active_session)
        
        # Validate required Tautulli session fields
        required_fields = [
            'session_key', 'rating_key', 'user_id', 'user', 'friendly_name',
            'player', 'product', 'platform', 'machine_id', 'ip_address',
            'media_type', 'title', 'state', 'view_offset', 'duration',
            'transcode_decision', 'video_decision', 'audio_decision'
        ]
        
        for field in required_fields:
            self.assertIn(field, transformed, f"Missing required field: {field}")
            # Allow empty strings but not None
            self.assertIsNotNone(transformed[field], f"Field {field} should not be None")
        
        # Validate specific data types
        self.assertIsInstance(transformed['view_offset'], (int, str))
        self.assertIsInstance(transformed['duration'], (int, str))
        self.assertIn(transformed['state'], ['playing', 'paused', 'stopped'])
        self.assertIn(transformed['transcode_decision'], ['direct play', 'copy', 'transcode'])
        
        print(f"✅ Session transformation test passed")
        print(f"   Session: {transformed.get('user')} watching {transformed.get('title')}")
        print(f"   State: {transformed.get('state')}, Progress: {transformed.get('view_offset')}/{transformed.get('duration')}")
    
    def test_user_data_transformation(self):
        """Test user data transformation"""
        # Get user data from Emby
        users_data = self.emby.get_users_list()
        if not users_data or not users_data.get('Items'):
            self.skipTest("No user data available")
        
        user = users_data['Items'][0]  # Test with first user
        
        # Import the EmbyConnect class
        from embyconnect import EmbyConnect
        emby_client = EmbyConnect()
        
        # Transform the user data
        transformed = emby_client.transform_user_data(user)
        
        # Validate required Tautulli user fields
        required_fields = [
            'user_id', 'username', 'friendly_name', 'is_admin', 'is_home_user',
            'is_active', 'thumb', 'allow_guest', 'deleted_user'
        ]
        
        for field in required_fields:
            self.assertIn(field, transformed, f"Missing required field: {field}")
        
        # Validate specific data types
        self.assertIsInstance(transformed['is_admin'], int)
        self.assertIsInstance(transformed['is_active'], int)
        self.assertIn(transformed['is_admin'], [0, 1])
        self.assertIn(transformed['is_active'], [0, 1])
        
        print(f"✅ User transformation test passed")
        print(f"   User: {transformed.get('username')} (Admin: {bool(transformed.get('is_admin'))})")
    
    def test_library_data_transformation(self):
        """Test library data transformation"""
        # Get library data from Emby
        libraries = self.emby.get_libraries_list()
        if not libraries:
            self.skipTest("No library data available")
        
        library = libraries[0]  # Test with first library
        
        # Import the EmbyConnect class
        from embyconnect import EmbyConnect
        emby_client = EmbyConnect()
        
        # Transform the library data
        transformed = emby_client.transform_library_data(library)
        
        # Validate required Tautulli library fields
        required_fields = [
            'section_id', 'section_name', 'section_type', 'agent', 'scanner',
            'language', 'uuid', 'locations', 'is_active'
        ]
        
        for field in required_fields:
            self.assertIn(field, transformed, f"Missing required field: {field}")
        
        # Validate specific data types
        self.assertIsInstance(transformed['is_active'], int)
        self.assertIn(transformed['section_type'], ['movie', 'show', 'artist', 'photo', 'mixed'])
        
        print(f"✅ Library transformation test passed")
        print(f"   Library: {transformed.get('section_name')} (Type: {transformed.get('section_type')})")
    
    def test_full_activity_transformation(self):
        """Test the full get_current_activity transformation"""
        # Import the EmbyConnect class
        from embyconnect import EmbyConnect
        emby_client = EmbyConnect()
        
        # Get current activity (this uses transformation internally)
        activity = emby_client.get_current_activity()
        
        # Validate structure
        self.assertIn('stream_count', activity)
        self.assertIn('sessions', activity)
        self.assertIsInstance(activity['sessions'], list)
        
        stream_count = int(activity['stream_count'])
        self.assertEqual(len(activity['sessions']), stream_count)
        
        print(f"✅ Full activity transformation test passed")
        print(f"   Active streams: {activity.get('stream_count')}")
        
        # Validate each session in the activity
        for i, session in enumerate(activity['sessions']):
            self.assertIn('user', session, f"Session {i} missing user field")
            self.assertIn('title', session, f"Session {i} missing title field")
            self.assertIn('state', session, f"Session {i} missing state field")
    
    def test_transformation_with_empty_data(self):
        """Test transformations handle empty/invalid data gracefully"""
        from embyconnect import EmbyConnect
        emby_client = EmbyConnect()
        
        # Test with empty data
        self.assertEqual(emby_client.transform_session_data({}), {})
        self.assertEqual(emby_client.transform_session_data(None), {})
        self.assertEqual(emby_client.transform_user_data({}), {})
        self.assertEqual(emby_client.transform_user_data(None), {})
        self.assertEqual(emby_client.transform_library_data({}), {})
        self.assertEqual(emby_client.transform_library_data(None), {})
        
        # Test with session data missing NowPlayingItem
        session_without_media = {'Id': 'test123', 'UserName': 'TestUser'}
        self.assertEqual(emby_client.transform_session_data(session_without_media), {})
        
        print("✅ Empty data handling test passed")
    
    def test_build_full_title(self):
        """Test the _build_full_title helper method"""
        from embyconnect import EmbyConnect
        emby_client = EmbyConnect()
        
        # Test episode title building
        episode_data = {
            'Type': 'Episode',
            'SeriesName': 'Test Series',
            'ParentIndexNumber': 1,
            'IndexNumber': 5,
            'Name': 'Test Episode'
        }
        expected = "Test Series - s01e05 - Test Episode"
        result = emby_client._build_full_title(episode_data)
        self.assertEqual(result, expected)
        
        # Test movie title building
        movie_data = {
            'Type': 'Movie',
            'Name': 'Test Movie',
            'ProductionYear': 2023
        }
        expected = "Test Movie (2023)"
        result = emby_client._build_full_title(movie_data)
        self.assertEqual(result, expected)
        
        # Test track title building
        track_data = {
            'Type': 'Track',
            'AlbumArtist': 'Test Artist',
            'Name': 'Test Song'
        }
        expected = "Test Artist - Test Song"
        result = emby_client._build_full_title(track_data)
        self.assertEqual(result, expected)
        
        print("✅ Full title building test passed")


def run_transformation_tests():
    """Run all transformation tests"""
    print("=" * 80)
    print("EMBY DATA TRANSFORMATION TESTS")
    print("=" * 80)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestEmbyTransformations)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 80)
    if result.wasSuccessful():
        print("✅ ALL TRANSFORMATION TESTS PASSED")
        print("Data transformation methods are working correctly!")
    else:
        print("❌ SOME TRANSFORMATION TESTS FAILED")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")
        
        if result.errors:
            print("\nErrors:")  
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")
    
    print("=" * 80)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_transformation_tests()
    sys.exit(0 if success else 1)