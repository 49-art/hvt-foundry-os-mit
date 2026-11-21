"""
HVT connectors: one small module per outside service, all with the same shape.

Every connector says:
  id, name, category, cost_type ("free", "open source", "free key", "paid"),
  what_it_does (plain English), credentials it needs, docs_url, pricing (text +
  vendor URL + date checked, or None), status:
    "working-tested"      — we called the real service from our box on the date shown and it worked
    "code-ready-needs-key"— code written against the vendor's official docs (checked on the date shown);
                            it cannot be tested until the owner adds their own key
    "unverified"          — we could not read the official docs today, or the service needs a
                            business/partner account we don't have; treat as a starting point only
and has test_connection() and run(action, params).

Credentials are saved per scope (the Studio, or one shop) in a local secrets file
that is never included in a zip or git, and always masked on screen.
"""
from __future__ import annotations

import base64
import importlib
import json
import os
import pkgutil
import re
import threading
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from netutil import NetError, fetch, fetch_json  # noqa: E402

CHECKED = "2026-09-26"
STATUSES = ("working-tested", "code-ready-needs-key", "unverified")


class ConnectorError(Exception):
    def __init__(self, message: str, code: int = 400):
        super().__init__(message)
        self.code = code


def mask(v: str) -> str:
    v = str(v or "")
    if not v:
        return ""
    return "••••" + v[-4:] if len(v) > 8 else "••••"


def basic(user: str, pw: str) -> str:
    return "Basic " + base64.b64encode(f"{user}:{pw}".encode()).decode()


class Connector:
    id = "base"
    name = "Base"
    category = "Other"
    cost_type = "free"
    what_it_does = ""
    credentials: List[Dict[str, Any]] = []      # {key, label, secret, help, required}
    docs_url = ""
    docs_checked = CHECKED
    pricing: Optional[Dict[str, str]] = None    # {text, url, checked}
    status = "unverified"
    status_note = ""
    live_tested_on: Optional[str] = None
    actions: Dict[str, Dict[str, Any]] = {}     # name -> {label, params: [{key,label,example}]}
    shop_features: List[str] = []               # what a shop app can switch on

    def __init__(self, creds: Optional[Dict[str, str]] = None, fetcher: Callable = fetch, contact: str = ""):
        self.creds = creds or {}
        self.fetch = fetcher
        self.contact = contact

    # -- helpers
    def need(self, *keys: str) -> None:
        missing = [k for k in keys if not str(self.creds.get(k) or "").strip()]
        if missing:
            labels = [c["label"] for c in self.credentials if c["key"] in missing] or missing
            raise ConnectorError("Add these first (Connectors screen): " + ", ".join(labels), 412)

    def get_json(self, url, headers=None, **kw):
        return fetch_json(url, headers=headers, fetcher=self.fetch, contact=self.contact, **kw)

    def send_json(self, url, method="POST", headers=None, body=None, form=None, **kw):
        return fetch_json(url, method=method, headers=headers, body=body, form=form,
                          fetcher=self.fetch, contact=self.contact, **kw)

    # -- interface
    def test_connection(self) -> Dict[str, Any]:
        raise NotImplementedError

    def run(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        fn = getattr(self, "act_" + action, None)
        if action not in self.actions or fn is None:
            raise ConnectorError(f"{self.name} has no action {action!r}.", 404)
        return fn(params or {})

    @classmethod
    def describe(cls) -> Dict[str, Any]:
        return {"id": cls.id, "name": cls.name, "category": cls.category, "cost_type": cls.cost_type,
                "what_it_does": cls.what_it_does,
                "credentials": [{k: v for k, v in c.items()} for c in cls.credentials],
                "docs_url": cls.docs_url, "docs_checked": cls.docs_checked, "pricing": cls.pricing,
                "status": cls.status, "status_note": cls.status_note, "live_tested_on": cls.live_tested_on,
                "actions": cls.actions, "shop_features": cls.shop_features}


def _safe_test(c: Connector) -> Dict[str, Any]:
    try:
        r = c.test_connection()
        r.setdefault("ok", True)
        return r
    except ConnectorError as e:
        return {"ok": False, "message": str(e)}
    except NetError as e:
        msg = str(e)
        if e.kind == "auth":
            msg = "The service said the key or login is wrong or doesn't have permission (" + str(e.status) + ")."
        return {"ok": False, "message": msg, "kind": e.kind}
    except (KeyError, TypeError, ValueError, AttributeError, IndexError) as e:
        return {"ok": False, "message": "The service answered, but not in the shape we expected. "
                                        f"Check the key and settings ({type(e).__name__}).", "kind": "bad_data"}


# ------------------------------------------------------------------ registry
_REGISTRY: Dict[str, type] = {}


def registry() -> Dict[str, type]:
    if not _REGISTRY:
        pkg = Path(__file__).resolve().parent
        for m in sorted(pkgutil.iter_modules([str(pkg)]), key=lambda m: m.name):
            if m.name.startswith("_"):
                continue
            mod = importlib.import_module(f"{__name__}.{m.name}")
            for obj in vars(mod).values():
                if isinstance(obj, type) and issubclass(obj, Connector) and obj is not Connector and obj.id != "base" \
                        and obj.__module__ == mod.__name__:
                    _REGISTRY[obj.id] = obj
    return _REGISTRY


def catalogue() -> List[Dict[str, Any]]:
    return sorted((c.describe() for c in registry().values()), key=lambda d: (d["category"], d["name"]))


# --------------------------------------------------------- credential store
SCOPE_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


class CredentialStore:
    """Local secrets per scope. One JSON file per scope in `folder`. Never exported."""

    def __init__(self, folder: Path | str):
        self.folder = Path(folder)
        self.lock = threading.RLock()

    def _path(self, scope: str) -> Path:
        if not SCOPE_RE.match(scope or ""):
            raise ConnectorError("Bad scope name.")
        return self.folder / f"{scope}.secrets.json"

    def load(self, scope: str) -> Dict[str, Any]:
        p = self._path(scope)
        with self.lock:
            if p.exists():
                try:
                    return json.loads(p.read_text(encoding="utf-8"))
                except ValueError:
                    return {}
            return {}

    def _write(self, scope: str, data: Dict[str, Any]) -> None:
        p = self._path(scope)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
        try:
            os.chmod(p, 0o600)
        except OSError:
            pass

    def creds(self, scope: str, cid: str) -> Dict[str, str]:
        return dict(self.load(scope).get("credentials", {}).get(cid, {}))

    def save_creds(self, scope: str, cid: str, values: Dict[str, str]) -> Dict[str, str]:
        with self.lock:
            d = self.load(scope)
            cur = d.setdefault("credentials", {}).setdefault(cid, {})
            for k, v in (values or {}).items():
                v = "" if v is None else str(v)
                if v.startswith("••••"):
                    continue                         # masked value sent back unchanged
                if v == "":
                    cur.pop(k, None)
                else:
                    cur[k] = v.strip()
            self._write(scope, d)
            return self.masked(scope, cid)

    def masked(self, scope: str, cid: str) -> Dict[str, str]:
        cls = registry().get(cid)
        secret_keys = {c["key"] for c in (cls.credentials if cls else []) if c.get("secret", True)}
        return {k: (mask(v) if (k in secret_keys or not cls) else v) for k, v in self.creds(scope, cid).items()}

    # custom API definitions (non-secret) live alongside, in a separate file
    def _cpath(self, scope: str) -> Path:
        return self.folder / f"{scope}.custom_apis.json"

    def custom_defs(self, scope: str) -> Dict[str, Any]:
        p = self._cpath(scope)
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except ValueError:
                return {}
        return {}

    def save_custom_def(self, scope: str, slug: str, definition: Dict[str, Any]) -> Dict[str, Any]:
        if not SCOPE_RE.match(slug or ""):
            raise ConnectorError("Custom API name must be letters, numbers, - or _.")
        with self.lock:
            d = self.custom_defs(scope)
            d[slug] = definition
            self._cpath(scope).parent.mkdir(parents=True, exist_ok=True)
            self._cpath(scope).write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding="utf-8")
            return definition

    def enabled(self, scope: str) -> List[str]:
        return list(self.load(scope).get("enabled", []))

    def set_enabled(self, scope: str, cid: str, on: bool) -> List[str]:
        with self.lock:
            d = self.load(scope)
            en = [x for x in d.get("enabled", []) if x != cid]
            if on:
                en.append(cid)
            d["enabled"] = en
            self._write(scope, d)
            return en


