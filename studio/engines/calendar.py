"""
Calendar helpers.
  * ics(booking)            – a standard .ics file (RFC 5545). Works with no key: the customer or
                              owner taps it and it goes into Apple/Google/Outlook calendar.
  * google_event(booking)   – the JSON body for Google Calendar's events.insert
                              (POST https://www.googleapis.com/calendar/v3/calendars/{calendarId}/events,
                              docs checked 2026-09-26). Sent by the google_calendar connector (needs the
                              owner's own Google OAuth credentials).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

TZ = "Europe/London"


def _name(v, lang="en"):
    if isinstance(v, dict):
        return v.get(lang) or next(iter(v.values()), "")
    return v or ""


def _esc(s: str) -> str:
    return (s or "").replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def ics(shop: Dict[str, Any], b: Dict[str, Any]) -> str:
    d = b["date"].replace("-", "")
    st, en = b["start"].replace(":", "") + "00", b["end"].replace(":", "") + "00"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    loc = ", ".join(x for x in (shop.get("address"), shop.get("postcode")) if x)
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//HVT Foundry card app//EN", "CALSCALE:GREGORIAN", "BEGIN:VEVENT",
             f"UID:{b['id']}-{b['ref']}@shop-app", f"DTSTAMP:{stamp}",
             f"DTSTART;TZID={TZ}:{d}T{st}", f"DTEND;TZID={TZ}:{d}T{en}",
             f"SUMMARY:{_esc(_name(b.get('service_name')) + ' — ' + shop.get('name', ''))}",
             f"LOCATION:{_esc(loc)}", f"DESCRIPTION:{_esc('Booking ref ' + b['ref'] + ' (' + b['status'] + ')')}",
             "END:VEVENT", "END:VCALENDAR"]
    return "\r\n".join(lines) + "\r\n"


def google_event(shop: Dict[str, Any], b: Dict[str, Any], staff_name: str = "") -> Dict[str, Any]:
    return {"summary": f"{_name(b.get('service_name'))} — {b['name']}" + (f" ({staff_name})" if staff_name else ""),
            "location": ", ".join(x for x in (shop.get("address"), shop.get("postcode")) if x),
            "description": f"Booking {b['id']} / ref {b['ref']}. Phone {b['phone']}. Notes: {b.get('notes', '')}",
            "start": {"dateTime": f"{b['date']}T{b['start']}:00", "timeZone": TZ},
            "end": {"dateTime": f"{b['date']}T{b['end']}:00", "timeZone": TZ},
            "extendedProperties": {"private": {"hvt_booking": b["id"]}}}
