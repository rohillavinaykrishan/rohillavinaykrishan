#!/usr/bin/env python3
"""Million-agent swarm with a quantum-inspired search rule and a hash-chained ledger.

What this really is (no hype):
  * Agents   - each agent is one row in a NumPy array, so a million of them run
               together on a normal CPU. They are simple searchers, not minds.
  * "Quantum" - Quantum-behaved Particle Swarm Optimisation (QPSO, Sun et al. 2004).
               It is a classical algorithm whose move rule is borrowed from the
               quantum delta-potential well. No quantum computer is used.
  * Ledger   - every round's best answer is written into a SHA-256 block that
               links to the previous one and carries a small proof-of-work, so
               any later edit to the history is detected. It runs locally; it
               is not a public cryptocurrency network.

The swarm minimises a hard test function (Rastrigin: lots of local traps,
true minimum 0 at the origin) and reports how close it got and how fast.

Usage:
  python3 swarm.py                       # 1,000,000 agents, 8 dimensions
  python3 swarm.py --agents 5000000 --rounds 60
  python3 swarm.py --save ledger.json    # keep the ledger for anchor.py
"""
import argparse
import hashlib
import json
import time

import numpy as np


def rastrigin(x):
    return 10.0 * x.shape[1] + np.sum(x * x - 10.0 * np.cos(2.0 * np.pi * x), axis=1)


class Ledger:
    """A minimal blockchain: hash-linked blocks with proof-of-work."""

    def __init__(self, difficulty=4):
        self.difficulty = difficulty
        self.blocks = []
        self._add({"note": "genesis"})

    @staticmethod
    def _hash(block):
        body = {k: v for k, v in block.items() if k != "hash"}
        return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()

    def _add(self, data):
        block = {
            "index": len(self.blocks),
            "prev": self.blocks[-1]["hash"] if self.blocks else "0" * 64,
            "data": data,
            "nonce": 0,
        }
        target = "0" * self.difficulty
        while True:
            h = self._hash(block)
            if h.startswith(target):
                break
            block["nonce"] += 1
        block["hash"] = h
        self.blocks.append(block)
        return block

    def record(self, data):
        return self._add(data)

    def verify(self):
        target = "0" * self.difficulty
        for i, b in enumerate(self.blocks):
            if b["hash"] != self._hash(b) or not b["hash"].startswith(target):
                return False, i
            if i and b["prev"] != self.blocks[i - 1]["hash"]:
                return False, i
        return True, None


def run(agents, dim, rounds, seed, difficulty, save=None):
    rng = np.random.default_rng(seed)
    lo, hi = -5.12, 5.12
    x = rng.uniform(lo, hi, (agents, dim)).astype(np.float32)
    pbest = x.copy()
    pscore = rastrigin(pbest)
    g = int(np.argmin(pscore))
    gbest, gscore = pbest[g].copy(), float(pscore[g])
    ledger = Ledger(difficulty)

    print(f"Agents: {agents:,}  dimensions: {dim}  rounds: {rounds}")
    print(f"Start best score: {gscore:.4f}  (perfect = 0)\n")
    t0 = time.perf_counter()
    for r in range(1, rounds + 1):
        # QPSO move: each agent jumps around an attractor between its own best
        # and the swarm's best, with a step drawn from the quantum-well rule.
        beta = 1.0 - 0.5 * r / rounds
        mbest = pbest.mean(axis=0)
        phi = rng.random((agents, dim), dtype=np.float32)
        attractor = phi * pbest + (1.0 - phi) * gbest
        u = rng.random((agents, dim), dtype=np.float32) + 1e-12
        step = beta * np.abs(mbest - x) * np.log(1.0 / u)
        sign = np.where(rng.random((agents, dim)) < 0.5, -1.0, 1.0).astype(np.float32)
        x = np.clip(attractor + sign * step, lo, hi)

        score = rastrigin(x)
        better = score < pscore
        pbest[better] = x[better]
        pscore[better] = score[better]
        g = int(np.argmin(pscore))
        if pscore[g] < gscore:
            gbest, gscore = pbest[g].copy(), float(pscore[g])

        block = ledger.record({
            "round": r,
            "best_score": round(gscore, 6),
            "improved_agents": int(better.sum()),
            "best_position_sha256": hashlib.sha256(gbest.tobytes()).hexdigest(),
        })
        if r == 1 or r % 10 == 0 or r == rounds:
            print(f"round {r:3d}  best {gscore:10.6f}  "
                  f"improved {int(better.sum()):>9,}  block {block['hash'][:16]}...")
    elapsed = time.perf_counter() - t0

    evals = agents * (rounds + 1)
    ok, _ = ledger.verify()
    print(f"\nFinal best score: {gscore:.6f}  at {np.round(gbest, 4).tolist()}")
    print(f"Time: {elapsed:.2f}s  ->  {evals / elapsed:,.0f} agent-evaluations per second")
    print(f"Ledger: {len(ledger.blocks)} blocks, chain valid = {ok}")
    if save:
        with open(save, "w") as f:
            json.dump({"difficulty": ledger.difficulty, "blocks": ledger.blocks}, f, indent=1)
        print(f"Ledger saved to {save}  (anchor it on a public chain with anchor.py)")

    # Tamper test: change one past result and show the chain catches it.
    ledger.blocks[len(ledger.blocks) // 2]["data"]["best_score"] = -999.0
    ok, bad = ledger.verify()
    print(f"Tamper test: edited block {len(ledger.blocks) // 2} -> chain valid = {ok} "
          f"(broken at block {bad})")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--agents", type=int, default=1_000_000)
    p.add_argument("--dim", type=int, default=8)
    p.add_argument("--rounds", type=int, default=50)
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--difficulty", type=int, default=4, help="leading zero hex digits of proof-of-work")
    p.add_argument("--save", help="write the ledger to this JSON file")
    a = p.parse_args()
    run(a.agents, a.dim, a.rounds, a.seed, a.difficulty, a.save)
