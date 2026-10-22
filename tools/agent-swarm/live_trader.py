#!/usr/bin/env python3
"""Run the swarm's trading rule on live prices, once per call (e.g. once a day).

Paper mode (default): a pretend wallet in paper_state.json follows the rule on
real live prices. No account, no keys, no money.

Live mode (--live): places real market orders on Coinbase Advanced Trade
through ccxt. It refuses to run unless all of these are set, and it stops
itself for good once the loss limit is hit:
  COINBASE_API_KEY / COINBASE_API_SECRET   - API key with trade permission only
                                             (never withdraw permission)
  --max-usd N        largest amount of USD the bot may ever put in
  --stop-loss-pct P  sell everything and stop if the bot's money falls P%
                     below what it started with

Usage:
  python3 trader.py --save-rule rule.json            # let the swarm pick a rule
  python3 live_trader.py --rule rule.json            # paper trade, one step
  python3 live_trader.py --rule rule.json --live --max-usd 50 --stop-loss-pct 20

Needs: pip install -r requirements.txt
"""
import argparse
import json
import os
import sys
import time

import ccxt

FEE = 0.001
CA_BUNDLE = "/root/.ccr/ca-bundle.crt"  # Claude Code cloud proxy; harmless elsewhere


def exchange(live):
    if os.path.exists(CA_BUNDLE):
        os.environ.setdefault("REQUESTS_CA_BUNDLE", CA_BUNDLE)
    opts = {"enableRateLimit": True}
    if os.environ.get("HTTPS_PROXY"):
        opts["httpsProxy"] = os.environ["HTTPS_PROXY"]
    if live:
        opts["apiKey"] = os.environ["COINBASE_API_KEY"]
        opts["secret"] = os.environ["COINBASE_API_SECRET"].replace("\\n", "\n")
    return ccxt.coinbase(opts)


def signal(ex, symbol, rule):
    """True = hold the coin. Uses only fully closed daily candles."""
    need = rule["slow"] + 2
    candles = ex.fetch_ohlcv(symbol, "1d", limit=need + 1)
    today = int(time.time() // 86400 * 86400 * 1000)
    closes = [c[4] for c in candles if c[0] < today][-need:]
    if len(closes) < rule["slow"]:
        sys.exit(f"Only {len(closes)} daily candles available; rule needs {rule['slow']}.")
    fast = sum(closes[-rule["fast"]:]) / rule["fast"]
    slow = sum(closes[-rule["slow"]:]) / rule["slow"]
    return fast > slow * (1 + rule["band"]), fast, slow


def load(path, default):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default


def save(path, state):
    with open(path, "w") as f:
        json.dump(state, f, indent=1)


def paper_step(ex, a, rule, want_coin, price):
    st = load(a.state, {"usd": a.start_usd, "coin": 0.0, "start_usd": a.start_usd,
                        "start_price": price, "log": []})
    action = "hold"
    if want_coin and st["usd"] > 0:
        st["coin"], st["usd"], action = st["usd"] * (1 - FEE) / price, 0.0, "BUY"
    elif not want_coin and st["coin"] > 0:
        st["usd"], st["coin"], action = st["coin"] * price * (1 - FEE), 0.0, "SELL"
    value = st["usd"] + st["coin"] * price
    hold = st["start_usd"] * price / st["start_price"]
    st["log"].append({"time": time.strftime("%Y-%m-%d %H:%M"), "price": price,
                      "action": action, "value": round(value, 2)})
    save(a.state, st)
    print(f"PAPER {action:4s} at {price:,.2f}  wallet {value:,.2f} USD "
          f"({value / st['start_usd'] - 1:+.1%})  just-holding {hold:,.2f} USD")


def live_step(ex, a, rule, want_coin, price):
    base, quote = a.symbol.split("/")
    st = load(a.state, {"stopped": False, "start_value": None})
    if st["stopped"]:
        sys.exit("Bot is stopped by its loss limit. Delete the state file only if you mean to restart.")
    bal = ex.fetch_balance()
    coin, usd = bal["free"].get(base, 0.0), bal["free"].get(quote, 0.0)
    bot_coin = min(coin, st.get("bot_coin", 0.0))
    bot_usd = st.get("bot_usd", min(usd, a.max_usd))
    value = bot_usd + bot_coin * price
    if st["start_value"] is None:
        st["start_value"] = value
    print(f"LIVE  {a.symbol} {price:,.2f}  bot money {value:,.2f} {quote} (start {st['start_value']:,.2f})")

    if value < st["start_value"] * (1 - a.stop_loss_pct / 100):
        if bot_coin > 0:
            ex.create_market_sell_order(a.symbol, ex.amount_to_precision(a.symbol, bot_coin))
        st["stopped"] = True
        save(a.state, st)
        sys.exit(f"Loss limit {a.stop_loss_pct}% hit: sold to cash and stopped.")

    if want_coin and bot_usd >= 1:
        cost = min(bot_usd, a.max_usd, usd)
        order = ex.create_market_buy_order_with_cost(a.symbol, cost)
        st["bot_usd"], st["bot_coin"] = bot_usd - cost, bot_coin + cost * (1 - FEE) / price
        print(f"BUY  {cost:,.2f} {quote} of {base}  order {order.get('id')}")
    elif not want_coin and bot_coin > 0:
        order = ex.create_market_sell_order(a.symbol, ex.amount_to_precision(a.symbol, bot_coin))
        st["bot_usd"], st["bot_coin"] = bot_usd + bot_coin * price * (1 - FEE), 0.0
        print(f"SELL {bot_coin} {base}  order {order.get('id')}")
    else:
        st.setdefault("bot_usd", bot_usd)
        st.setdefault("bot_coin", bot_coin)
        print("hold - nothing to do")
    save(a.state, st)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rule", required=True, help="rule JSON from trader.py --save-rule")
    ap.add_argument("--symbol", default="BTC/USD")
    ap.add_argument("--state", help="state file (default paper_state.json / live_state.json)")
    ap.add_argument("--start-usd", type=float, default=1000.0, help="paper wallet size")
    ap.add_argument("--live", action="store_true", help="trade real money")
    ap.add_argument("--max-usd", type=float, help="live: most USD the bot may ever use")
    ap.add_argument("--stop-loss-pct", type=float, help="live: stop for good after this % loss")
    a = ap.parse_args()
    a.state = a.state or ("live_state.json" if a.live else "paper_state.json")

    if a.live:
        missing = [n for n in ("COINBASE_API_KEY", "COINBASE_API_SECRET") if not os.environ.get(n)]
        if missing or a.max_usd is None or a.stop_loss_pct is None:
            sys.exit("Live mode needs COINBASE_API_KEY, COINBASE_API_SECRET, --max-usd and --stop-loss-pct.")

    with open(a.rule) as f:
        rule = json.load(f)
    ex = exchange(a.live)
    want_coin, fast, slow = signal(ex, a.symbol, rule)
    price = ex.fetch_ticker(a.symbol)["last"]
    print(f"Rule {rule['fast']}/{rule['slow']} band {rule['band']:.4f}: fast avg {fast:,.2f}, "
          f"slow avg {slow:,.2f} -> {'be IN' if want_coin else 'be OUT'}")
    (live_step if a.live else paper_step)(ex, a, rule, want_coin, price)


if __name__ == "__main__":
    main()
