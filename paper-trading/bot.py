#!/usr/bin/env python3
"""
Paper trading bot — SIMULATION ONLY, no real money, no real broker.

Runs on a schedule (see .github/workflows/paper-trading-bot.yml), fetches
daily candles for the watchlist from Yahoo Finance's public chart API (no
API key required), applies a rule-based volatility/momentum strategy, and
updates state.json with simulated buys/sells. Nothing here places a real
order or touches real funds.
"""
import json
import os
import time
import datetime
import urllib.request
import urllib.error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
STATE_PATH = os.path.join(BASE_DIR, "state.json")

YAHOO_URL = "https://query1.finance.yahoo.com/v8/finance/chart"


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def fetch_candles(symbol, range_="1y"):
    url = f"{YAHOO_URL}/{symbol}?range={range_}&interval=1d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        print(f"  [{symbol}] fetch error: {e}")
        return None

    result_list = data.get("chart", {}).get("result")
    if not result_list:
        print(f"  [{symbol}] no data: {data.get('chart', {}).get('error')!r}")
        return None

    quote = result_list[0]["indicators"]["quote"][0]
    closes, highs, lows = [], [], []
    for h, l, c in zip(quote.get("high", []), quote.get("low", []), quote.get("close", [])):
        if h is None or l is None or c is None:
            continue
        highs.append(h)
        lows.append(l)
        closes.append(c)

    if len(closes) < 2:
        print(f"  [{symbol}] insufficient data ({len(closes)} bars)")
        return None
    return {"c": closes, "h": highs, "l": lows}


def sma(values, period):
    if len(values) < period:
        return None
    return sum(values[-period:]) / period


def rsi(closes, period=14):
    if len(closes) < period + 1:
        return None
    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    last = deltas[-period:]
    gains = [d for d in last if d > 0]
    losses = [-d for d in last if d < 0]
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - 100 / (1 + rs)


def atr(highs, lows, closes, period=14):
    if len(closes) < period + 1:
        return None
    trs = []
    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1]),
        )
        trs.append(tr)
    last = trs[-period:]
    return sum(last) / period


def analyze(symbol, candles, cfg):
    closes, highs, lows = candles["c"], candles["h"], candles["l"]
    if len(closes) < cfg["breakout_lookback"] + 1:
        return None
    price = closes[-1]
    a = atr(highs, lows, closes, cfg["rsi_period"])
    r = rsi(closes, cfg["rsi_period"])
    if a is None or r is None:
        return None
    atr_pct = a / price
    lookback_high = max(highs[-(cfg["breakout_lookback"] + 1):-1])
    breakout = price > lookback_high
    return {
        "price": price,
        "atr_pct": atr_pct,
        "rsi": r,
        "breakout": breakout,
    }


def business_days_between(start, end):
    days = 0
    cur = start
    while cur < end:
        cur += datetime.timedelta(days=1)
        if cur.weekday() < 5:
            days += 1
    return days


def process_exits(state, cfg, analyses, today):
    today_date = datetime.date.fromisoformat(today)
    for symbol in list(state["positions"].keys()):
        pos = state["positions"][symbol]
        info = analyses.get(symbol)
        if info is None:
            continue
        price = info["price"]
        state["last_prices"][symbol] = price
        pnl_pct = (price - pos["entry_price"]) / pos["entry_price"]
        entry_date = datetime.date.fromisoformat(pos["entry_date"])
        pos["days_held"] = business_days_between(entry_date, today_date)

        reason = None
        if pnl_pct >= cfg["take_profit_pct"]:
            reason = "take_profit"
        elif pnl_pct <= -cfg["stop_loss_pct"]:
            reason = "stop_loss"
        elif pos["days_held"] >= cfg["max_hold_days"]:
            reason = "time_exit"

        if reason:
            proceeds = pos["shares"] * price
            pnl = proceeds - pos["shares"] * pos["entry_price"]
            state["cash"] += proceeds
            state["trade_log"].append({
                "date": today,
                "symbol": symbol,
                "action": "SELL",
                "shares": pos["shares"],
                "price": price,
                "reason": reason,
                "pnl": round(pnl, 2),
            })
            del state["positions"][symbol]
            print(f"  SELL {symbol}: {pos['shares']:.4f} sh @ {price:.2f} "
                  f"({reason}, pnl={pnl:.2f})")


