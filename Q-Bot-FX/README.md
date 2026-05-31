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

## Prompt 28 Milestone - Multi-Symbol AI Brain

Prompt 28 nang cap Q-Bot-FX thanh AI Portfolio Brain: nhin nhieu symbol cung luc, xep hang co hoi toan market, va uu tien von thong minh.

### Thanh phan moi

- Multi-Symbol Ranking Engine (`backend/services/multi_symbol_ai/ranking_engine.py`)
- Smart Capital Distribution (`capital_distribution.py`)
- Cross-Market Awareness (`cross_market.py`)
- AI Priority Queue (`priority_queue.py`)
- Portfolio Brain Orchestrator (`portfolio_brain.py`)
- Telegram/Terminal Reporting (`reporting.py`)

### Nang luc moi

- Xep hang setup manh nhat trong nhieu symbol
- Chon symbol uu tien thay vi co dinh symbol dau tien
- Uu tien von theo chat luong co hoi (opportunity-weighted)
- Co cross-market insight (vi du xu huong USD tren nhieu cap)
- Gui Telegram "TOP SETUP HOM NAY" va ly do loai bo setup yeu

### Compatibility va Risk impact

- Khong sua execution core va MT5 order placement
- Khong pha Prompt 23-27
- Chi inject lop portfolio opportunity truoc khi tao signal va gui report

### Test command Prompt 28

```bash
python -m py_compile backend
python backend/services/multi_symbol_ai/test_multi_symbol_ai.py
python backend/services/adaptive_ai/test_adaptive_ai.py
python backend/services/learning/test_learning.py
python backend/services/capital/test_capital_manager.py
python backend/main.py --once
```

### Future extensibility

- De mo rong Prompt 29+ cho execution timing theo top setup
- De ket hop session intelligence va market-cycle prediction
- De nang cap thanh autonomous portfolio optimization

## Prompt 29 Milestone - AI Session & Timing Intelligence

Prompt 29 bo sung market timing awareness de bot biet khi nao nen trade va khi nao nen ne.

### Session AI modules

- `backend/services/session_ai/session_detector.py`
- `backend/services/session_ai/timing_score.py`
- `backend/services/session_ai/spread_guard.py`
- `backend/services/session_ai/volatility_trap.py`
- `backend/services/session_ai/session_memory.py`
- `backend/services/session_ai/timing_report.py`
- `backend/services/session_ai/test_session_ai.py`

### Nang luc moi

- Nhan dien session: Asian, London, New York, overlap
- Cham diem timing quality theo gio/session/spread/trap
- Phat hien spread mo rong va rollover danger
- Phat hien fake volatility/fake breakout
- Time-based learning: luu session trong learning memory
- Gui Telegram session timing report de canh bao

### Compatibility

- Khong sua execution core va MT5 order placement
- Khong pha Prompt 23->28
- Chi them protective layer theo session/timing

### Test command Prompt 29

```bash
python -m py_compile backend
python backend/services/session_ai/test_session_ai.py
python backend/main.py --once
```

## Prompt 30 Milestone - AI Patience & Execution Intelligence

Prompt 30 bo sung execution intelligence layer de bot khong vao lenh ngay khi co signal.

### Modules moi

- `backend/services/execution_ai/patience_engine.py`
- `backend/services/execution_ai/entry_optimizer.py`
- `backend/services/execution_ai/candle_confirmation.py`
- `backend/services/execution_ai/fomo_detector.py`
- `backend/services/execution_ai/execution_cooldown.py`
- `backend/services/execution_ai/execution_report.py`
- `backend/services/execution_ai/test_execution_ai.py`

### Nang luc moi

- Cho candle confirm truoc execution
- Phat hien va ne FOMO/chase price
- Danh gia RR va quality entry
- Kich hoat cooldown khi market nguy hiem
- Delay/block execution neu timing xau, spread xau, fake volatility cao

### Integration

Flow moi:
Signal -> Adaptive AI -> Session AI -> Execution AI -> Risk Manager -> Order Placement

### Compatibility

- Khong sua TradeExecutor core
- Khong sua MT5 order placement logic
- Khong pha Prompt 23 -> 29

### Test command Prompt 30

