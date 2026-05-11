# CI Mini

CI Mini kiểm tra nhanh các dịch vụ Q-Bot-FX và gửi báo cáo PASS/FAIL về Telegram.

## Cấu hình Telegram

Đặt biến môi trường trước khi chạy cron:

```bash
export TELEGRAM_BOT_TOKEN="<bot-token>"
export TELEGRAM_CHAT_ID="<chat-id>"
```

Có thể dùng biến riêng cho CI Mini nếu không muốn dùng chung bot chính:

```bash
export CI_MINI_TELEGRAM_TOKEN="<bot-token>"
export CI_MINI_TELEGRAM_CHAT_ID="<chat-id>"
```

## Chạy thủ công

```bash
cd /root/Q-Bot-FX/ci-mini && python3 ci_runner.py
```

## Cron mỗi 5 phút

```cron
*/5 * * * * cd /root/Q-Bot-FX/ci-mini && python3 ci_runner.py
```
<<<<<<< HEAD
=======


## Level 1.5 report

`ci_runner.py` hiện gửi báo cáo chi tiết theo từng service:

- Backend API
- Trading API
- Telegram credentials
- Smoke Trade

Kết quả cuối báo `SYSTEM STATUS: HEALTHY` nếu tất cả OK hoặc `SYSTEM STATUS: ERROR` nếu có service FAIL.
>>>>>>> origin/codex/setup-ci-mini-for-automatic-testing
