"""
Booking engine (v3): services, stylists, opening hours, free slots, holds, deposits and bookings.

Written to the rules in the Hair Salon & Barber theory test (26 Sept 2026), including the
six fixes that test found. Each rule names the test case that proves it
(studio/test_salon_theory_cases.py):

  * Per-stylist calendars; "any stylist" tries each qualified stylist in turn.   (B1, B17)
  * A stylist can never hold two active bookings that overlap. The check runs at the
    moment of saving, under one lock, on one server.                              (B2, B3, B16)
  * A buffer (clean-up time) is added after every booking...                      (B4)
    ...but the trailing buffer may run past closing time, so the last slot of
    the day is not lost.                                          FIX 1           (B5)
  * A slot is only offered if the whole service fits the stylist's day.          (B6)
  * Breaks can be marked flexible. A flexible break does not block a long service
    (3 hours or more by default): the stylist takes the break during it. FIX 2   (B7)
  * Services can have segments (active / processing / active). Only the active
    parts block the stylist. The client still sits in a chair the whole time. FIX 3 (B8)
  * Cancelled bookings stop holding time straight away. Inside the owner's window
    a customer cancellation is flagged "late cancel"; the owner decides any fee.   (B9, B10)
  * No-show can only be marked after start + grace. It counts against the client,
    and the owner's rule can then ask for a deposit next time.                     (B11)
  * HELD: when a deposit is needed, the booking is saved as "held" with an expiry
    time (10 minutes by default). Held time blocks other bookings until it expires.
    Paid in time = confirmed; declined = released; no answer = expires.          (B12-B14)
  * A payment that arrives after the hold expired is re-checked. If the slot is still
    free it is confirmed; if not, it is marked "refund due" and the owner is alerted.
    It is never simply confirmed.                                 FIX 4           (B15)
  * Patch tests: a service can need a recorded, clear patch test at least the owner's
    set gap (48 hours by default) before the appointment.                         (B18)
  * Times are Europe/London wall-clock times (see store.now_local).               (B19)
  * A request replayed after the phone was offline is checked like any other; if the
    time has gone, the customer is told and offered other times.                  (B20)

Two booking modes (the card decides which one is on):
  * "request" - 4-star default. The customer asks for a time; the shop confirms it.
  * "instant" - optional module "automated booking". Confirmed (or held for a
                deposit) straight away. Needs the always-on shop server.
"""
from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .store import EngineError, JsonStore, new_code, now_local

DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
STATUSES = ("held", "requested", "confirmed", "done", "cancelled", "no_show", "declined", "expired", "refund_due")
DEFAULTS = {
    "slot_minutes": 15, "buffer_minutes": 0, "min_notice_minutes": 60, "max_days_ahead": 60,
    "hold_minutes": 10,                 # how long a slot is held while the client pays a deposit
    "late_cancel_hours": 24,            # cancellations inside this window are flagged "late cancel"
    "no_show_grace_minutes": 15,        # a no-show can only be marked this long after the start
    "deposit_after_no_shows": 1,        # ask for a deposit once a client has this many no-shows (0 = never)
    "patch_test_gap_hours": 48,         # a patch test must be at least this long before a colour
    "long_service_minutes": 180,        # flexible breaks don't block services this long or longer
    "buffer_may_pass_closing": 1,       # 1 = the clean-up buffer may run past closing (fix 1)
}
MONEY = re.compile(r"\d{1,5}(\.\d{1,2})?")


class SlotTaken(EngineError):
    """The time asked for is not free any more. Carries other times to offer."""

    def __init__(self, msg: str, alternatives: Optional[List[str]] = None):
        super().__init__(msg)
        self.alternatives = alternatives or []


def _tm(s: str) -> int:
    if not s or not re.fullmatch(r"[0-2]\d:[0-5]\d", str(s)):
        raise EngineError("Times must look like 09:30.")
    return int(s[:2]) * 60 + int(s[3:])


