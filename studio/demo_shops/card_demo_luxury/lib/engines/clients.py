"""
Client notes, allergies and patch tests.

GDPR note (UK GDPR): allergy and skin-reaction details are health data, a
"special category". This engine therefore:
  * refuses to store any allergy / patch-test detail unless the owner ticks
    that the client gave explicit consent, and records when and the wording;
  * keeps everything in data/private/clients.json on the shop's own computer
    (never in the public site, never in an exported zip, never sent anywhere);
  * can export one client's record (right of access) and erase it (right to
    erasure) from the admin page.
This is a technical safeguard, not legal advice; the shop remains the data
controller and should read the ICO's guidance.
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any, Callable, Dict

from .store import EngineError, JsonStore, now_local

CONSENT_TEXT = ("I agree that {shop} may keep notes about my hair, allergies and patch-test results so they can "
                "treat me safely. They are kept on the salon's own computer only. I can ask to see or delete them at any time.")


class Clients:
    def __init__(self, path: Path | str, shop: Callable[[], Dict[str, Any]], now=now_local):
        self.store = JsonStore(path, lambda: {"clients": {}, "seq": 0})
        self.shop, self.now = shop, now

    def consent_text(self) -> str:
        return CONSENT_TEXT.format(shop=self.shop().get("name", "the salon"))

    def save(self, rec: Dict[str, Any]) -> Dict[str, Any]:
        name = str(rec.get("name") or "").strip()[:80]
        if not name:
            raise EngineError("A client record needs a name.")
        health = any(str(rec.get(k) or "").strip() for k in ("allergies",)) or bool(rec.get("patch_tests"))
        consent = bool(rec.get("consent"))
        if health and not consent:
            raise EngineError("Tick that the client gave consent before saving allergy or patch-test details.")

        def f(d):
            cid = rec.get("id")
            if cid and cid in d["clients"]:
                c = d["clients"][cid]
            else:
                d["seq"] += 1
                cid = f"CL{d['seq']:04d}"
                c = d["clients"][cid] = {"id": cid, "created_at": self.now().isoformat(), "patch_tests": []}
            c.update(name=name, phone=str(rec.get("phone") or "")[:16], email=str(rec.get("email") or "")[:120],
                     hair_notes=str(rec.get("hair_notes") or "")[:1000], allergies=str(rec.get("allergies") or "")[:500],
                     updated_at=self.now().isoformat())
            if consent and not c.get("consent"):
                c["consent"] = {"given": True, "at": self.now().isoformat(), "wording": self.consent_text()}
            if not consent:
                c["consent"] = c.get("consent") or {"given": False}
            return c
        return self.store.update(f)

    def add_patch_test(self, cid: str, product: str, result: str, tested_on: str = "", valid_days: int = 180) -> Dict[str, Any]:
        if result not in ("clear", "reaction", "not read yet"):
            raise EngineError("Result must be clear, reaction or not read yet.")
        t = date.fromisoformat(tested_on) if tested_on else self.now().date()

        def f(d):
            c = d["clients"].get(cid)
            if not c:
                raise EngineError("No such client.")
            if not (c.get("consent") or {}).get("given"):
                raise EngineError("This client hasn't given consent, so a patch test can't be recorded here.")
            c["patch_tests"].append({"product": product[:120], "result": result, "tested_on": t.isoformat(),
                                     "retest_by": (t + timedelta(days=int(valid_days))).isoformat()})
            return c
        return self.store.update(f)

    def due_patch_tests(self):
        today, out = self.now().date().isoformat(), []
        for c in self.store.load()["clients"].values():
            if c["patch_tests"]:
                last = c["patch_tests"][-1]
                if last["retest_by"] <= today or last["result"] != "clear":
                    out.append({"id": c["id"], "name": c["name"], "last": last})
        return out

    def export(self, cid: str) -> Dict[str, Any]:
        c = self.store.load()["clients"].get(cid)
        if not c:
            raise EngineError("No such client.")
        return {"exported_at": self.now().isoformat(), "shop": self.shop().get("name"), "record": c}

    def erase(self, cid: str) -> Dict[str, Any]:
        def f(d):
            if cid not in d["clients"]:
                raise EngineError("No such client.")
            del d["clients"][cid]
            d.setdefault("erasures", []).append({"id": cid, "at": self.now().isoformat()})
            return {"erased": cid}
        return self.store.update(f)

    def all(self):
        return list(self.store.load()["clients"].values())

    def patch_tests_for(self, phone: str):
        """Recorded patch tests for a client found by phone number (used by the booking
        engine's patch-test rule). Only clients who gave consent have any recorded."""
        from .booking import phone_key
        k = phone_key(phone)
        out = []
        for c in self.store.load()["clients"].values():
            if k and phone_key(c.get("phone", "")) == k and (c.get("consent") or {}).get("given"):
                out.extend(c.get("patch_tests") or [])
        return out
