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

"""
EmbyConnect Bridge - Integration layer between standalone EmbyConnect and Tautulli infrastructure

This module provides a bridge that:
1. Integrates standalone EmbyConnect with Tautulli's logging and configuration systems
2. Maintains compatibility with existing PmsConnect interface
3. Handles Emby-specific configuration and connection management
"""

import os
import sys

# Add the project root to Python path to import our standalone EmbyConnect
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import plexpy
from plexpy import logger

# Import our standalone EmbyConnect
from embyconnect_standalone import EmbyConnect as StandaloneEmbyConnect


class EmbyConnect:
    """
    Bridge class that integrates standalone EmbyConnect with Tautulli infrastructure.
    
    This class:
    - Uses Tautulli's configuration system for Emby server settings
    - Integrates with Tautulli's logging system
    - Maintains API compatibility with PmsConnect where possible
    - Provides Emby-specific functionality through the standalone implementation
    """
    
    def __init__(self):
        """Initialize EmbyConnect with Tautulli configuration."""
        self._get_emby_config()
        
        # Initialize the standalone EmbyConnect with our config
        self.emby_connect = StandaloneEmbyConnect(
            server_url=self.server_url,
            api_key=self.api_key,
            timeout=self.timeout,
            verify_ssl=self.verify_ssl
        )
        
        logger.info("EmbyConnect Bridge :: Initialized with server: %s" % self.server_url)
    
    def _get_emby_config(self):
        """Extract Emby configuration from Tautulli config."""
        try:
            # Check environment variables first (for testing/development)
            import os
            if os.getenv('EMBY_URL') or os.getenv('EMBY_SERVER_URL'):
                self.server_url = os.getenv('EMBY_URL') or os.getenv('EMBY_SERVER_URL', '')
                self.api_key = os.getenv('EMBY_API_KEY', '')
                self.timeout = int(os.getenv('EMBY_TIMEOUT', '30'))
                self.verify_ssl = os.getenv('EMBY_VERIFY_SSL', 'true').lower() == 'true'
                logger.info("EmbyConnect Bridge :: Using environment configuration: %s" % self.server_url)
                return
            
            # Use Tautulli CONFIG system (primary configuration method)
            self.server_url = plexpy.CONFIG.EMBY_SERVER_URL or ''
            self.api_key = plexpy.CONFIG.EMBY_API_KEY or ''
            self.timeout = plexpy.CONFIG.EMBY_TIMEOUT or 30
            self.verify_ssl = bool(plexpy.CONFIG.EMBY_VERIFY_SSL)
            
            if self.server_url:
                logger.info("EmbyConnect Bridge :: Using Tautulli configuration: %s" % self.server_url)
            else:
                logger.warning("EmbyConnect Bridge :: No Emby server configured. Please set EMBY_SERVER_URL in settings.")
            
        except Exception as e:
            logger.error("EmbyConnect Bridge :: Failed to get configuration: %s" % e)
            # Use safe defaults
            self.server_url = ''
            self.api_key = ''
            self.timeout = 30
            self.verify_ssl = True
    
    def get_server_info(self):
        """Get Emby server information - bridges to standalone method."""
        try:
            result = self.emby_connect.get_server_info()
            if result:
                logger.debug("EmbyConnect Bridge :: Retrieved server info for: %s" % result.get('ServerName', 'Unknown'))
            return result
        except Exception as e:
            logger.error("EmbyConnect Bridge :: Error getting server info: %s" % e)
            return None
    
    def get_current_activity(self):
        """
        Get current activity - main method used by activity_pinger.py
        
        Returns data in format compatible with PmsConnect expectations:
        {
            'sessions': [list of session objects with Tautulli-compatible fields]
        }
        """
        try:
            raw_sessions = self.emby_connect.get_sessions()
            if raw_sessions:
                # Transform sessions to Tautulli format
                transformed_sessions = []
                for session in raw_sessions:
                    try:
                        transformed = self.emby_connect.transform_session_data(session)
                        if transformed:
                            transformed_sessions.append(transformed)
                    except Exception as e:
                        logger.error("EmbyConnect Bridge :: Error transforming session: %s" % e)
                        continue
                
                logger.debug("EmbyConnect Bridge :: Retrieved %d active sessions (%d transformed)" % 
                           (len(raw_sessions), len(transformed_sessions)))
                return {'sessions': transformed_sessions}
            else:
                logger.debug("EmbyConnect Bridge :: No active sessions found")
                return {'sessions': []}
        except Exception as e:
            logger.error("EmbyConnect Bridge :: Error getting current activity: %s" % e)
            return {'sessions': []}
    
    def get_metadata(self, rating_key, media_type=None):
        """Get metadata for a specific item - used by activity handlers."""
        try:
            metadata = self.emby_connect.get_item_details(rating_key)
            if metadata:
                transformed_metadata = self.emby_connect.transform_metadata(metadata)
                logger.debug("EmbyConnect Bridge :: Retrieved metadata for rating_key: %s" % rating_key)
                return transformed_metadata
            return None
        except Exception as e:
            logger.error("EmbyConnect Bridge :: Error getting metadata for %s: %s" % (rating_key, e))
            return None
    
    def get_user_info(self, user_id):
        """Get user information - used by activity processors."""
        try:
            user_info = self.emby_connect.get_user(user_id)
            if user_info:
                logger.debug("EmbyConnect Bridge :: Retrieved user info for: %s" % user_id)
            return user_info
        except Exception as e:
            logger.error("EmbyConnect Bridge :: Error getting user info for %s: %s" % (user_id, e))
            return None
    
    def get_users(self):
        """Get all users - used by user management."""
        try:
            raw_users = self.emby_connect.get_users_list()
            if raw_users:
                # Transform users to Tautulli format
                transformed_users = []
                for user in raw_users:
                    try:
                        transformed = self.emby_connect.transform_user_data(user)
                        if transformed:
                            transformed_users.append(transformed)
                    except Exception as e:
                        logger.error("EmbyConnect Bridge :: Error transforming user: %s" % e)
                        continue
                
                logger.debug("EmbyConnect Bridge :: Retrieved %d users (%d transformed)" % 
                           (len(raw_users), len(transformed_users)))
                return transformed_users
            else:
                logger.debug("EmbyConnect Bridge :: No users found")
                return []
        except Exception as e:
            logger.error("EmbyConnect Bridge :: Error getting users: %s" % e)
            return []
    
    def get_libraries(self):
        """Get all libraries - used by library management."""
        try:
            libraries = self.emby_connect.get_libraries()
            if libraries:
                logger.debug("EmbyConnect Bridge :: Retrieved %d libraries" % len(libraries))
            return libraries
        except Exception as e:
            logger.error("EmbyConnect Bridge :: Error getting libraries: %s" % e)
            return []
    
    def get_library_details(self):
        """
        Get library details in format expected by libraries.py
        Returns list of libraries with section_id, section_name, section_type, etc.
        """
        try:
            raw_libraries = self.emby_connect.get_libraries()
            if not raw_libraries:
                logger.warning("EmbyConnect Bridge :: No libraries found")
                return []
            
            # Transform to Tautulli format
            transformed_libraries = []
            for lib in raw_libraries:
                try:
                    transformed = self.emby_connect.transform_library_data(lib)
                    if transformed:
                        transformed_libraries.append(transformed)
                except Exception as e:
                    logger.error("EmbyConnect Bridge :: Error transforming library: %s" % e)
                    continue
            
            logger.debug("EmbyConnect Bridge :: Retrieved %d library details (%d transformed)" % 
                       (len(raw_libraries), len(transformed_libraries)))
            return transformed_libraries
            
        except Exception as e:
            logger.error("EmbyConnect Bridge :: Error getting library details: %s" % e)
            return []
    
    def test_connection(self):
        """Test connection to Emby server."""
        try:
            server_info = self.get_server_info()
            if server_info:
                logger.info("EmbyConnect Bridge :: Connection test successful")
                return True
            else:
                logger.error("EmbyConnect Bridge :: Connection test failed - no server info")
                return False
        except Exception as e:
            logger.error("EmbyConnect Bridge :: Connection test failed: %s" % e)
            return False


# Compatibility aliases for existing code
class PmsConnect:
    """
    Compatibility wrapper that redirects PmsConnect calls to EmbyConnect.
    
    This allows existing code to work without modification while we transition
    from Plex to Emby. Eventually this can be removed once all references are updated.
    """
    
    def __init__(self):
        logger.warning("PmsConnect :: Redirecting to EmbyConnect for Emby compatibility")
        self.emby_connect = EmbyConnect()
    
    def __getattr__(self, name):
        """Redirect all method calls to EmbyConnect."""
        return getattr(self.emby_connect, name)


def create_emby_connect():
    """Factory function to create EmbyConnect instance."""
    return EmbyConnect()


def create_pms_connect():
    """Factory function that creates EmbyConnect but maintains PmsConnect interface."""
    return PmsConnect()