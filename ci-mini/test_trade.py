"""Trading simulation smoke test used by CI Mini."""

from __future__ import annotations

import requests


def test_trade(url: str = "http://localhost:8000/test-trade") -> tuple[bool, str]:
    """Call the trading engine test endpoint and return a CI-friendly result."""
    try:
        response = requests.post(url, timeout=10)
    except requests.RequestException as exc:
        return False, str(exc)

    if response.status_code == 200:
        return True, "OK"

    return False, f"Lỗi HTTP {response.status_code}: {response.text[:200]}"


if __name__ == "__main__":
    ok, message = test_trade()
    print(f"Trade test: {ok} ({message})")
