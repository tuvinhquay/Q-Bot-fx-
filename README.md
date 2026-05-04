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

