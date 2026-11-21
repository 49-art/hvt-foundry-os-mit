"""Money helpers: store pence as whole numbers, show pounds."""
import re

from .store import EngineError


def to_pence(v) -> int:
    s = str(v if v is not None else "").replace("£", "").strip()
    if not re.fullmatch(r"\d{1,6}(\.\d{1,2})?", s):
        raise EngineError("Amounts must be a number like 25 or 25.50.")
    pounds, _, p = s.partition(".")
    return int(pounds) * 100 + int((p + "00")[:2])


def pounds(pence: int) -> str:
    return f"£{pence // 100}.{pence % 100:02d}"