```bash
python -m py_compile backend
python backend/services/execution_ai/test_execution_ai.py
python backend/main.py --once
python backend/services/session_ai/test_session_ai.py
python backend/services/multi_symbol_ai/test_multi_symbol_ai.py
python backend/services/adaptive_ai/test_adaptive_ai.py
python backend/services/learning/test_learning.py
python backend/services/capital/test_capital_manager.py
```

## Prompt 31 Milestone - Deployment & Cloud Backup System

Prompt 31 adds the deployment safety layer for Q-Bot-FX. It prepares the bot for safer demo/live operation by protecting AI data, checking disk usage, preparing restore points, and laying the foundation for Firebase/VPS/EXE workflows.

### New Deployment Modules

- `backend/services/deployment/backup_manager.py`: local backup, restore, list, cleanup
- `backend/services/deployment/firebase_backup.py`: Firebase upload/download/verify adapter
- `backend/services/deployment/firebase_quota_guard.py`: free-tier upload/download/storage quota guard
- `backend/services/deployment/storage_guard.py`: disk usage monitoring
- `backend/services/deployment/file_rotation.py`: rotate generated files by age/count
- `backend/services/deployment/data_compressor.py`: compress old JSON data
- `backend/services/deployment/recovery_manager.py`: integrity check and restore from latest backup
- `backend/services/deployment/deployment_report.py`: deployment and backup status report

### Backup Scope

The deployment layer protects AI runtime data such as:

- `learning_memory.json`
- `adaptive_memory.json`
- `trade_history.json`
- `capital_state.json`
- `session_memory.json`

Backups are stored under `backups/` as zip recovery points. Runtime zip files are not committed.

### Firebase Sync

Firebase support is dependency-light and client-injectable. Without a configured Firebase client, the system safely reports `local-only` mode instead of crashing.

### Storage Guard

Disk usage is monitored with warning/danger thresholds:

- above 80 percent: warning
- above 90 percent: cleanup recommended

### Recovery Manager

On integrity failure, corrupted JSON runtime data can be restored from the newest local backup.

### EXE Build Guide

Install PyInstaller, then run:

```bash
python build_exe.py
```

Target output:

```text
QBotFX.exe
```

### Test command Prompt 31

```bash
python -m py_compile backend
python backend/services/deployment/test_backup.py
python backend/main.py --once
```

## Prompt 32 Milestone - Self-Contained EXE Deployment Automation

Prompt 32 upgrades the deployment layer so a successful EXE build prepares a usable runtime folder automatically.

### Self-Contained Dist Layout

After running:

```bash
python build_exe.py
```

the build script prepares:

```text
dist/
QBotFX.exe
.env
data/
logs/
backups/
charts/
runtime/
build_report.txt
```

If PyInstaller is missing or the build fails, the script still creates the deployment folder and `build_report.txt` with a failed status so troubleshooting is clear.

### Runtime Checker

`backend/services/deployment/runtime_checker.py` checks:

- MT5 terminal visibility
- `.env`
- `data/`
- `logs/`
- `backups/`
- important config keys: `GEMINI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `MT5_LOGIN`

At startup, Q-Bot-FX prints:

```text
[STARTUP CHECK] OK
```

or:

```text
[STARTUP CHECK] WARNING
```

Warnings do not crash the bot.

### Auto Log Rotation

`backend/services/deployment/log_rotation.py` archives logs larger than 10MB and keeps up to 30 archived log files.

### Backup Automation

The build process creates `daily_backup.zip` under `dist/backups/` for runtime memory files when available.

### Troubleshooting

- Missing PyInstaller: run `pip install pyinstaller`
- Missing `.env`: create `.env` before build if you want it copied into `dist/`
- Missing MT5 warning: set `MT5_TERMINAL_PATH` or install MetaTrader 5 in a standard folder
- Build failed but dist exists: inspect `dist/build_report.txt`

### Test command Prompt 32

```bash
python -m py_compile backend
python backend/services/deployment/test_backup.py
python backend/main.py --once
python backend/services/learning/test_learning.py
python backend/services/capital/test_capital_manager.py
python backend/services/adaptive_ai/test_adaptive_ai.py
python backend/services/multi_symbol_ai/test_multi_symbol_ai.py
python backend/services/session_ai/test_session_ai.py
python backend/services/execution_ai/test_execution_ai.py
```
