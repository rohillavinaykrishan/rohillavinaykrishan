#!/usr/bin/env python3
"""Put the swarm ledger's fingerprint on a public Ethereum blockchain.

The newest block hash of ledger.json is written into the data field of a
zero-value transaction from your wallet to itself. After that, anyone can look
the transaction up on a block explorer and check that your ledger has not been
changed since: the whole local chain hangs off that one hash.

Default network is Sepolia, Ethereum's public test network. Test ETH is free
from a faucet and has no money value. Mainnet costs real ETH in gas fees and
needs --i-understand-real-money.

Steps:
  python3 anchor.py --new-wallet           # make an address, fund it from a Sepolia faucet
  export ANCHOR_PRIVATE_KEY=0x...          # never commit this key
  python3 anchor.py ledger.json            # dry run: checks everything, sends nothing
  python3 anchor.py ledger.json --send     # broadcast the transaction
  python3 anchor.py ledger.json --check 0xTXHASH   # prove a ledger matches an anchor

Needs: pip install eth-account
"""
import argparse
import json
import os
import sys
import urllib.request

from eth_account import Account

from swarm import Ledger

NETWORKS = {
    "sepolia": {"rpc": "https://ethereum-sepolia-rpc.publicnode.com", "chain_id": 11155111,
                "explorer": "https://sepolia.etherscan.io/tx/"},
    "mainnet": {"rpc": "https://ethereum-rpc.publicnode.com", "chain_id": 1,
                "explorer": "https://etherscan.io/tx/"},
}


def rpc(url, method, *params):
    req = urllib.request.Request(
        url, json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": list(params)}).encode(),
        {"content-type": "application/json", "user-agent": "agent-swarm-anchor/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.load(r)
    if "error" in out:
        raise RuntimeError(f"{method}: {out['error'].get('message', out['error'])}")
    return out["result"]


def load_tip(path):
    with open(path) as f:
        saved = json.load(f)
    ledger = Ledger.__new__(Ledger)
    ledger.difficulty, ledger.blocks = saved["difficulty"], saved["blocks"]
    ok, bad = ledger.verify()
    if not ok:
        sys.exit(f"{path} is not a valid chain (broken at block {bad}); refusing to anchor it.")
    return ledger.blocks[-1]["hash"], len(ledger.blocks)


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("ledger", nargs="?", help="ledger JSON written by swarm.py --save")
    p.add_argument("--network", choices=NETWORKS, default="sepolia")
    p.add_argument("--send", action="store_true", help="actually broadcast (default is a dry run)")
    p.add_argument("--new-wallet", action="store_true", help="create a fresh wallet and exit")
    p.add_argument("--check", metavar="TXHASH", help="verify the ledger against an existing anchor")
    p.add_argument("--i-understand-real-money", action="store_true", help="required for mainnet")
    a = p.parse_args()

    if a.new_wallet:
        acct = Account.create()
        print(f"Address:     {acct.address}")
        print(f"Private key: {acct.key.hex()}")
        print("Save the key somewhere safe and private. Anyone with it controls the wallet.")
        print("Get free test ETH: search 'Sepolia faucet' and paste the address.")
        return
    if not a.ledger:
        p.error("give the ledger JSON file")
    if a.network == "mainnet" and not a.i_understand_real_money:
        sys.exit("Mainnet spends real ETH on gas. Add --i-understand-real-money if you mean it.")

    net = NETWORKS[a.network]
    tip, count = load_tip(a.ledger)
    print(f"Ledger {a.ledger}: {count} blocks, valid, tip hash {tip}")

    if a.check:
        tx = rpc(net["rpc"], "eth_getTransactionByHash", a.check)
        if not tx:
            sys.exit("Transaction not found on " + a.network)
        match = tx["input"].lower() == "0x" + tip
        print(f"On-chain data: {tx['input']}")
        print("MATCH: this ledger is exactly the one anchored." if match
              else "NO MATCH: the ledger differs from what was anchored.")
        sys.exit(0 if match else 1)

    key = os.environ.get("ANCHOR_PRIVATE_KEY")
    if not key:
        sys.exit("Set ANCHOR_PRIVATE_KEY (make one with --new-wallet).")
    acct = Account.from_key(key)
    tx = {"from": acct.address, "to": acct.address, "value": "0x0", "data": "0x" + tip}
    gas = int(int(rpc(net["rpc"], "eth_estimateGas", tx), 16) * 1.2)
    tip_fee = int(rpc(net["rpc"], "eth_maxPriorityFeePerGas"), 16)
    base = int(rpc(net["rpc"], "eth_getBlockByNumber", "latest", False)["baseFeePerGas"], 16)
    max_fee = 2 * base + tip_fee
    balance = int(rpc(net["rpc"], "eth_getBalance", acct.address, "latest"), 16)
    nonce = int(rpc(net["rpc"], "eth_getTransactionCount", acct.address, "pending"), 16)
    cost = gas * max_fee
    print(f"Network {a.network}, wallet {acct.address}")
    print(f"Balance {balance / 1e18:.6f} ETH, worst-case fee {cost / 1e18:.12f} ETH")
    if balance < cost:
        sys.exit("Not enough ETH for gas. Fund the wallet first (Sepolia faucets are free).")
    if not a.send:
        print("Dry run OK. Add --send to broadcast.")
        return

    signed = acct.sign_transaction({
        "type": 2, "chainId": net["chain_id"], "nonce": nonce, "to": acct.address, "value": 0,
        "data": "0x" + tip, "gas": gas, "maxFeePerGas": max_fee, "maxPriorityFeePerGas": tip_fee,
    })
    txhash = rpc(net["rpc"], "eth_sendRawTransaction", "0x" + signed.raw_transaction.hex().removeprefix("0x"))
    print(f"Sent: {net['explorer']}{txhash}")
    print(f"Later, prove the ledger is unchanged: python3 anchor.py {a.ledger} --check {txhash}")


if __name__ == "__main__":
    main()
