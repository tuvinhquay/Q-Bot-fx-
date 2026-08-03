# ============================================================
# formatter.py V2 Production
# Q-Bot FX
# Telegram Notification Engine
#
# Phiên bản:
#     Production V2
#
# Mục tiêu:
#     Chuẩn hóa toàn bộ thông báo Telegram
#     bằng tiếng Việt.
#
# Tác giả:
#     Q-Bot FX Project
#
# ============================================================

from __future__ import annotations

from typing import Any

# ============================================================
# PART 1
# IMPORT TOÀN BỘ MODULE
# ============================================================

from backend.services.telegram.icons import *

from backend.services.telegram.templates import *

from backend.services.telegram.ai_explainer import (
    explain_ai_confidence,
    explain_ai_signal,
)

from backend.services.telegram.risk_explainer import (
    explain_portfolio_heat,
    explain_dynamic_risk,
    explain_correlation_risk,
    explain_directional_bias,
)

from backend.services.telegram.status_engine import (
    classify_alert_status,
)

# ============================================================
# PART 2
# CẤU HÌNH GIAO DIỆN TELEGRAM
# ============================================================

TELEGRAM_WIDTH = 30

TITLE_SIGNAL = "🔥 Q-BOT FX | TÍN HIỆU GIAO DỊCH"

TITLE_HEARTBEAT = "💓 Q-BOT FX HEARTBEAT"

TITLE_ONLINE = "🟢 Q-BOT-FX ONLINE"

TITLE_DASHBOARD = "📊 Q-BOT FX DASHBOARD"

TITLE_AI = "🧠 ĐÁNH GIÁ AI"

TITLE_RISK = "⚠️ RỦI RO"

TITLE_RESULT = "🎯 KẾT LUẬN"

TITLE_SYSTEM = "🤖 HỆ THỐNG"

TITLE_ACCOUNT = "💰 TÀI KHOẢN"

TITLE_MARKET = "📈 THỊ TRƯỜNG"

TITLE_SERVICE = "📡 DỊCH VỤ"

TITLE_BRAIN = "🧠 BRAIN"

TITLE_PORTFOLIO = "📂 DANH MỤC"

TITLE_SCALPING = "⚡ SCALPING"

TITLE_FOREX = "💱 FOREX"

# ============================================================
# PART 3
# HÀM TIỆN ÍCH
# ============================================================

def line():

    return "━━━━━━━━━━━━━━━━━━"


def blank():

    return ""


def section(title: str):

    return f"{title}\n{line()}"


def yes(flag: bool):

    return "🟢" if flag else "🔴"


def value(text):

    return "N/A" if text is None else text


# ============================================================
# PART 4
# CHUẨN HÓA DỮ LIỆU
# ============================================================

def as_float(value: Any, default: float = 0.0):

    try:

        return float(value)

    except Exception:

        return default


def as_percent(value):

    return f"{as_float(value):.2f}%"


def as_price(value):

    return f"{as_float(value):.5f}"


def as_money(value):

    return f"{as_float(value):.2f} USD"


# ============================================================
# PART 5
# FORMAT TÍN HIỆU GIAO DỊCH
# ============================================================

def build_trade_signal(

    signal,

    symbol,

    trade_levels,

    adaptive,

    market_regime,

    portfolio,

):

    ai_score = as_float(

        adaptive.get("adaptive_score")

    )

    ai_text = explain_ai_signal(ai_score)

    ai_confidence = explain_ai_confidence(ai_score)

    portfolio_heat = as_float(

        portfolio.get("portfolio_heat")

    )

    dynamic_risk = as_float(

        portfolio.get("dynamic_risk")

    )

    correlation = portfolio.get(

        "correlation_risk",

        "LOW",

    )

    direction = portfolio.get(

        "directional_bias",

        "NEUTRAL",

    )

    status = classify_alert_status(

        ai_score,

        dynamic_risk,

        portfolio_heat,

        correlation,

    )

    message = ""

    message += TITLE_SIGNAL + "\n\n"

    message += f"{RISK_ICON} Cặp tiền: {symbol}\n"

    message += f"{TREND_ICON} Xu hướng: {signal}\n\n"

    message += f"{MONEY_ICON} Entry: {as_price(trade_levels.get('entry'))}\n"

    message += f"🛑 Cắt lỗ: {as_price(trade_levels.get('stop_loss'))}\n"

    message += f"🎯 Chốt lời: {as_price(trade_levels.get('take_profit'))}\n\n"

    message += section(TITLE_AI) + "\n"

    message += f"📊 Điểm AI: {ai_score:.2f}/100\n"

    message += f"⚖️ Độ tự tin: {ai_confidence}\n"

    message += f"🌍 Thị trường: {market_regime.get('regime','UNKNOWN')}\n"

    message += f"🤖 {ai_text}\n\n"

    message += section(TITLE_RISK) + "\n"

    message += f"🔥 Nhiệt danh mục: {portfolio_heat:.2f}%\n"

    message += f"💰 Rủi ro động: {dynamic_risk:.2f}%\n"

    message += f"🔗 Tương quan: {correlation}\n"

    message += f"📦 Danh mục: {direction}\n"

    message += f"• {explain_portfolio_heat(portfolio_heat)}\n"

    message += f"• {explain_dynamic_risk(dynamic_risk)}\n"

    message += f"• {explain_correlation_risk(correlation)}\n"

    message += f"• {explain_directional_bias(direction)}\n\n"

    message += section(TITLE_RESULT) + "\n"

    message += f"🤖 {status.reason}\n"

    message += f"⚠️ Mức cảnh báo: {status.level}\n"

    message += "🕒 Khung thời gian: H1"

    return message

