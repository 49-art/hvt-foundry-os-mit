#!/usr/bin/env python3
"""
HVT Foundry Studio — web server.

Start:   python3 studio/app.py            (then open http://localhost:8000)
Options: --port 8000  --host 127.0.0.1  --no-browser  --data PATH

Python standard library only. Runs on the Foundry Kernel (kernel/foundry_kernel.py).
"""
from __future__ import annotations

import argparse
import json
import secrets
import time
import mimetypes
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, unquote, parse_qs

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from studio_core import Studio, StudioRefusal  # noqa: E402

STATIC = HERE / "static"


SESSIONS: dict = {}           # Studio login tokens (only used when a Studio password is set)


def make_handler(studio: Studio):
    class Handler(BaseHTTPRequestHandler):
        server_version = "HVTFoundryStudio/0.3"

        def _locked(self, path):
            """True if a Studio password is set and this request has no valid login."""
            if not studio.settings.load().get("studio_password_hash"):
                return False
            if path in ("/api/login", "/api/auth-status"):
                return False
            tok = ""
            for part in (self.headers.get("Cookie") or "").split(";"):
                k, _, v = part.strip().partition("=")
                if k == "hvt_studio":
                    tok = v
            return not (SESSIONS.get(tok, 0) > time.time())

        def _query(self):
            return {k: v[0] for k, v in parse_qs(urlparse(self.path).query).items()}

        def log_message(self, fmt, *args):  # quieter console
            if "--verbose" in sys.argv:
                super().log_message(fmt, *args)

        # ---------------------------------------------------------- helpers
        def _send(self, code, body: bytes, ctype="application/json; charset=utf-8"):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, code, obj):
            self._send(code, json.dumps(obj, ensure_ascii=False, indent=1).encode("utf-8"))

        def _body(self):
            n = int(self.headers.get("Content-Length") or 0)
            if not n:
                return {}
            try:
                return json.loads(self.rfile.read(n).decode("utf-8"))
            except json.JSONDecodeError:
                raise StudioRefusal("Request body is not valid JSON.", 400)

        def _run(self, fn):
            try:
                self._json(200, fn())
            except StudioRefusal as e:
                self._json(e.code, {"refused": True, "code": e.code, "message": str(e)})
            except (TypeError, KeyError, ValueError, AttributeError) as e:
                self._json(400, {"refused": True, "code": 400, "message": f"Bad request: {e}"})

        # ------------------------------------------------------------ GET
        def do_GET(self):
            path = unquote(urlparse(self.path).path)
            parts = [p for p in path.split("/") if p]
            if parts and parts[0] == "shops" and len(parts) >= 2:
                return self._shop_preview(parts[1], "/".join(parts[2:]))
            if parts and parts[0] == "cardapps" and len(parts) >= 2:
                return self._card_preview(parts[1], "/".join(parts[2:]))
            if not parts or parts[0] != "api":
                return self._static(path)
            if self._locked(path):
                return self._json(401, {"refused": True, "code": 401, "login_required": True, "message": "Please log in to the Studio."})
            r = parts[1:]
            q = self._query()
            if r == ["auth-status"]:
                return self._json(200, {"password_set": bool(studio.settings.load().get("studio_password_hash"))})
            if r == ["communities"]:
                return self._run(studio.community_catalogue)
            if r == ["queries"]:
                return self._run(lambda: studio.preview_queries(q.get("community", "other"), q.get("category", "suppliers"),
                                                                q.get("area", "London"), q.get("free_text", "")))
            if r == ["settings"]:
                return self._run(studio.get_settings)
            if r == ["connectors"]:
                return self._run(lambda: studio.connectors_list(q.get("scope", "studio")))
            if len(r) == 3 and r[0] == "sessions" and r[2] == "shop-app":
                return self._run(lambda: studio.shop_app_draft(r[1]))
            if len(r) == 2 and r[0] == "exports":
                f = studio.export_file(r[1])
                if not f:
                    return self._json(404, {"refused": True, "code": 404, "message": "No such export."})
                body = f.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "application/zip")
                self.send_header("Content-Disposition", f'attachment; filename="{f.name}"')
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if r == ["state"]:
                return self._run(studio.summary)
            if r == ["cards"]:
                return self._run(studio.card_list)
            if len(r) == 2 and r[0] == "cards":
                return self._run(lambda: studio.card_detail(r[1]))
            if r == ["card-apps"]:
                return self._run(studio.card_apps)
            if r == ["business-types"]:
                return self._run(studio.business_types)
            if len(r) == 2 and r[0] == "card":
                return self._run(lambda: {"id": r[1], "markdown": studio.card_markdown(r[1])})
            if r == ["overlay"]:
                return self._run(lambda: {"markdown": studio.overlay_markdown()})
            if r == ["sessions"]:
                return self._run(studio.sessions)
            if len(r) == 2 and r[0] == "sessions":
                return self._run(lambda: studio.session_detail(r[1]))
            if r == ["queue"]:
                return self._run(studio.review_queue)
            if len(r) == 3 and r[0] == "wishes" and r[2] == "history":
                return self._run(lambda: studio.wish_history(r[1]))
            if r == ["audit"]:
                return self._run(studio.audit)
            if len(r) == 2 and r[0] == "preview":
                q = dict(p.split("=", 1) for p in (urlparse(self.path).query or "").split("&") if "=" in p)
                q = {k: unquote(v) or None for k, v in q.items()}
                return self._run(lambda: studio.configurator(r[1], q.get("size"), q.get("budget"), q.get("tech")))
            self._json(404, {"refused": True, "code": 404, "message": "Not found"})

        # ----------------------------------------------------------- POST
        def do_POST(self):
            parts = [p for p in unquote(urlparse(self.path).path).split("/") if p]
            if not parts or parts[0] != "api":
                return self._json(404, {"message": "Not found"})
            r = parts[1:]
            path = "/" + "/".join(parts)
            if r == ["login"]:
                try:
                    b = self._body()
                except StudioRefusal as e:
                    return self._json(400, {"message": str(e)})
                if not studio.check_studio_password(b.get("password", "")):
                    time.sleep(1)
                    return self._json(403, {"refused": True, "code": 403, "message": "Wrong Studio password."})
                tok = secrets.token_urlsafe(32)
                SESSIONS[tok] = time.time() + 12 * 3600
                body = json.dumps({"ok": True}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Set-Cookie", f"hvt_studio={tok}; HttpOnly; SameSite=Strict; Path=/; Max-Age=43200")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            if self._locked(path):
                return self._json(401, {"refused": True, "code": 401, "login_required": True, "message": "Please log in to the Studio."})

            def route():
                b = self._body()
                if r == ["search"]:
                    return studio.live_search(b)
                if r == ["settings"]:
                    return studio.save_settings(b)
                if len(r) == 3 and r[0] == "connectors":
                    return studio.connector_op(b.get("scope", "studio"), r[1], r[2], b)
                if len(r) == 3 and r[0] == "sessions" and r[2] == "save-result":
                    return studio.save_search_result(r[1], b.get("result") or {}, b.get("note", ""))
                if len(r) == 3 and r[0] == "sessions" and r[2] == "shop-app":
                    return studio.build_shop_app(r[1], b.get("shop") or {}, b.get("password", ""))
                if len(r) == 4 and r[0] == "sessions" and r[2] == "shop-app" and r[3] == "export":
                    return studio.export_shop_app(r[1])
                if r == ["boot"]:
                    return studio.boot()
                if len(r) == 3 and r[0] == "cards" and r[2] == "preview":
                    return studio.card_preview(r[1], b.get("preset", ""), b.get("modules") or {})
                if len(r) == 3 and r[0] == "cards" and r[2] == "build":
                    return studio.build_card_app(r[1], b.get("shop") or {}, b.get("password", ""), b.get("app_id", ""),
                                                 b.get("session_id", ""))
                if len(r) == 3 and r[0] == "card-apps" and r[2] == "export":
                    return studio.export_card_app(r[1])
                if r == ["sessions"]:
                    return studio.open_session(b["business_type_id"], b.get("business_name", ""),
                                               b.get("location", ""), b.get("run_by", ""), b.get("notes", ""))
                if len(r) == 3 and r[0] == "sessions":
                    sid, act = r[1], r[2]
                    if act == "classify":
                        return studio.classify(sid, b.get("business_type_id"), b.get("sector"),
                                               b.get("market_industry"), b.get("owner_words", ""))
                    if act == "configure":
                        return studio.run_configurator(sid, b.get("size"), b.get("budget"), b.get("tech"))
                    if act == "response":
                        return studio.record_owner_response(sid, b["proposal_id"], b["decision"], b.get("owner_words", ""))
                    if act == "wishes":
                        return studio.capture_wish(sid, b.get("description", ""), b.get("priority"),
                                                   b.get("linked_problems") or [], b.get("linked_capabilities", ""),
                                                   bool(b.get("customer_asset_flag")))
                    if act == "close":
                        return studio.close_session(sid)
                    if act == "follow-up":
                        return studio.offer_follow_up(sid)
                if len(r) == 3 and r[0] == "wishes" and r[2] == "resolve":
                    return studio.resolve_wish(r[1], b.get("outcome", ""), b.get("reason", ""), b.get("capability", ""))
                if r == ["authority-test"]:
                    return studio.authority_test(b.get("case", ""))
                raise StudioRefusal("Not found", 404)
            self._run(route)

        def _shop_preview(self, folder, rel):
            site = studio.shop_site_dir(folder)
            if not site:
                return self._send(404, b"Not found", "text/plain")
            f = (site / (rel or "index.html")).resolve()
            if not f.is_file() or site not in f.parents:
                return self._send(404, b"Not found", "text/plain")
            ctype = mimetypes.guess_type(str(f))[0] or "application/octet-stream"
            if f.suffix == ".webmanifest":
                ctype = "application/manifest+json"
            if ctype.startswith("text/") or ctype.endswith(("javascript", "json")):
                ctype += "; charset=utf-8"
            self._send(200, f.read_bytes(), ctype)

        def _card_preview(self, folder, rel):
            app_dir = studio.card_app_dir(folder)
            if not app_dir:
                return self._send(404, b"Not found", "text/plain")
            site = (app_dir / "site").resolve()
            if rel in ("queue", "queue/"):
                rel = "queue.html"
            f = (site / (rel or "index.html")).resolve()
            if not f.is_file() or site not in f.parents:
                return self._send(404, b"Not found", "text/plain")
            ctype = mimetypes.guess_type(str(f))[0] or "application/octet-stream"
            if f.suffix == ".webmanifest":
                ctype = "application/manifest+json"
            if f.suffix == ".svg":
                ctype = "image/svg+xml"
            if ctype.startswith("text/") or ctype.endswith(("javascript", "json")):
                ctype += "; charset=utf-8"
            self._send(200, f.read_bytes(), ctype)

        # --------------------------------------------------------- static
        def _static(self, path):
            rel = "index.html" if path in ("", "/") else path.lstrip("/")
            f = (STATIC / rel).resolve()
            if not f.is_file() or STATIC not in f.parents:
                f = STATIC / "index.html"
            ctype = mimetypes.guess_type(str(f))[0] or "application/octet-stream"
            if ctype.startswith("text/") or ctype.endswith("javascript"):
                ctype += "; charset=utf-8"
            self._send(200, f.read_bytes(), ctype)

    return Handler


def make_server(host="127.0.0.1", port=8000, data=None, fetcher=None, settings_path=None):
    studio = Studio(state_path=data, fetcher=fetcher, settings_path=settings_path)
    httpd = ThreadingHTTPServer((host, port), make_handler(studio))
    return httpd, studio


def main(argv=None):
    ap = argparse.ArgumentParser(description="HVT Foundry Studio")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--data", default=None, help="path to the JSON state file (default studio/data/studio_state.json)")
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args(argv)
    httpd, studio = make_server(a.host, a.port, a.data)
    url = f"http://localhost:{a.port}"
    print("HVT Foundry Studio", studio.summary()["studio_version"])
    print("Kernel boot:", "OK — all 4 gates behaved as expected" if studio.booted else "FAILED — see the Boot screen")
    print("Saving to:", studio.store.path)
    print(f"Open {url} in your browser.  Press Ctrl+C to stop.")
    if not a.no_browser:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped. Your work is saved.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
