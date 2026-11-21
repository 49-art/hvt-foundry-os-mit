"""Stamp cards: e.g. 'every 6th cut free'. Each card has a code the customer keeps."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict

from .store import EngineError, JsonStore, new_code, now_local


class Loyalty:
    def __init__(self, path: Path | str, shop: Callable[[], Dict[str, Any]], now=now_local):
        self.store = JsonStore(path, lambda: {"cards": {}})
        self.shop, self.now = shop, now

    def rules(self) -> Dict[str, Any]:
        r = (self.shop().get("loyalty") or {})
        n = int(r.get("stamps_needed") or 6)
        if not 2 <= n <= 30:
            raise EngineError("Stamps needed must be between 2 and 30.")
        return {"stamps_needed": n, "reward": r.get("reward") or "A free visit (ask in the shop for details)"}

    def new_card(self, name: str = "", phone: str = "") -> Dict[str, Any]:
        def f(d):
            code = new_code(8)
            while code in d["cards"]:
                code = new_code(8)
            d["cards"][code] = {"code": code, "name": (name or "")[:60], "phone": (phone or "")[:16], "stamps": 0,
                                "rewards_ready": 0, "rewards_used": 0, "log": [], "created_at": self.now().isoformat()}
            return d["cards"][code]
        return self.store.update(f)

    def stamp(self, code: str, n: int = 1, note: str = "") -> Dict[str, Any]:
        if not 1 <= int(n) <= 5:
            raise EngineError("Add between 1 and 5 stamps at a time.")
        need = self.rules()["stamps_needed"]

        def f(d):
            c = d["cards"].get((code or "").upper())
            if not c:
                raise EngineError("No loyalty card with that code.")
            c["stamps"] += int(n)
            while c["stamps"] >= need:
                c["stamps"] -= need
                c["rewards_ready"] += 1
            c["log"].append({"at": self.now().isoformat(), "stamps": int(n), "note": note[:80]})
            return c
        return self.store.update(f)

    def redeem(self, code: str) -> Dict[str, Any]:
        def f(d):
            c = d["cards"].get((code or "").upper())
            if not c:
                raise EngineError("No loyalty card with that code.")
            if c["rewards_ready"] < 1:
                raise EngineError("This card has no reward ready yet.")
            c["rewards_ready"] -= 1
            c["rewards_used"] += 1
            c["log"].append({"at": self.now().isoformat(), "redeemed": 1})
            return c
        return self.store.update(f)

    def public_view(self, code: str) -> Dict[str, Any]:
        c = self.store.load()["cards"].get((code or "").upper())
        if not c:
            raise EngineError("No loyalty card with that code.")
        r = self.rules()
        return {"code": c["code"], "stamps": c["stamps"], "stamps_needed": r["stamps_needed"],
                "rewards_ready": c["rewards_ready"], "reward": r["reward"]}

    def all(self):
        return list(self.store.load()["cards"].values())
