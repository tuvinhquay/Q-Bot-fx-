"""Natural-language Vietnamese learning report for Telegram."""

from __future__ import annotations

from typing import Any

from backend.services.telegram.icons import AI_ICON, CHECK_ICON, SUCCESS_ICON, WARNING_ICON


def build_learning_report(snapshot: dict[str, Any], analysis: dict[str, Any]) -> str:
    warnings = analysis.get("warnings", [])
    suggestions = analysis.get("suggestions", [])
    confidence_insight = analysis.get("confidence_insight", "Chua du du lieu danh gia")

    warning_line = f"{WARNING_ICON} {warnings[0]}" if warnings else f"{SUCCESS_ICON} Chua ghi nhan canh bao lon"
    suggestion_line = (
        f"{CHECK_ICON} Goi y: {suggestions[0]}"
        if suggestions
        else f"{CHECK_ICON} Goi y: tiep tuc thu thap du lieu de hoc on dinh hon"
    )

    return (
        f"{AI_ICON} AI LEARNING REPORT\n"
        "━━━━━━━━━━━━━━\n"
        f"{SUCCESS_ICON} Symbol tot nhat: {snapshot.get('best_symbol', 'N/A')}\n"
        f"{warning_line}\n"
        f"{CHECK_ICON} Win rate hien tai: {snapshot.get('win_rate', 0.0):.2f}%\n"
        f"🌍 Market tot nhat: {snapshot.get('best_regime', 'N/A')}\n"
        f"{WARNING_ICON} Market rui ro cao: {snapshot.get('dangerous_regime', 'N/A')}\n"
        f"{suggestion_line}\n"
        f"🤖 {confidence_insight}"
    )
