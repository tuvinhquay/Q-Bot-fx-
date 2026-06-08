"""Nova-Bot-FX Production Test Suite."""

from __future__ import annotations

import sys

sys.path.insert(0, ".")

from backend.brain.nova_config import get_nova_brain_root, NOVA_BRAIN_ROOT
from backend.brain.system_health import get_health
from backend.brain.startup_validator import StartupValidator
from backend.brain.smart_backup import SmartBackupManager
from backend.brain.brain_database import get_brain


def test_nova_brain_location() -> bool:
    """Test Nova Brain root detection."""
    print("\n[TEST 1] Nova Brain Location Detection")
    try:
        brain_root = get_nova_brain_root()
        print(f"  Nova Brain Root: {brain_root}")
        print(f"  Exists: {brain_root.exists()}")
        assert brain_root.exists(), "Brain directory should exist"
        print("  [PASS]")
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


def test_system_health_db() -> bool:
    """Test system health database."""
    print("\n[TEST 2] System Health Database")
    try:
        health = get_health()
        health.log_memory_warning(88.5)
        health.log_cpu_warning(92.0)
        errors = health.get_recent_errors()
        warnings = health.get_recent_warnings()
        print(f"  Recent errors: {len(errors)}")
        print(f"  Recent warnings: {len(warnings)}")
        print("  [PASS]")
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


def test_startup_validator() -> bool:
    """Test startup validation."""
    print("\n[TEST 3] Startup Validation")
    try:
        validator = StartupValidator()
        results = validator.run_all_checks()
        summary = validator.get_summary()

        print(f"  Checks performed: {len(results)}")
        for check_name, result in results.items():
            status = result.get("status", "UNKNOWN")
            print(f"    {check_name}: {status}")

        print(f"  Overall: {'OK' if summary['all_ok'] else 'WARNING'}")
        print("  [PASS]")
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


def test_smart_backup() -> bool:
    """Test smart backup system."""
    print("\n[TEST 4] Smart Backup System")
    try:
        backup_info = SmartBackupManager.get_backup_info()
        print(f"  Backup count: {backup_info.get('count', 0)}")
        print(f"  Total size: {backup_info.get('total_size_mb', 0)} MB")
        print(f"  Disk free: {backup_info.get('disk_free_mb', 0)} MB")
        print("  [PASS]")
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


def test_brain_databases() -> bool:
    """Test all brain databases."""
    print("\n[TEST 5] Brain Databases")
    try:
        brain = get_brain()
        status = brain.get_brain_status()

        print(f"  Location: {status.get('location')}")
        print(f"  Databases: {status.get('databases', 0)}/5")
        print(f"  Size: {status.get('size_mb', 0)} MB")
        print(f"  Memory records: {status.get('memory_records', 0)}")

        assert status.get('databases', 0) >= 4, "Should have at least 4 databases"
        print("  [PASS]")
        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


def run_production_tests() -> dict[str, bool]:
    """Run all production tests."""
    print("=" * 70)
    print("  NOVA-BOT-FX PRODUCTION TEST SUITE")
    print("=" * 70)

    tests = [
        ("Nova Brain Location", test_nova_brain_location),
        ("System Health DB", test_system_health_db),
        ("Startup Validator", test_startup_validator),
        ("Smart Backup", test_smart_backup),
        ("Brain Databases", test_brain_databases),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"  [ERROR] {test_name}: {e}")
            results[test_name] = False

    print("\n" + "=" * 70)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"  RESULTS: {passed}/{total} tests passed")
    print("=" * 70)

    return results


if __name__ == "__main__":
    results = run_production_tests()
    sys.exit(0 if all(results.values()) else 1)
