# Tautulli4Emby Copilot Instructions

## Architecture Overview

This is a **media server monitoring application** (originally for Plex, being adapted for Emby) with a **multi-layered event-driven architecture**:

- **Core Data Flow**: `pmsconnect.py` → `activity_pinger.py` → `activity_handler.py` → `activity_processor.py` → SQLite database
- **Web Layer**: CherryPy web server in `webserve.py` with Mako templates in `data/interfaces/default/`
- **Real-time**: WebSocket connection (`web_socket.py`) + HTTP polling for session monitoring
- **Storage**: SQLite with custom ORM-like patterns in `database.py`

## Key Components & Data Flow

### Session Monitoring Pipeline
1. **`PmsConnect`** (`pmsconnect.py`) - HTTP client for Plex/Emby API calls
2. **`activity_pinger.py`** - Scheduled polling (every ~5s) to check active sessions
3. **`ActivityHandler`** (`activity_handler.py`) - Processes websocket timeline events 
4. **`ActivityProcessor`** (`activity_processor.py`) - Writes session data to temp tables and history

### Critical Data Structures
- **Session objects**: Temporary tracking in `sessions` table, permanent in `session_history`
- **Raw stream info**: JSON blob stored in `raw_stream_info` column for metadata preservation
- **State tracking**: `playing`, `paused`, `stopped`, `buffering` states with transition notifications

## Development Patterns

### Database Layer
- **Custom SQLite wrapper**: Use `database.MonitorDatabase()` for all DB operations
- **Upsert pattern**: `db.upsert(table_name, value_dict, key_dict)` for insert-or-update
- **Transaction handling**: Database auto-commits, use `with db_lock:` for thread safety

```python
# Standard DB pattern
db = database.MonitorDatabase()
result = db.select_single("SELECT * FROM sessions WHERE session_key = ?", [session_key])
```

### Configuration System
- **Global config**: `plexpy.CONFIG` object loaded from `config.ini`
- **Config definitions**: Centralized in `config.py` with type validation
- **Runtime updates**: Config changes immediately reflected, saved via `CONFIG.write()`

### Notification System
- **Queue-based**: `plexpy.NOTIFY_QUEUE.put({'stream_data': session, 'notify_action': 'on_start'})`
- **Event types**: `on_start`, `on_stop`, `on_pause`, `on_resume`, `on_watched`, `on_error`
- **Handler**: `notification_handler.py` processes queue asynchronously

### API Patterns
- **Decorators**: `@requireAuth()`, `@addtoapi()` for web endpoints
- **CherryPy**: All web endpoints in `WebInterface` class with `@cherrypy.expose`
- **JSON responses**: Use `@cherrypy.tools.json_out()` for API endpoints

```python
@cherrypy.expose
@cherrypy.tools.json_out()
@requireAuth()
@addtoapi()
def get_activity(self, session_key=None, **kwargs):
    # API endpoint pattern
```

## Critical Developer Knowledge

### Session Lifecycle
- **WebSocket events**: Drive real-time updates via `ActivityHandler.process()`
- **Polling fallback**: `activity_pinger.check_active_sessions()` every monitoring interval
- **State persistence**: Sessions stored in temp table, written to history on completion
- **Metadata caching**: Uses `session_key` as cache key, cleared on session changes

### Data Consistency
- **Session keys**: Unique identifiers from Plex/Emby, used throughout as primary reference
- **Rating keys**: Media item identifiers, can change during session (live TV)
- **Grouping logic**: `ActivityProcessor.group_history()` merges related sessions

### Thread Safety
- **Global locks**: `monitor_lock` in `activity_pinger.py`, `db_lock` in `database.py`
- **Scheduler**: `plexpy.SCHED` (APScheduler) for background tasks
- **Queue processing**: Notification queue processed in separate thread

## Key Files for Common Tasks

- **Add new API endpoint**: `webserve.py` (add method to `WebInterface`)
- **Modify session tracking**: `activity_processor.py` (session data structure)
- **Add configuration option**: `config.py` (_CONFIG_DEFINITIONS)
- **Database schema changes**: `__init__.py` (database upgrade section ~line 2200)
- **Add notification trigger**: `activity_handler.py` (event methods like `on_start`)

## Essential Startup Flow

1. `Tautulli.py` → `plexpy.__init__.py` (global initialization)
2. Database setup/upgrade in `initialize()` 
3. Config loading from `config.ini`
4. Web server start via `webstart.py`
5. Background scheduler + monitoring threads
6. WebSocket connection establishment

## Debugging Entry Points

- **Session issues**: Check `activity_pinger.py` logging + `sessions` table
- **WebSocket problems**: `web_socket.py` with websocket debug logging
- **Database locks**: Look for `db_lock` contention in logs
- **API failures**: `pmsconnect.py` HTTP client + `request_handler` errors