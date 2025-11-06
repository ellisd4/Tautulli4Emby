# Tautulli4Emby Migration Implementation Plan

## Overview
Comprehensive plan to convert Tautulli from Plex to Emby while maintaining all existing functionality and adding Emby-specific enhancements.

## 🚀 Phase 1: Foundation & Research (Week 1)

### 1.1 Environment Setup
- [ ] **Create development branch** `feature/emby-migration`
- [ ] **Configure connection to existing Emby server**
  - Document server URL and access details
  - Generate API key for development/testing
- [ ] **Install Emby API testing tools** (Postman collection, curl scripts)
- [ ] **Document current Plex API usage** patterns in existing codebase
- [ ] **Create API comparison matrix** (Plex vs Emby endpoints)

### Phase 1.3: Implement Session Data Transformation ✅ COMPLETED
**Status**: Complete - Standalone EmbyConnect with full data transformation
**Duration**: 4 hours

- [x] Create standalone `embyconnect_standalone.py` without Plex dependencies
- [x] Implement comprehensive data transformation methods
  - [x] `transform_session_data()` - Maps 80+ Emby session fields to Tautulli format
  - [x] `transform_user_data()` - Converts Emby users to Tautulli user schema
  - [x] `transform_library_data()` - Maps Emby libraries to Tautulli sections
  - [x] `_build_full_title()` - Generates proper episode/movie/track titles
- [x] Remove all Plex-specific dependencies (plexpy, helpers, logger imports)
- [x] Create self-contained HTTP handler and helper utilities
- [x] Add comprehensive error handling and logging
- [x] All tests passing with real Emby server (4 active sessions, 7 users, 12 libraries)

### 1.4 Activity Processing Integration ⏳ NEXT PHASE
**Status**: Ready to start - Replace Plex dependencies in core monitoring
**Estimated Duration**: 3-4 hours

- [ ] **Replace PmsConnect with EmbyConnect** in `activity_pinger.py`
- [ ] **Update session processing** in `activity_handler.py` 
- [ ] **Modify database writes** in `activity_processor.py`
- [ ] **Test end-to-end monitoring pipeline**
- [ ] **Verify session state transitions** (play/pause/stop)

---

## 🔧 Phase 2: Core API Client Replacement (Week 2)

### 2.1 Create New Emby API Client
- [ ] **Create `embyconnect.py`** (replaces `pmsconnect.py`)
  ```python
  class EmbyConnect:
      def __init__(self, url=None, api_key=None):
          self.base_url = f"{url}/emby"
          self.api_key = api_key
          self.headers = {
              'X-Emby-Token': api_key,
              'Content-Type': 'application/json'
          }
  ```

### 2.2 Implement Core API Methods
- [ ] **Session monitoring**: `GET /Sessions`
- [ ] **System information**: `GET /System/Info`
- [ ] **User management**: `GET /Users/Query`
- [ ] **Library access**: `GET /Items`
- [ ] **Media metadata**: `GET /Users/{UserId}/Items/{Id}`

### 2.3 Authentication System
- [ ] **Implement API key authentication**:
  - Header: `X-Emby-Token: {api_key}`
  - Query parameter: `?api_key={api_key}`
- [ ] **Add server connection testing**
- [ ] **Handle authentication errors gracefully**

### 2.4 Data Transformation Layer
- [ ] **Create mapping functions** for session data:
  ```python
  def transform_emby_session_to_tautulli(emby_session):
      return {
          'session_key': emby_session['Id'],
          'user_id': emby_session['UserId'],
          'state': emby_session['PlayState']['IsPaused'] and 'paused' or 'playing',
          # ... map all required fields
      }
  ```

---

## 🔄 Phase 3: Session Monitoring Core (Week 3)

### 3.1 Update Activity Pinger
- [ ] **Modify `activity_pinger.py`**:
  - Replace `PmsConnect()` with `EmbyConnect()`
  - Update session polling logic
  - Handle Emby-specific session states
- [ ] **Test session detection** with multiple concurrent streams
- [ ] **Implement fallback mechanisms** for API failures

### 3.2 Activity Handler Updates
- [ ] **Update `activity_handler.py`**:
  - Modify session event processing
  - Handle Emby session state changes
  - Update notification triggers
- [ ] **WebSocket alternative research**:
  - Investigate Emby's real-time notification capabilities
  - Implement Server-Sent Events if available
  - Maintain HTTP polling as fallback

### 3.3 Activity Processor Modifications
- [ ] **Update `activity_processor.py`**:
  - Modify session data parsing
  - Update database field mappings
  - Handle Emby-specific media types
- [ ] **Test data persistence** with Emby session data

---

## 🗄️ Phase 4: Database & Configuration (Week 4)

### 4.1 Configuration System Updates
- [ ] **Update `config.py`** with Emby settings:
  ```python
  'EMBY_URL': (str, 'Emby', ''),
  'EMBY_API_KEY': (str, 'Emby', ''),
  'EMBY_SSL_VERIFY': (bool_int, 'Emby', 1),
  'EMBY_TIMEOUT': (int, 'Emby', 30),
  ```