# ============================================================
# PART 6
# HEARTBEAT ENGINE
# Chức năng:
#     Hiển thị trạng thái sống của Q-Bot FX.
#     Gửi định kỳ lên Telegram.
# ============================================================

def build_heartbeat(
    balance: float,
    equity: float,
    market_status: str,
    mt5_connected: bool,
    trading_active: bool,
    current_time: str,
) -> str:

    text = ""

    text += f"{TITLE_HEARTBEAT}\n"
    text += line() + "\n\n"

    text += f"{yes(mt5_connected)} MT5 Connected\n"
    text += f"{yes(trading_active)} Auto Trading\n\n"

    text += f"💰 Balance : {as_money(balance)}\n"
    text += f"📈 Equity  : {as_money(equity)}\n"

    text += f"🌍 Market : {market_status}\n"

    text += f"🕒 Time : {current_time}\n\n"

    if mt5_connected:
        text += "🟢 Hệ thống hoạt động bình thường"
    else:
        text += "🔴 Mất kết nối MT5"

    return text


# ============================================================
# PART 7
# ONLINE STATUS
# Chức năng:
#     Báo cáo tổng quan hệ thống.
# ============================================================

def build_online_status(

    version,
    branch,
    node,
    uptime,

):

    text = ""

    text += TITLE_ONLINE + "\n\n"

    text += section(TITLE_SYSTEM) + "\n"

    text += f"Version : {version}\n"
    text += f"Branch  : {branch}\n"
    text += f"Node    : {node}\n"
    text += f"Uptime  : {uptime}"

    return text


# ============================================================
# PART 8
# DASHBOARD
# Chức năng:
#     Dashboard chính của Telegram.
# ============================================================

def build_dashboard(

    account,
    balance,
    equity,
    profit_today,
    drawdown,
    open_trade,

    market_session,
    spread,
    market_status,

):

    msg = ""

    msg += "📊 Q-BOT FX DASHBOARD\n"
    msg += line() + "\n\n"

    # =======================
    # ACCOUNT
    # =======================

    msg += section(TITLE_ACCOUNT) + "\n"

    msg += f"👤 Account : {account}\n"

    msg += f"💰 Balance : {as_money(balance)}\n"

    msg += f"📈 Equity : {as_money(equity)}\n"

    msg += f"💵 Profit Today : {profit_today}\n"

    msg += f"📉 Drawdown : {drawdown}\n"

    msg += f"📦 Open Trades : {open_trade}\n\n"

    # =======================
    # MARKET
    # =======================

    msg += section(TITLE_MARKET) + "\n"

    msg += f"🌍 Session : {market_session}\n"

    msg += f"📊 Spread : {spread}\n"

    msg += f"📌 Market : {market_status}"

    return msg


# ============================================================
# PART 9
# AI STATUS
# Chức năng:
#     Báo cáo trạng thái AI.
# ============================================================

def build_ai_status(

    gemini,

    adaptive_ai,

    execution_ai,

    confidence,

    last_scan,

):

    text = ""

    text += section(TITLE_AI) + "\n"

    text += f"Gemini : {gemini}\n"

    text += f"Adaptive AI : {adaptive_ai}\n"

    text += f"Execution AI : {execution_ai}\n"

    text += f"Confidence : {confidence}\n"

    text += f"Last Scan : {last_scan}"

    return text


# ============================================================
# PART 10
# RISK STATUS
# Chức năng:
#     Hiển thị tình trạng rủi ro.
# ============================================================

def build_risk_status(

    portfolio_heat,

    exposure,

    drawdown,

    correlation,

    dynamic_risk,

):

    text = ""

    text += section(TITLE_RISK) + "\n"

    text += f"🔥 Heat : {portfolio_heat}\n"

    text += f"📦 Exposure : {exposure}\n"

    text += f"📉 Drawdown : {drawdown}\n"

    text += f"🔗 Correlation : {correlation}\n"

    text += f"💰 Dynamic Risk : {dynamic_risk}"

    return text


