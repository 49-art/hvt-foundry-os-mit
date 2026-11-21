"""
Reminder and review-request messages.

Without any key: builds a WhatsApp "click to chat" link (wa.me) with the text
filled in; the owner taps it and presses send in their own WhatsApp.
With a Twilio key (connector twilio_sms): the admin page can send it as an SMS.
Nothing is ever sent automatically without the owner pressing a button.
"""
from __future__ import annotations

from urllib.parse import quote
import re
from typing import Any, Dict


def uk_to_wa(phone: str) -> str:
    d = re.sub(r"\D", "", phone or "")
    if d.startswith("0"):
        d = "44" + d[1:]
    return d


def wa_link(phone: str, text: str) -> str:
    return f"https://wa.me/{uk_to_wa(phone)}?text={quote(text)}"


def reminder_text(shop: Dict[str, Any], b: Dict[str, Any]) -> str:
    tpl = (shop.get("messages") or {}).get("reminder") or (
        "Hi {first}, a reminder of your {service} at {shop} on {date} at {time}. "
        "Reply here if you need to change it. {policy}")
    return _fill(tpl, shop, b)


def review_text(shop: Dict[str, Any], b: Dict[str, Any]) -> str:
    tpl = (shop.get("messages") or {}).get("review") or (
        "Thanks for visiting {shop}, {first}! If you have a minute, a Google review really helps us: {review_link}")
    return _fill(tpl, shop, b)


def google_review_link(place_id: str) -> str:
    """Google's documented write-review link pattern (support.google.com/business/answer/7035772)."""
    place_id = re.sub(r"[^A-Za-z0-9_\-]", "", place_id or "")
    return f"https://search.google.com/local/writereview?placeid={place_id}" if place_id else ""


def _fill(tpl: str, shop: Dict[str, Any], b: Dict[str, Any]) -> str:
    name = b.get("service_name")
    if isinstance(name, dict):
        name = name.get(shop.get("default_language", "en")) or next(iter(name.values()), "")
    vals = {"first": (b.get("name") or "").split(" ")[0], "service": name or "appointment", "shop": shop.get("name", ""),
            "date": b.get("date", ""), "time": b.get("start", ""),
            "policy": (shop.get("policy_short") or ""), "review_link": google_review_link(shop.get("google_place_id", ""))}
    out = tpl
    for k, v in vals.items():
        out = out.replace("{" + k + "}", str(v))
    return re.sub(r"\s+", " ", out).strip()


def reminder_due(b: Dict[str, Any], hours_before: int = 24) -> Dict[str, str]:
    """When the reminder for a booking is due: the same London clock time the day before
    (for 24 hours), worked out in London time, with the matching UTC time for a sender that
    runs on UTC. Right across the clock changes - never a fixed +1. Theory test B19."""
    from datetime import datetime, timedelta
    from .store import to_utc
    appt = datetime.fromisoformat(f"{b['date']}T{b['start']}")
    local = appt - timedelta(hours=int(hours_before))          # wall-clock arithmetic in London time
    return {"local": local.isoformat(timespec="minutes"), "utc": to_utc(local).isoformat(timespec="minutes") + "Z",
            "label": local.strftime("%a %d %b %H:%M") + " (London time)"}


def reminder_links(shop: Dict[str, Any], bookings) -> list:
    hrs = int((shop.get("booking") or {}).get("reminder_hours", 24) or 24)
    return [{"booking": b["id"], "name": b["name"], "time": f"{b['date']} {b['start']}", "text": reminder_text(shop, b),
             "whatsapp_link": wa_link(b["phone"], reminder_text(shop, b)), "contact_ok": b.get("contact_ok", False),
             "due": reminder_due(b, hrs)}
            for b in bookings]
