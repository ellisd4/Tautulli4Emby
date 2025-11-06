#!/usr/bin/env python3
"""
Simplified EmbyConnect Transformation Tests
Tests data transformation methods without full Tautulli dependencies
"""
import json
import sys
import os


# Mock helpers for testing
class MockHelpers:
    @staticmethod
    def timestamp():
        import time
        return int(time.time())


# Simplified EmbyConnect class for testing transformations
class SimpleEmbyConnect:
    """Simplified EmbyConnect for transformation testing"""
    
    def __init__(self):
        pass
    
    def transform_session_data(self, emby_session):
        """Transform Emby session data to Tautulli format"""
        if not emby_session or not emby_session.get('NowPlayingItem'):
            return {}
        
        # Extract key data structures
        play_state = emby_session.get('PlayState', {})
        now_playing = emby_session.get('NowPlayingItem', {})
        media_streams = now_playing.get('MediaStreams', [])
        
        # Find video, audio, and subtitle streams
        video_stream = next((s for s in media_streams if s.get('Type') == 'Video'), {})
        audio_stream = next((s for s in media_streams if s.get('Type') == 'Audio' and s.get('IsDefault')), {})
        subtitle_stream = next((s for s in media_streams if s.get('Type') == 'Subtitle' and 
                              s.get('Index') == play_state.get('SubtitleStreamIndex', -1)), {})
        
        # Helper function to safely convert ticks to milliseconds
        def ticks_to_ms(ticks):
            return int(ticks / 10000) if ticks else 0
        
        # Helper function to get media type
        def get_media_type():
            item_type = now_playing.get('Type', '').lower()
            if item_type == 'episode':
                return 'episode'
            elif item_type == 'movie':
                return 'movie'
            elif item_type == 'track':
                return 'track'
            elif item_type == 'photo':
                return 'photo'
            elif item_type in ['channel', 'program']:
                return 'live'
            else:
                return 'clip'
        
        # Helper function to determine transcode decision
        def get_transcode_decision():
            play_method = play_state.get('PlayMethod', 'DirectPlay')
            if play_method == 'DirectPlay':
                return 'direct play'
            elif play_method == 'DirectStream':
                return 'copy'
            else:
                return 'transcode'
        
        # Build the transformed session data matching Tautulli's schema
        transformed_session = {
            # Session identification
            'session_key': emby_session.get('Id', ''),
            'session_id': emby_session.get('Id', ''),
            'transcode_key': '',
            'rating_key': now_playing.get('Id', ''),
            'rating_key_websocket': now_playing.get('Id', ''),
            
            # User information
            'user_id': emby_session.get('UserId', ''),
            'user': emby_session.get('UserName', ''),
            'friendly_name': emby_session.get('DeviceName', ''),
            
            # Client/Device information
            'player': emby_session.get('Client', ''),
            'product': emby_session.get('Client', ''),
            'platform': emby_session.get('Client', '').replace(' ', '').lower(),
            'machine_id': emby_session.get('DeviceId', ''),
            'ip_address': emby_session.get('RemoteEndPoint', '').split(':')[0] if emby_session.get('RemoteEndPoint') else '',
            
            # Media information
            'media_type': get_media_type(),
            'section_id': now_playing.get('ParentId', ''),
            'title': now_playing.get('Name', ''),
            'parent_title': now_playing.get('SeriesName', '') or now_playing.get('Album', ''),
            'grandparent_title': now_playing.get('SeriesName', ''),
            'original_title': now_playing.get('OriginalTitle', ''),
            'full_title': self._build_full_title(now_playing),
            'year': now_playing.get('ProductionYear', ''),
            'originally_available_at': now_playing.get('PremiereDate', ''),
            'added_at': MockHelpers.timestamp() if now_playing.get('DateCreated') else '',
            'guid': now_playing.get('Id', ''),
            
            # Media hierarchy
            'parent_rating_key': now_playing.get('SeasonId', '') or now_playing.get('AlbumId', ''),
            'grandparent_rating_key': now_playing.get('SeriesId', '') or now_playing.get('AlbumArtistId', ''),
            'media_index': now_playing.get('IndexNumber', ''),
            'parent_media_index': now_playing.get('ParentIndexNumber', ''),
            
            # Playback state
            'state': 'paused' if play_state.get('IsPaused') else 'playing',
            'view_offset': ticks_to_ms(play_state.get('PositionTicks', 0)),
            'duration': ticks_to_ms(now_playing.get('RunTimeTicks', 0)),
            'started': MockHelpers.timestamp(),
            'stopped': None,
            'paused_counter': 0,
            
            # Quality and transcoding
            'transcode_decision': get_transcode_decision(),
            'video_decision': 'direct play' if play_state.get('PlayMethod') == 'DirectPlay' else 'copy',
            'audio_decision': 'direct play' if play_state.get('PlayMethod') == 'DirectPlay' else 'copy',
            'quality_profile': '',
            
            # Video stream information
            'width': video_stream.get('Width', ''),
            'height': video_stream.get('Height', ''),
            'container': now_playing.get('Container', ''),
            'bitrate': now_playing.get('Bitrate', ''),
            'video_codec': video_stream.get('Codec', ''),
            'video_resolution': f"{video_stream.get('Height', '')}p" if video_stream.get('Height') else '',
            'aspect_ratio': video_stream.get('AspectRatio', ''),
            
            # Audio stream information
            'audio_codec': audio_stream.get('Codec', ''),
            'audio_channels': audio_stream.get('Channels', ''),
            'audio_language': audio_stream.get('Language', ''),
            
            # Subtitle information
            'subtitle_codec': subtitle_stream.get('Codec', ''),
            'subtitle_forced': 1 if subtitle_stream.get('IsForced') else 0,
            'subtitle_language': subtitle_stream.get('Language', ''),
            'subtitles': 1 if play_state.get('SubtitleStreamIndex', -1) >= 0 else 0,
            
            # Raw stream info for debugging
            'raw_stream_info': json.dumps(emby_session)
        }
        
        return transformed_session
    
    def _build_full_title(self, now_playing):
        """Build full title string for media item"""
        media_type = now_playing.get('Type', '').lower()
        
        if media_type == 'episode':
            series = now_playing.get('SeriesName', '')
            season = now_playing.get('ParentIndexNumber', '')
            episode = now_playing.get('IndexNumber', '')
            title = now_playing.get('Name', '')
            
            if series and season and episode and title:
                return f"{series} - s{season:02d}e{episode:02d} - {title}"
            elif series and title:
                return f"{series} - {title}"
            else:
                return title
                
        elif media_type == 'movie':
            title = now_playing.get('Name', '')
            year = now_playing.get('ProductionYear', '')
            if title and year:
                return f"{title} ({year})"
            else:
                return title
                
        elif media_type == 'track':
            artist = now_playing.get('AlbumArtist', '')
            track = now_playing.get('Name', '')
            if artist and track:
                return f"{artist} - {track}"
            else:
                return track
                
        else:
            return now_playing.get('Name', '')
    
    def transform_user_data(self, emby_user):
        """Transform Emby user data to Tautulli format"""
        if not emby_user:
            return {}
        
        policy = emby_user.get('Policy', {})
        
        transformed_user = {
            'user_id': emby_user.get('Id', ''),
            'username': emby_user.get('Name', ''),
            'friendly_name': emby_user.get('Name', ''),
            'email': emby_user.get('Email', ''),
            'is_admin': 1 if policy.get('IsAdministrator', False) else 0,
            'is_home_user': 1,
            'is_active': 1 if not policy.get('IsDisabled', False) else 0,
            'thumb': f"/emby/Users/{emby_user.get('Id')}/Images/Primary" if emby_user.get('PrimaryImageTag') else '',
            'allow_guest': 0,
            'deleted_user': 0,
            'keep_history': 1
        }
        
        return transformed_user
    
    def transform_library_data(self, emby_library):
        """Transform Emby library data to Tautulli format"""
        if not emby_library:
            return {}
        
        # Map Emby collection types to Tautulli section types
        def get_section_type():
            collection_type = emby_library.get('CollectionType', '').lower()
            type_mapping = {
                'movies': 'movie',
                'tvshows': 'show',
                'music': 'artist',
                'photos': 'photo',
                'mixed': 'mixed'
            }
            return type_mapping.get(collection_type, 'mixed')
        
        transformed_library = {
            'section_id': emby_library.get('ItemId', ''),
            'section_name': emby_library.get('Name', ''),
            'section_type': get_section_type(),
            'agent': 'com.emby.agent.none',
            'scanner': 'Emby Media Scanner',
            'language': 'en',
            'uuid': emby_library.get('ItemId', ''),
            'locations': json.dumps(emby_library.get('Locations', [])),
            'is_active': 1,
            'collection_type': emby_library.get('CollectionType', '')
        }
        
        return transformed_library


