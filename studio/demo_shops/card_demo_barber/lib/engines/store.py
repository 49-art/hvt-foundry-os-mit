"""Tiny JSON file store with a lock and atomic writes."""
from __future__ import annotations

import json
import os
import secrets
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional

_LOCKS: Dict[str, threading.RLock] = {}
_GUARD = threading.Lock()
# Codes without look-alike characters (no 0/O, 1/I/L) so they can be read out over the counter.
CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"


def lock_for(path: Path) -> threading.RLock:
    key = str(Path(path).resolve())
    with _GUARD:
        if key not in _LOCKS:
            _LOCKS[key] = threading.RLock()
        return _LOCKS[key]


def new_code(n: int = 8) -> str:
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(n))


SHOP_TZ = "Europe/London"


def _last_sunday(year: int, month: int) -> int:
    from calendar import monthrange
    last = monthrange(year, month)[1]
    return max(d for d in range(last - 6, last + 1) if datetime(year, month, d).weekday() == 6)


def uk_offset_hours(local: datetime) -> int:
    """UK clock offset from UTC for a London wall-clock time: 1 in summer time (BST), else 0.
    Stdlib-only fallback for computers without the time-zone database (e.g. some Windows PCs).
    Summer time runs from 01:00 UTC on the last Sunday in March to 01:00 UTC on the last
    Sunday in October."""
    y = local.year
    start = datetime(y, 3, _last_sunday(y, 3), 2, 0)      # 01:00 UTC = 02:00 local (clocks jump to 02:00 BST)
    end = datetime(y, 10, _last_sunday(y, 10), 1, 0)      # 01:00 UTC = 02:00 BST, back to 01:00 GMT
    return 1 if start <= local.replace(tzinfo=None) < end else 0


def to_utc(local: datetime) -> datetime:
    """London wall-clock time -> UTC (plain date-time)."""
    try:
        from zoneinfo import ZoneInfo
        from datetime import timezone
        return local.replace(tzinfo=ZoneInfo(SHOP_TZ)).astimezone(timezone.utc).replace(tzinfo=None)
    except Exception:                      # pragma: no cover - zone database missing
        from datetime import timedelta
        return local - timedelta(hours=uk_offset_hours(local))


def now_local() -> datetime:
    """The shop's wall-clock time (Europe/London), as a plain date-time.

    Uses the time-zone database (or the UK rule above if it is missing), never a fixed +1,
    so it is right on both sides of the October and March clock changes, and right even
    when the server itself runs on UTC, as most hosting does. Theory test B19."""
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo(SHOP_TZ)).replace(microsecond=0, tzinfo=None)
    except Exception:                      # pragma: no cover - zone database missing
        from datetime import timedelta, timezone
        u = datetime.now(timezone.utc).replace(tzinfo=None, microsecond=0)
        guess = u + timedelta(hours=1)
        return u + timedelta(hours=uk_offset_hours(guess))


class EngineError(ValueError):
    """A plain-English refusal from an engine (shown to the owner or customer)."""


class JsonStore:
    def __init__(self, path: Path | str, default: Optional[Callable[[], Dict[str, Any]]] = None):
        self.path = Path(path)
        self.default = default or (lambda: {})
        self.lock = lock_for(self.path)

    def load(self) -> Dict[str, Any]:
        with self.lock:
            if not self.path.exists():
                return self.default()
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                raise EngineError(f"The file {self.path.name} is damaged. Restore it from a backup.")

    def save(self, data: Dict[str, Any]) -> None:
        with self.lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(self.path.suffix + ".tmp")
            tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
            os.replace(tmp, self.path)

    def update(self, fn: Callable[[Dict[str, Any]], Any]) -> Any:
        """Load, change and save under one lock. fn returns the result to hand back."""
        with self.lock:
            data = self.load()
            result = fn(data)
            self.save(data)
            return result
