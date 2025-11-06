# Plex to Emby API Mapping Documentation

## Overview
This document maps existing Plex API usage in Tautulli to equivalent Emby API endpoints to facilitate the migration process.

## Authentication
| Aspect | Plex | Emby |
|--------|------|------|
| Method | X-Plex-Token header | X-Emby-Token header or api_key query param |
| Token Location | `plexpy.CONFIG.PMS_TOKEN` | `emby_api_key` (new config) |
| Authentication Test | `GET /` | `GET /System/Info` |

## Core API Endpoints Mapping

### Session Monitoring (Critical - High Priority)
| Function | Plex Endpoint | Emby Endpoint | Status | Notes |
|----------|---------------|---------------|---------|-------|
| Active Sessions | `GET /status/sessions` | `GET /Sessions` | ✅ Mapped | Core monitoring functionality |
| Session Details | Included in sessions | `GET /Sessions/{Id}` | ✅ Mapped | More detailed in Emby |

### System Information (High Priority)
| Function | Plex Endpoint | Emby Endpoint | Status | Notes |
|----------|---------------|---------------|---------|-------|
| Server Info | `GET /` | `GET /System/Info` | ✅ Mapped | Server status and version |
| Server Preferences | `GET /:/prefs` | `GET /System/Configuration` | ✅ Mapped | Server settings |
| Server Identity | `GET /identity` | `GET /System/Info/Public` | ✅ Mapped | Public server info |

### User Management (High Priority)
| Function | Plex Endpoint | Emby Endpoint | Status | Notes |
|----------|---------------|---------------|---------|-------|
| Users List | `GET /accounts` | `GET /Users/Query` | ✅ Mapped | All users |
| User Details | `GET /accounts/{id}` | `GET /Users/{Id}` | ✅ Mapped | Individual user info |
| User Authentication | `POST /users/sign_in.xml` | `POST /Users/AuthenticateByName` | ✅ Mapped | User login |

### Library Management (High Priority)
| Function | Plex Endpoint | Emby Endpoint | Status | Notes |
|----------|---------------|---------------|---------|-------|
| Libraries List | `GET /library/sections` | `GET /Library/VirtualFolders` | ✅ Mapped | Library sections |
| Library Contents | `GET /library/sections/{id}/all` | `GET /Users/{UserId}/Items` | ✅ Mapped | Requires user context |
| Recently Added | `GET /library/recentlyAdded` | `GET /Users/{UserId}/Items/Latest` | ✅ Mapped | Recent additions |

### Media Metadata (High Priority)
| Function | Plex Endpoint | Emby Endpoint | Status | Notes |
|----------|---------------|---------------|---------|-------|
| Item Details | `GET /library/metadata/{id}` | `GET /Users/{UserId}/Items/{Id}` | ✅ Mapped | Requires user context |
| Item Children | `GET /library/metadata/{id}/children` | `GET /Users/{UserId}/Items/{Id}/Items` | ✅ Mapped | Episodes, tracks, etc. |

### Activity & History (Medium Priority)
| Function | Plex Endpoint | Emby Endpoint | Status | Notes |
|----------|---------------|---------------|---------|-------|
| Activity History | Custom Tautulli tracking | `GET /System/ActivityLog/Entries` | 🆕 New | Emby has built-in activity log |
| Play History | Custom Tautulli tracking | Custom Tautulli tracking | ➡️ Unchanged | Continue using Tautulli's tracking |

### Remote Control (Medium Priority)
| Function | Plex Endpoint | Emby Endpoint | Status | Notes |
|----------|---------------|---------------|---------|-------|
| Play Control | `GET/POST /player/playback/*` | `POST /Sessions/{Id}/Playing/{Command}` | ✅ Mapped | Play, pause, stop |
| Navigation | `GET/POST /player/navigation/*` | `POST /Sessions/{Id}/Command/{Command}` | ✅ Mapped | Navigate interface |
| Send Message | `GET /player/application/displayMessage` | `POST /Sessions/{Id}/Message` | ✅ Mapped | Display messages |

## Data Structure Mapping

