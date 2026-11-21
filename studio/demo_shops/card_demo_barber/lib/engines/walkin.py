"""
Walk-in queue for barbers (v3).

Customers join on their phone or at the counter. The board shows who is in the chair
and who is next; each customer's ticket page says "You're next" when it is their turn.
The public board only ever shows a ticket number and a first name. Phone numbers stay
in the owner's view.

Rules, each proved by a theory-test case (studio/test_salon_theory_cases.py):
  * Waits are worked out from each person's own service length, on a small timeline
    per chair: who is in the chair now and when they finish, who is ahead, and any
    BOOKED appointments in the same chairs (mixed shops).                (Q1, Q5 - fix 6)
  * Leaving moves everyone behind up one.                                 (Q2)
  * Skipping (called but not there): first time back 2 places, second
    time taken off the queue.                                             (Q3)
  * A barber who becomes free calls the FIRST PERSON HE CAN SERVE, not
    strictly the first in line ("wants Ash only" doesn't block Ben). (Q4 - fix 5)
  * Joining stops when the estimated finish would be after closing.       (Q6)
  * One place per phone number.                                           (Q7)
  * Every ticket answer carries the time it was checked, so a phone that
    loses signal shows "last checked at ..." instead of guessing.         (Q8)
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .store import EngineError, JsonStore, new_code, now_local

WAITING, CALLED, IN_CHAIR, DONE, LEFT, REMOVED = "waiting", "called", "in_chair", "done", "left", "removed"
ACTIVE = (WAITING, CALLED, IN_CHAIR)
DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def _min(dt: datetime) -> int:
    return dt.hour * 60 + dt.minute


def _hm(m: int) -> str:
    return f"{(m // 60) % 24:02d}:{m % 60:02d}"


def _pkey(p: str) -> str:
    d = "".join(ch for ch in str(p or "") if ch.isdigit())
    return d[2:] if d.startswith("44") else d.lstrip("0")


class WalkInQueue:
    def __init__(self, path: Path | str, shop: Callable[[], Dict[str, Any]], now: Callable[[], datetime] = now_local,
                 booked: Optional[Callable[[str, str], List[Tuple[int, int]]]] = None):
        """booked(barber_id, 'YYYY-MM-DD') -> booked (start, end) minutes for that barber today,
        from the booking engine. None = this shop takes walk-ins only."""
        self.store = JsonStore(path, lambda: {"day": "", "n": 0, "open": True, "tickets": []})
        self.shop = shop
        self.now = now
        self.booked = booked

    # ------------------------------------------------------------ helpers
    def _today(self, data):
        today = self.now().date().isoformat()
        if data.get("day") != today:                  # a fresh queue each morning; yesterday kept in history
            data.setdefault("history", []).extend(data.get("tickets", []))
            data["history"] = data["history"][-500:]
            data.update(day=today, n=0, tickets=[])
        return data

    def _barbers(self) -> List[Dict[str, Any]]:
        return [s for s in self.shop().get("staff", []) if s.get("walk_ins", True) is not False]

    def _dur(self, service_id: str) -> int:
        for s in self.shop().get("services", []):
            if s.get("id") == service_id:
                return int(s.get("duration_min") or 30)
        return int((self.shop().get("walkin") or {}).get("default_minutes", 30))

    def _close(self) -> Optional[int]:
        """Closing time today in minutes; None if no hours are set; -1 if closed today."""
        shop = self.shop()
        w = shop.get("walkin") or {}
        if w.get("last_finish"):
            return int(w["last_finish"][:2]) * 60 + int(w["last_finish"][3:5])
        day = DAYS[self.now().weekday()]
        h = next((x for x in shop.get("hours", []) if x.get("day") == day), None)
        if not shop.get("hours"):
            return None
        if not h or h.get("closed") or not h.get("close"):
            return -1
        return int(h["close"][:2]) * 60 + int(h["close"][3:5])

    def _busy_blocks(self, barber: str, day: str) -> List[Tuple[int, int]]:
        if not self.booked:
            return []
        try:
            return sorted(self.booked(barber, day))
        except Exception:                             # never let the board fail because of bookings
            return []

    def _timeline(self, d, upto: Optional[Dict[str, Any]] = None, extra: Optional[Dict[str, Any]] = None) -> Dict[str, int]:
        """Estimated start minute for each waiting ticket (by number), in queue order.
        `extra` = a not-yet-joined ticket placed at the back, for "if you joined now"."""
        now_m = _min(self.now())
        pool_all = [b["id"] for b in self._barbers()] or ["chair"]
        free = {b: now_m for b in pool_all}
        for t in d["tickets"]:                        # who is in a chair now, and till when
            if t["status"] in (CALLED, IN_CHAIR) and t.get("chair") in free:
                since = datetime.fromisoformat(t.get("started_at") or t.get("called_at") or self.now().isoformat())
                free[t["chair"]] = max(free[t["chair"]], _min(since) + self._dur(t["service_id"]))
        booked = {b: self._busy_blocks(b, d["day"]) for b in pool_all}

        def next_fit(b, t, dur):
            for s, e in booked[b]:
                if e <= t:
                    continue
                if t + dur <= s:
                    return t
                t = max(t, e)
            return t

        out = {}
        line = [t for t in d["tickets"] if t["status"] == WAITING] + ([extra] if extra else [])
        for t in line:
            dur = self._dur(t["service_id"])
            pool = [t["barber"]] if t["barber"] in free else pool_all
            cand = min(pool, key=lambda b: (next_fit(b, free[b], dur), pool_all.index(b)))
            start = next_fit(cand, free[cand], dur)
            free[cand] = start + dur
            out[t["no"]] = start
            if upto is not None and t is upto:
                break
        return out

    def _wait(self, d, t) -> int:
        return max(0, self._timeline(d, upto=t).get(t["no"], _min(self.now())) - _min(self.now()))

    def _position(self, d, t) -> int:
        """1 = next. Counts waiting tickets ahead that the same barber(s) could serve."""
        ahead = 0
        for x in d["tickets"]:
            if x is t:
                break
            if x["status"] == WAITING and (t["barber"] == "any" or x["barber"] in ("any", t["barber"])):
                ahead += 1
        return ahead + 1

    # ------------------------------------------------------------ actions
    def set_open(self, on: bool) -> Dict[str, Any]:
        return self.store.update(lambda d: self._today(d).update(open=bool(on)) or {"open": d["open"]})

    def join(self, name: str, service_id: str = "", barber: str = "any", phone: str = "") -> Dict[str, Any]:
        name = (name or "").strip()[:24]
        if not name:
            raise EngineError("Please give a first name (or initials) for the board.")
        barber = barber or "any"
        if barber != "any" and barber not in {b["id"] for b in self._barbers()}:
            raise EngineError("That barber isn't taking walk-ins today.")
        if service_id and not any(s.get("id") == service_id for s in self.shop().get("services", [])):
            raise EngineError("That service isn't on the price list.")
        limit = int((self.shop().get("walkin") or {}).get("max_waiting", 25))
        phone = (phone or "")[:16]

        def add(d):
            self._today(d)
            if not d.get("open", True):
                raise EngineError("The walk-in queue is closed for now. Please call the shop.")
            if phone and _pkey(phone):
                for x in d["tickets"]:
                    if x["status"] in ACTIVE and _pkey(x.get("phone")) == _pkey(phone):
                        raise EngineError(f"This phone number already has a place in the queue (ticket {x['no']}).")
            if sum(1 for t in d["tickets"] if t["status"] == WAITING) >= limit:
                raise EngineError("The queue is full right now. Please try again a bit later.")
            close = self._close()
            if close == -1:
                raise EngineError("The shop is closed today.")
            probe = {"no": "new", "service_id": service_id, "barber": barber, "status": WAITING}
            start = self._timeline(d, extra=probe)["new"]
            if close is not None and start + self._dur(service_id) > close:
                raise EngineError("Sorry, the queue is closed for today - we wouldn't finish before closing. "
                                  "Please book for another day, or call the shop.")
            d["n"] += 1
            t = {"no": f"{d['n']:03d}", "token": new_code(10), "name": name, "service_id": service_id,
                 "barber": barber, "phone": phone, "status": WAITING, "skips": 0,
                 "joined_at": self.now().isoformat(), "called_at": None, "started_at": None, "chair": ""}
            d["tickets"].append(t)
            return t
        t = self.store.update(add)
        return dict(self.ticket(t["token"]), token=t["token"])

    def ticket(self, token: str) -> Dict[str, Any]:
        d = self._today(self.store.load())
        names = {b["id"]: b.get("name", "") for b in self._barbers()}
        for t in d["tickets"]:
            if t["token"] == token:
                out = {"no": t["no"], "name": t["name"], "status": t["status"],
                       "chair": names.get(t["chair"], t["chair"]), "checked_at": self.now().isoformat(timespec="minutes")}
                if t["status"] == WAITING:
                    pos, wait = self._position(d, t), self._wait(d, t)
                    out.update(position=pos, youre_next=pos == 1, wait_minutes=wait,
                               about=_hm(_min(self.now()) + wait))
                return out
        raise EngineError("That ticket isn't in today's queue.")

    def board(self) -> Dict[str, Any]:
        d = self._today(self.store.load())
        waiting = [t for t in d["tickets"] if t["status"] == WAITING]
        names = {b["id"]: b.get("name", "") for b in self._barbers()}
        tl = self._timeline(d, extra={"no": "new", "service_id": "", "barber": "any", "status": WAITING})
        now_m = _min(self.now())
        first = lambda n: (n or "").split()[0] if (n or "").split() else ""  # noqa: E731
        return {"open": d.get("open", True), "day": d["day"], "checked_at": self.now().isoformat(timespec="minutes"),
                "now_serving": [{"no": t["no"], "name": first(t["name"]), "chair": names.get(t["chair"], t["chair"]),
                                 "status": t["status"]} for t in d["tickets"] if t["status"] in (CALLED, IN_CHAIR)],
                "next": [{"no": t["no"], "name": first(t["name"]), "barber": names.get(t["barber"], "Any barber"),
                          "about": _hm(tl.get(t["no"], now_m))} for t in waiting[:6]],
                "waiting_count": len(waiting),
                "estimated_wait_minutes": max(0, tl["new"] - now_m)}

    def call_next(self, chair: str) -> Dict[str, Any]:
        """A barber becomes free and calls the first waiting customer they can serve (fix 5)."""
        def f(d):
            self._today(d)
            for t in d["tickets"]:
                if t["status"] == WAITING and t["barber"] in ("any", chair):
                    t.update(status=CALLED, chair=chair, called_at=self.now().isoformat())
                    return t
            raise EngineError("Nobody is waiting who this barber can serve.")
        return self.store.update(f)

    def skip(self, no: str) -> Dict[str, Any]:
        """Called but not there. First time: back 2 places. Second time: off the queue."""
        def f(d):
            self._today(d)
            t = next((x for x in d["tickets"] if x["no"] == no and x["status"] in (WAITING, CALLED)), None)
            if not t:
                raise EngineError("No such waiting ticket today.")
            t["skips"] = int(t.get("skips", 0)) + 1
            if t["skips"] >= 2:
                t["status"] = REMOVED
                return {"no": no, "removed": True}
            waiting_before = [x for x in d["tickets"] if x["status"] == WAITING and x is not t]
            old_index = [x for x in d["tickets"] if x["status"] == WAITING or x is t].index(t)
            d["tickets"].remove(t)
            t.update(status=WAITING, chair="", called_at=None)
            target = min(old_index + 2, len(waiting_before))
            if target >= len(waiting_before):
                d["tickets"].append(t)
            else:
                d["tickets"].insert(d["tickets"].index(waiting_before[target]), t)
            pos = [x for x in d["tickets"] if x["status"] == WAITING].index(t) + 1
            return {"no": no, "removed": False, "new_position": pos}
        return self.store.update(f)

    def set_status(self, no: str, status: str) -> Dict[str, Any]:
        if status not in (IN_CHAIR, DONE, LEFT, WAITING, REMOVED):
            raise EngineError("Unknown queue status.")

        def f(d):
            self._today(d)
            for t in d["tickets"]:
                if t["no"] == no:
                    t["status"] = status
                    if status == IN_CHAIR:
                        t["started_at"] = self.now().isoformat()
                    return t
            raise EngineError("No such ticket today.")
        return self.store.update(f)

    def leave(self, token: str) -> Dict[str, Any]:
        def f(d):
            self._today(d)
            for t in d["tickets"]:
                if t["token"] == token and t["status"] == WAITING:
                    t["status"] = LEFT
                    return {"ok": True}
            raise EngineError("That ticket can't be cancelled now.")
        return self.store.update(f)

    def admin_list(self) -> List[Dict[str, Any]]:
        return self._today(self.store.load())["tickets"]
