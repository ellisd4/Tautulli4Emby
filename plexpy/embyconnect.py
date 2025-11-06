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
        # This will be implemented in Phase 1.3
        # For now, return the raw Emby session data
        return emby_session

    def transform_user_data(self, emby_user):
        """
        Transform Emby user data to Tautulli format.
        
        Parameters required:    emby_user { Emby user object }
        
        Output: dict (Tautulli user format) 
        """
        # This will be implemented in Phase 1.3
        # For now, return the raw Emby user data
        return emby_user

    def transform_library_data(self, emby_library):
        """
        Transform Emby library data to Tautulli format.
        
        Parameters required:    emby_library { Emby library object }
        
        Output: dict (Tautulli library format)
        """
        # This will be implemented in Phase 1.3
        # For now, return the raw Emby library data
        return emby_library

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