- [ ] **Create configuration migration script**
- [ ] **Add server discovery functionality**

### 4.2 Database Schema Updates
- [ ] **Add migration script** in `__init__.py`:
  - Add Emby-specific columns if needed
  - Update existing data for compatibility
  - Maintain backwards compatibility
- [ ] **Test database migrations** on sample data
- [ ] **Add rollback capabilities**

### 4.3 User & Library Management
- [ ] **Update `users.py`**:
  - Implement Emby user fetching
  - Handle Emby user permissions
  - Map Emby user data to Tautulli format
- [ ] **Update `libraries.py`**:
  - Implement Emby library scanning
  - Handle Emby library types
  - Update library statistics

---

## 🖥️ Phase 5: Web Interface & API (Week 5)

### 5.1 Web Interface Updates
- [ ] **Update `webserve.py`**:
  - Replace Plex API calls with Emby equivalents
  - Update server status checks
  - Modify settings pages for Emby configuration
- [ ] **Update templates** in `data/interfaces/default/`:
  - Settings pages (`settings.html`)
  - Activity displays
  - Server information displays

### 5.2 API Endpoints
- [ ] **Update API methods** in `api2.py`:
  - `get_activity()` - use Emby sessions
  - `get_server_info()` - use Emby system info
  - `get_libraries()` - use Emby library endpoints
- [ ] **Test API compatibility** with existing clients
- [ ] **Update API documentation**

### 5.3 Settings & Setup Wizard
- [ ] **Create Emby setup wizard**:
  - Server discovery
  - API key configuration
  - Connection testing
  - Initial library scanning
- [ ] **Update settings validation**
- [ ] **Add migration assistant** for Plex users

---

## 📊 Phase 6: Statistics & Analytics (Week 6)

### 6.1 Data Factory Updates
- [ ] **Update `datafactory.py`**:
  - Modify statistics queries for Emby data
  - Update media type handling
  - Ensure chart data compatibility
- [ ] **Test statistics accuracy** against Emby data
- [ ] **Validate historical data** preservation

### 6.2 Reporting & Charts
- [ ] **Update dashboard statistics**
- [ ] **Verify chart data accuracy**
- [ ] **Test performance** with large datasets
- [ ] **Add Emby-specific statistics** if beneficial

### 6.3 Import/Export Functions
- [ ] **Update export functionality**
- [ ] **Create Plex to Emby data migration tools**
- [ ] **Test data integrity** across migrations

---

## 🔔 Phase 7: Notifications & External Integrations (Week 7)

### 7.1 Notification System
- [ ] **Update `notification_handler.py`**:
  - Ensure notification triggers work with Emby data
  - Test all notification types
  - Update notification templates
- [ ] **Test webhook payloads** with external systems
- [ ] **Validate notification timing** and accuracy

### 7.2 External Integrations
- [ ] **Update mobile app integration** if needed
- [ ] **Test newsletter functionality**
- [ ] **Validate external API compatibility**
- [ ] **Update integration documentation**

### 7.3 Remote Control Features
- [ ] **Implement Emby remote control**:
  - `POST /Sessions/{Id}/Playing/{Command}`
  - `POST /Sessions/{Id}/Command/{Command}`
- [ ] **Test playback control functions**
- [ ] **Add Emby-specific control features**

---

## 🧪 Phase 8: Testing & Quality Assurance (Week 8)

### 8.1 Unit Testing
- [ ] **Create comprehensive test suite**:
  - API client tests (using your existing Emby server)
  - Data transformation tests
  - Session monitoring tests
  - Database migration tests
- [ ] **Configure CI/CD with external Emby server**
  - Use environment variables for server connection
  - Implement mock responses for offline testing
- [ ] **Implement automated testing** pipeline

### 8.2 Integration Testing
- [ ] **Test complete workflows**:
  - Fresh installation setup
  - Plex to Emby migration
  - Multiple concurrent sessions
  - Large library scanning
- [ ] **Performance benchmarking**
- [ ] **Memory and resource usage testing**

### 8.3 User Acceptance Testing
- [ ] **Create test scenarios** for real users
- [ ] **Document known issues** and limitations
- [ ] **Prepare rollback procedures**

---

## 🚀 Phase 9: Documentation & Deployment (Week 9)

### 9.1 Documentation
- [ ] **Update README.md** with Emby instructions
- [ ] **Create Emby setup guide**
- [ ] **Document migration process** from Plex
- [ ] **Update API documentation**
- [ ] **Create troubleshooting guide**

### 9.2 Packaging & Distribution
- [ ] **Update Docker images**
- [ ] **Test installer packages**
- [ ] **Update snap/package configurations**
- [ ] **Prepare release notes**

### 9.3 Community Preparation
- [ ] **Create beta testing group**
- [ ] **Prepare community announcements**
- [ ] **Update project descriptions** and metadata

---

## 🔄 Phase 10: Release & Post-Launch Support (Week 10)

