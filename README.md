# Q-Bot-fx-
Ứng dụng công nghệ tài chính – Trading Bot + AI + Dashboard

======================================================
🔥 FIRST LIVE RUN
======================================================

Bước khởi tạo hệ thống

1. Tạo Firebase project
2. Tạo Service Account → copy credentials vào ENV
3. Lấy Firebase Web Config trong Project Settings
4. Lấy Gemini API Key
5. Tạo file .env tại root theo .env.example
6. Chạy toàn bộ hệ thống:

powershell ./run-local.ps1


======================================================
🌍 ROOT ENV VARIABLES
======================================================

GEMINI_API_KEY
FIREBASE_PROJECT_ID
FIREBASE_CLIENT_EMAIL
FIREBASE_PRIVATE_KEY
NEXT_PUBLIC_FIREBASE_API_KEY
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
NEXT_PUBLIC_FIREBASE_PROJECT_ID
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID
NEXT_PUBLIC_FIREBASE_APP_ID


======================================================
📄 VÍ DỤ FILE .ENV
======================================================

GEMINI_API_KEY=your_gemini_api_key
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_CLIENT_EMAIL=your_client_email
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"

NEXT_PUBLIC_FIREBASE_API_KEY=your_web_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_messaging_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id


======================================================
🤖 CI MINI – AUTOMATIC TESTING (GitHub Actions)
======================================================

Mỗi lần Push hoặc tạo Pull Request:

• GitHub cài Python 3.11  
• Tự động chạy pytest  
• Nếu test FAIL → không cho merge  

➡️ Giúp phát triển bằng prompt an toàn.


======================================================
🧠 CI MINI – HEALTH MONITORING
======================================================

CI Mini nằm trong thư mục ci-mini/ và chạy health check cho:

Telegram Bot → http://localhost:3000/health  
Backend API → http://localhost:3000/api/health  
Python Trading Engine → http://localhost:8000/health  
Trading smoke test → POST http://localhost:8000/test-trade  

Chạy thủ công:

cd ci-mini
python3 ci_runner.py

Cron server Linux (mỗi 5 phút):

*/5 * * * * cd /root/Q-Bot-FX/ci-mini && python3 ci_runner.py


======================================================
🚨 CI MINI TELEGRAM ALERTS
======================================================

Mỗi lần Push hoặc tạo Pull Request:

✅ Tests PASS → Telegram báo hệ thống ổn định  
❌ Tests FAIL → Telegram cảnh báo ngay  

ENV cần thiết:

TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID

Hoặc:

CI_MINI_TELEGRAM_TOKEN
CI_MINI_TELEGRAM_CHAT_ID


======================================================
🐍 PYTHON TRADING ENGINE HEALTH API
======================================================

cd Q-Bot-FX
uvicorn backend.health_api:app --host 0.0.0.0 --port 8000


======================================================
🚀 DEVELOPMENT WORKFLOW CHUẨN
======================================================

1️⃣ Viết Prompt  
2️⃣ Codex tạo branch  
3️⃣ Tạo Pull Request  
4️⃣ CI Mini chạy test tự động  
5️⃣ Merge vào main nếu PASS  
6️⃣ Pull về máy → test local  

➡️ Lặp lại cho đến khi hoàn thành hệ thống.