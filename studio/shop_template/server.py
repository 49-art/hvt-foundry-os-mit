#!/usr/bin/env python3
"""
The shop's own little web server (Python standard library only — nothing to install).

  python3 server.py                  start on http://localhost:8080  (customers see the shop, owner edits at /admin)
  python3 server.py --host 0.0.0.0   let phones on the same Wi-Fi open it
  python3 server.py --set-password   choose a new owner password
  python3 server.py --build          rebuild the public files in site/ from data/shop.json

The public app is just the files in site/. You can upload that folder to any
static web host. The admin page (/admin) only works when this server runs.
"""
from __future__ import annotations

import argparse
import getpass
import json
import mimetypes
import secrets
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "lib"))
import shopbuild  # noqa: E402

try:
    import connectors as hvtc  # noqa: E402
    import connectors.custom_api  # noqa: E402,F401
except Exception:          # the app still works without the connectors folder
    hvtc = None

SESSION_HOURS = 12
SCOPE = "shop"


class App:
    def __init__(self, app_dir: Path = HERE, fetcher=None):
        self.dir = Path(app_dir)
        self.sessions = {}
        self.fails = {}
        self.lock = threading.RLock()
        self.cm = None
        if hvtc:
            store = hvtc.CredentialStore(self.dir / "data")          # data/shop.secrets.json — never share this file
            self.cm = hvtc.ConnectorManager(store, fetcher or hvtc.fetch)

    def shop(self):
        return shopbuild.load_shop(self.dir)

    def login(self, pw, ip):
        with self.lock:
            n, t = self.fails.get(ip, (0, 0))
            if n >= 5 and time.time() - t < 60:
                raise PermissionError("Too many wrong tries. Wait a minute and try again.")
            h = self.shop().get("admin", {}).get("password_hash")
            if not h:
                raise PermissionError("No owner password is set yet. On the computer, run: python3 server.py --set-password")
            if not shopbuild.verify_password(pw, h):
                self.fails[ip] = (n + 1, time.time())
                raise PermissionError("Wrong password.")
            self.fails.pop(ip, None)
            tok = secrets.token_urlsafe(32)
            self.sessions[tok] = time.time() + SESSION_HOURS * 3600
            return tok

    def authed(self, tok):
        exp = self.sessions.get(tok or "")
        return bool(exp and exp > time.time())

    def save_shop(self, data):
        cur = self.shop()
        data = dict(data)
        data["admin"] = cur.get("admin", {})              # the password can't be changed through this route
        data.setdefault("suppliers", cur.get("suppliers", []))
        data["demo"] = cur.get("demo", False)
        return shopbuild.save_shop(self.dir, data)

    def set_password(self, old, new):
        cur = self.shop()
        h = cur.get("admin", {}).get("password_hash")
        if h and not shopbuild.verify_password(old, h):
            raise PermissionError("The current password is wrong.")
        cur["admin"] = {"password_hash": shopbuild.hash_password(new)}
        shopbuild.save_shop(self.dir, cur)
        self.sessions.clear()


def admin_view(shop):
    s = dict(shop)
    s["admin"] = {"password_set": bool(shop.get("admin", {}).get("password_hash"))}
    return s