### Session Data Fields
| Tautulli Field | Plex Source | Emby Source | Transformation |
|----------------|-------------|-------------|----------------|
| `session_key` | `sessionKey` | `Id` | Direct mapping |
| `user_id` | `User.id` | `UserId` | Direct mapping |
| `user` | `User.title` | `UserName` | Direct mapping |
| `state` | `Player.state` | `PlayState.IsPaused` | Convert boolean to string |
| `rating_key` | `ratingKey` | `NowPlayingItem.Id` | Direct mapping |
| `title` | `title` | `NowPlayingItem.Name` | Direct mapping |
| `media_type` | `type` | `NowPlayingItem.Type` | Convert to lowercase |
| `duration` | `duration` | `NowPlayingItem.RunTimeTicks / 10000` | Convert ticks to ms |
| `view_offset` | `viewOffset` | `PlayState.PositionTicks / 10000` | Convert ticks to ms |
| `transcode_decision` | `TranscodeSession.videoDecision` | `TranscodingInfo.IsVideoDirect` | Invert boolean logic |

### Media Item Fields
| Tautulli Field | Plex Source | Emby Source | Transformation |
|----------------|-------------|-------------|----------------|
| `rating_key` | `ratingKey` | `Id` | Direct mapping |
| `parent_rating_key` | `parentRatingKey` | `ParentId` | Direct mapping |
| `grandparent_rating_key` | `grandparentRatingKey` | `SeriesId` | Direct mapping |
| `title` | `title` | `Name` | Direct mapping |
| `year` | `year` | `ProductionYear` | Direct mapping |
| `media_index` | `index` | `IndexNumber` | Direct mapping |
| `parent_media_index` | `parentIndex` | `ParentIndexNumber` | Direct mapping |

## File Mapping - Where Changes Are Needed

### Core Files to Modify
1. **`plexpy/pmsconnect.py`** → Create **`plexpy/embyconnect.py`**
   - Replace HTTP client with Emby API calls
   - Update authentication headers
   - Transform response data structures

2. **`plexpy/activity_pinger.py`**
   - Replace `PmsConnect()` calls with `EmbyConnect()`
   - Update session parsing logic
   - Handle Emby-specific session states

3. **`plexpy/activity_handler.py`**
   - Update session event processing
   - Modify state change detection
   - Update notification triggers

4. **`plexpy/activity_processor.py`**
   - Update session data transformation
   - Modify database field mappings
   - Handle Emby-specific media types

5. **`plexpy/config.py`**
   - Add Emby server configuration options
   - Replace Plex settings with Emby equivalents

### Configuration Changes
```python
# New Emby configuration options to add
'EMBY_URL': (str, 'Emby', ''),
'EMBY_API_KEY': (str, 'Emby', ''),
'EMBY_SSL_VERIFY': (bool_int, 'Emby', 1),
'EMBY_TIMEOUT': (int, 'Emby', 30),
'EMBY_SERVER_NAME': (str, 'Emby', ''),
```

## Testing Strategy

### Phase 1 Testing Goals
- [ ] Verify API connectivity to Emby server
- [ ] Test authentication with API key
- [ ] Validate session data retrieval
- [ ] Confirm media metadata access
- [ ] Test user information retrieval

### Test Scenarios
1. **Connection Test**: Basic API connectivity and authentication
2. **Session Monitoring**: Retrieve active sessions during playback
3. **Media Library**: Access library structure and metadata
4. **User Management**: Retrieve user list and details
5. **System Information**: Get server info and status

## Implementation Priority

### Phase 1 (This Week)
- [x] Create development branch
- [x] Document API mappings
- [ ] Test Emby server connectivity
- [ ] Generate API key for development
- [ ] Create basic EmbyConnect class

### Phase 2 (Next Week)
- [ ] Implement core EmbyConnect methods
- [ ] Create data transformation functions
- [ ] Build session monitoring pipeline
- [ ] Test with real Emby data

## Notes & Considerations

### Advantages of Emby API
- More detailed transcoding information
- Built-in activity logging
- Simpler authentication mechanism
- Better documented API structure

### Potential Challenges
- Session state handling differences
- User context requirements for some endpoints
- WebSocket alternatives (if needed)
- Data migration from existing Tautulli installations

### Migration Strategy
1. **Parallel Development**: Keep Plex functionality while building Emby
2. **Configuration Toggle**: Allow switching between Plex and Emby
3. **Data Preservation**: Ensure no loss of historical data
4. **Rollback Capability**: Maintain ability to revert changes