# ---------------------------------------------------------------- manager
class ConnectorManager:
    def __init__(self, store: CredentialStore, fetcher: Callable = fetch, contact: str = ""):
        self.store, self.fetcher, self.contact = store, fetcher, contact

    def _make(self, scope: str, cid: str) -> Connector:
        if cid.startswith("custom:"):
            from .custom_api import CustomAPI
            slug = cid.split(":", 1)[1]
            d = self.store.custom_defs(scope).get(slug)
            if not d:
                raise ConnectorError(f"No custom API called {slug!r} here.", 404)
            return CustomAPI(self.store.creds(scope, cid), self.fetcher, self.contact, definition=d, slug=slug)
        cls = registry().get(cid)
        if not cls:
            raise ConnectorError(f"No connector {cid!r}.", 404)
        return cls(self.store.creds(scope, cid), self.fetcher, self.contact)

    def list(self, scope: str) -> List[Dict[str, Any]]:
        en = set(self.store.enabled(scope))
        out = []
        for d in catalogue():
            d["saved_credentials"] = self.store.masked(scope, d["id"])
            d["enabled"] = d["id"] in en
            out.append(d)
        for slug, definition in self.store.custom_defs(scope).items():
            from .custom_api import CustomAPI
            d = CustomAPI.describe_instance(slug, definition)
            d["saved_credentials"] = {k: mask(v) for k, v in self.store.creds(scope, d["id"]).items()}
            d["enabled"] = d["id"] in en
            out.append(d)
        return out

    def test(self, scope: str, cid: str) -> Dict[str, Any]:
        return _safe_test(self._make(scope, cid))

    def run(self, scope: str, cid: str, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        c = self._make(scope, cid)
        try:
            return {"ok": True, "result": c.run(action, params)}
        except NetError as e:
            msg = str(e)
            if e.kind == "auth":
                msg = f"The service refused the key/login ({e.status})."
            return {"ok": False, "message": msg, "kind": e.kind, "status": e.status, "detail": e.body[:300]}
        except (KeyError, TypeError, ValueError, AttributeError, IndexError) as e:
            return {"ok": False, "message": f"The service answered, but not in the shape we expected ({type(e).__name__}).",
                    "kind": "bad_data"}
