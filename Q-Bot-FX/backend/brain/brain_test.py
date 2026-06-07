"""Brain database tests."""

from __future__ import annotations

import tempfile
from pathlib import Path

from backend.brain.brain_database import BrainDatabaseManager, get_brain
from backend.brain.brain_export import export_brain, import_brain
from backend.brain.brain_migrate import migrate_legacy_json


def test_create_db() -> bool:
    """Test database creation."""
    try:
        brain = get_brain()
        status = brain.get_brain_status()
        assert status["databases"] == 4, "Should have 4 databases"
        print("✅ Test: Create DB - PASS")
        return True
    except Exception as e:
        print(f"❌ Test: Create DB - FAIL: {e}")
        return False


def test_write_read() -> bool:
    """Test write and read operations."""
    try:
        brain = get_brain()

        test_data = {"key1": "value1", "nested": {"key2": "value2"}}
        brain.save_memory("test", "test_key", test_data)

        loaded = brain.load_memory("test", "test_key")
        assert loaded == test_data, f"Data mismatch: {loaded} != {test_data}"

        print("✅ Test: Write/Read - PASS")
        return True
    except Exception as e:
        print(f"❌ Test: Write/Read - FAIL: {e}")
        return False


def test_trade_journal() -> bool:
    """Test trade journal."""
    try:
        brain = get_brain()

        trade = {
            "symbol": "EURUSD",
            "direction": "BUY",
            "entry_price": 1.0850,
            "exit_price": 1.0860,
            "profit": 10.0,
            "session": "LONDON",
            "strategy": "test",
            "result": "WIN",
        }

        trade_id = brain.add_trade(trade)
        assert trade_id is not None, "Trade should have ID"

        trades = brain.get_trades()
        assert len(trades) > 0, "Should have trades"

        print("✅ Test: Trade Journal - PASS")
        return True
    except Exception as e:
        print(f"❌ Test: Trade Journal - FAIL: {e}")
        return False


def test_learning() -> bool:
    """Test learning database."""
    try:
        brain = get_brain()

        lesson = {
            "category": "spread_guard",
            "event": "High spread detected",
            "decision": "Skip trade",
            "outcome": "Correct decision",
            "confidence": 0.95,
        }

        lesson_id = brain.add_lesson(lesson)
        assert lesson_id is not None, "Lesson should have ID"

        lessons = brain.get_lessons()
        assert len(lessons) > 0, "Should have lessons"

        print("✅ Test: Learning - PASS")
        return True
    except Exception as e:
        print(f"❌ Test: Learning - FAIL: {e}")
        return False


def test_backup() -> bool:
    """Test backup functionality."""
    try:
        brain = get_brain()
        backup_path = brain.create_backup()
        assert backup_path is not None, "Backup should be created"
        assert backup_path.exists(), "Backup file should exist"

        print("✅ Test: Backup - PASS")
        return True
    except Exception as e:
        print(f"❌ Test: Backup - FAIL: {e}")
        return False


def test_export_import() -> bool:
    """Test export and import."""
    try:
        export_file = export_brain("test_export")
        assert export_file is not None, "Export should succeed"
        assert export_file.exists(), "Export file should exist"

        print("✅ Test: Export - PASS")
        return True
    except Exception as e:
        print(f"❌ Test: Export/Import - FAIL: {e}")
        return False


def test_brain_status() -> bool:
    """Test brain status reporting."""
    try:
        brain = get_brain()
        status = brain.get_brain_status()

        assert "location" in status, "Status should have location"
        assert "databases" in status, "Status should have database count"
        assert "memory_records" in status, "Status should have memory record count"

        print("✅ Test: Brain Status - PASS")
        return True
    except Exception as e:
        print(f"❌ Test: Brain Status - FAIL: {e}")
        return False


def run_all_tests() -> dict[str, bool]:
    """Run all brain tests."""
    print("\n" + "=" * 50)
    print("BRAIN DATABASE TEST SUITE")
    print("=" * 50 + "\n")

    results = {
        "create_db": test_create_db(),
        "write_read": test_write_read(),
        "trade_journal": test_trade_journal(),
        "learning": test_learning(),
        "backup": test_backup(),
        "export_import": test_export_import(),
        "brain_status": test_brain_status(),
    }

    print("\n" + "=" * 50)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("=" * 50 + "\n")

    return results


if __name__ == "__main__":
    results = run_all_tests()
    exit(0 if all(results.values()) else 1)