def make_handler(app: App):
    class H(BaseHTTPRequestHandler):
        server_version = "ShopApp/1.0"

        def log_message(self, *a):
            pass

        def _send(self, code, body, ctype="application/json; charset=utf-8", extra=None):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Content-Type-Options", "nosniff")
            if ctype.startswith("application/json"):
                self.send_header("Cache-Control", "no-store")
            for k, v in (extra or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(body)

        def _json(self, code, obj, extra=None):
            self._send(code, json.dumps(obj, ensure_ascii=False).encode(), extra=extra)

        def _tok(self):
            for part in (self.headers.get("Cookie") or "").split(";"):
                k, _, v = part.strip().partition("=")
                if k == "shop_session":
                    return v
            return ""

        def _body(self):
            n = int(self.headers.get("Content-Length") or 0)
            if n > 3_000_000:
                raise ValueError("Too much data sent.")
            return json.loads(self.rfile.read(n).decode("utf-8")) if n else {}

        def do_GET(self):
            path = unquote(urlparse(self.path).path)
            if path == "/api/admin/me":
                return self._json(200, {"logged_in": app.authed(self._tok())})
            if path.startswith("/api/admin/"):
                if not app.authed(self._tok()):
                    return self._json(401, {"message": "Please log in."})
                if path == "/api/admin/shop":
                    return self._json(200, admin_view(app.shop()))
                if path == "/api/admin/connectors":
                    return self._json(200, app.cm.list(SCOPE) if app.cm else [])
                return self._json(404, {"message": "Not found"})
            if path in ("/admin", "/admin/"):
                return self._file(HERE / "admin" / "index.html")
            if path.startswith("/admin/"):
                return self._file(HERE / "admin" / path[len("/admin/"):], HERE / "admin")
            rel = path.lstrip("/") or "index.html"
            return self._file(HERE / "site" / rel, HERE / "site")

        def _file(self, f, root=None):
            f = f.resolve()
            root = (root or f.parent).resolve()
            if not f.is_file() or (root not in f.parents and f != root):
                return self._send(404, b"Not found", "text/plain")
            ctype = mimetypes.guess_type(str(f))[0] or "application/octet-stream"
            if f.suffix == ".webmanifest":
                ctype = "application/manifest+json"
            if ctype.startswith("text/") or ctype.endswith(("javascript", "json")):
                ctype += "; charset=utf-8"
            extra = {"Cache-Control": "no-cache"} if f.name in ("sw.js", "content.json", "index.html") else {}
            self._send(200, f.read_bytes(), ctype, extra)

        def do_POST(self):
            path = unquote(urlparse(self.path).path)
            try:
                b = self._body()
                if path == "/api/login":
                    tok = app.login(b.get("password", ""), self.client_address[0])
                    return self._json(200, {"ok": True}, {"Set-Cookie": f"shop_session={tok}; HttpOnly; SameSite=Strict; Path=/; Max-Age={SESSION_HOURS * 3600}"})
                if path == "/api/logout":
                    app.sessions.pop(self._tok(), None)
                    return self._json(200, {"ok": True}, {"Set-Cookie": "shop_session=; Path=/; Max-Age=0"})
                if not path.startswith("/api/admin/"):
                    return self._json(404, {"message": "Not found"})
                if not app.authed(self._tok()):
                    return self._json(401, {"message": "Please log in."})
                r = path[len("/api/admin/"):].split("/")
                if r == ["shop"]:
                    return self._json(200, {"ok": True, "shop": admin_view(app.save_shop(b))})
                if r == ["password"]:
                    app.set_password(b.get("old", ""), b.get("new", ""))
                    return self._json(200, {"ok": True, "message": "Password changed. Please log in again."})
                if not app.cm:
                    return self._json(501, {"message": "Connectors folder (lib/connectors) is missing."})
                if r == ["custom-api"]:
                    d = hvtc.custom_api.validate_definition(b.get("definition") or {})
                    app.cm.store.save_custom_def(SCOPE, b.get("slug", ""), d)
                    return self._json(200, {"ok": True})
                if r == ["openapi"]:
                    return self._json(200, hvtc.custom_api.parse_openapi(b.get("spec")))
                if len(r) == 3 and r[0] == "connectors":
                    cid, act = r[1], r[2]
                    if act == "credentials":
                        return self._json(200, {"ok": True, "saved": app.cm.store.save_creds(SCOPE, cid, b.get("values") or {})})
                    if act == "test":
                        return self._json(200, app.cm.test(SCOPE, cid))
                    if act == "run":
                        return self._json(200, app.cm.run(SCOPE, cid, b.get("action", ""), b.get("params") or {}))
                    if act == "enable":
                        return self._json(200, {"enabled": app.cm.store.set_enabled(SCOPE, cid, bool(b.get("on")))})
                return self._json(404, {"message": "Not found"})
            except PermissionError as e:
                return self._json(403, {"message": str(e)})
            except (ValueError, KeyError, TypeError) as e:
                return self._json(400, {"message": str(e)})
            except Exception as e:  # connector errors etc.
                code = getattr(e, "code", 500)
                return self._json(code if isinstance(code, int) and 400 <= code < 600 else 500, {"message": str(e)})

    return H


def main(argv=None):
    ap = argparse.ArgumentParser(description="Shop app server")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--set-password", action="store_true")
    ap.add_argument("--build", action="store_true")
    a = ap.parse_args(argv)
    app = App()
    if a.set_password:
        pw = getpass.getpass("New owner password (6+ characters): ")
        if pw != getpass.getpass("Type it again: "):
            print("They don't match. Nothing changed.")
            return
        shop = app.shop()
        shop["admin"] = {"password_hash": shopbuild.hash_password(pw)}
        shopbuild.save_shop(app.dir, shop)
        print("Password saved (only a scrambled version is stored).")
        return
    if a.build:
        shopbuild.save_shop(app.dir, app.shop())
        print("Rebuilt the public files in", app.dir / "site")
        return
    httpd = ThreadingHTTPServer((a.host, a.port), make_handler(app))
    print(f"{app.shop()['name']} — shop app running.")
    print(f"  Customers: http://localhost:{a.port}/")
    print(f"  Owner admin: http://localhost:{a.port}/admin")
    print("Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
