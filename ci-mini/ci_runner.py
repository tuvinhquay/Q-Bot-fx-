import subprocess
import sys


def run_tests():
    print("🚀 Running CI MINI tests...\n")

    result = subprocess.run(
        ["python", "-m", "pytest", "Q-Bot-FX"],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    print(result.stderr)

    return result.returncode == 0


def notify(status):
    subprocess.run(["python", "monitoring/ci_notifier.py", status])


if __name__ == "__main__":
    success = run_tests()

    if success:
        notify("success")
        sys.exit(0)
    else:
        notify("fail")
        sys.exit(1)
