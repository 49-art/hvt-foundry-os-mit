"""Gift vouchers with a balance that can be spent over several visits."""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any, Callable, Dict

from .money import pounds, to_pence
from .store import EngineError, JsonStore, new_code, now_local


class Vouchers:
    def __init__(self, path: Path | str, shop: Callable[[], Dict[str, Any]], now=now_local):
        self.store = JsonStore(path, lambda: {"vouchers": {}})
        self.shop, self.now = shop, now

    def issue(self, amount, buyer: str = "", for_name: str = "", months: int | None = None, paid: bool = True) -> Dict[str, Any]:
        pence = to_pence(amount)
        if not 100 <= pence <= 100000:
            raise EngineError("Vouchers can be from £1 to £1,000.")
        months = int(months or (self.shop().get("vouchers") or {}).get("valid_months") or 12)
        if not 1 <= months <= 60:
            raise EngineError("Validity must be between 1 and 60 months.")
        expires = (self.now().date() + timedelta(days=round(months * 30.44))).isoformat()

        def f(d):
            code = new_code(10)
            while code in d["vouchers"]:
                code = new_code(10)
            v = {"code": code, "value": pence, "balance": pence, "buyer": buyer[:60], "for": for_name[:60],
                 "issued": self.now().date().isoformat(), "expires": expires, "paid": bool(paid), "void": False, "log": []}
            d["vouchers"][code] = v
            return v
        return self.store.update(f)

    def _get(self, d, code):
        v = d["vouchers"].get((code or "").upper().replace("-", "").replace(" ", ""))
        if not v:
            raise EngineError("No voucher with that code.")
        return v

    def check(self, code: str) -> Dict[str, Any]:
        v = self._get(self.store.load(), code)
        expired = date.fromisoformat(v["expires"]) < self.now().date()
        return {"code": v["code"], "balance": pounds(v["balance"]), "balance_pence": v["balance"], "expires": v["expires"],
                "valid": not v["void"] and not expired and v["balance"] > 0, "expired": expired, "void": v["void"]}

    def redeem(self, code: str, amount) -> Dict[str, Any]:
        pence = to_pence(amount)

        def f(d):
            v = self._get(d, code)
            if v["void"]:
                raise EngineError("This voucher has been cancelled.")
            if date.fromisoformat(v["expires"]) < self.now().date():
                raise EngineError(f"This voucher expired on {v['expires']}.")
            if pence <= 0 or pence > v["balance"]:
                raise EngineError(f"This voucher only has {pounds(v['balance'])} left.")
            v["balance"] -= pence
            v["log"].append({"at": self.now().isoformat(), "spent": pence})
            return v
        return self.store.update(f)

    def void(self, code: str) -> Dict[str, Any]:
        def f(d):
            v = self._get(d, code)
            v["void"] = True
            return v
        return self.store.update(f)

    def all(self):
        return list(self.store.load()["vouchers"].values())
