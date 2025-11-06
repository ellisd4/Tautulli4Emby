# -*- coding: utf-8 -*-

# This file is part of Tautulli.
#
#  Tautulli is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Tautulli is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Tautulli.  If not, see <http://www.gnu.org/licenses/>.

import json
import os
import time
from urllib.parse import quote, urlencode

import plexpy
from plexpy import activity_processor
from plexpy import common
from plexpy import helpers
from plexpy import http_handler
from plexpy import libraries
from plexpy import logger
from plexpy import session
from plexpy import users
from plexpy.env_config import get_emby_config


def get_server_friendly_name():
    logger.info("Tautulli EmbyConnect :: Requesting name from server...")
    server_name = EmbyConnect().get_server_info().get('ServerName', '')

    if server_name and server_name != plexpy.CONFIG.EMBY_SERVER_NAME:
        plexpy.CONFIG.__setattr__('EMBY_SERVER_NAME', server_name)
        plexpy.CONFIG.write()
        logger.info("Tautulli EmbyConnect :: Server name retrieved.")

    return server_name


class EmbyConnect(object):
    """
    Retrieve data from Emby Server
    """

    def __init__(self, url=None, api_key=None):
        # Load Emby configuration from environment
        config = get_emby_config()
        
        self.url = url or config['url']
        self.api_key = api_key or config['api_key']
        self.timeout = config['timeout']
        self.ssl_verify = config['ssl_verify']
        
        # Set up request handler compatible with existing Tautulli infrastructure
        self.request_handler = http_handler.HTTPHandler(
            urls=self.url,
            token=self.api_key,
            timeout=self.timeout,
            ssl_verify=self.ssl_verify,
            # Emby uses X-Emby-Token header instead of X-Plex-Token
            token_header='X-Emby-Token'
        )

    def get_sessions(self, output_format=''):
        """
        Return current sessions from Emby server.

        Optional parameters:    output_format { dict, json }

        Output: array
        """
        uri = '/Sessions'
        request = self.request_handler.make_request(
            uri=uri,
            request_type='GET',
            output_format=output_format
        )
        return request

    def get_server_info(self, output_format=''):
        """
        Return server information from Emby server.

        Optional parameters:    output_format { dict, json }

        Output: dict
        """
        uri = '/System/Info'
        request = self.request_handler.make_request(
            uri=uri,
            request_type='GET',
            output_format=output_format
        )
        return request

    def get_server_info_public(self, output_format=''):
        """
        Return public server information from Emby server.

        Optional parameters:    output_format { dict, json }

        Output: dict
        """
        uri = '/System/Info/Public'
        request = self.request_handler.make_request(
            uri=uri,
            request_type='GET',
            output_format=output_format
        )
        return request

    def get_server_configuration(self, output_format=''):
        """
        Return server configuration from Emby server.

        Optional parameters:    output_format { dict, json }

        Output: dict
        """
        uri = '/System/Configuration'
        request = self.request_handler.make_request(
            uri=uri,
            request_type='GET',
            output_format=output_format
        )
        return request

    def get_libraries_list(self, output_format=''):
        """
        Return list of libraries on Emby server.

        Optional parameters:    output_format { dict, json }

        Output: array
        """
        uri = '/Library/VirtualFolders'
        request = self.request_handler.make_request(
            uri=uri,
            request_type='GET',
            output_format=output_format
        )
        return request

    def get_users_list(self, output_format=''):
        """
        Return list of users on Emby server.

        Optional parameters:    output_format { dict, json }

        Output: array
        """
        uri = '/Users/Query'
        request = self.request_handler.make_request(
            uri=uri,
            request_type='GET',
            output_format=output_format
        )
        return request

    def get_user_details(self, user_id='', output_format=''):
        """
        Return user details for specific user.

        Parameters required:    user_id { Emby user ID }
        Optional parameters:    output_format { dict, json }

        Output: dict
        """
        uri = f'/Users/{user_id}'
        request = self.request_handler.make_request(
            uri=uri,
            request_type='GET',
            output_format=output_format
        )
        return request

    def get_item_details(self, item_id='', user_id='', output_format=''):
        """
        Return item details for specific item.

        Parameters required:    item_id { Emby item ID }
                               user_id { Emby user ID }
        Optional parameters:    output_format { dict, json }

        Output: dict
        """
        uri = f'/Users/{user_id}/Items/{item_id}'
        request = self.request_handler.make_request(
            uri=uri,
            request_type='GET',
            output_format=output_format
        )
        return request

    def get_item_children(self, item_id='', user_id='', output_format=''):
        """
        Return children items for specific item.

        Parameters required:    item_id { Emby item ID }
                               user_id { Emby user ID }
        Optional parameters:    output_format { dict, json }

        Output: array
        """
        uri = f'/Users/{user_id}/Items/{item_id}/Items'
        request = self.request_handler.make_request(
            uri=uri,
            request_type='GET',
            output_format=output_format
        )
        return request

    def get_recently_added(self, user_id='', start_index=0, limit=50, output_format=''):
        """
        Return list of recently added items.

        Parameters required:    user_id { Emby user ID }
        Optional parameters:    start_index { item number to start from }
                               limit { number of results to return }
                               output_format { dict, json }

        Output: array
        """
        params = {
            'StartIndex': start_index,
            'Limit': limit,
            'Recursive': 'true',
            'SortBy': 'DateCreated',
            'SortOrder': 'Descending'
        }
        uri = f'/Users/{user_id}/Items/Latest?' + urlencode(params)
        request = self.request_handler.make_request(
            uri=uri,
            request_type='GET',
            output_format=output_format
        )
        return request

    def get_activity_log(self, start_index=0, limit=100, output_format=''):
        """
        Return system activity log entries.

        Optional parameters:    start_index { entry number to start from }
                               limit { number of results to return }
                               output_format { dict, json }

        Output: array
        """
        params = {
            'StartIndex': start_index,
            'Limit': limit
        }
        uri = f'/System/ActivityLog/Entries?' + urlencode(params)
        request = self.request_handler.make_request(
            uri=uri,
            request_type='GET',
            output_format=output_format
        )
        return request

    def terminate_session(self, session_id='', message=''):
        """
        Terminate a streaming session.

        Parameters required:    session_id { Emby session ID }
        Optional parameters:    message { termination message }

        Output: response
        """
        if not session_id:
            logger.warn("Tautulli EmbyConnect :: Failed to terminate session: Missing session_id")
            return False

        message = message or 'The server owner has ended the stream.'
        
        # Send message to session
        uri = f'/Sessions/{session_id}/Message'
        data = {
            'Header': 'Stream Terminated',
            'Text': message,
            'TimeoutMs': 5000
        }
        
        logger.info(f"Tautulli EmbyConnect :: Terminating session {session_id}.")
        
        response = self.request_handler.make_request(
            uri=uri,
            request_type='POST',
            data=json.dumps(data),
            return_response=True
        )
        
        # Also try to stop playback
        stop_uri = f'/Sessions/{session_id}/Playing/Stop'
        self.request_handler.make_request(
            uri=stop_uri,
            request_type='POST'
        )
        
        return response.ok if response else False

    def send_command(self, session_id='', command='', output_format=''):
        """
        Send a command to a specific session.

        Parameters required:    session_id { Emby session ID }
                               command { command to send }
        Optional parameters:    output_format { dict, json }

        Output: response
        """
        if command in ['Play', 'Pause', 'Stop', 'PlayPause']:
            uri = f'/Sessions/{session_id}/Playing/{command}'
        else:
            uri = f'/Sessions/{session_id}/Command/{command}'
            
        request = self.request_handler.make_request(
            uri=uri,
            request_type='POST',
            output_format=output_format,
            return_response=True
        )
        return request

    def send_message(self, session_id='', header='', text='', timeout_ms=5000, output_format=''):
        """
        Send a message to a specific session.

        Parameters required:    session_id { Emby session ID }
                               header { message header }
                               text { message text }
        Optional parameters:    timeout_ms { message timeout in milliseconds }
                               output_format { dict, json }

        Output: response
        """
        uri = f'/Sessions/{session_id}/Message'
        data = {
            'Header': header,
            'Text': text,
            'TimeoutMs': timeout_ms
        }
        
        request = self.request_handler.make_request(
            uri=uri,
            request_type='POST',
            data=json.dumps(data),
            output_format=output_format,
            return_response=True
        )
        return request

    # Helper methods for data transformation
    def transform_session_data(self, emby_session):
        """
        Transform Emby session data to Tautulli format.
        
        Parameters required:    emby_session { Emby session object }
        
        Output: dict (Tautulli session format)
        """
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
            'transcode_key': '',  # Emby doesn't use transcode keys like Plex
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
            'section_id': now_playing.get('ParentId', ''),  # Use parent as library section
            'title': now_playing.get('Name', ''),
            'parent_title': now_playing.get('SeriesName', '') or now_playing.get('Album', ''),
            'grandparent_title': now_playing.get('SeriesName', ''),
            'original_title': now_playing.get('OriginalTitle', ''),
            'full_title': self._build_full_title(now_playing),
            'year': now_playing.get('ProductionYear', ''),
            'originally_available_at': now_playing.get('PremiereDate', ''),
            'added_at': helpers.timestamp() if now_playing.get('DateCreated') else '',
            'guid': now_playing.get('Id', ''),
            
            # Media hierarchy (for episodes/tracks)
            'parent_rating_key': now_playing.get('SeasonId', '') or now_playing.get('AlbumId', ''),
            'grandparent_rating_key': now_playing.get('SeriesId', '') or now_playing.get('AlbumArtistId', ''),
            'media_index': now_playing.get('IndexNumber', ''),
            'parent_media_index': now_playing.get('ParentIndexNumber', ''),
            
            # Playback state
            'state': 'paused' if play_state.get('IsPaused') else 'playing',
            'view_offset': ticks_to_ms(play_state.get('PositionTicks', 0)),
            'duration': ticks_to_ms(now_playing.get('RunTimeTicks', 0)),
            'started': helpers.timestamp(),  # Set when session is first seen
            'stopped': None,  # Set when session ends
            'paused_counter': 0,  # Managed by activity processor
            
            # Quality and transcoding
            'transcode_decision': get_transcode_decision(),
            'video_decision': 'direct play' if play_state.get('PlayMethod') == 'DirectPlay' else 'copy',
            'audio_decision': 'direct play' if play_state.get('PlayMethod') == 'DirectPlay' else 'copy',
            'quality_profile': '',  # Emby doesn't expose quality profiles like Plex
            
            # Video stream information
            'width': video_stream.get('Width', ''),
            'height': video_stream.get('Height', ''),
            'container': now_playing.get('Container', ''),
            'bitrate': now_playing.get('Bitrate', ''),
            'video_codec': video_stream.get('Codec', ''),
            'video_bitrate': video_stream.get('BitRate', ''),
            'video_width': video_stream.get('Width', ''),
            'video_height': video_stream.get('Height', ''),
            'video_resolution': f"{video_stream.get('Height', '')}p" if video_stream.get('Height') else '',
            'video_framerate': str(video_stream.get('AverageFrameRate', '')) if video_stream.get('AverageFrameRate') else '',
            'video_scan_type': 'interlaced' if video_stream.get('IsInterlaced') else 'progressive',
            'video_full_resolution': f"{video_stream.get('Width', '')}x{video_stream.get('Height', '')}" if video_stream.get('Width') and video_stream.get('Height') else '',
            'video_dynamic_range': video_stream.get('VideoRange', ''),
            'aspect_ratio': video_stream.get('AspectRatio', ''),
            
            # Audio stream information
            'audio_codec': audio_stream.get('Codec', ''),
            'audio_bitrate': audio_stream.get('BitRate', ''),
            'audio_channels': audio_stream.get('Channels', ''),
            'audio_language': audio_stream.get('Language', ''),
            'audio_language_code': audio_stream.get('Language', ''),
            
            # Subtitle information
            'subtitle_codec': subtitle_stream.get('Codec', ''),
            'subtitle_forced': 1 if subtitle_stream.get('IsForced') else 0,
            'subtitle_language': subtitle_stream.get('Language', ''),
            'subtitles': 1 if play_state.get('SubtitleStreamIndex', -1) >= 0 else 0,
            
            # Transcoding information (mostly empty for Emby DirectPlay/DirectStream)
            'transcode_protocol': '',
            'transcode_container': '',
            'transcode_video_codec': '',
            'transcode_audio_codec': '',
            'transcode_audio_channels': '',
            'transcode_width': '',
            'transcode_height': '',
            'transcode_hw_decoding': '',
            'transcode_hw_encoding': '',
            
            # Stream information (current stream being played)
            'stream_bitrate': video_stream.get('BitRate', ''),
            'stream_video_resolution': f"{video_stream.get('Height', '')}p" if video_stream.get('Height') else '',
            'stream_container_decision': 'direct play' if play_state.get('PlayMethod') == 'DirectPlay' else 'copy',
            'stream_container': now_playing.get('Container', ''),
            'stream_video_decision': 'direct play' if play_state.get('PlayMethod') == 'DirectPlay' else 'copy',
            'stream_video_codec': video_stream.get('Codec', ''),
            'stream_video_bitrate': video_stream.get('BitRate', ''),
            'stream_video_width': video_stream.get('Width', ''),
            'stream_video_height': video_stream.get('Height', ''),
            'stream_video_framerate': str(video_stream.get('AverageFrameRate', '')) if video_stream.get('AverageFrameRate') else '',
            'stream_video_scan_type': 'interlaced' if video_stream.get('IsInterlaced') else 'progressive',
            'stream_video_full_resolution': f"{video_stream.get('Width', '')}x{video_stream.get('Height', '')}" if video_stream.get('Width') and video_stream.get('Height') else '',
            'stream_video_dynamic_range': video_stream.get('VideoRange', ''),
            'stream_audio_decision': 'direct play' if play_state.get('PlayMethod') == 'DirectPlay' else 'copy',
            'stream_audio_codec': audio_stream.get('Codec', ''),
            'stream_audio_bitrate': audio_stream.get('BitRate', ''),
            'stream_audio_channels': audio_stream.get('Channels', ''),
            'stream_audio_language': audio_stream.get('Language', ''),
            'stream_audio_language_code': audio_stream.get('Language', ''),
            'stream_subtitle_decision': 'none' if play_state.get('SubtitleStreamIndex', -1) < 0 else 'burn',
            'stream_subtitle_codec': subtitle_stream.get('Codec', ''),
            'stream_subtitle_forced': 1 if subtitle_stream.get('IsForced') else 0,
            'stream_subtitle_language': subtitle_stream.get('Language', ''),
            
            # Image/artwork information
            'thumb': f"/emby/Items/{now_playing.get('Id')}/Images/Primary" if now_playing.get('ImageTags', {}).get('Primary') else '',
            'parent_thumb': f"/emby/Items/{now_playing.get('ParentId')}/Images/Primary" if now_playing.get('ParentId') else '',
            'grandparent_thumb': f"/emby/Items/{now_playing.get('SeriesId')}/Images/Primary" if now_playing.get('SeriesId') else '',
            
            # Network and connection
            'bandwidth': 0,  # Emby doesn't expose bandwidth like Plex
            'location': 'lan',  # Could be enhanced to detect remote vs local
            'secure': 1 if emby_session.get('Protocol') == 'HTTPS' else 0,
            'relayed': 0,  # Emby doesn't have relay concept like Plex
            
            # Live TV specific fields
            'live': 1 if now_playing.get('IsLive') else 0,
            'live_uuid': now_playing.get('LiveStreamId', ''),
            'channel_call_sign': now_playing.get('ChannelName', ''),
            'channel_id': now_playing.get('ChannelId', ''),
            'channel_identifier': now_playing.get('ChannelId', ''),
            'channel_title': now_playing.get('ChannelName', ''),
            'channel_thumb': '',
            'channel_vcn': '',
            
            # Optimization flags
            'synced_version': 0,
            'synced_version_profile': '',
            'optimized_version': 0,
            'optimized_version_profile': '',
            'optimized_version_title': '',
            
            # Buffer and interaction tracking
            'buffer_count': 0,
            'buffer_last_triggered': 0,
            'last_paused': 0,
            'watched': 0,
            'intro': 0,
            'credits': 0,
            'commercial': 0,
            'marker': 0,
            'initial_stream': 1,
            'write_attempts': 0,
            
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
        """
        Transform Emby user data to Tautulli format.
        
        Parameters required:    emby_user { Emby user object }
        
        Output: dict (Tautulli user format) 
        """
        if not emby_user:
            return {}
        
        # Extract policy information
        policy = emby_user.get('Policy', {})
        config = emby_user.get('Configuration', {})
        
        # Build the transformed user data matching Tautulli's users table schema
        transformed_user = {
            # Core user identification
            'user_id': emby_user.get('Id', ''),
            'username': emby_user.get('Name', ''),
            'friendly_name': emby_user.get('Name', ''),
            'email': emby_user.get('Email', ''),
            
            # User status and permissions
            'is_admin': 1 if policy.get('IsAdministrator', False) else 0,
            'is_home_user': 1,  # All Emby users are considered "home" users
            'is_allow_sync': 1 if policy.get('EnableSyncTranscoding', True) else 0,
            'is_restricted': 1 if policy.get('IsDisabled', False) else 0,
            'is_active': 1 if not policy.get('IsDisabled', False) else 0,
            
            # Timestamps
            'created_at': helpers.timestamp() if emby_user.get('DateCreated') else '',
            'last_seen': helpers.timestamp() if emby_user.get('LastLoginDate') else '',
            
            # User preferences
            'thumb': f"/emby/Users/{emby_user.get('Id')}/Images/Primary" if emby_user.get('PrimaryImageTag') else '',
            'custom_avatar_url': '',
            'avatar_url': f"/emby/Users/{emby_user.get('Id')}/Images/Primary" if emby_user.get('PrimaryImageTag') else '',
            
            # Access control
            'allow_guest': 0,  # Emby doesn't have guest concept like Plex
            'deleted_user': 0,
            'shared_libraries': '',  # Will be populated separately if needed
            'filter_all': '',
            'filter_movies': '',
            'filter_tv': '',
            'filter_music': '',
            'filter_photos': '',
            
            # User statistics (will be calculated by Tautulli)
            'plays': 0,
            'duration': 0,
            'last_played': '',
            'last_rating_key': '',
            'ip_address': '',
            'platform': '',
            'player': '',
            'user_agent': '',
            
            # Additional fields for compatibility
            'server_token': '',
            'shared_libraries_excluded': '',
            'keep_history': 1,
            'allow_local_network': 1 if policy.get('EnableRemoteAccess', True) else 0,
            'allow_remote_access': 1 if policy.get('EnableRemoteAccess', True) else 0,
            'row_id': None  # Will be set by database
        }
        
        return transformed_user

    def transform_library_data(self, emby_library):
        """
        Transform Emby library data to Tautulli format.
        
        Parameters required:    emby_library { Emby library object }
        
        Output: dict (Tautulli library format)
        """
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
                'books': 'photo',  # Tautulli doesn't have books, use photo
                'homevideos': 'movie',
                'musicvideos': 'movie',
                'mixed': 'mixed'
            }
            return type_mapping.get(collection_type, 'mixed')
        
        # Build the transformed library data matching Tautulli's library_sections table schema
        transformed_library = {
            # Core library identification
            'section_id': emby_library.get('ItemId', ''),
            'section_name': emby_library.get('Name', ''),
            'section_type': get_section_type(),
            'agent': 'com.plexapp.agents.none',  # Emby doesn't use agents like Plex
            'scanner': 'Emby Media Scanner',
            'language': 'en',
            'uuid': emby_library.get('ItemId', ''),
            
            # Library paths and locations
            'library_art': '',  # Emby libraries don't have art like Plex
            'library_thumb': '',
            'parent_count': 0,  # Will be populated by library scan
            'child_count': 0,   # Will be populated by library scan
            'primary_key': emby_library.get('ItemId', ''),
            
            # Library settings and preferences
            'show_advanced': 1,
            'show_hidden': 0,
            'deleted_section': 0,
            'section_deleted': 0,
            'custom_art_url': '',
            'custom_thumb_url': '',
            
            # Refresh and sync settings
            'refreshing': 0,
            'sync_to_users': 1,
            'count': 0,  # Will be populated by library scan
            'parent_count': 0,
            'child_count': 0,
            'item_count': 0,
            
            # Timestamps
            'created_at': helpers.timestamp(),
            'updated_at': helpers.timestamp(),
            'last_accessed': helpers.timestamp(),
            'last_scanned': helpers.timestamp(),
            
            # Library paths (extracted from locations)
            'locations': json.dumps(emby_library.get('Locations', [])),
            'paths': ';'.join(emby_library.get('Locations', [])),
            
            # Additional metadata
            'collection_type': emby_library.get('CollectionType', ''),
            'library_id': emby_library.get('ItemId', ''),
            'refresh_enabled': 1,
            'enable_auto_sort': 1,
            'enable_chapter_image_generation': 1,
            'include_in_dashboard': 1,
            'is_active': 1,
            'keep_history': 1,
            'row_id': None  # Will be set by database
        }
        
        return transformed_library

    def get_current_activity(self, skip_cache=False):
        """
        Return processed and validated session list.
        This method transforms Emby sessions to match Tautulli's expected format.

        Output: dict with session count and sessions list
        """
        try:
            # Get sessions from Emby API
            sessions_data = self.get_sessions(output_format='dict')
            
            if not sessions_data:
                return {
                    'stream_count': '0',
                    'sessions': []
                }

            # Filter only sessions with active playback
            active_sessions = []
            for session in sessions_data:
                # Only include sessions that have NowPlayingItem (actively playing content)
                if session.get('NowPlayingItem'):
                    transformed_session = self.transform_session_data(session)
                    active_sessions.append(transformed_session)

            return {
                'stream_count': str(len(active_sessions)),
                'sessions': session.mask_session_info(active_sessions)
            }

        except Exception as e:
            logger.error(f"Tautulli EmbyConnect :: Error getting current activity: {e}")
            return {
                'stream_count': '0',
                'sessions': []
            }

    def get_server_identity(self):
        """
        Return server identity information.
        
        Output: dict
        """
        try:
            server_info = self.get_server_info_public(output_format='dict')
            
            # Transform to match Plex identity format
            identity = {
                'machine_identifier': server_info.get('Id', ''),
                'version': server_info.get('Version', ''),
                'server_name': server_info.get('ServerName', ''),
                'product_name': server_info.get('ProductName', 'Emby Server')
            }
            
            return identity
            
        except Exception as e:
            logger.error(f"Tautulli EmbyConnect :: Error getting server identity: {e}")
            return {}

    def get_server_friendly_name(self):
        """
        Return server friendly name.
        
        Output: string
        """
        try:
            server_info = self.get_server_info(output_format='dict')
            return server_info.get('ServerName', '')
        except Exception as e:
            logger.error(f"Tautulli EmbyConnect :: Error getting server friendly name: {e}")
            return ''

    # Compatibility methods to maintain API compatibility with existing Tautulli code
    def get_metadata(self, rating_key='', output_format=''):
        """
        Compatibility method for get_item_details.
        Note: Requires user context - will use admin user for now.
        """
        # This needs to be enhanced with proper user context management
        logger.debug("Tautulli EmbyConnect :: get_metadata called - needs user context implementation")
        return self.get_item_details(item_id=rating_key, user_id='admin', output_format=output_format)

    def get_server_prefs(self, output_format=''):
        """
        Compatibility method for get_server_configuration.
        """
        return self.get_server_configuration(output_format=output_format)

    def get_local_server_identity(self, output_format=''):
        """
        Compatibility method for get_server_info_public.
        """
        return self.get_server_info_public(output_format=output_format)