def test_transformations():
    """Test transformation methods with sample data"""
    print("=" * 80)
    print("SIMPLIFIED EMBY DATA TRANSFORMATION TESTS")
    print("=" * 80)
    
    emby = SimpleEmbyConnect()
    
    # Test 1: Session data transformation with sample data
    print("\\nTest 1: Session Data Transformation")
    sample_session = {
        "PlayState": {
            "PositionTicks": 909997742,
            "IsPaused": False,
            "PlayMethod": "DirectStream"
        },
        "Id": "test_session_123",
        "UserId": "user_456",
        "UserName": "Test User",
        "Client": "Test Client",
        "DeviceName": "Test Device",
        "DeviceId": "device_789",
        "RemoteEndPoint": "192.168.1.100:8096",
        "NowPlayingItem": {
            "Name": "Test Episode",
            "Id": "item_123",
            "Type": "Episode",
            "SeriesName": "Test Series",
            "ParentIndexNumber": 1,
            "IndexNumber": 5,
            "ProductionYear": 2023,
            "RunTimeTicks": 25852500000,
            "Container": "mkv",
            "MediaStreams": [
                {
                    "Type": "Video",
                    "Codec": "h264",
                    "Width": 1920,
                    "Height": 1080,
                    "AspectRatio": "16:9"
                },
                {
                    "Type": "Audio",
                    "Codec": "ac3",
                    "Channels": 6,
                    "Language": "eng",
                    "IsDefault": True
                }
            ]
        }
    }
    
    transformed_session = emby.transform_session_data(sample_session)
    
    # Validate required fields
    required_fields = [
        'session_key', 'rating_key', 'user_id', 'user', 'friendly_name',
        'player', 'product', 'platform', 'media_type', 'title', 'state',
        'view_offset', 'duration', 'transcode_decision'
    ]
    
    missing_fields = [field for field in required_fields if field not in transformed_session]
    if missing_fields:
        print(f"❌ Missing fields: {missing_fields}")
        return False
    
    print("✅ Session transformation successful")
    print(f"   Title: {transformed_session.get('full_title')}")
    print(f"   User: {transformed_session.get('user')} on {transformed_session.get('player')}")
    print(f"   State: {transformed_session.get('state')}, Progress: {transformed_session.get('view_offset')}/{transformed_session.get('duration')}")
    
    # Test 2: User data transformation
    print("\\nTest 2: User Data Transformation")
    sample_user = {
        "Id": "user_123",
        "Name": "Test User",
        "Email": "test@example.com",
        "Policy": {
            "IsAdministrator": True,
            "IsDisabled": False
        },
        "PrimaryImageTag": "abc123"
    }
    
    transformed_user = emby.transform_user_data(sample_user)
    
    user_required_fields = ['user_id', 'username', 'is_admin', 'is_active']
    user_missing_fields = [field for field in user_required_fields if field not in transformed_user]
    if user_missing_fields:
        print(f"❌ Missing user fields: {user_missing_fields}")
        return False
    
    print("✅ User transformation successful")
    print(f"   User: {transformed_user.get('username')} (Admin: {bool(transformed_user.get('is_admin'))})")
    
    # Test 3: Library data transformation
    print("\\nTest 3: Library Data Transformation")
    sample_library = {
        "ItemId": "lib_123",
        "Name": "Test Movies",
        "CollectionType": "movies",
        "Locations": ["/mnt/movies"]
    }
    
    transformed_library = emby.transform_library_data(sample_library)
    
    lib_required_fields = ['section_id', 'section_name', 'section_type', 'is_active']
    lib_missing_fields = [field for field in lib_required_fields if field not in transformed_library]
    if lib_missing_fields:
        print(f"❌ Missing library fields: {lib_missing_fields}")
        return False
    
    print("✅ Library transformation successful")
    print(f"   Library: {transformed_library.get('section_name')} (Type: {transformed_library.get('section_type')})")
    
    # Test 4: Full title building
    print("\\nTest 4: Full Title Building")
    
    # Test episode title
    episode_title = emby._build_full_title({
        'Type': 'Episode',
        'SeriesName': 'Test Series',
        'ParentIndexNumber': 1,
        'IndexNumber': 5,
        'Name': 'Test Episode'
    })
    expected_episode = "Test Series - s01e05 - Test Episode"
    if episode_title != expected_episode:
        print(f"❌ Episode title mismatch: {episode_title} != {expected_episode}")
        return False
    
    # Test movie title
    movie_title = emby._build_full_title({
        'Type': 'Movie',
        'Name': 'Test Movie',
        'ProductionYear': 2023
    })
    expected_movie = "Test Movie (2023)"
    if movie_title != expected_movie:
        print(f"❌ Movie title mismatch: {movie_title} != {expected_movie}")
        return False
    
    print("✅ Full title building successful")
    print(f"   Episode: {episode_title}")
    print(f"   Movie: {movie_title}")
    
    # Test 5: Empty data handling
    print("\\nTest 5: Empty Data Handling")
    
    # Test with empty/None data
    empty_tests = [
        (emby.transform_session_data({}), "session empty dict"),
        (emby.transform_session_data(None), "session None"),
        (emby.transform_user_data({}), "user empty dict"),
        (emby.transform_user_data(None), "user None"),
        (emby.transform_library_data({}), "library empty dict"),
        (emby.transform_library_data(None), "library None")
    ]
    
    for result, test_name in empty_tests:
        if result != {}:
            print(f"❌ {test_name} should return empty dict, got: {type(result)}")
            return False
    
    # Test session without NowPlayingItem
    session_no_media = emby.transform_session_data({'Id': 'test', 'UserName': 'Test'})
    if session_no_media != {}:
        print(f"❌ Session without NowPlayingItem should return empty dict")
        return False
    
    print("✅ Empty data handling successful")
    
    print("\\n" + "=" * 80)
    print("✅ ALL TRANSFORMATION TESTS PASSED!")
    print("Data transformation methods are working correctly!")
    print("=" * 80)
    
    return True


if __name__ == '__main__':
    success = test_transformations()
    sys.exit(0 if success else 1)