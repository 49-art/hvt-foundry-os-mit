"""Local counts only: page opens and button taps per day. No cookies, no IP addresses, no personal data."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from .store import JsonStore, now_local

EVENTS = ("open", "book_start", "book_sent", "call", "whatsapp", "directions", "review_click", "install",
          "queue_join", "voucher_check", "loyalty_check", "shop_view", "platform_link")


class Analytics:
    def __init__(self, path: Path | str, now=now_local):
        self.store = JsonStore(path, lambda: {"days": {}})
        self.now = now

    def hit(self, event: str) -> bool:
        if event not in EVENTS:
            return False
        day = self.now().date().isoformat()

        def f(d):
            e = d["days"].setdefault(day, {})
            e[event] = e.get(event, 0) + 1
            if len(d["days"]) > 400:
                for k in sorted(d["days"])[:-400]:
                    del d["days"][k]
            return True
        return self.store.update(f)

    def summary(self, days: int = 30) -> Dict[str, Any]:
        d = self.store.load()["days"]
        keys = sorted(d)[-days:]
        total = {e: sum(d[k].get(e, 0) for k in keys) for e in EVENTS}
        return {"days": {k: d[k] for k in keys}, "totals": total, "note": "Counted on the shop's own computer. No cookies or personal data."}
