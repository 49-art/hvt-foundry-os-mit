"""
Custom API — connect any REST service (open source or paid) without writing code.

The owner or salesperson gives: a base URL, how to log in (none / API key in a
header / bearer token / basic username+password), and simple actions
(GET or POST to a path, with {placeholders}). An OpenAPI (Swagger) JSON file can
be imported to list its endpoints and turn them into actions.
"""
from __future__ import annotations

import json
import re
import urllib.parse
from typing import Any, Dict, List

from . import Connector, ConnectorError, basic, mask

AUTH_TYPES = {"none": "No login", "api_key_header": "API key in a header", "bearer": "Bearer token", "basic": "Username + password (basic)"}
PH = re.compile(r"\{([A-Za-z0-9_]+)\}")


def validate_definition(d: Dict[str, Any]) -> Dict[str, Any]:
    base = str(d.get("base_url") or "").strip().rstrip("/")
    if not re.match(r"^https?://[^\s/]+", base):
        raise ConnectorError("Base URL must start with https:// (or http:// for a service on your own network).")
    auth = d.get("auth_type") or "none"
    if auth not in AUTH_TYPES:
        raise ConnectorError(f"Login type must be one of {list(AUTH_TYPES)}.")
    actions = []
    for a in d.get("actions") or []:
        name = re.sub(r"[^A-Za-z0-9_]", "_", str(a.get("name") or "").strip())[:40]
        method = str(a.get("method") or "GET").upper()
        path = "/" + str(a.get("path") or "").lstrip("/")
        if not name or method not in ("GET", "POST", "PUT", "PATCH", "DELETE"):
            raise ConnectorError("Each action needs a name and a method (GET, POST, PUT, PATCH, DELETE).")
        actions.append({"name": name, "method": method, "path": path, "label": a.get("label") or name,
                        "body_template": a.get("body_template") or "", "summary": a.get("summary") or ""})
    return {"label": str(d.get("label") or "Custom API")[:80], "base_url": base, "auth_type": auth,
            "header_name": str(d.get("header_name") or "X-API-Key")[:60], "actions": actions,
            "test_path": "/" + str(d.get("test_path") or "").lstrip("/") if d.get("test_path") else "",
            "notes": str(d.get("notes") or "")[:500], "cost_type": d.get("cost_type") or "unknown"}


def parse_openapi(spec: Any) -> Dict[str, Any]:
    """Read an OpenAPI 3 / Swagger 2 JSON document and list its endpoints."""
    if isinstance(spec, (str, bytes)):
        try:
            spec = json.loads(spec)
        except ValueError:
            raise ConnectorError("That isn't valid JSON. (YAML OpenAPI files aren't supported; convert to JSON first.)")
    if not isinstance(spec, dict) or not ("openapi" in spec or "swagger" in spec) or "paths" not in spec:
        raise ConnectorError("That doesn't look like an OpenAPI/Swagger file (needs 'openapi' or 'swagger' and 'paths').")
    base = ""
    if spec.get("servers"):
        base = spec["servers"][0].get("url", "")
    elif spec.get("host"):
        base = f"{(spec.get('schemes') or ['https'])[0]}://{spec['host']}{spec.get('basePath', '')}"
    eps: List[Dict[str, str]] = []
    for path, ops in (spec.get("paths") or {}).items():
        for m, op in (ops or {}).items():
            if m.lower() in ("get", "post", "put", "patch", "delete"):
                op = op or {}
                eps.append({"method": m.upper(), "path": path,
                            "name": re.sub(r"[^A-Za-z0-9_]", "_", op.get("operationId") or f"{m}_{path}")[:40].strip("_"),
                            "summary": (op.get("summary") or op.get("description") or "")[:160]})
    auth = "none"
    schemes = (spec.get("components") or {}).get("securitySchemes") or spec.get("securityDefinitions") or {}
    header_name = "X-API-Key"
    for s in schemes.values():
        t = (s.get("type") or "").lower()
        if t == "apikey" and s.get("in") == "header":
            auth, header_name = "api_key_header", s.get("name") or header_name
            break
        if t == "http" and s.get("scheme") == "bearer" or t == "oauth2":
            auth = "bearer"
            break
        if t == "http" and s.get("scheme") == "basic" or t == "basic":
            auth = "basic"
            break
    return {"title": (spec.get("info") or {}).get("title", "API"), "version": (spec.get("info") or {}).get("version", ""),
            "base_url": base, "auth_type": auth, "header_name": header_name, "endpoints": eps}


