"""Nova-Bot-FX Production Build Script."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


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
        print(f"[OK] {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description}")
        print(f"  stdout: {e.stdout}")
        print(f"  stderr: {e.stderr}")
        return False


def build_nova_bot() -> bool:
    """Build Nova-Bot-FX production executable."""
    print_section("NOVA-BOT-FX PRODUCTION BUILD")

    project_root = Path(__file__).resolve().parent
    os.chdir(project_root)

    print(f"Project Root: {project_root}")
    print(f"Python Version: {sys.version}")
    print(f"Platform: {sys.platform}")

    # Step 1: Clean old builds
    print_section("STEP 1: CLEAN OLD BUILDS")
    for old_dir in ["build", "dist"]:
        if Path(old_dir).exists():
            shutil.rmtree(old_dir)
            print(f"[OK] Removed {old_dir}/")

    # Step 2: Verify dependencies
    print_section("STEP 2: VERIFY DEPENDENCIES")
    required_packages = [
        "MetaTrader5",
        "psutil",
        "requests",
        "telegram",
        "python-dotenv",
        "pyinstaller",
    ]

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"[OK] {package}")
        except ImportError:
            print(f"[ERROR] Missing package: {package}")
            return False

    # Step 3: Build with PyInstaller
    print_section("STEP 3: BUILD WITH PYINSTALLER")
    spec_file = "Nova-Bot-FX.spec"
    if not Path(spec_file).exists():
        print(f"[ERROR] Spec file not found: {spec_file}")
        return False

    cmd = [sys.executable, "-m", "PyInstaller", spec_file, "--clean"]
    if not run_command(cmd, "Building Nova-Bot-FX.exe"):
        return False

    # Step 4: Verify executable
    print_section("STEP 4: VERIFY EXECUTABLE")
    exe_path = Path("dist/Nova-Bot-FX/Nova-Bot-FX.exe")
    if not exe_path.exists():
        print(f"[ERROR] Executable not created: {exe_path}")
        return False

    exe_size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"[OK] Executable created: {exe_path}")
    print(f"[OK] Size: {exe_size_mb:.1f} MB")

    # Step 5: Verify no AppData usage
    print_section("STEP 5: VERIFY NO APPDATA USAGE")
    exe_dir = Path("dist/Nova-Bot-FX")
    suspicious_files = []
    for item in exe_dir.rglob("*"):
        if "temp" in item.name.lower() or "appdata" in str(item).lower():
            suspicious_files.append(str(item))

    if suspicious_files:
        print(f"[WARNING] Found suspicious files:")
        for f in suspicious_files:
            print(f"  {f}")
    else:
        print("[OK] No AppData or Temp references found")

    # Step 6: List contents
    print_section("STEP 6: BUILD CONTENTS")
    exe_dir = Path("dist/Nova-Bot-FX")
    for item in sorted(exe_dir.iterdir())[:10]:
        if item.is_file():
            size_mb = item.stat().st_size / (1024 * 1024)
            print(f"  {item.name}: {size_mb:.2f} MB")
        elif item.is_dir():
            print(f"  {item.name}/ (directory)")

    # Step 7: Summary
    print_section("BUILD SUMMARY")
    print(f"[OK] Build completed successfully!")
    print(f"[OK] Executable: dist/Nova-Bot-FX/Nova-Bot-FX.exe")
    print(f"[OK] Size: {exe_size_mb:.1f} MB")
    print(f"[OK] Distribution: dist/Nova-Bot-FX/")
    print("\nNext steps:")
    print("1. Copy entire dist/Nova-Bot-FX folder")
    print("2. Run Nova-Bot-FX.exe on target machine")
    print("3. Brain data will be stored in E:\\NOVA_BRAIN or D:\\NOVA_BRAIN")

    return True


if __name__ == "__main__":
    success = build_nova_bot()
    sys.exit(0 if success else 1)
