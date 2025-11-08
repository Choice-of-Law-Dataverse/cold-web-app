# Database Connection Management - Best Practices Implementation

## Overview

This document describes the improvements made to database and HTTP connection management in the backend application to follow best practices.

## Problems Addressed

### 1. Multiple Database Engine Instances
**Before:** Each service (`SearchService`, `LandingPageService`, `SitemapService`) created its own SQLAlchemy engine instance, leading to:
- Inefficient resource usage
- Multiple connection pools competing for database connections
- No centralized control over connection lifecycle

**After:** Single `DatabaseManager` singleton that all services use, ensuring:
- One connection pool shared across all services
- Centralized lifecycle management
- Efficient resource utilization

### 2. No Connection Pooling Configuration
**Before:** Database engines were created without any pooling configuration:
```python
self.engine = sa.create_engine(connection_string)
```

**After:** Properly configured connection pooling:
```python
self.engine = sa.create_engine(
    connection_string,
    poolclass=QueuePool,
    pool_size=5,              # Maintain 5 persistent connections
    max_overflow=10,          # Allow up to 10 additional connections
    pool_timeout=30,          # Wait 30s for connection from pool
    pool_recycle=3600,        # Recycle connections after 1 hour
    pool_pre_ping=True,       # Test connections before use
)
```

### 3. HTTP Connection Management
**Before:** `NocoDBService` created new HTTP connections for every API call:
```python
resp = requests.get(url, headers=self.headers)
```

**After:** Reuses HTTP connections via session pooling:
```python
self.session = http_session_manager.get_session()
resp = self.session.get(url, headers=self.headers)
```

### 4. No Lifecycle Management
**Before:** No cleanup of database connections on application shutdown.

**After:** Proper startup and shutdown handling:
```python
@app.on_event("startup")
async def startup_event():
    db_manager.initialize(...)
    http_session_manager.initialize(...)

@app.on_event("shutdown")
async def shutdown_event():
    db_manager.dispose()
    http_session_manager.close()
```

## Architecture

### Singleton Managers

#### DatabaseManager
- **Purpose:** Manages the main database connection pool
- **Configuration:**
  - Pool size: 5 connections
  - Max overflow: 10 additional connections
  - Pool recycle: 3600 seconds (1 hour)
  - Pre-ping enabled: Validates connections before use

#### SuggestionsDBManager
- **Purpose:** Manages suggestions database connection pool
- **Configuration:**
  - Pool size: 3 connections (lower traffic expected)
  - Max overflow: 5 additional connections
  - Pool recycle: 3600 seconds
  - Pre-ping enabled

#### HTTPSessionManager
- **Purpose:** Manages HTTP connection pooling for API clients
- **Configuration:**
  - Pool connections: 10
  - Pool max size: 20
  - Max retries: 3
  - Retry backoff factor: 0.3
  - Retry on status codes: 429, 500, 502, 503, 504

## Usage

### Database Access

Services that need database access continue to use the `Database` class:

```python
from app.services.database import Database
from app.config import config

class MyService:
    def __init__(self):
        self.db = Database(config.SQL_CONN_STRING)
    
    def query_data(self):
        return self.db.execute_query("SELECT * FROM my_table")
```

The `Database` class now automatically uses the singleton `DatabaseManager` under the hood.

### HTTP Requests via NocoDB

The `NocoDBService` automatically uses the `HTTPSessionManager`:

```python
from app.services.nocodb import NocoDBService

service = NocoDBService(base_url, api_token)
data = service.get_row("table_name", "record_id")
```

No code changes required in services using `NocoDBService`.

## Benefits

1. **Resource Efficiency:**
   - Reuses database connections instead of creating new ones
   - Reuses HTTP connections, avoiding TCP handshake overhead

2. **Improved Performance:**
   - Connection pooling reduces latency
   - Pre-ping prevents using stale connections
   - HTTP connection reuse speeds up API calls

3. **Better Reliability:**
   - Automatic retry strategy for HTTP requests
   - Connection validation before use
   - Graceful handling of connection failures

4. **Scalability:**
   - Controlled connection limits prevent overwhelming database
   - Max overflow handles traffic spikes
   - Connection recycling prevents long-lived connection issues

5. **Maintainability:**
   - Centralized configuration
   - Easy to tune pooling parameters
   - Clear separation of concerns

## Configuration

Connection pool settings can be adjusted in `app/main.py`:

```python
@app.on_event("startup")
async def startup_event():
    # Main database
    db_manager.initialize(
        connection_string=config.SQL_CONN_STRING,
        pool_size=5,        # Adjust based on load
        max_overflow=10,    # Adjust based on peak traffic
        pool_recycle=3600,  # Adjust based on database timeouts
    )
    
    # HTTP session
    http_session_manager.initialize(
        pool_connections=10,  # Adjust based on API endpoints
        pool_maxsize=20,      # Adjust based on concurrent requests
        max_retries=3,        # Adjust based on reliability needs
    )
```

## Testing

Run the verification script to ensure proper functioning:

```bash
cd backend
python3 tests/verify_connection_management.py
```

Or run the full test suite:

```bash
cd backend
python3 -m pytest tests/test_connection_managers.py tests/test_database_integration.py -v
```

## Migration Notes

This implementation is **backwards compatible**. Existing code continues to work without modifications:

- Services can still instantiate `Database` with a connection string
- `NocoDBService` works without changes
- `SuggestionService` works without changes

The main difference is that all instances now share the same underlying connection pools.

## Best Practices Applied

1. ✅ **Connection Pooling:** Configured with appropriate sizes
2. ✅ **Singleton Pattern:** Ensures single pool per database
3. ✅ **Pool Pre-ping:** Validates connections before use
4. ✅ **Connection Recycling:** Prevents stale connections
5. ✅ **Lifecycle Management:** Proper startup/shutdown handling
6. ✅ **HTTP Session Reuse:** Avoids TCP connection overhead
7. ✅ **Retry Strategy:** Handles transient failures
8. ✅ **Bounded Resources:** Limits prevent resource exhaustion

## Monitoring

To monitor connection pool usage, SQLAlchemy provides built-in pool events. You can enable logging:

```python
import logging
logging.getLogger('sqlalchemy.pool').setLevel(logging.DEBUG)
```

This will log:
- Connection checkouts/checkins
- Pool size changes
- Connection recycling events

## Future Improvements

Potential enhancements for consideration:

1. **Metrics Collection:** Add Prometheus metrics for pool usage
2. **Dynamic Pool Sizing:** Adjust pool size based on load
3. **Connection Health Checks:** Periodic validation of pooled connections
4. **Circuit Breaker:** Prevent cascading failures
5. **Connection Tracing:** Detailed connection lifecycle logging