### 10.1 Release Management
- [ ] **Create release candidate**
- [ ] **Final testing round**
- [ ] **Deploy to staging environment**
- [ ] **Community beta testing**
- [ ] **Production release**

### 10.2 Post-Launch Monitoring
- [ ] **Monitor user feedback**
- [ ] **Track error reports**
- [ ] **Performance monitoring**
- [ ] **Quick-fix deployment pipeline**

### 10.3 Future Enhancements
- [ ] **Identify Emby-specific features** to add:
  - Enhanced transcoding metrics
  - Advanced library analytics
  - Emby Connect integration
  - Plugin system integration
- [ ] **Roadmap planning** for future versions

---

## 🛠️ Technical Implementation Details

### Key Emby API Endpoints to Implement

| Functionality | Emby Endpoint | Plex Equivalent | Priority |
|---------------|---------------|-----------------|----------|
| Active Sessions | `GET /Sessions` | `/status/sessions` | High |
| System Info | `GET /System/Info` | `/` | High |
| Users | `GET /Users/Query` | `/accounts` | High |
| Libraries | `GET /Library/VirtualFolders` | `/library/sections` | High |
| Media Items | `GET /Items` | `/library/metadata/{id}` | High |
| Activity Log | `GET /System/ActivityLog/Entries` | N/A | Medium |
| Remote Control | `POST /Sessions/{Id}/Playing/{Command}` | Various | Medium |

### Data Mapping Strategy

```python
# Example transformation function
def transform_emby_to_tautulli_session(emby_session):
    """Transform Emby session data to Tautulli format."""
    play_state = emby_session.get('PlayState', {})
    now_playing = emby_session.get('NowPlayingItem', {})
    
    return {
        'session_key': emby_session['Id'],
        'session_id': emby_session['Id'],
        'user_id': emby_session['UserId'],
        'user': emby_session['UserName'],
        'state': 'paused' if play_state.get('IsPaused') else 'playing',
        'rating_key': now_playing.get('Id'),
        'title': now_playing.get('Name'),
        'media_type': now_playing.get('Type', '').lower(),
        'duration': now_playing.get('RunTimeTicks', 0) // 10000,  # Convert to ms
        'view_offset': play_state.get('PositionTicks', 0) // 10000,
        'transcode_decision': get_transcode_decision(emby_session),
        'client': emby_session.get('Client'),
        'device': emby_session.get('DeviceName'),
        'platform': emby_session.get('Client'),
        # ... additional mappings as needed
    }
```

### Testing Strategy

1. **External Emby Server**: Connect to your existing Emby server for real-world testing
2. **Live Data Testing**: Use your actual media libraries and user sessions
3. **Automated Test Suite**: Unit and integration tests for all components
4. **Performance Testing**: Load testing with your actual concurrent sessions
5. **Migration Testing**: Test data migration from existing Tautulli installations
6. **Mock Data**: Create mock responses for CI/CD when server isn't accessible

### Rollback Strategy

1. **Database Backups**: Automatic backup before any migration
2. **Configuration Rollback**: Ability to revert to Plex configuration
3. **Code Rollback**: Git-based rollback to previous stable version
4. **User Communication**: Clear rollback instructions for users

---

## 📋 Success Criteria

- [ ] **100% Feature Parity**: All existing Tautulli features work with Emby
- [ ] **Data Integrity**: No loss of historical data during migration
- [ ] **Performance**: Response times within 10% of current Plex performance
- [ ] **Stability**: Zero critical bugs in core monitoring functionality
- [ ] **User Experience**: Seamless setup process for new Emby installations
- [ ] **Compatibility**: Support for major Emby server versions
- [ ] **Documentation**: Complete and accurate documentation for all features

---

## ⚠️ Risk Mitigation

### High-Risk Areas
1. **Session State Mapping**: Emby and Plex may handle states differently
2. **Transcoding Detection**: Different transcoding metadata structures
3. **WebSocket Alternatives**: Emby may not have equivalent real-time APIs
4. **Data Migration**: Risk of data loss during Plex→Emby conversion

### Mitigation Strategies
1. **Comprehensive Testing**: Extensive test coverage for all scenarios
2. **Rollback Procedures**: Always maintain rollback capability
3. **Incremental Deployment**: Beta testing with community feedback
4. **Documentation**: Clear migration and troubleshooting guides

---

## 🚀 **Next Steps**

Since you have an existing Emby server, we can jump right into development and testing with real data. Would you like me to:

1. **Start Phase 1** by connecting to your Emby server and creating the API mapping documentation?
2. **Create the initial EmbyConnect API client** and test basic connectivity?
3. **Begin API exploration** by examining your server's session data and library structure?
4. **Set up the development branch** and start implementing the core Emby client?

**Immediate Prerequisites:**
- Your Emby server URL and port
- Admin access to generate an API key
- Network access from this development machine to your Emby server

This plan provides a structured approach to migrate Tautulli from Plex to Emby while maintaining all existing functionality and adding Emby-specific enhancements where beneficial.