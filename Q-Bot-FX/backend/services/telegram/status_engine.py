"""Status engine to classify Telegram alert severity."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AlertStatus:
    level: str
    reason: str


def classify_alert_status(
    ai_score: float,
    dynamic_risk: float,
    portfolio_heat: float,
    correlation_risk: str,
) -> AlertStatus:
    """Classify SAFE/WARNING/DANGER from signal context."""
    if dynamic_risk > 3:
        return AlertStatus(level="DANGER", reason="Rủi ro động đang ở mức cao")

    if portfolio_heat > 5 or str(correlation_risk).strip().upper() == "HIGH":
        return AlertStatus(level="WARNING", reason="Danh mục có dấu hiệu rủi ro cần theo dõi")

    if ai_score > 60 and portfolio_heat < 5:
        return AlertStatus(level="SAFE", reason="Tín hiệu ổn định trong ngưỡng an toàn")

    return AlertStatus(level="WARNING", reason="Cần quan sát thêm trước khi mở rộng vị thế")
