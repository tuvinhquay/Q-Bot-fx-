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

## Prompt 26 Milestone - Smart Capital Manager

Prompt 26 nang cap bot tu "co tri nho" len "co ban nang sinh ton von" bang mot capital intelligence layer tach biet.
Layer nay khong sua TradeExecutor core, MT5 execution, portfolio logic Prompt 23, telegram foundation Prompt 24, hoac learning core Prompt 25.

### Thanh phan moi

- Smart Capital Manager (`backend/services/capital/capital_manager.py`)
- Drawdown Guard: warning/danger/emergency theo nguong -3/-5/-8
- Survival Mode: tu dong chuyen DEFENSIVE khi drawdown cao, loss streak lon, volatility cao
- Confidence Engine: confidence/emotional risk/market danger score
- Recovery Engine: risk ladder sau chuoi thua (0.3 -> 0.6)
- Smart Risk Allocator: toi uu risk trong hard safety cap
- Capital Report: thong diep tu nhien de gui Telegram

### Bot bao ve von nhu the nao

- Theo doi drawdown ngay/tuan/floating
- Giam risk va lot khi nguy hiem
- Han che overtrading thong qua allocator va recovery ladder
- Giu che do phong thu cho den khi dieu kien thi truong on dinh hon

### Dynamic Risk Evolution

- Risk co the giam manh khi danger (vi du 1.0% -> 0.4%-0.5%)
- Risk tang nhe khi on dinh va confidence cao (vi du 1.0% -> 1.3%)
- Luon ton tai safety cap de tranh vuot qua muc nguy hiem

### Test command Prompt 26

```bash
python -m py_compile backend
python backend/services/capital/test_capital_manager.py
python backend/services/learning/test_learning.py
python backend/main.py --once
```

### Roadmap Prompt 27

- Tich hop capital mode vao strategy selection theo symbol
- Mo rong allocation theo multi-symbol portfolio heat
- Nang cap confidence engine voi trong so regime thong minh hon

## Prompt 27 Milestone - AI Adaptive Intelligence Engine

Prompt 27 bo sung tang Adaptive Intelligence de bot dung tri nho cho quyet dinh song con.
He thong nay tach biet khoi execution core va MT5 order placement.

### Architecture moi

- `backend/services/adaptive_ai/adaptive_engine.py`: trung tam tong hop adaptive score
- `regime_memory.py`: regime learning + luu an toan vao `data/adaptive_memory.json`
- `symbol_behavior.py`: theo doi quality tung symbol
- `confidence_adjuster.py`: tu dong tang/ha confidence
- `opportunity_ranker.py`: xep hang co hoi giao dich
- `self_protection.py`: block trade/cooldown/risk multiplier
- `adaptive_report.py`: adaptive report cho terminal va Telegram

### Adaptive behaviors

- Nho regime tot/xau va uu tien regime phu hop
- Danh gia symbol manh/yeu de uu tien setup
- Tu dong giam confidence khi loss streak, volatility cao, survival mode bat
- Tu dong block trade khi confidence qua thap hoac danger qua cao
- Tang tuong thich voi Prompt 26 qua risk multiplier self-protection

### Test command Prompt 27

```bash
python -m py_compile backend
python backend/services/adaptive_ai/test_adaptive_ai.py
python backend/services/learning/test_learning.py
python backend/services/capital/test_capital_manager.py
python backend/main.py --once
```

### Roadmap Prompt 28

- Adaptive selection theo multi-symbol scanner
- Meta-learning cho regime transition
- Tu dong can bang co hoi va risk tren portfolio rong hon
