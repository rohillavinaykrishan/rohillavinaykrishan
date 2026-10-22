#!/usr/bin/env python3
"""Let the swarm search for a trading rule on real BTC prices - on paper only.

Every agent is one trading rule: buy BTC when the fast moving average is above
the slow one by more than a band, otherwise hold cash. The swarm (same QPSO
search as swarm.py) tunes the three numbers on the older 70% of the price
history, then the winner is tested on the newest 30% it has never seen, next
to plain buy-and-hold. A 0.1% fee is charged on every switch.

This never places a real trade and never touches money. A rule that looks good
on past prices often fails later; read the unseen-period result, not the
training one, and treat even that as a hint, not a promise.

Usage:
  python3 trader.py                      # 200,000 agents, ~1000 days of BTC-USD
  python3 trader.py --agents 1000000 --product ETH-USD
"""
import argparse
import json
import time
import urllib.request

import numpy as np

FEE = 0.001
MAX_WIN = 200


def fetch_closes(product, days):
    """Daily closes from Coinbase's public market-data API, oldest first."""
    closes, end = {}, int(time.time())
    while len(closes) < days:
        start = end - 300 * 86400
        url = (f"https://api.exchange.coinbase.com/products/{product}/candles"
               f"?granularity=86400&start={start}&end={end}")
        req = urllib.request.Request(url, headers={"user-agent": "agent-swarm-trader/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            rows = json.load(r)
        if not rows:
            break
        for t, _lo, _hi, _open, close, _vol in rows:
            closes[t] = close
        end = start
    return np.array([closes[t] for t in sorted(closes)][-days:], dtype=np.float64)


def moving_averages(close):
    """ma[w, t] = mean of the w closes ending at day t (NaN until w days exist)."""
    c = np.concatenate([[0.0], np.cumsum(close)])
    ma = np.full((MAX_WIN + 1, close.size), np.nan, dtype=np.float32)
    for w in range(1, MAX_WIN + 1):
        ma[w, w - 1:] = (c[w:] - c[:-w]) / w
    return ma


def backtest(params, ma, rets, lo, hi, chunk=20000):
    """Total return and Sharpe ratio of each rule over days lo..hi."""
    total = np.empty(len(params))
    sharpe = np.empty(len(params))
    for i in range(0, len(params), chunk):
        p = params[i:i + chunk]
        fast, slow = p[:, 0].astype(int), p[:, 1].astype(int)
        band = p[:, 2:3].astype(np.float32)
        sig = (ma[fast, lo - 1:hi - 1] > ma[slow, lo - 1:hi - 1] * (1 + band)).astype(np.float32)
        switches = np.abs(np.diff(sig, axis=1, prepend=0))
        daily = sig * rets[lo:hi] - switches * FEE
        total[i:i + chunk] = np.exp(np.sum(np.log1p(daily), axis=1)) - 1
        sd = daily.std(axis=1)
        sharpe[i:i + chunk] = np.where(sd > 0, daily.mean(axis=1) / np.maximum(sd, 1e-12) * np.sqrt(365), -9)
    return total, sharpe


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--agents", type=int, default=200_000)
    ap.add_argument("--rounds", type=int, default=15)
    ap.add_argument("--product", default="BTC-USD")
    ap.add_argument("--days", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()

    close = fetch_closes(a.product, a.days)
    rets = np.concatenate([[0.0], close[1:] / close[:-1] - 1]).astype(np.float32)
    ma = moving_averages(close)
    split = int(close.size * 0.7)
    train, test = (MAX_WIN, split), (split, close.size)
    print(f"{a.product}: {close.size} days, last close {close[-1]:,.2f}")
    print(f"Training days {train[0]}-{train[1]}, unseen test days {test[0]}-{test[1]}\n")

    rng = np.random.default_rng(a.seed)
    lo = np.array([2, 10, 0.0])
    hi = np.array([60, MAX_WIN, 0.05])

    def legal(x):
        x = np.clip(x, lo, hi)
        x[:, :2] = np.round(x[:, :2])
        x[:, 1] = np.maximum(x[:, 1], x[:, 0] + 1)
        return x

    x = legal(rng.uniform(lo, hi, (a.agents, 3)))
    pbest = x.copy()
    pscore = backtest(pbest, ma, rets, *train)[1]
    g = int(np.argmax(pscore))
    t0 = time.perf_counter()
    for r in range(1, a.rounds + 1):
        beta = 1.0 - 0.5 * r / a.rounds
        mbest = pbest.mean(axis=0)
        phi = rng.random(x.shape)
        attractor = phi * pbest + (1 - phi) * pbest[g]
        step = beta * np.abs(mbest - x) * np.log(1 / (rng.random(x.shape) + 1e-12))
        x = legal(attractor + np.where(rng.random(x.shape) < 0.5, -1, 1) * step)
        score = backtest(x, ma, rets, *train)[1]
        better = score > pscore
        pbest[better], pscore[better] = x[better], score[better]
        g = int(np.argmax(pscore))
        print(f"round {r:2d}  best training Sharpe {pscore[g]:.3f}")
    print(f"Search time {time.perf_counter() - t0:.1f}s for {a.agents * (a.rounds + 1):,} backtests\n")

    best = pbest[g:g + 1]
    fast, slow, band = int(best[0, 0]), int(best[0, 1]), best[0, 2]
    print(f"Best rule: buy when {fast}-day average > {slow}-day average x {1 + band:.4f}, else cash")
    for name, (lo_d, hi_d) in (("Training", train), ("UNSEEN TEST", test)):
        tot, sh = backtest(best, ma, rets, lo_d, hi_d)
        hold = close[hi_d - 1] / close[lo_d - 1] - 1
        print(f"{name:12s} rule {tot[0]:+8.1%} (Sharpe {sh[0]:5.2f})   buy-and-hold {hold:+8.1%}")
    print("\nPaper result only. Past prices do not promise future profit.")


if __name__ == "__main__":
    main()
