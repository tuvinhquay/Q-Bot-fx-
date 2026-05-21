from __future__ import annotations


def _bucket(symbol: str, signal: str):
    base = symbol[:3]
    quote = symbol[3:6]
    direction = 1 if signal == "BUY" else -1
    return {
        base: direction,
        quote: -direction,
    }


def calculate_exposure(open_trades, pending_symbol: str, pending_signal: str, max_abs_exposure: int = 3):
    exposure = {}

    for t in open_trades:
        s = t.get("symbol", "")
        sig = t.get("signal", "BUY")
        b = _bucket(s, sig)
        for k, v in b.items():
            exposure[k] = exposure.get(k, 0) + v

    pending_bucket = _bucket(pending_symbol, pending_signal)
    for k, v in pending_bucket.items():
        exposure[k] = exposure.get(k, 0) + v

    directional = "NEUTRAL"
    if exposure.get("USD", 0) > 0:
        directional = "USD Long"
    elif exposure.get("USD", 0) < 0:
        directional = "USD Short"

    for cur, value in exposure.items():
        if abs(value) > max_abs_exposure:
            return {
                "allow_trade": False,
                "reason": f"{cur} exposure too high",
                "exposure": exposure,
                "directional_bias": directional,
            }

    return {
        "allow_trade": True,
        "reason": "OK",
        "exposure": exposure,
        "directional_bias": directional,
    }
