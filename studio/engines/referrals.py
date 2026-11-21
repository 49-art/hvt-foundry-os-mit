"""Referral codes: a client shares a code; when a new client books with it, both are noted for the owner's reward."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict

from .store import EngineError, JsonStore, new_code, now_local


class Referrals:
    def __init__(self, path: Path | str, shop: Callable[[], Dict[str, Any]], now=now_local):
        self.store = JsonStore(path, lambda: {"codes": {}})
        self.shop, self.now = shop, now

    def create(self, owner_name: str, phone: str = "") -> Dict[str, Any]:
        if not (owner_name or "").strip():
            raise EngineError("Whose code is it? Give a name.")

        def f(d):
            code = "R" + new_code(5)
            d["codes"][code] = {"code": code, "owner": owner_name[:60], "phone": phone[:16], "uses": [],
                                "created_at": self.now().isoformat()}
            return d["codes"][code]
        return self.store.update(f)

    def use(self, code: str, new_client: str, booking_id: str = "") -> Dict[str, Any]:
        def f(d):
            c = d["codes"].get((code or "").upper())
            if not c:
                raise EngineError("That referral code isn't recognised.")
            if any(u["new_client"].lower() == new_client.lower() for u in c["uses"]):
                raise EngineError("This person has already used this code.")
            c["uses"].append({"new_client": new_client[:60], "booking": booking_id, "at": self.now().isoformat(),
                              "rewarded": False})
            return c
        return self.store.update(f)

    def valid(self, code: str) -> bool:
        return (code or "").upper() in self.store.load()["codes"]

    def all(self):
        return list(self.store.load()["codes"].values())