# ============================================================
# PART 11
# BRAIN STATUS
# ------------------------------------------------------------
# Chức năng:
#     Hiển thị trạng thái bộ não AI của Q-Bot FX.
#
# Sau này sẽ kết nối:
#     Memory
#     Knowledge
#     Adaptive AI
#     Gemini
# ============================================================

def build_brain_status(

    brain_path,

    database_size,

    database_count,

    memory_records,

    last_backup,

):

    text = ""

    text += section(TITLE_BRAIN) + "\n"

    text += f"📂 Vị trí : {brain_path}\n"

    text += f"💾 Dung lượng : {database_size}\n"

    text += f"🗄️ Cơ sở dữ liệu : {database_count}\n"

    text += f"🧠 Bộ nhớ AI : {memory_records}\n"

    text += f"💽 Sao lưu : {last_backup}"

    return text


# ============================================================
# PART 12
# PORTFOLIO STATUS
# ------------------------------------------------------------
# Chức năng:
#     Hiển thị trạng thái danh mục.
#
# Sau này:
#     Multi Symbol
#     AI Portfolio
# ============================================================

def build_portfolio_status(

    open_trade,

    total_profit,

    today_profit,

    exposure,

    portfolio_heat,

):

    text = ""

    text += section(TITLE_PORTFOLIO) + "\n"

    text += f"📦 Lệnh đang mở : {open_trade}\n"

    text += f"💰 Lợi nhuận : {total_profit}\n"

    text += f"📈 Hôm nay : {today_profit}\n"

    text += f"⚖️ Exposure : {exposure}\n"

    text += f"🔥 Portfolio Heat : {portfolio_heat}"

    return text


# ============================================================
# PART 13
# SCALPING XAU/USD
# ------------------------------------------------------------
# Chức năng:
#     Theo dõi riêng chiến lược Scalping Vàng.
#
# Sau này:
#     AI Scalping
#     Auto Entry
#     Auto Exit
# ============================================================

def build_scalping_status(

    signal,

    entry,

    sl,

    tp,

    confidence,

):

    text = ""

    text += section(TITLE_SCALPING) + "\n"

    text += "🥇 XAU/USD\n\n"

    text += f"📈 Tín hiệu : {signal}\n"

    text += f"💰 Entry : {entry}\n"

    text += f"🛑 Stop Loss : {sl}\n"

    text += f"🎯 Take Profit : {tp}\n"

    text += f"🧠 AI Confidence : {confidence}"

    return text


# ============================================================
# PART 14
# FOREX SCANNER
# ------------------------------------------------------------
# Chức năng:
#     Quét toàn bộ Forex.
#
# Sau này:
#     Top Opportunity
#     Top Trend
#     Multi Symbol
# ============================================================

def build_forex_scanner(

    symbol,

    trend,

    score,

    spread,

):

    text = ""

    text += section(TITLE_FOREX) + "\n"

    text += f"💱 {symbol}\n"

    text += f"📈 Xu hướng : {trend}\n"

    text += f"🧠 AI Score : {score}\n"

    text += f"📊 Spread : {spread}"

    return text


# ============================================================
# PART 15
# CONTROL CENTER
# ------------------------------------------------------------
# Chức năng:
#     Menu Telegram.
#
# Sau này:
#     Inline Keyboard
#     Callback
# ============================================================

def build_control_center():

    text = ""

    text += "🤖 Q-BOT FX CONTROL CENTER\n"

    text += line() + "\n"

    text += "📊 Dashboard\n"

    text += "⚡ Scalping XAU/USD\n"

    text += "💱 Forex Scanner\n"

    text += "🧠 AI Status\n"

    text += "📂 Portfolio\n"

    text += "⚙️ Hệ thống\n"

    text += "📜 Nhật ký\n"

    text += "🔄 Khởi động lại"

    return text


# ============================================================
# PART 16
# EXPORT API
# ------------------------------------------------------------
# Chức năng:
#     Tập trung toàn bộ API formatter.
#
# Sau này:
#     Chỉ cần import formatter.py
#     là có toàn bộ giao diện Telegram.
# ============================================================

__all__ = [

    "build_trade_signal",

    "build_heartbeat",

    "build_online_status",

    "build_dashboard",

    "build_ai_status",

    "build_risk_status",

    "build_brain_status",

    "build_portfolio_status",

    "build_scalping_status",

    "build_forex_scanner",

    "build_control_center",

]

# ============================================================
# PART 17
# TƯƠNG THÍCH VỚI PHIÊN BẢN CŨ
# ------------------------------------------------------------
# Chức năng:
#     Giữ nguyên tên hàm cũ để các module chưa cập nhật
#     vẫn hoạt động bình thường.
#
# Không được xóa.
# Sau này khi toàn bộ project chuyển sang
# build_trade_signal() thì mới bỏ PART này.
# ============================================================

build_telegram_caption = build_trade_signal