def process_entries(state, cfg, analyses, today):
    slots_free = cfg["max_positions"] - len(state["positions"])
    if slots_free <= 0:
        return

    candidates = []
    for symbol, info in analyses.items():
        if symbol in state["positions"]:
            continue
        if info["atr_pct"] < cfg["atr_volatility_min_pct"]:
            continue
        if not info["breakout"]:
            continue
        if info["rsi"] >= cfg["rsi_overbought"]:
            continue
        candidates.append((symbol, info))

    candidates.sort(key=lambda x: x[1]["atr_pct"], reverse=True)

    for symbol, info in candidates[:slots_free]:
        allocation = state["cash"] * cfg["position_size_pct"]
        price = info["price"]
        if allocation < 0.01 or state["cash"] < allocation:
            continue
        shares = allocation / price
        state["cash"] -= allocation
        state["positions"][symbol] = {
            "shares": shares,
            "entry_price": price,
            "entry_date": today,
            "days_held": 0,
        }
        state["trade_log"].append({
            "date": today,
            "symbol": symbol,
            "action": "BUY",
            "shares": shares,
            "price": price,
            "reason": f"breakout, atr%={info['atr_pct']:.3f}, rsi={info['rsi']:.1f}",
        })
        print(f"  BUY {symbol}: {shares:.4f} sh @ {price:.2f} "
              f"(atr%={info['atr_pct']:.3f}, rsi={info['rsi']:.1f})")


def build_watchlist_snapshot(cfg, analyses, positions):
    snapshot = {}
    for symbol, info in analyses.items():
        if symbol in positions:
            signal = "in_position"
        elif (info["atr_pct"] >= cfg["atr_volatility_min_pct"]
              and info["breakout"]
              and info["rsi"] < cfg["rsi_overbought"]):
            signal = "buy_candidate"
        else:
            signal = "no_signal"
        snapshot[symbol] = {
            "price": info["price"],
            "atr_pct": round(info["atr_pct"], 4),
            "rsi": round(info["rsi"], 1),
            "breakout": info["breakout"],
            "signal": signal,
        }
    return snapshot


def update_equity(state, analyses, today):
    equity = state["cash"]
    for symbol, pos in state["positions"].items():
        price = analyses.get(symbol, {}).get("price", state["last_prices"].get(symbol, pos["entry_price"]))
        state["last_prices"][symbol] = price
        equity += pos["shares"] * price

    history = state["equity_history"]
    if history and history[-1]["date"] == today:
        history[-1]["equity"] = round(equity, 2)
    else:
        history.append({"date": today, "equity": round(equity, 2)})


def main():
    cfg = load_json(CONFIG_PATH)
    state = load_json(STATE_PATH)
    today = datetime.date.today().isoformat()

    symbols = sorted(set(cfg["watchlist"]) | set(state["positions"].keys()))
    print(f"Fetching {len(symbols)} symbols...")

    analyses = {}
    for symbol in symbols:
        candles = fetch_candles(symbol)
        if candles is not None:
            info = analyze(symbol, candles, cfg)
            if info is not None:
                analyses[symbol] = info
        time.sleep(0.5)  # be polite between requests

    process_exits(state, cfg, analyses, today)
    process_entries(state, cfg, analyses, today)
    update_equity(state, analyses, today)
    state["watchlist_snapshot"] = build_watchlist_snapshot(cfg, analyses, state["positions"])
    state["last_run"] = datetime.datetime.utcnow().isoformat() + "Z"

    save_json(STATE_PATH, state)
    print(f"Done. Cash={state['cash']:.2f}, "
          f"positions={list(state['positions'].keys())}, "
          f"equity={state['equity_history'][-1]['equity']:.2f}")


if __name__ == "__main__":
    main()
