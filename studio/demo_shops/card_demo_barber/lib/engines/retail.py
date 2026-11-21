"""Retail products (hair products etc.): stock counts, sales and low-stock warnings."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, List

from .store import EngineError, JsonStore, now_local


class Retail:
    """Stock lives in data/private/stock.json keyed by product id; the product list itself is in shop.json."""
    def __init__(self, path: Path | str, shop: Callable[[], Dict[str, Any]], now=now_local):
        self.store = JsonStore(path, lambda: {"stock": {}, "moves": []})
        self.shop, self.now = shop, now

    def products(self) -> List[Dict[str, Any]]:
        stock = self.store.load()["stock"]
        out = []
        for p in self.shop().get("products", []):
            q = stock.get(p["id"], {}).get("qty", 0)
            low = int(p.get("low_stock") or 2)
            out.append(dict(p, qty=q, low=q <= low))
        return out

    def _move(self, pid: str, delta: int, why: str):
        if pid not in {p["id"] for p in self.shop().get("products", [])}:
            raise EngineError("No such product.")

        def f(d):
            cur = d["stock"].setdefault(pid, {"qty": 0})
            if cur["qty"] + delta < 0:
                raise EngineError(f"Only {cur['qty']} in stock.")
            cur["qty"] += delta
            d["moves"].append({"at": self.now().isoformat(), "product": pid, "delta": delta, "why": why})
            d["moves"] = d["moves"][-2000:]
            return {"product": pid, "qty": cur["qty"]}
        return self.store.update(f)

    def receive(self, pid: str, qty: int) -> Dict[str, Any]:
        if not 1 <= int(qty) <= 10000:
            raise EngineError("Quantity must be 1 or more.")
        return self._move(pid, int(qty), "received")

    def sell(self, pid: str, qty: int = 1) -> Dict[str, Any]:
        if not 1 <= int(qty) <= 1000:
            raise EngineError("Quantity must be 1 or more.")
        return self._move(pid, -int(qty), "sold")

    def set_count(self, pid: str, qty: int) -> Dict[str, Any]:
        cur = self.store.load()["stock"].get(pid, {}).get("qty", 0)
        return self._move(pid, int(qty) - cur, "stock count")

    def public_stock(self) -> Dict[str, bool]:
        """Customers only see in stock / out of stock, never counts."""
        return {p["id"]: p["qty"] > 0 for p in self.products()}
