import subprocess
import time
import sys

print("🚀 QBot FX SYSTEM LAUNCHER")
print("=" * 40)

processes = []

def start_process(cmd, name):
    print(f"▶️ Starting {name}...")
    p = subprocess.Popen(cmd, shell=True)
    processes.append(p)

try:
    # 1️⃣ Start Node Telegram backend
    start_process(
        "cd backend && npm run dev",
        "Telegram Backend (port 3000)"
    )

    # 2️⃣ Start Python Trading Engine
    start_process(
        "cd Q-Bot-FX && python -m uvicorn backend.health_api:app --port 8000",
        "Trading Engine API (port 8000)"
    )

    # 3️⃣ Wait services boot
    print("\n⏳ Waiting services to boot...")
    time.sleep(6)

    # 4️⃣ Run CI MINI
    print("\n🛡️ Running CI Mini check...\n")
    result = subprocess.run("python ci-mini/ci_runner.py", shell=True)

    if result.returncode == 0:
        print("\n🟢 SYSTEM READY")
    else:
        print("\n🔴 SYSTEM HAS ERRORS")

    print("\n💡 Press CTRL+C to stop all services.")

    # giữ process sống
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n🛑 Shutting down all services...")
    for p in processes:
        p.kill()
    sys.exit()