class CustomAPI(Connector):
    id = "custom_api"
    name = "Custom API (any REST service)"
    category = "Custom"
    cost_type = "free"
    what_it_does = ("Add any open-source or paid service that has a web API: paste its address, choose how it logs in, "
                    "and add simple actions. Or import its OpenAPI file to list what it can do.")
    credentials = [{"key": "secret", "label": "API key / token / password", "secret": True, "required": False},
                   {"key": "username", "label": "Username (basic login only)", "secret": False, "required": False}]
    docs_url = "https://spec.openapis.org/oas/latest.html"
    status = "working-tested"
    status_note = "Tested live on 2026-09-26 against frankfurter.dev's public API and its OpenAPI file, and by automated tests."
    live_tested_on = "2026-09-26"
    actions = {}

    def __init__(self, creds=None, fetcher=None, contact="", definition=None, slug=""):
        from netutil import fetch
        super().__init__(creds, fetcher or fetch, contact)
        self.d = validate_definition(definition or {})
        self.slug = slug
        self.actions = {a["name"]: {"label": a["label"], "params": [{"key": k, "label": k} for k in self._placeholders(a)]}
                        for a in self.d["actions"]}

    @staticmethod
    def _placeholders(a):
        return sorted(set(PH.findall(a["path"]) + PH.findall(a.get("body_template") or "")))

    @classmethod
    def describe_instance(cls, slug, definition):
        d = validate_definition(definition)
        base = cls.describe()
        base.update({"id": f"custom:{slug}", "name": d["label"] + " (custom)", "what_it_does": d["notes"] or f"Custom API at {d['base_url']}",
                     "docs_url": d["base_url"], "cost_type": d["cost_type"], "status": "unverified",
                     "status_note": "Added by you. Use Test to check it.", "pricing": None, "live_tested_on": None,
                     "definition": d,
                     "actions": {a["name"]: {"label": a["label"], "method": a["method"], "path": a["path"],
                                             "params": [{"key": k, "label": k} for k in cls._placeholders(a)]} for a in d["actions"]}})
        return base

    def _headers(self):
        t, s = self.d["auth_type"], self.creds.get("secret", "")
        if t == "none":
            return {}
        if not s:
            raise ConnectorError("This API needs a key/token/password. Add it on the Connectors screen.", 412)
        if t == "api_key_header":
            return {self.d["header_name"]: s}
        if t == "bearer":
            return {"Authorization": "Bearer " + s}
        return {"Authorization": basic(self.creds.get("username", ""), s)}

    def _call(self, method, path, params=None, body_template=""):
        params = params or {}
        used = set(PH.findall(path)) | set(PH.findall(body_template or ""))
        path = PH.sub(lambda m: urllib.parse.quote(str(params.get(m.group(1), "")), safe=""), path)
        url = self.d["base_url"] + path
        extra = {k: v for k, v in params.items() if k not in used and not k.startswith("_")}
        body = None
        if body_template:
            txt = PH.sub(lambda m: json.dumps(str(params.get(m.group(1), "")))[1:-1], body_template)
            try:
                body = json.loads(txt)
            except ValueError:
                raise ConnectorError("The body template isn't valid JSON after filling in the values.")
        elif method == "GET" and extra:
            url += ("&" if "?" in url else "?") + urllib.parse.urlencode(extra)
        status, headers, raw = self.fetch(url, method=method, headers=dict(self._headers(), Accept="application/json",
                                          **({"Content-Type": "application/json"} if body is not None else {})),
                                          data=json.dumps(body).encode() if body is not None else None, timeout=20, contact=self.contact)
        text = raw.decode("utf-8", "replace")
        try:
            return {"status": status, "json": json.loads(text)}
        except ValueError:
            return {"status": status, "text": text[:2000]}

    def test_connection(self):
        r = self._call("GET", self.d.get("test_path") or (self.d["actions"][0]["path"] if self.d["actions"] and self.d["actions"][0]["method"] == "GET" else "/"))
        return {"ok": True, "message": f"The service answered (HTTP {r['status']})."}

    def run(self, action, params):
        a = next((x for x in self.d["actions"] if x["name"] == action), None)
        if not a:
            raise ConnectorError(f"No action {action!r}.", 404)
        return self._call(a["method"], a["path"], params, a.get("body_template"))
