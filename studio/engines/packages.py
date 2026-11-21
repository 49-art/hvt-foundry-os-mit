"""Memberships and prepaid packages, e.g. '5 beard trims' or 'monthly blow-dry club'."""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any, Callable, Dict

from .store import EngineError, JsonStore, new_code, now_local


class Packages:
    def __init__(self, path: Path | str, shop: Callable[[], Dict[str, Any]], now=now_local):
        self.store = JsonStore(path, lambda: {"sold": {}})
        self.shop, self.now = shop, now

    def plans(self):
        return (self.shop().get("packages") or [])

    def sell(self, plan_id: str, client_name: str, phone: str = "") -> Dict[str, Any]:
        plan = next((p for p in self.plans() if p.get("id") == plan_id), None)
        if not plan:
            raise EngineError("No such package.")
        uses = int(plan.get("uses") or 0)
        if not 1 <= uses <= 100:
            raise EngineError("A package needs between 1 and 100 visits.")
        days = int(plan.get("valid_days") or 365)

        def f(d):
            code = new_code(8)
            d["sold"][code] = {"code": code, "plan_id": plan_id, "plan_name": plan.get("name"), "client": client_name[:60],
                               "phone": phone[:16], "uses_total": uses, "uses_left": uses,
                               "sold": self.now().date().isoformat(),
                               "expires": (self.now().date() + timedelta(days=days)).isoformat(), "log": []}
            return d["sold"][code]
        return self.store.update(f)

    def use(self, code: str) -> Dict[str, Any]:
        def f(d):
            p = d["sold"].get((code or "").upper())
            if not p:
                raise EngineError("No package with that code.")
            if date.fromisoformat(p["expires"]) < self.now().date():
                raise EngineError(f"This package ended on {p['expires']}.")
            if p["uses_left"] < 1:
                raise EngineError("All visits on this package have been used.")
            p["uses_left"] -= 1
            p["log"].append({"at": self.now().isoformat()})
            return p
        return self.store.update(f)

    def all(self):
        return list(self.store.load()["sold"].values())
