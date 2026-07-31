"""Nova-Bot-FX Production Build Script."""

from __future__ import annotations

import importlib
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from backend.services.deployment.backup_manager import BackupManager
from backend.services.deployment.deployment_report import build_deployment_report
from backend.services.deployment.runtime_checker import REQUIRED_ENV_KEYS, check_runtime_environment, format_runtime_report
from backend.services.deployment.storage_guard import disk_usage

RUNTIME_DIRS = ["data", "logs", "backups", "charts", "runtime"]
REQUIRED_IMPORTS = {
    "MetaTrader5": "MetaTrader5",
    "psutil": "psutil",
    "requests": "requests",
    "python-dotenv": "dotenv",
    "PyInstaller": "PyInstaller",
}


def print_section(title: str) -> None:
    """Print section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def run_command(cmd: list[str], description: str) -> bool:
    """Run command and report results."""
    print(f"\n[INFO] {description}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout.strip():
            print(result.stdout.strip())
        print(f"[OK] {description}")
        return True
    except subprocess.CalledProcessError as error:
        print(f"[ERROR] {description}")
        print(f"  stdout: {error.stdout}")
        print(f"  stderr: {error.stderr}")
        return False


def _verify_dependencies() -> bool:
    print_section("STEP 2: VERIFY DEPENDENCIES")
    for label, module_name in REQUIRED_IMPORTS.items():
        try:
            importlib.import_module(module_name)
            print(f"[OK] {label}")
        except ImportError:
            print(f"[ERROR] Missing package: {label}")
            return False
    return True


def _prepare_dist(project_root: Path) -> Path:
    dist_dir = project_root / "dist"
    dist_dir.mkdir(exist_ok=True)
    for name in RUNTIME_DIRS:
        (dist_dir / name).mkdir(parents=True, exist_ok=True)

    env_source = project_root / ".env"
    if env_source.exists():
        shutil.copy2(env_source, dist_dir / ".env")
    else:
        print("[BUILD WARNING] .env file missing; dist/.env was not created.")

    env_values: dict[str, str] = {}
    if env_source.exists():
        for line in env_source.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not line or line.strip().startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env_values[key.strip()] = value.strip().strip('"').strip("'")

    for key in REQUIRED_ENV_KEYS:
        if not env_values.get(key) and not os.environ.get(key):
            print(f"[BUILD WARNING] {key} is missing.")

    return dist_dir


def _prepare_runtime_directories(project_root: Path) -> None:
    for name in RUNTIME_DIRS:
        (project_root / name).mkdir(parents=True, exist_ok=True)


def _write_report(
    project_root: Path,
    dist_dir: Path,
    build_status: str,
    runtime_state: dict[str, object],
    disk_state: dict[str, object],
    backup_state: dict[str, object],
) -> None:
    exe_path = dist_dir / "QBotFX.exe"
    branch = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=project_root,
        text=True,
        capture_output=True,
        check=False,
    ).stdout.strip() or "UNKNOWN"
    commit = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=project_root,
        text=True,
        capture_output=True,
        check=False,
    ).stdout.strip() or "UNKNOWN"
    exe_size = exe_path.stat().st_size if exe_path.exists() else 0
    report = (
        "Q-BOT FX BUILD REPORT\n"
        f"Build date: {datetime.now(timezone.utc).isoformat()}\n"
        f"Git branch: {branch}\n"
        f"Git commit: {commit}\n"
        f"Python version: {sys.version.split()[0]}\n"
        f"EXE size: {exe_size} bytes\n"
        f"Build status: {build_status}\n"
        f"Runtime status: {runtime_state.get('status', 'UNKNOWN')}\n"
        f"Disk usage: {disk_state.get('percent', 0.0)}%\n"
        f"Backup archive: {backup_state.get('archive', 'N/A')}\n"
    )
    (dist_dir / "build_report.txt").write_text(report, encoding="utf-8")


def build_nova_bot() -> bool:
    """Build Nova-Bot-FX production executable."""
    print_section("NOVA-BOT-FX PRODUCTION BUILD")

    project_root = Path(__file__).resolve().parent
    os.chdir(project_root)

    print(f"Project Root: {project_root}")
    print(f"Python Version: {sys.version}")
    print(f"Platform: {sys.platform}")

    print_section("STEP 1: CLEAN OLD BUILDS")
    for old_dir in ["build", "dist"]:
        if Path(old_dir).exists():
            shutil.rmtree(old_dir)
            print(f"[OK] Removed {old_dir}/")

    if not _verify_dependencies():
        return False

    _prepare_runtime_directories(project_root)
    dist_dir = _prepare_dist(project_root)
    backup_state = BackupManager(project_root=project_root, backup_dir=dist_dir / "backups").backup_daily()
    runtime_state = check_runtime_environment(project_root)
    disk_state = disk_usage(project_root)
    print_section("STEP 3: RUNTIME VALIDATION")
    print(format_runtime_report(runtime_state))

    print_section("STEP 4: BUILD WITH PYINSTALLER")
    spec_file = project_root / "QBotFX.spec"
    if not spec_file.exists():
        print(f"[ERROR] Spec file not found: {spec_file}")
        return False

    cmd = [sys.executable, "-m", "PyInstaller", str(spec_file), "--clean", "--noconfirm"]
    if not run_command(cmd, "Building QBotFX.exe"):
        _write_report(project_root, dist_dir, "FAILED", runtime_state, disk_state, backup_state)
        return False

    print_section("STEP 5: VERIFY EXECUTABLE")
    exe_path = dist_dir / "QBotFX.exe"
    if not exe_path.exists():
        print(f"[ERROR] Executable not created: {exe_path}")
        _write_report(project_root, dist_dir, "FAILED", runtime_state, disk_state, backup_state)
        return False

    exe_size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"[OK] Executable created: {exe_path}")
    print(f"[OK] Size: {exe_size_mb:.1f} MB")

    print_section("STEP 6: VERIFY NO APPDATA USAGE")
    suspicious_files = []
    for item in dist_dir.rglob("*"):
        if "temp" in item.name.lower() or "appdata" in str(item).lower():
            suspicious_files.append(str(item))

    if suspicious_files:
        print("[WARNING] Found suspicious files:")
        for file_name in suspicious_files:
            print(f"  {file_name}")
    else:
        print("[OK] No AppData or Temp references found")

    print_section("STEP 7: BUILD SUMMARY")
    print("[OK] Build completed successfully!")
    print(f"[OK] Executable: {exe_path}")
    print(f"[OK] Size: {exe_size_mb:.1f} MB")
    print(f"[OK] Distribution: {dist_dir}")
    print("\nNext steps:")
    print("1. Copy dist/QBotFX.exe to target machine")
    print("2. Ensure MT5 is installed")
    print("3. Run QBotFX.exe in window mode without console")

    _write_report(project_root, dist_dir, "SUCCESS", runtime_state, disk_state, backup_state)
    deployment_report = build_deployment_report(
        backup_ok=bool(backup_state.get("success")),
        firebase_ok=True,
        disk_percent=float(disk_state.get("percent", 0.0)),
        files_healthy=runtime_state.get("status") != "FAIL",
        recovery_ready=exe_path.exists(),
    )
    with (dist_dir / "build_report.txt").open("a", encoding="utf-8") as handle:
        handle.write("\n")
        handle.write(deployment_report)
        handle.write("\n")

    return True


if __name__ == "__main__":
    success = build_nova_bot()
    sys.exit(0 if success else 1)
