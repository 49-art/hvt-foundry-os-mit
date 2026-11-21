"""
Small, polite internet helper for HVT Foundry Studio (standard library only).

Every outside call in the Studio and in the shop apps goes through fetch(), so
tests can swap it for a fake and nothing touches the internet during tests.
"""
from __future__ import annotations

import json
import socket
import ssl
import urllib.error
import urllib.request
from typing import Any, Dict, Optional, Tuple

BASE_UA = "HVT-Foundry-Studio/2.0 (independent high-street shop research tool; python-urllib)"


class NetError(Exception):
    """A failed outside call, with a plain-English message.

    kind is one of: offline, timeout, blocked, http, auth, bad_data, not_configured
    """

    def __init__(self, kind: str, message: str, status: Optional[int] = None, body: str = ""):
        super().__init__(message)
        self.kind = kind
        self.status = status
        self.body = body[:600]


def user_agent(contact: str = "") -> str:
    return f"{BASE_UA}; contact {contact}" if contact else BASE_UA


def fetch(url: str, method: str = "GET", headers: Optional[Dict[str, str]] = None,
          data: Optional[bytes] = None, timeout: float = 20.0,
          contact: str = "") -> Tuple[int, Dict[str, str], bytes]:
    """Do one HTTP request. Returns (status, headers, body). Raises NetError."""
    h = {"User-Agent": user_agent(contact), "Accept": "*/*"}
    h.update(headers or {})
    req = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context()) as r:
            return r.status, {k.lower(): v for k, v in r.headers.items()}, r.read()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace") if e.fp else ""
        kind = "auth" if e.code in (401, 403) else ("blocked" if e.code in (429,) else "http")
        raise NetError(kind, f"The service answered with an error ({e.code}).", e.code, body)
    except (socket.timeout, TimeoutError):
        raise NetError("timeout", "The service took too long to answer. Try again in a minute.")
    except urllib.error.URLError as e:
        reason = getattr(e, "reason", e)
        if isinstance(reason, (socket.timeout, TimeoutError)):
            raise NetError("timeout", "The service took too long to answer. Try again in a minute.")
        raise NetError("offline", "Can't reach the internet from this device (or the service is down). "
                                  "Check Wi-Fi or mobile data and try again.")
    except (ConnectionError, OSError):
        raise NetError("offline", "Can't reach the internet from this device. Check Wi-Fi or mobile data.")


def fetch_json(url: str, method: str = "GET", headers: Optional[Dict[str, str]] = None,
               body: Any = None, form: Optional[Dict[str, Any]] = None, timeout: float = 20.0,
               contact: str = "", fetcher=None) -> Any:
    """fetch() + JSON decode. body is sent as JSON; form as x-www-form-urlencoded."""
    import urllib.parse
    fetcher = fetcher or fetch
    h = {"Accept": "application/json"}
    h.update(headers or {})
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        h.setdefault("Content-Type", "application/json")
    elif form is not None:
        data = urllib.parse.urlencode(form).encode("utf-8")
        h.setdefault("Content-Type", "application/x-www-form-urlencoded")
    status, _, raw = fetcher(url, method=method, headers=h, data=data, timeout=timeout, contact=contact)
    try:
        return json.loads(raw.decode("utf-8") or "null")
    except (ValueError, UnicodeDecodeError):
        raise NetError("bad_data", "The service sent back something that isn't the expected data.", status)
