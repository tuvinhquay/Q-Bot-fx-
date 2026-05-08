# Q-Bot-fx-
"Ứng dụng công nghệ tài chính"

## 🔥 FIRST LIVE RUN

1. Tạo Firebase project
2. Tạo service account và copy thông tin vào môi trường
3. Lấy Firebase web config từ phần Project settings
4. Lấy Gemini API key
5. Tạo file `.env` tại root với nội dung dựa trên `.env.example`
6. Chạy toàn bộ hệ thống bằng:

```bash
powershell ./run-local.ps1
```

### Root env variables

`GEMINI_API_KEY`, `FIREBASE_PROJECT_ID`, `FIREBASE_CLIENT_EMAIL`, `FIREBASE_PRIVATE_KEY`, `NEXT_PUBLIC_FIREBASE_API_KEY`, `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`, `NEXT_PUBLIC_FIREBASE_PROJECT_ID`, `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET`, `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID`, `NEXT_PUBLIC_FIREBASE_APP_ID`

### Local env file

Tạo file `.env` hoặc `.env.local` ở root với giá trị tương ứng. Ví dụ:

```env
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
```


## 🧠 CI Mini monitoring

CI Mini nằm trong thư mục `ci-mini/` và chạy health check cho:

- Bot Telegram: `http://localhost:3000/health`
- Backend API: `http://localhost:3000/api/health`
- Python Trading Engine: `http://localhost:8000/health`
- Trading smoke test: `POST http://localhost:8000/test-trade`

Chạy thủ công:

```bash
cd ci-mini && python3 ci_runner.py
```

Cron mỗi 5 phút trên server Linux:

```cron
*/5 * * * * cd /root/Q-Bot-FX/ci-mini && python3 ci_runner.py
```

Để gửi báo cáo Telegram, đặt `TELEGRAM_BOT_TOKEN` và `TELEGRAM_CHAT_ID` hoặc cặp biến riêng `CI_MINI_TELEGRAM_TOKEN` và `CI_MINI_TELEGRAM_CHAT_ID`.

Python Trading Engine health API có thể chạy bằng:

```bash
cd Q-Bot-FX && uvicorn backend.health_api:app --host 0.0.0.0 --port 8000
```
