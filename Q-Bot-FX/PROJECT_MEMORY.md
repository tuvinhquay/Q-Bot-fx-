# PROJECT_MEMORY

## Project Identity

- Project name: Q-Bot-FX
- Domain: Forex trading automation with MT5, AI decision layers, Telegram reporting, monitoring, recovery, and deployment support
- Repository source: `D:\Q-Bot-fx-\Q-Bot-FX`
- Git root for this checkout: `D:\Q-Bot-fx-`

## Mission

Build and operate an enterprise-style trading system that can:

- Detect market opportunities
- Protect capital
- Report system health
- Preserve learning and operational memory
- Support long-running execution with recovery and deployment tooling

## Overall Architecture

The project is organized as a layered system:

- `src/`: root TypeScript bot surface
- `backend/`: lightweight Node helper service layer
- `ci-mini/`: fast health-check and smoke-test runner
- `dashboard-web/`: dashboard bridge and MT5 typing support
- `worker-bot/`: Python worker path
- `monitoring/`: alert and notification helpers
- `Q-Bot-FX/`: main enterprise feature tree and prompt history
- `Q-Bot-FX/backend/services/deployment/`: backup, restore, and deployment reporting
- `Q-Bot-FX/backend/services/heartbeat/`: continuous production heartbeat and dashboard loop
- `Q-Bot-FX/backend/services/telegram/`: Telegram monitoring dashboard and commands

## Design Philosophy

- Keep trading logic separated from infrastructure and monitoring
- Add capability through new layers instead of rewriting the core
- Preserve backward compatibility between prompts
- Prefer operational safety, recovery, and observability
- Treat docs and history as first-class project assets

## Core Components

- Trading Engine
- Risk Engine
- Signal Engine
- Execution Engine
- Learning Engine
- Memory Engine
- Monitoring
- Recovery
- Telegram
- Dashboard
- MT5
- Database
- Health
- Node Identity
- Adaptive System
- CI Mini
- Deployment support
- Production heartbeat
- Daily and weekly reports
- Backup and restore automation
- Runtime telemetry collection

## Repository Structure

- Root-level orchestration and helper files live beside the git root
- Main product source lives under `Q-Bot-FX/`
- Prompt-specific documentation is stored inside `Q-Bot-FX/`
- Generated build artifacts may appear under `build/` and `dist/`
- Runtime and analytics artifacts may appear under `data/`, `charts/`, and `tests/`

## Development Process

- Work prompt by prompt
- Keep each prompt’s scope isolated
- Record each major milestone in docs
- Prefer branch history and build reports over memory alone
- Use CI Mini and monitoring layers as validation signals when testing is allowed

## Working Rules

- Do not change trading logic unless a later prompt explicitly requires it
- Do not add modules casually
- Do not refactor just for style
- Keep operational layers separate from execution layers
- Keep the source of record inside the repository, not in temporary worktrees

## Current State

- Prompt 34.v1 is the current production build line for this checkout
- Prompt 34 remains the stable production base underneath Prompt 34.v1
- The current branch is `prompt-34-v1-production-build`
- Current commit: `2e3cee0`
- Prompt 34.v1 focus: production deployment, live monitoring, telemetry capture, backup/restore, Telegram dashboard, and EXE build packaging

## Prompt 33A Stable Foundation

Prompt 33A is the active base line for future work. It adds infrastructure-only capabilities and does not change trading or risk logic.

### Prompt 33A Modules

- `backend/services/mt5/auto_login_engine.py`
- `backend/services/mt5/connection_manager.py`
- `backend/services/device/device_health.py`
- `backend/services/telegram/monitoring_center.py`
- `backend/services/heartbeat/heartbeat_engine.py`
- `backend/services/health/health_check.py`
- `backend/services/recovery/crash_guard.py`
- `backend/services/node/node_identity.py`

## Prompt 34 Production Layer

Prompt 34 extends the stable foundation with operational layers only. It does not change strategy, risk, signal, or execution logic.

### Prompt 34 Modules

- `backend/main.py`
- `backend/core/scheduler.py`
- `backend/core/signal_pipeline.py`
- `backend/notifications/telegram_notifier.py`
- `backend/services/deployment/backup_manager.py`
- `backend/services/deployment/deployment_report.py`
- `backend/services/deployment/recovery_manager.py`
- `backend/services/heartbeat/heartbeat_engine.py`
- `backend/services/telegram/monitoring_center.py`
- `build_nova.py`
- `QBotFX.spec`

### Prompt 34 Outcomes

- Auto-start and crash recovery loop for the production runtime
- 5-second heartbeat with live dashboard refresh
- Telegram dashboard commands for health, logs, reports, and restart control
- Daily and weekly report generation for production telemetry
- Backup and restore coverage for learning, adaptive, trade, config, logs, and database files
- One-file, windowed EXE packaging through PyInstaller
- Runtime telemetry capture for Prompt 35 preparation

## Prompt 34.v1 Production Build

Prompt 34.v1 keeps Prompt 34 stable and adds the final production packaging and validation pass on a separate branch.

### Prompt 34.v1 Status

- Branch: `prompt-34-v1-production-build`
- Build status: PASS
- Test status: PASS
- EXE status: `D:\Q-Bot-fx-\Q-Bot-FX\dist\QBotFX.exe` created successfully
- Next step: install the EXE on the laptop and run 2–3 weeks of live production monitoring

### Prompt 33A Outcomes

- MT5 auto-login and connection support
- Device health reporting
- Telegram monitoring commands
- Heartbeat generation
- Health checks for infrastructure
- Crash notification and recovery hook
- Node identity reporting

## Next Target

- Next prompt after production validation: Prompt 35
- Expected direction: data-driven AI optimization from real production telemetry

## Prompt 34 Production Candidate

Prompt 34 turns the Prompt 33A foundation into a production-deployment line focused on long-running operation, live monitoring, recovery, and EXE packaging.

### Prompt 34 Modules

- `backend/brain/nova_config.py`
- `backend/brain/system_health.py`
- `backend/brain/smart_backup.py`
- `backend/brain/startup_validator.py`
- `backend/notifications/telegram_notifier.py`
- `backend/core/scheduler.py`
- `backend/core/signal_pipeline.py`
- `backend/services/heartbeat/heartbeat_engine.py`
- `backend/services/telegram/monitoring_center.py`
- `backend/services/deployment/backup_manager.py`
- `backend/services/deployment/deployment_report.py`
- `backend/services/deployment/recovery_manager.py`
- `build_nova.py`
- `QBotFX.spec`

### Prompt 34 Outcomes

- One-file EXE build path for `QBotFX.exe`
- No-console windowed production packaging
- 5-second heartbeat dashboard editing flow
- Telegram live dashboard and monitoring commands
- Daily and weekly production reports
- Broader backup coverage for memory, config, logs, and runtime files
- Crash restart guard in the application entrypoint
- Production readiness for laptop deployment and live telemetry collection

## Update Policy

- Update this file only when the project changes in a major way
- Use `HISTORY_PROGRESS.md` for prompt-by-prompt history
