"""Staff rota (shifts) and a simple commission tracker."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable, Dict, List

from .money import pounds, to_pence
from .store import EngineError, JsonStore, now_local


class Rota:
    def __init__(self, path: Path | str, shop: Callable[[], Dict[str, Any]], now=now_local):
        self.store = JsonStore(path, lambda: {"shifts": [], "takings": [], "seq": 0})
        self.shop, self.now = shop, now

    def _staff(self, sid):
        st = next((s for s in self.shop().get("staff", []) if s.get("id") == sid), None)
        if not st:
            raise EngineError("No such staff member.")
        return st

    def add_shift(self, staff_id: str, day: str, start: str, end: str) -> Dict[str, Any]:
        self._staff(staff_id)
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day or "") or not all(re.fullmatch(r"[0-2]\d:[0-5]\d", x or "") for x in (start, end)):
            raise EngineError("Use a date like 2026-10-03 and times like 09:00.")
        if end <= start:
            raise EngineError("A shift must end after it starts.")

        def f(d):
            for s in d["shifts"]:
                if s["staff_id"] == staff_id and s["date"] == day and start < s["end"] and s["start"] < end:
                    raise EngineError("That overlaps another shift for the same person.")
            d["seq"] += 1
            s = {"id": f"SH{d['seq']:05d}", "staff_id": staff_id, "date": day, "start": start, "end": end}
            d["shifts"].append(s)
            return s
        return self.store.update(f)

    def remove_shift(self, shift_id: str) -> Dict[str, Any]:
        def f(d):
            before = len(d["shifts"])
            d["shifts"] = [s for s in d["shifts"] if s["id"] != shift_id]
            if len(d["shifts"]) == before:
                raise EngineError("No such shift.")
            return {"removed": shift_id}
        return self.store.update(f)

    def week(self, day_from: str, day_to: str) -> List[Dict[str, Any]]:
        return sorted([s for s in self.store.load()["shifts"] if day_from <= s["date"] <= day_to],
                      key=lambda s: (s["date"], s["start"]))

    def add_takings(self, staff_id: str, day: str, amount, kind: str = "service", ref: str = "") -> Dict[str, Any]:
        self._staff(staff_id)
        if kind not in ("service", "retail"):
            raise EngineError("Kind must be service or retail.")
        pence = to_pence(amount)

        def f(d):
            d["seq"] += 1
            t = {"id": f"TK{d['seq']:05d}", "staff_id": staff_id, "date": day, "pence": pence, "kind": kind, "ref": ref[:20]}
            d["takings"].append(t)
            return t
        return self.store.update(f)

    def commission(self, day_from: str, day_to: str) -> List[Dict[str, Any]]:
        """Per staff: takings and commission at the owner-set rates (percent). Rounded down to the penny."""
        out = []
        tk = [t for t in self.store.load()["takings"] if day_from <= t["date"] <= day_to]
        for st in self.shop().get("staff", []):
            rate_s = float((st.get("commission") or {}).get("service_percent") or 0)
            rate_r = float((st.get("commission") or {}).get("retail_percent") or 0)
            s = sum(t["pence"] for t in tk if t["staff_id"] == st["id"] and t["kind"] == "service")
            r = sum(t["pence"] for t in tk if t["staff_id"] == st["id"] and t["kind"] == "retail")
            c = int(s * rate_s / 100) + int(r * rate_r / 100)
            out.append({"staff_id": st["id"], "name": st.get("name"), "service_takings": pounds(s), "retail_takings": pounds(r),
                        "service_percent": rate_s, "retail_percent": rate_r, "commission": pounds(c), "commission_pence": c})
        return out
