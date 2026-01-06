import requests
from datetime import datetime, timezone


def map_symbol(symbol: str) -> str:
    if symbol.upper() == "XAUUSD":
        return "GC=F"
    if symbol.upper() == "GC":
        return "GC=F"
    return symbol


def fetch_prices(symbol: str, interval: str, rng: str) -> list[dict]:
    ysymbol = map_symbol(symbol)
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ysymbol}"
    params = {"interval": interval, "range": rng}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json,text/plain,*/*",
    }
    resp = requests.get(url, params=params, headers=headers, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    result = data.get("chart", {}).get("result", [])
    if not result:
        return []
    res0 = result[0]
    ts_list = res0.get("timestamp", []) or []
    indicators = res0.get("indicators", {}) or {}
    quote = (indicators.get("quote") or [{}])[0]
    adj_close = (indicators.get("adjclose") or [{}])[0]
    out = []
    for i, ts in enumerate(ts_list):
        o = quote.get("open", [None])[i] if quote.get("open") else None
        h = quote.get("high", [None])[i] if quote.get("high") else None
        l = quote.get("low", [None])[i] if quote.get("low") else None
        c = quote.get("close", [None])[i] if quote.get("close") else None
        v = quote.get("volume", [None])[i] if quote.get("volume") else None
        # prefer adjclose if available
        if adj_close.get("adjclose") and adj_close["adjclose"][i] is not None:
            c = adj_close["adjclose"][i]
        if None in (o, h, l, c):
            continue
        out.append(
            {
                "ts": datetime.fromtimestamp(ts, tz=timezone.utc).replace(tzinfo=None),
                "open": float(o),
                "high": float(h),
                "low": float(l),
                "close": float(c),
                "volume": float(v) if v is not None else None,
            }
        )
    return out
