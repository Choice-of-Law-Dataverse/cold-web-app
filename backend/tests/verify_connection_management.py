#!/usr/bin/env python3
"""
Verification script to test database connection management.
This script verifies that the singleton managers work correctly.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.db_manager import db_manager, suggestions_db_manager
from app.services.http_session_manager import http_session_manager
from app.services.database import Database


def test_database_manager_singleton():
    """Test that DatabaseManager is a singleton."""
    from app.services.db_manager import DatabaseManager

    m1 = DatabaseManager()
    m2 = DatabaseManager()
    assert m1 is m2, "DatabaseManager is not a singleton!"
    print("✓ DatabaseManager singleton verified")


def test_suggestions_db_manager_singleton():
    """Test that SuggestionsDBManager is a singleton."""
    from app.services.db_manager import SuggestionsDBManager

    m1 = SuggestionsDBManager()
    m2 = SuggestionsDBManager()
    assert m1 is m2, "SuggestionsDBManager is not a singleton!"
    print("✓ SuggestionsDBManager singleton verified")


def test_http_session_manager_singleton():
    """Test that HTTPSessionManager is a singleton."""
    from app.services.http_session_manager import HTTPSessionManager

    m1 = HTTPSessionManager()
    m2 = HTTPSessionManager()
    assert m1 is m2, "HTTPSessionManager is not a singleton!"
    print("✓ HTTPSessionManager singleton verified")


def test_database_manager_initialization():
    """Test DatabaseManager initialization and disposal."""
    # Reset state
    db_manager._engine = None
    db_manager._session_factory = None

    # Initialize
    db_manager.initialize(connection_string="sqlite:///:memory:")
    assert db_manager.is_initialized, "DatabaseManager failed to initialize!"
    print("✓ DatabaseManager initialization verified")

    # Get session
    session = db_manager.get_session()
    assert session is not None, "Failed to get session!"
    session.close()
    print("✓ DatabaseManager session creation verified")

    # Dispose
    db_manager.dispose()
    assert not db_manager.is_initialized, "DatabaseManager failed to dispose!"
    print("✓ DatabaseManager disposal verified")


def test_http_session_manager_initialization():
    """Test HTTPSessionManager initialization."""
    # Reset state
    http_session_manager._session = None

    # Initialize
    http_session_manager.initialize()
    assert http_session_manager.is_initialized, "HTTPSessionManager failed to initialize!"
    print("✓ HTTPSessionManager initialization verified")

    # Get session
    session = http_session_manager.get_session()
    assert session is not None, "Failed to get HTTP session!"
    print("✓ HTTPSessionManager session creation verified")

    # Close
    http_session_manager.close()
    assert not http_session_manager.is_initialized, "HTTPSessionManager failed to close!"
    print("✓ HTTPSessionManager closure verified")


def test_database_uses_manager():
    """Test that Database class uses the singleton manager."""
    # Reset state
    db_manager._engine = None
    db_manager._session_factory = None

    # Create Database instance
    db = Database(connection_string="sqlite:///:memory:")
    assert db_manager.is_initialized, "Database didn't initialize the manager!"
    print("✓ Database class uses DatabaseManager")

    # Create another instance - should reuse same engine
    db2 = Database(connection_string="sqlite:///:memory:")
    assert db.engine is db2.engine, "Database instances don't share engine!"
    print("✓ Multiple Database instances share the same engine")

    # Cleanup
    db_manager.dispose()


def test_database_query_execution():
    """Test that Database can execute queries using the manager."""
    # Reset state
    db_manager._engine = None
    db_manager._session_factory = None

    # Create Database instance
    db = Database(connection_string="sqlite:///:memory:")

    # Create a test table
    from sqlalchemy import text

    with db_manager.get_session() as session:
        session.execute(text("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)"))
        session.execute(text("INSERT INTO test VALUES (1, 'test1')"))
        session.execute(text("INSERT INTO test VALUES (2, 'test2')"))
        session.commit()

    # Query using Database
    results = db.execute_query("SELECT * FROM test ORDER BY id")
    assert results is not None, "Query returned None!"
    assert len(results) == 2, f"Expected 2 results, got {len(results)}"
    assert results[0]["name"] == "test1", "First result incorrect!"
    assert results[1]["name"] == "test2", "Second result incorrect!"
    print("✓ Database query execution verified")

    # Cleanup
    db_manager.dispose()


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Connection Management Verification")
    print("=" * 60)
    print()

    tests = [
        test_database_manager_singleton,
        test_suggestions_db_manager_singleton,
        test_http_session_manager_singleton,
        test_database_manager_initialization,
        test_http_session_manager_initialization,
        test_database_uses_manager,
        test_database_query_execution,
    ]

    failed = []
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed.append((test.__name__, e))

    print()
    print("=" * 60)
    if failed:
        print(f"FAILED: {len(failed)} test(s) failed")
        for name, error in failed:
            print(f"  - {name}: {error}")
        sys.exit(1)
    else:
        print("SUCCESS: All verification tests passed!")
        print("=" * 60)
        sys.exit(0)


if __name__ == "__main__":
    main()