def _hm(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"


def _date(s: str) -> date:
    try:
        return datetime.strptime(str(s), "%Y-%m-%d").date()
    except (TypeError, ValueError):
        raise EngineError("Dates must look like 2026-10-03.")


def _at(d: date, minutes: int) -> datetime:
    return datetime.combine(d, datetime.min.time()) + timedelta(minutes=minutes)


def clean_phone(p: str) -> str:
    p = re.sub(r"[^\d+]", "", str(p or ""))
    if len(re.sub(r"\D", "", p)) < 10:
        raise EngineError("Please give a phone number we can reach you on.")
    return p[:16]


def phone_key(p: str) -> str:
    """Compare phone numbers by digits only, ignoring a leading 0 / +44."""
    d = re.sub(r"\D", "", str(p or ""))
    return d[2:] if d.startswith("44") else d.lstrip("0")


def parse_segments(text_or_list, duration: int) -> List[Tuple[str, int]]:
    """'45 active, 45 processing, 30 active' -> [("active",45),("processing",45),("active",30)].
    Empty = one active block for the whole service."""
    if not text_or_list:
        return [("active", int(duration))]
    if isinstance(text_or_list, list):
        segs = [(str(k), int(m)) for k, m in text_or_list]
    else:
        segs = []
        for part in str(text_or_list).split(","):
            m = re.fullmatch(r"\s*(\d{1,3})\s*(?:min|mins|minutes)?\s*(active|processing)\s*", part, re.I)
            if not m:
                raise EngineError("Segments must look like: 45 active, 45 processing, 30 active")
            segs.append((m.group(2).lower(), int(m.group(1))))
    if any(k not in ("active", "processing") or mins <= 0 for k, mins in segs):
        raise EngineError("Each segment needs minutes and 'active' or 'processing'.")
    if sum(mins for _, mins in segs) != int(duration):
        raise EngineError(f"The segments add up to {sum(m for _, m in segs)} minutes, but the service is {duration} minutes.")
    return segs


def parse_breaks(v) -> List[Dict[str, Any]]:
    """'13:00-13:30' or '13:00-13:30, 16:00-16:15' or a list of {start, end, flexible}."""
    out = []
    if isinstance(v, list):
        for b in v:
            out.append({"start": _tm(b["start"]), "end": _tm(b["end"]), "flexible": bool(b.get("flexible", True))})
        return out
    for part in str(v or "").split(","):
        part = part.strip()
        if not part:
            continue
        m = re.fullmatch(r"([0-2]\d:[0-5]\d)\s*[-–]\s*([0-2]\d:[0-5]\d)", part)
        if not m:
            raise EngineError("Breaks must look like 13:00-13:30")
        out.append({"start": _tm(m.group(1)), "end": _tm(m.group(2)), "flexible": True})
    return out


class BookingEngine:
    def __init__(self, path: Path | str, shop: Callable[[], Dict[str, Any]], now: Callable[[], datetime] = now_local,
                 patch_tests: Optional[Callable[[str], Optional[List[Dict[str, Any]]]]] = None,
                 deposits_on: Optional[Callable[[], bool]] = None):
        """patch_tests(phone) -> list of {tested_on, result} for that client, or None when the
        client-records module is off (then patch-test services can only be requested, not booked).
        deposits_on() -> whether the Deposits module is switched on for this shop."""
        self.store = JsonStore(path, lambda: {"bookings": [], "seq": 0, "no_shows": {}, "alerts": [], "payments_seen": []})
        self.shop = shop
        self.now = now
        self.patch_tests = patch_tests
        self.deposits_on = deposits_on or (lambda: False)

    # ------------------------------------------------------------- settings
    def settings(self) -> Dict[str, Any]:
        s = dict(DEFAULTS)
        s.update({k: v for k, v in (self.shop().get("booking") or {}).items() if k in DEFAULTS and isinstance(v, int)})
        s["no_show_deposit"] = str((self.shop().get("booking") or {}).get("no_show_deposit") or "10")
        return s

    def service(self, sid: str) -> Dict[str, Any]:
        for s in self.shop().get("services", []):
            if s.get("id") == sid:
                return s
        raise EngineError("That service isn't on the price list.")

    def duration(self, svc: Dict[str, Any]) -> int:
        return int(svc.get("duration_min") or 30)

    def blocks_for(self, svc: Dict[str, Any], start: int) -> List[Tuple[int, int]]:
        """Stylist time a service takes. Processing segments leave the stylist free (fix 3)."""
        out, t = [], start
        for kind, mins in parse_segments(svc.get("segments"), self.duration(svc)):
            if kind == "active":
                out.append((t, t + mins))
            t += mins
        return out

    def staff_for(self, service: Dict[str, Any], branch: str = "") -> List[Dict[str, Any]]:
        allowed = set(service.get("staff_ids") or [])
        out = []
        for st in self.shop().get("staff", []):
            if st.get("bookable", True) is False:
                continue
            if allowed and st.get("id") not in allowed:
                continue
            if branch and st.get("branch") and st.get("branch") != branch:
                continue
            out.append(st)
        return out

    def _shop_hours(self, d: date, branch: str = ""):
        shop = self.shop()
        hours = shop.get("hours", [])
        if branch:
            for b in shop.get("branches", []):
                if b.get("id") == branch and b.get("hours"):
                    hours = b["hours"]
        h = next((x for x in hours if x.get("day") == DAYS[d.weekday()]), None)
        if not h or h.get("closed") or not h.get("open") or not h.get("close"):
            return None
        if d.isoformat() in (shop.get("closed_dates") or []):
            return None
        return _tm(h["open"]), _tm(h["close"])

    def working_window(self, staff: Dict[str, Any], d: date, branch: str = ""):
        """Minutes (start, end) a stylist works that day, inside the shop's hours; None if not working."""
        shop_h = self._shop_hours(d, branch)
        if not shop_h:
            return None
        if d.isoformat() in (staff.get("days_off") or []):
            return None
        own = (staff.get("days") or {}).get(DAYS[d.weekday()], "shop")
        if own is None or own is False:
            return None
        if isinstance(own, dict) and own.get("start") and own.get("end"):
            s, e = max(shop_h[0], _tm(own["start"])), min(shop_h[1], _tm(own["end"]))
            return (s, e) if e > s else None
        return shop_h

    # ---------------------------------------------------------- availability
    def _live(self, b: Dict[str, Any]) -> bool:
        """Does this booking hold the stylist's time right now?"""
        if b["status"] in ("requested", "confirmed"):
            return True
        if b["status"] == "held":
            return bool(b.get("hold_until")) and self.now() <= datetime.fromisoformat(b["hold_until"])
        return False

    def _busy(self, data, staff_id: str, d: str, ignore: str = ""):
        out = []
        for b in data["bookings"]:
            if b["staff_id"] == staff_id and b["date"] == d and b["id"] != ignore and self._live(b):
                for s, e in (b.get("busy") or [[_tm(b["start"]), _tm(b["end"])]]):
                    out.append((s, e))
        return out

    def busy_blocks(self, staff_id: str, day: str) -> List[Tuple[int, int]]:
        """Booked stylist time on a day, buffer included (used by the walk-in queue)."""
        buf = self.settings()["buffer_minutes"]
        return sorted((s, e + buf) for s, e in self._busy(self.store.load(), staff_id, day))

    def why_not(self, data, staff, d: date, start: int, svc: Dict[str, Any], branch: str = "", ignore: str = "") -> str:
        """'' if the service fits this stylist at this time, else a plain reason."""
        win = self.working_window(staff, d, branch)
        if not win:
            return "not working that day"
        s = self.settings()
        buf, dur = s["buffer_minutes"], self.duration(svc)
        end = start + dur
        need_end = end if s["buffer_may_pass_closing"] else end + buf          # fix 1
        if start < win[0] or need_end > win[1]:
            return "outside working hours"
        blocks = self.blocks_for(svc, start)
        for br in parse_breaks(staff.get("breaks")):
            if br["flexible"] and dur >= s["long_service_minutes"]:            # fix 2
                continue
            if any(bs < br["end"] and br["start"] < be for bs, be in blocks):
                return "stylist's break"
        for bs, be in blocks:
            for xs, xe in self._busy(data, staff["id"], d.isoformat(), ignore):
                if bs < xe + buf and xs < be + buf:
                    return "already booked then"
        return ""

    def _check_window(self, d: date, start: Optional[int] = None):
        s = self.settings()
        now = self.now()
        if d < now.date():
            raise EngineError("That date has already gone.")
        if d > now.date() + timedelta(days=s["max_days_ahead"]):
            raise EngineError(f"Bookings open {s['max_days_ahead']} days ahead.")
        if start is not None and _at(d, start) < now + timedelta(minutes=s["min_notice_minutes"]):
            raise EngineError(f"Please book at least {s['min_notice_minutes']} minutes ahead.")

    def slots(self, service_id: str, day: str, staff_id: str = "any", branch: str = "", data=None) -> Dict[str, Any]:
        """Free start times for a service on a day. Each time lists which stylists are free."""
        svc = self.service(service_id)
        d = _date(day)
        try:
            self._check_window(d)
        except EngineError as e:
            return {"date": day, "slots": [], "note": str(e)}
        s = self.settings()
        staff = [x for x in self.staff_for(svc, branch) if staff_id in ("", "any") or x["id"] == staff_id]
        data = data if data is not None else self.store.load()
        earliest = self.now() + timedelta(minutes=s["min_notice_minutes"])
        times: Dict[int, List[str]] = {}
        for st in staff:
            win = self.working_window(st, d, branch)
            if not win:
                continue
            t = win[0]
            while t + self.duration(svc) <= win[1]:
                if _at(d, t) >= earliest and not self.why_not(data, st, d, t, svc, branch):
                    times.setdefault(t, []).append(st["id"])
                t += s["slot_minutes"]
        note = "" if times else ("Closed or fully booked that day." if staff else "Nobody offers this service on that day.")
        return {"date": day, "service_id": service_id, "duration_min": self.duration(svc),
                "slots": [{"time": _hm(t), "staff": ids} for t, ids in sorted(times.items())], "note": note}

    def open_days(self, days: int = 14, branch: str = "") -> List[Dict[str, Any]]:
        out, today = [], self.now().date()
        for i in range(days):
            d = today + timedelta(days=i)
            h = self._shop_hours(d, branch)
            out.append({"date": d.isoformat(), "day": DAYS[d.weekday()], "open": _hm(h[0]) if h else "",
                        "close": _hm(h[1]) if h else "", "closed": not h})
        return out

    # ------------------------------------------------------------- safety
    def patch_test_problem(self, svc: Dict[str, Any], phone: str, d: date) -> Optional[str]:
        """None if fine; a plain reason if the patch-test rule blocks this booking; 'unknown' if
        client records are off (the salon must check it themselves)."""
        if not svc.get("needs_patch_test"):
            return None
        if self.patch_tests is None:
            return "unknown"
        tests = [t for t in (self.patch_tests(phone) or []) if t.get("result") == "clear" and t.get("tested_on")
                 and (not t.get("retest_by") or t["retest_by"] >= d.isoformat())]
        if not tests:
            return "This service needs a patch test first. Please book a patch test (it's quick), then book this."
        gap = self.settings()["patch_test_gap_hours"]
        last = max(date.fromisoformat(t["tested_on"]) for t in tests)
        if (d - last).days * 24 < gap:
            return f"Your patch test needs to be at least {gap} hours before this appointment. Please pick a later day."
        return None

    def no_show_count(self, phone: str) -> int:
        return int(self.store.load().get("no_shows", {}).get(phone_key(phone), 0))

    def deposit_needed(self, svc: Dict[str, Any], phone: str) -> str:
        """Deposit amount (as text) if one is needed, else ''."""
        if not self.deposits_on():
            return ""
        dep = str(svc.get("deposit") or "")
        if dep and MONEY.fullmatch(dep) and float(dep) > 0:
            return dep
        s = self.settings()
        if s["deposit_after_no_shows"] and self.no_show_count(phone) >= s["deposit_after_no_shows"]:
            return s["no_show_deposit"]
        return ""

    # --------------------------------------------------------------- create
    def create(self, req: Dict[str, Any], mode: str = "request", channel: str = "app") -> Dict[str, Any]:
        if mode not in ("request", "instant"):
            raise EngineError("Unknown booking mode.")
        svc = self.service(str(req.get("service_id") or ""))
        d = _date(req.get("date"))
        start = _tm(req.get("time") or "")
        dur = self.duration(svc)
        branch = str(req.get("branch") or "")[:40]
        name = str(req.get("name") or "").strip()[:80]
        if not name:
            raise EngineError("Please give your name.")
        phone = clean_phone(req.get("phone"))
        if self.shop().get("policy_required") and not req.get("accept_policy"):
            raise EngineError("Please read and tick the cancellation policy.")
        self._check_window(d, start)
        oh = self._shop_hours(d, branch)
        if not oh:
            raise EngineError("The shop is closed that day.")
        if start < oh[0] or start + dur > oh[1]:
            raise EngineError(f"Please pick a time between {_hm(oh[0])} and {_hm(oh[1] - dur)} that day.")
        want = str(req.get("staff_id") or "any")
        candidates = self.staff_for(svc, branch)
        if want != "any":
            candidates = [c for c in candidates if c["id"] == want]
            if not candidates:
                raise EngineError("That stylist doesn't offer this service.")
        flags = []
        pt = self.patch_test_problem(svc, phone, d)
        if pt == "unknown":
            mode = "request"                                    # the salon checks the patch test itself
            flags.append("patch test needed - salon to check")
        elif pt:
            raise EngineError(pt)
        deposit = self.deposit_needed(svc, phone)
        if deposit and mode == "request":
            flags.append(f"deposit £{deposit} to take before confirming")
        if self.no_show_count(phone):
            flags.append(f"client has {self.no_show_count(phone)} earlier no-show(s)")

        def add(data):
            staff_id, reasons = "", []
            if mode == "instant" or want != "any":
                for c in candidates:                             # 'any' tries each stylist in turn (B17)
                    r = self.why_not(data, c, d, start, svc, branch)
                    if not r:
                        staff_id = c["id"]
                        break
                    reasons.append(r)
                if not staff_id:
                    alts = [x["time"] for x in self.slots(svc["id"], d.isoformat(), want, branch, data)["slots"]][:6]
                    why = reasons[0] if len(set(reasons)) == 1 else "not free then"
                    raise SlotTaken(f"Sorry, that time isn't available ({why}). " +
                                    ("Free times that day: " + ", ".join(alts) if alts else "Please try another day."), alts)
            data["seq"] += 1
            now = self.now()
            st = staff_id and next(c for c in candidates if c["id"] == staff_id)
            status = ("held" if deposit else "confirmed") if mode == "instant" else "requested"
            b = {"id": f"BK{data['seq']:05d}", "ref": new_code(6), "service_id": svc["id"],
                 "service_name": svc.get("name"), "price_from": svc.get("price_from", ""),
                 "date": d.isoformat(), "start": _hm(start), "end": _hm(start + dur),
                 "busy": [list(x) for x in self.blocks_for(svc, start)] if st else [],
                 "staff_id": staff_id, "staff_requested": want, "branch": branch, "name": name, "phone": phone,
                 "email": str(req.get("email") or "")[:120], "notes": str(req.get("notes") or "")[:400],
                 "hair_type": str(req.get("hair_type") or "")[:40], "contact_ok": bool(req.get("contact_ok")),
                 "referral_code": str(req.get("referral_code") or "")[:12].upper(),
                 "status": status, "mode": mode, "channel": channel, "flags": flags,
                 "deposit": {"amount": deposit, "state": "due" if deposit else "none"},
                 "hold_until": (now + timedelta(minutes=self.settings()["hold_minutes"])).isoformat() if status == "held" else None,
                 "created_at": now.isoformat(), "history": [{"at": now.isoformat(), "status": status}]}
            data["bookings"].append(b)
            return b
        return self.store.update(add)

    # -------------------------------------------------------------- deposits
    def attach_payment(self, bid: str, provider: str, link: str, link_id: str = "") -> Dict[str, Any]:
        def f(data, b):
            b["deposit"].update(provider=provider, link=link, link_id=link_id)
        return self._set(bid, f, log=False)

    def find_by_payment(self, provider: str, link_id: str) -> Optional[Dict[str, Any]]:
        for b in self.store.load()["bookings"]:
            dep = b.get("deposit") or {}
            if dep.get("provider") == provider and link_id and dep.get("link_id") == link_id:
                return b
        return None

    def payment_result(self, bid: str, success: bool, source: str = "owner", event_id: str = "") -> Dict[str, Any]:
        """A payment answer arrived (payment firm's message, a status check, or the owner).
        Paid in time -> confirmed. Declined -> released. Paid late -> re-check the slot (fix 4)."""
        out = {"result": ""}

        def f(data, b):
            self._pay(data, b, success, source, event_id, out)
        b = self._set(bid, f)
        return {"booking": b, "result": out["result"]}

    def _pay(self, data, b, success, source, event_id, out):
        if True:
            if event_id:
                if event_id in data.setdefault("payments_seen", []):
                    out["result"] = "already handled"
                    return
                data["payments_seen"].append(event_id)
            dep = b.setdefault("deposit", {"amount": "", "state": "none"})
            dep["source"] = source
            if not success:
                if b["status"] == "held":
                    b["status"] = "cancelled"
                    b.setdefault("flags", []).append("deposit failed - slot released")
                dep["state"] = "failed"
                out["result"] = "payment failed - slot released"
                return
            dep.update(state="paid", paid_at=self.now().isoformat())
            b["flags"] = [f for f in b.get("flags", []) if not f.startswith("deposit £")]
            if b["status"] == "confirmed":
                out["result"] = "already confirmed"
                return
            if b["status"] == "held" and self._live(b):
                b["status"] = "confirmed"
                out["result"] = "confirmed"
                return
            if b["status"] in ("held", "expired", "cancelled"):
                svc = self.service(b["service_id"])
                staff = next((s for s in self.shop().get("staff", []) if s["id"] == b["staff_id"]), None)
                why = self.why_not(data, staff, _date(b["date"]), _tm(b["start"]), svc, b.get("branch", ""), ignore=b["id"]) \
                    if staff else "stylist missing"
                if not why:
                    b["status"] = "confirmed"
                    out["result"] = "confirmed (paid late, time was still free)"
                    return
                b["status"] = "refund_due"
                dep["state"] = "refund_due"
                msg = (f"Refund needed: {b['name']} paid the deposit for {b['date']} {b['start']} after the hold ran out, "
                       f"and that time had already gone ({why}). Refund them and offer another time.")
                data.setdefault("alerts", []).append({"at": self.now().isoformat(), "booking": b["id"], "text": msg, "done": False})
                out["result"] = "refund due - owner alerted"
                return
            out["result"] = f"payment noted (booking is {b['status']})"

    def expire_holds(self) -> int:
        """Mark held bookings whose time ran out as 'expired' (they already stopped blocking)."""
        def f(data):
            n = 0
            for b in data["bookings"]:
                if b["status"] == "held" and not self._live(b):
                    b["status"] = "expired"
                    b["history"].append({"at": self.now().isoformat(), "status": "expired"})
                    n += 1
            return n
        return self.store.update(f)

    def alerts(self) -> List[Dict[str, Any]]:
        return [a for a in self.store.load().get("alerts", []) if not a.get("done")]

    def clear_alert(self, booking_id: str) -> int:
        def f(d):
            n = 0
            for a in d.get("alerts", []):
                if a["booking"] == booking_id and not a.get("done"):
                    a["done"], a["done_at"], n = True, self.now().isoformat(), n + 1
            return n
        return self.store.update(f)

    # ---------------------------------------------------------------- owner
    def get(self, bid: str) -> Dict[str, Any]:
        for b in self.store.load()["bookings"]:
            if b["id"] == bid or b["ref"] == bid:
                return b
        raise EngineError("No such booking.")

    def public_status(self, ref: str) -> Dict[str, Any]:
        b = self.get(ref)
        out = {k: b.get(k) for k in ("ref", "service_name", "date", "start", "end", "status", "hold_until")}
        if b["status"] == "held" and not self._live(b):
            out["status"] = "expired"
        out["deposit"] = {k: (b.get("deposit") or {}).get(k) for k in ("amount", "state", "link")}
        out["first_name"] = b["name"].split()[0]
        return out

    def _set(self, bid, fn, log=True):
        def upd(data):
            for b in data["bookings"]:
                if b["id"] == bid or b["ref"] == bid:
                    fn(data, b)
                    if log:
                        b["history"].append({"at": self.now().isoformat(), "status": b["status"]})
                    return b
            raise EngineError("No such booking.")
        return self.store.update(upd)

    def confirm(self, bid: str, staff_id: str = "") -> Dict[str, Any]:
        def f(data, b):
            if b["status"] not in ("requested", "confirmed", "held"):
                raise EngineError(f"This booking is {b['status']}; it can't be confirmed.")
            svc = self.service(b["service_id"])
            d, start = _date(b["date"]), _tm(b["start"])
            pick = staff_id or b["staff_id"]
            cands = [c for c in self.staff_for(svc, b.get("branch", "")) if not pick or c["id"] == pick]
            free = [c for c in cands if not self.why_not(data, c, d, start, svc, b.get("branch", ""), ignore=b["id"])]
            if not free:
                raise EngineError("That stylist already has a booking then (or isn't working). Choose another stylist or time.")
            b["staff_id"], b["status"] = free[0]["id"], "confirmed"
            b["busy"] = [list(x) for x in self.blocks_for(svc, start)]
        return self._set(bid, f)

    def move(self, bid: str, day: str, time: str, staff_id: str = "") -> Dict[str, Any]:
        def f(data, b):
            d, start = _date(day), _tm(time)
            svc = self.service(b["service_id"])
            pick = staff_id or b["staff_id"]
            cands = [c for c in self.staff_for(svc, b.get("branch", "")) if not pick or c["id"] == pick]
            free = [c for c in cands if not self.why_not(data, c, d, start, svc, b.get("branch", ""), ignore=b["id"])]
            if not free:
                raise EngineError("That time clashes with another booking.")
            b.update(date=d.isoformat(), start=_hm(start), end=_hm(start + self.duration(svc)), staff_id=free[0]["id"],
                     busy=[list(x) for x in self.blocks_for(svc, start)])
        return self._set(bid, f)

    def set_status(self, bid: str, status: str, price_paid: Optional[str] = None, reason: str = "", by: str = "owner") -> Dict[str, Any]:
        if status not in ("done", "cancelled", "no_show", "declined"):
            raise EngineError("Unknown status.")
        s = self.settings()

        def f(data, b):
            if b["status"] in ("cancelled", "declined", "expired", "refund_due") and status != "cancelled":
                raise EngineError(f"This booking is {b['status']}.")
            start = _at(_date(b["date"]), _tm(b["start"]))
            if status == "no_show":
                if self.now() < start + timedelta(minutes=s["no_show_grace_minutes"]):
                    raise EngineError(f"You can mark a no-show {s['no_show_grace_minutes']} minutes after the start time.")
                k = phone_key(b["phone"])
                data.setdefault("no_shows", {})[k] = int(data["no_shows"].get(k, 0)) + 1
            if status == "cancelled" and by == "customer" and start - self.now() < timedelta(hours=s["late_cancel_hours"]):
                b.setdefault("flags", []).append("late cancel - policy applies")
            b["status"] = status
            if reason:
                b["reason"] = reason[:200]
            if price_paid not in (None, ""):
                if not MONEY.fullmatch(str(price_paid)):
                    raise EngineError("Amount paid must be a number like 35.00.")
                b["price_paid"] = str(price_paid)
        return self._set(bid, f)

    def cancel_by_customer(self, ref: str, phone: str) -> Dict[str, Any]:
        b = self.get(ref)
        if phone_key(b["phone"])[-4:] != phone_key(phone)[-4:]:
            raise EngineError("The phone number doesn't match this booking.")
        return self.set_status(b["id"], "cancelled", reason="cancelled by customer", by="customer")

    def list(self, day_from: str = "", day_to: str = "", status: str = "") -> List[Dict[str, Any]]:
        out = []
        for b in self.store.load()["bookings"]:
            if day_from and b["date"] < day_from:
                continue
            if day_to and b["date"] > day_to:
                continue
            if status and b["status"] != status:
                continue
            out.append(b)
        return sorted(out, key=lambda b: (b["date"], b["start"], b["id"]))

    def clashes(self) -> List[str]:
        """Self-check used by tests and the admin page: any stylist double-booked (active blocks)?"""
        data, bad = self.store.load(), []
        act = [b for b in data["bookings"] if self._live(b) and b["staff_id"]]
        for i, a in enumerate(act):
            for b in act[i + 1:]:
                if a["staff_id"] != b["staff_id"] or a["date"] != b["date"]:
                    continue
                for s1, e1 in (a.get("busy") or [[_tm(a["start"]), _tm(a["end"])]]):
                    for s2, e2 in (b.get("busy") or [[_tm(b["start"]), _tm(b["end"])]]):
                        if s1 < e2 and s2 < e1:
                            bad.append(f"{a['id']} and {b['id']}")
        return sorted(set(bad))
