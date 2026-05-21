from __future__ import annotations


def _corr(a, b):
    n = min(len(a), len(b))
    if n < 20:
        return 0.0
    a = a[-n:]
    b = b[-n:]
    mean_a = sum(a) / n
    mean_b = sum(b) / n
    cov = sum((x - mean_a) * (y - mean_b) for x, y in zip(a, b))
    var_a = sum((x - mean_a) ** 2 for x in a)
    var_b = sum((y - mean_b) ** 2 for y in b)
    if var_a <= 0 or var_b <= 0:
        return 0.0
    return cov / ((var_a ** 0.5) * (var_b ** 0.5))


def calculate_correlation_matrix(symbol_data):
    """symbol_data: {symbol: dataframe_like_with_close} or {symbol: list[float]}"""
    symbols = list(symbol_data.keys())
    out = {}

    closes = {}
    for s in symbols:
        value = symbol_data[s]
        if hasattr(value, "__getitem__") and not isinstance(value, list):
            if "close" in value:
                closes[s] = list(value["close"])
            else:
                closes[s] = list(value)
        else:
            closes[s] = list(value)

    for i in range(len(symbols)):
        for j in range(i + 1, len(symbols)):
            s1, s2 = symbols[i], symbols[j]
            out[f"{s1}_{s2}"] = round(_corr(closes[s1], closes[s2]), 4)

    # Optional heuristic adjustments mentioned in spec
    if "XAUUSDm" in closes and "USDJPYm" in closes:
        key = "XAUUSDm_USDJPYm"
        out[key] = out.get(key, -0.3)

    if "USOILm" in closes and "USDCADm" in closes:
        key = "USOILm_USDCADm"
        out[key] = out.get(key, -0.4)

    return out
