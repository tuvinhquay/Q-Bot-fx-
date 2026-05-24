# Q-Bot-FX

Q-Bot-FX là Forex Trading Bot kết nối MT5, có AI, Risk Management, Telegram.

## Project Structure

```text
Q-Bot-FX/
├── backend/
│   ├── core/
│   │   └── init.py
│   ├── mt5/
│   │   └── init.py
│   ├── data/
│   │   └── init.py
│   ├── analysis/
│   │   └── init.py
│   ├── strategy/
│   │   └── init.py
│   ├── risk/
│   │   └── init.py
│   ├── execution/
│   │   └── init.py
│   ├── logging/
│   │   └── init.py
│   ├── database/
│   │   └── init.py
│   ├── services/
│   │   └── init.py
│   └── main.py
├── config/
│   └── settings.py
├── .env.example
├── requirements.txt
└── README.md
```

## Prompt 25 Milestone - AI Learning Memory

Prompt 25 bo sung mot learning layer doc lap de bot bat dau "co tri nho" va tu hoc.
Layer nay khong sua logic execution, risk manager, portfolio manager hay adaptive core.

### Thanh phan moi

- AI Learning Memory: luu nho cac ban ghi giao dich vao `data/learning_memory.json`
- Trade Journal: tao nhat ky giao dich dang `[AI JOURNAL]`
- Performance Tracker: thong ke total trade, win/loss rate, avg pnl, best/worst symbol, best/dangerous regime
- Learning Analyzer: phat hien warning va suggestion tu du lieu lich su
- Learning Report: tao bao cao tu nhien de gui Telegram (tuong thich Prompt 24)

### Bot da hoc duoc gi sau Prompt 25

- Biet cap tien nao dang hoat dong tot/xau
- Biet market regime nao de gay drawdown
- Co insight muc do tin cay dua tren kich thuoc mau

### Test commands

```bash
python -m py_compile backend
python backend/services/learning/test_learning.py
python backend/main.py --once
```

### Roadmap Prompt 26

- Nang cap tu memory thong ke sang adaptive AI tu dong dieu chinh theo regime
- Toi uu confidence model dua tren ket qua thuc te
- Mo rong learning feedback loop theo nhieu timeframe
