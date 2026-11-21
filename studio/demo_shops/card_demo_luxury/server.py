#!/usr/bin/env python3
"""
Shop app server for a card-based app (standard library only).

  python3 server.py                 start (customers: http://localhost:8080/, owner: /admin, queue board: /queue)
  python3 server.py --set-password  set or change the owner password
  python3 server.py --build         rebuild the public files after editing data/shop.json by hand

Private data (bookings, clients, vouchers, keys) lives in data/private/ and
data/shop.secrets.json on this computer only. Back up the whole folder.
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
import os
from datetime import date, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "lib"))
import cardbuild  # noqa: E402
import cards_runtime  # noqa: E402
from engines import (analytics, booking, calendar, clients, loyalty, messages, packages, referrals,  # noqa: E402
                     retail, rota, suppliers, vouchers, walkin)
from engines.store import EngineError, now_local  # noqa: E402

try:
    import connectors as hvtc  # noqa: E402
    import connectors.custom_api  # noqa: E402,F401
    from netutil import fetch as net_fetch  # noqa: E402
except Exception:          # the app still works without the connectors folder
    hvtc, net_fetch = None, None

SESSION_HOURS = 12
SCOPE = "shop"
PAY_PROVIDERS = ("stripe", "square", "sumup")


class Off(Exception):
    """A module is switched off."""


class App:
    def __init__(self, app_dir: Path = HERE, fetcher=None, now=None):
        self.dir = Path(app_dir)
        self.sessions, self.fails, self.hits = {}, {}, {}
        self.lock = threading.RLock()
        self.fetcher = fetcher or net_fetch
        p = self.dir / "data" / "private"
        now = now or self._demo_clock()
        kw = {"now": now} if now else {}
        self.now = now or now_local
        shop = self.shop
        self.clients = clients.Clients(p / "clients.json", shop, **kw)
        self.booking = booking.BookingEngine(
            p / "bookings.json", shop, patch_tests=self._patch_tests,
            deposits_on=lambda: bool(self.shop()["modules"].get("deposits")), **kw)
        self.queue = walkin.WalkInQueue(p / "walkin.json", shop, booked=self._booked_for_queue, **kw)
        self.loyalty = loyalty.Loyalty(p / "loyalty.json", shop, **kw)
        self.vouchers = vouchers.Vouchers(p / "vouchers.json", shop, **kw)
        self.packages = packages.Packages(p / "packages.json", shop, **kw)
        self.retail = retail.Retail(p / "stock.json", shop, **kw)
        self.rota = rota.Rota(p / "rota.json", shop, **kw)
        self.referrals = referrals.Referrals(p / "referrals.json", shop, **kw)
        self.analytics = analytics.Analytics(p / "analytics.json", **kw)
        self.cm = None
        if hvtc:
            self.cm = hvtc.ConnectorManager(hvtc.CredentialStore(self.dir / "data"), self.fetcher or hvtc.fetch)

    # -------------------------------------------------------------- basics
    def _demo_clock(self):
        """Demo shops only: SHOP_DEMO_NOW=2026-10-24T10:30 makes the app act as if it were that
        time, so screenshots taken at night still show an open shop. Ignored for real shops."""
        v = os.environ.get("SHOP_DEMO_NOW", "")
        if not v:
            return None
        try:
            if not cardbuild.load_shop(self.dir).get("demo"):
                return None
            start, real = datetime.fromisoformat(v), time.time()
            return lambda: (start + timedelta(seconds=int(time.time() - real))).replace(microsecond=0)
        except Exception:
            return None

    def _patch_tests(self, phone):
        """Patch-test records for the booking rule; None when client records are off."""
        if not self.shop()["modules"].get("client_records"):
            return None
        return self.clients.patch_tests_for(phone)

    def _booked_for_queue(self, barber, day):
        """Booked time in the same chairs, so walk-in waits include appointments (mixed shops)."""
        if not self.shop()["modules"].get("auto_booking") and not self.shop()["modules"].get("booking_request"):
            return []
        return self.booking.busy_blocks(barber, day)

    def pay_provider(self):
        """The payment firm the owner picked for deposits, if it's switched on and has its key."""
        if not self.cm:
            return ""
        want = str(self.shop().get("deposit_provider") or "")
        on = set(self.cm.store.enabled(SCOPE))
        for cid in ([want] if want else []) + list(PAY_PROVIDERS):
            if cid in PAY_PROVIDERS and cid in on and self.cm.store.creds(SCOPE, cid):
                return cid
        return ""

    def shop(self):
        return cardbuild.load_shop(self.dir)

    def card(self):
        return cardbuild.load_card(self.dir)

    def on(self, *mods):
        m = self.shop()["modules"]
        if not any(m.get(x) for x in mods):
            raise Off("This feature is switched off for this shop.")

    def throttle(self, ip, what, n=30, per=60):
        with self.lock:
            k = (ip, what)
            ts = [t for t in self.hits.get(k, []) if time.time() - t < per]
            if len(ts) >= n:
                raise PermissionError("Too many tries. Please wait a minute.")
            ts.append(time.time())
            self.hits[k] = ts

    def login(self, pw, ip):
        with self.lock:
            n, t = self.fails.get(ip, (0, 0))
            if n >= 5 and time.time() - t < 60:
                raise PermissionError("Too many wrong tries. Wait a minute and try again.")
            h = self.shop().get("admin", {}).get("password_hash")
            if not h:
                raise PermissionError("No owner password is set yet. On the computer, run: python3 server.py --set-password")
            if not cardbuild.verify_password(pw, h):
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
        data.setdefault("modules", cur.get("modules", {}))
        data["demo"] = cur.get("demo", False)
        for k in ("lat", "lon"):
            data.setdefault(k, cur.get(k))
        return cardbuild.save_shop(self.dir, data)

    def set_modules(self, changes):
        cur = self.shop()
        mods = dict(cur.get("modules", {}))
        mods.update({k: bool(v) for k, v in (changes or {}).items()})
        cur["modules"] = cards_runtime.resolve(self.card(), mods)
        return cardbuild.save_shop(self.dir, cur)["modules"]

    def set_password(self, old, new):
        cur = self.shop()
        h = cur.get("admin", {}).get("password_hash")
        if h and not cardbuild.verify_password(old, h):
            raise PermissionError("The current password is wrong.")
        cur["admin"] = {"password_hash": cardbuild.hash_password(new)}
        cardbuild.save_shop(self.dir, cur)
        self.sessions.clear()

    # ------------------------------------------------------------ bookings
    def book(self, b):
        self.on("booking_request", "auto_booking")
        shop = self.shop()
        mode = "instant" if shop["modules"].get("auto_booking") else "request"
        ref = (b.get("referral_code") or "").strip().upper()
        if ref:
            self.on("referrals")
            if not self.referrals.valid(ref):
                raise EngineError("That referral code isn't recognised.")
        provider = self.pay_provider() if shop["modules"].get("deposits") else ""
        if mode == "instant" and shop["modules"].get("deposits") and not provider:
            svc = self.booking.service(str(b.get("service_id") or ""))
            if self.booking.deposit_needed(svc, b.get("phone", "")):
                mode = "request"          # no payment firm connected: the shop confirms and takes the deposit itself
        bk = self.booking.create(b, mode)
        if ref:
            self.referrals.use(ref, bk["name"], bk["id"])
        self.analytics.hit("book_sent")
        out = {k: bk[k] for k in ("ref", "status", "date", "start", "end", "service_name", "staff_id", "hold_until")}
        out["ics_url"] = f"/api/booking/{bk['ref']}.ics"
        if bk["status"] == "held":
            out["deposit"] = bk["deposit"]["amount"]
            r = self.cm.run(SCOPE, provider, "deposit_link", {"ref": bk["ref"], "name": bk["service_name"] or "",
                                                             "price": bk["deposit"]["amount"],
                                                             "callback_url": shop.get("public_url", "").rstrip("/") + "/api/pay/sumup"
                                                             if shop.get("public_url") else ""})
            if r.get("ok") and (r.get("result") or {}).get("url"):
                res = r["result"]
                self.booking.attach_payment(bk["id"], provider, res["url"], res.get("id") or "")
                out["pay_link"] = res["url"]
            else:
                out["pay_problem"] = ("We couldn't make the payment link just now. Your time is held for a few "
                                      "minutes - please call or WhatsApp the shop to pay the deposit.")
        elif "patch test needed - salon to check" in bk.get("flags", []):
            out["note"] = "This service needs a patch test. The salon will check yours before confirming."
        elif bk["deposit"].get("amount") and bk["status"] == "requested":
            out["note"] = (f"This service needs a £{bk['deposit']['amount']} deposit. "
                           "The shop will tell you how to pay it when they confirm your time.")
        return out

    def handle_payment(self, provider, raw, headers):
        """A payment firm's message. Checked first; only then can it confirm a booking."""
        if not self.cm:
            raise PermissionError("Payments aren't set up.")
        from connectors import payments
        creds = self.cm.store.creds(SCOPE, provider)
        if provider == "stripe":
            ev = payments.verify_stripe(raw, headers.get("Stripe-Signature", ""), creds.get("webhook_secret", ""))
            got = payments.stripe_outcome(ev)
        elif provider == "square":
            ev = payments.verify_square(raw, headers.get("x-square-hmacsha256-signature", ""),
                                        creds.get("signature_key", ""), creds.get("notification_url", ""))
            got = payments.square_outcome(ev)
        elif provider == "sumup":
            cid = str((json.loads(raw.decode("utf-8") or "{}") or {}).get("id") or "")
            r = self.cm.run(SCOPE, "sumup", "checkout_status", {"id": cid})   # never trust the message itself
            st = (r.get("result") or {}).get("status") if r.get("ok") else None
            got = (cid, st == "PAID", f"sumup-{cid}-{st}") if st in ("PAID", "FAILED", "EXPIRED") else None
        else:
            raise KeyError("Not found")
        if not got:
            return {"ok": True, "ignored": True}
        link_id, paid, event_id = got
        bk = self.booking.find_by_payment(provider, link_id)
        if not bk:
            return {"ok": True, "ignored": True, "why": "no booking for that payment"}
        res = self.booking.payment_result(bk["id"], paid, source=provider, event_id=event_id)
        return {"ok": True, "result": res["result"]}

    def mark_done(self, bid, price_paid):
        b = self.booking.set_status(bid, "done", price_paid)
        if price_paid and b.get("staff_id") and self.shop()["modules"].get("rota"):
            self.rota.add_takings(b["staff_id"], b["date"], price_paid, "service", b["id"])
        return b


def admin_view(shop):
    s = dict(shop)
    s["admin"] = {"password_set": bool(shop.get("admin", {}).get("password_hash"))}
    return s


def make_handler(app: App):
    class H(BaseHTTPRequestHandler):
        server_version = "ShopApp/2.0"

        def log_message(self, *a):
            pass

        def _send(self, code, body, ctype="application/json; charset=utf-8", extra=None):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "same-origin")
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
            if n > 4_000_000:
                raise ValueError("Too much data sent.")
            return json.loads(self.rfile.read(n).decode("utf-8")) if n else {}

        def _q(self):
            return {k: v[0] for k, v in parse_qs(urlparse(self.path).query).items()}

        def _guard(self, fn):
            try:
                r = fn()
                if isinstance(r, tuple):
                    return self._send(*r)
                return self._json(200, r)
            except Off as e:
                return self._json(404, {"message": str(e), "switched_off": True})
            except PermissionError as e:
                return self._json(403, {"message": str(e)})
            except booking.SlotTaken as e:
                return self._json(409, {"message": str(e), "alternatives": e.alternatives, "slot_taken": True})
            except (EngineError, ValueError, KeyError, TypeError) as e:
                return self._json(400, {"message": str(e)})
            except Exception as e:  # connector errors etc.
                code = getattr(e, "code", 500)
                return self._json(code if isinstance(code, int) and 400 <= code < 600 else 500, {"message": str(e)})

        # ---------------------------------------------------------- GET
        def do_GET(self):
            path = unquote(urlparse(self.path).path)
            q = self._q()
            ip = self.client_address[0]
            if path == "/api/admin/me":
                return self._json(200, {"logged_in": app.authed(self._tok())})
            if path.startswith("/api/admin/"):
                if not app.authed(self._tok()):
                    return self._json(401, {"message": "Please log in."})
                return self._guard(lambda: self.admin_get(path[len("/api/admin/"):].split("/"), q))
            if path.startswith("/api/"):
                return self._guard(lambda: self.public_get(path[len("/api/"):].split("/"), q, ip))
            if path == "/admin":                      # trailing slash so admin.css / admin.js load
                self.send_response(301)
                self.send_header("Location", "/admin/")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            if path == "/admin/":
                return self._file(HERE / "admin" / "index.html")
            if path.startswith("/admin/"):
                return self._file(HERE / "admin" / path[len("/admin/"):], HERE / "admin")
            if path in ("/queue", "/queue/"):
                return self._file(HERE / "site" / "queue.html")
            rel = path.lstrip("/") or "index.html"
            return self._file(HERE / "site" / rel, HERE / "site")

        def public_get(self, r, q, ip):
            if r == ["days"]:
                app.on("booking_request", "auto_booking")
                return {"days": app.booking.open_days(21, q.get("branch", "")), "mode": "instant" if app.shop()["modules"].get("auto_booking") else "request"}
            if r == ["slots"]:
                app.on("auto_booking")
                return app.booking.slots(q.get("service", ""), q.get("date", ""), q.get("staff", "any"), q.get("branch", ""))
            if len(r) == 2 and r[0] == "booking":
                app.throttle(ip, "booking-status")
                if r[1].endswith(".ics"):
                    b = app.booking.get(r[1][:-4])
                    return (200, calendar.ics(app.shop(), b).encode(), "text/calendar; charset=utf-8",
                            {"Content-Disposition": f'attachment; filename="booking-{b["ref"]}.ics"'})
                return app.booking.public_status(r[1])
            if r == ["queue", "board"]:
                app.on("walkin_queue")
                return app.queue.board()
            if len(r) == 3 and r[:2] == ["queue", "ticket"]:
                app.on("walkin_queue")
                return app.queue.ticket(r[2])
            if len(r) == 2 and r[0] == "loyalty":
                app.on("loyalty")
                app.throttle(ip, "loyalty", 20)
                app.analytics.hit("loyalty_check")
                return app.loyalty.public_view(r[1])
            if len(r) == 2 and r[0] == "voucher":
                app.on("vouchers")
                app.throttle(ip, "voucher", 20)
                app.analytics.hit("voucher_check")
                v = app.vouchers.check(r[1])
                return {k: v[k] for k in ("balance", "expires", "valid", "expired")}
            if r == ["stock"]:
                app.on("retail")
                return app.retail.public_stock()
            raise KeyError("Not found")

        def admin_get(self, r, q):
            today = app.now().date()
            if r == ["shop"]:
                return admin_view(app.shop())
            if r == ["card"]:
                card = app.card()
                return {"card": {k: card[k] for k in ("card_id", "title", "version", "status", "presets", "variants",
                                                      "content_schema", "service_options", "record_note")},
                        "modules": cards_runtime.catalogue(card), "on": app.shop()["modules"],
                        "today": today.isoformat()}
            if r == ["bookings"]:
                app.booking.expire_holds()
                return {"bookings": app.booking.list(q.get("from", (today - timedelta(days=7)).isoformat()), q.get("to", "")),
                        "clashes": app.booking.clashes(), "alerts": app.booking.alerts(),
                        "pay_provider": app.pay_provider()}
            if r == ["alerts"]:
                return {"alerts": app.booking.alerts()}
            if r == ["reminders"]:
                app.on("reminders")
                day = q.get("date") or (today + timedelta(days=1)).isoformat()
                return {"date": day, "items": messages.reminder_links(app.shop(), app.booking.list(day, day, "confirmed"))}
            if r == ["review-requests"]:
                app.on("review_requests")
                shop = app.shop()
                done = app.booking.list((today - timedelta(days=7)).isoformat(), today.isoformat(), "done")
                return {"review_link": messages.google_review_link(shop.get("google_place_id", "")),
                        "items": [{"booking": b["id"], "name": b["name"], "text": messages.review_text(shop, b),
                                   "whatsapp_link": messages.wa_link(b["phone"], messages.review_text(shop, b))} for b in done]}
            if r == ["queue"]:
                app.on("walkin_queue")
                return {"tickets": app.queue.admin_list(), "board": app.queue.board()}
            if r == ["loyalty"]:
                app.on("loyalty")
                return {"cards": app.loyalty.all(), "rules": app.loyalty.rules()}
            if r == ["vouchers"]:
                app.on("vouchers")
                return {"vouchers": app.vouchers.all()}
            if r == ["packages"]:
                app.on("packages")
                return {"plans": app.packages.plans(), "sold": app.packages.all()}
            if r == ["products"]:
                app.on("retail")
                return {"products": app.retail.products()}
            if r == ["clients"]:
                app.on("client_records")
                return {"clients": app.clients.all(), "due": app.clients.due_patch_tests(), "consent_text": app.clients.consent_text()}
            if len(r) == 3 and r[:2] == ["clients", "export"]:
                app.on("client_records")
                return app.clients.export(r[2])
            if r == ["rota"]:
                app.on("rota")
                f = q.get("from") or (today - timedelta(days=today.weekday())).isoformat()
                t = q.get("to") or (date.fromisoformat(f) + timedelta(days=6)).isoformat()
                return {"from": f, "to": t, "shifts": app.rota.week(f, t), "commission": app.rota.commission(f, t)}
            if r == ["referrals"]:
                app.on("referrals")
                return {"codes": app.referrals.all()}
            if r == ["analytics"]:
                app.on("analytics")
                return app.analytics.summary(int(q.get("days") or 30))
            if r == ["connectors"]:
                return app.cm.list(SCOPE) if app.cm else []
            raise KeyError("Not found")

        def _file(self, f, root=None):
            f = f.resolve()
            root = (root or f.parent).resolve()
            if not f.is_file() or (root not in f.parents and f != root):
                return self._send(404, b"Not found", "text/plain")
            ctype = mimetypes.guess_type(str(f))[0] or "application/octet-stream"
            if f.suffix == ".webmanifest":
                ctype = "application/manifest+json"
            if f.suffix == ".svg":
                ctype = "image/svg+xml"
            if ctype.startswith("text/") or ctype.endswith(("javascript", "json")):
                ctype += "; charset=utf-8"
            extra = {"Cache-Control": "no-cache"} if f.name in ("sw.js", "content.json", "index.html") else {}
            self._send(200, f.read_bytes(), ctype, extra)

        # --------------------------------------------------------- POST
        def do_POST(self):
            path = unquote(urlparse(self.path).path)
            ip = self.client_address[0]

            def run():
                if path.startswith("/api/pay/"):
                    app.throttle(ip, "pay", 60)
                    n = int(self.headers.get("Content-Length") or 0)
                    if n > 1_000_000:
                        raise ValueError("Too much data sent.")
                    return app.handle_payment(path[len("/api/pay/"):], self.rfile.read(n) if n else b"", self.headers)
                b = self._body()
                if path == "/api/login":
                    tok = app.login(b.get("password", ""), ip)
                    return (200, json.dumps({"ok": True}).encode(), "application/json",
                            {"Set-Cookie": f"shop_session={tok}; HttpOnly; SameSite=Strict; Path=/; Max-Age={SESSION_HOURS * 3600}"})
                if path == "/api/logout":
                    app.sessions.pop(self._tok(), None)
                    return (200, b'{"ok":true}', "application/json", {"Set-Cookie": "shop_session=; Path=/; Max-Age=0"})
                if path.startswith("/api/admin/"):
                    if not app.authed(self._tok()):
                        return (401, json.dumps({"message": "Please log in."}).encode(), "application/json")
                    return self.admin_post(path[len("/api/admin/"):].split("/"), b)
                return self.public_post(path[len("/api/"):].split("/"), b, ip)
            return self._guard(run)

        def public_post(self, r, b, ip):
            if r == ["book"]:
                app.throttle(ip, "book", 10)
                return app.book(b)
            if len(r) == 3 and r[0] == "booking" and r[2] == "cancel":
                app.throttle(ip, "cancel", 10)
                bk = app.booking.cancel_by_customer(r[1], b.get("phone", ""))
                return {"ref": bk["ref"], "status": bk["status"]}
            if r == ["queue", "join"]:
                app.on("walkin_queue")
                app.throttle(ip, "queue", 6)
                app.analytics.hit("queue_join")
                return app.queue.join(b.get("name", ""), b.get("service_id", ""), b.get("barber", "any"), b.get("phone", ""))
            if r == ["queue", "leave"]:
                app.on("walkin_queue")
                return app.queue.leave(b.get("token", ""))
            if r == ["hit"]:
                app.throttle(ip, "hit", 120)
                return {"ok": app.analytics.hit(str(b.get("event", "")))} if app.shop()["modules"].get("analytics") else {"ok": False}
            raise KeyError("Not found")

        def admin_post(self, r, b):
            if r == ["shop"]:
                return {"ok": True, "shop": admin_view(app.save_shop(b))}
            if r == ["modules"]:
                return {"ok": True, "on": app.set_modules(b.get("modules") or {})}
            if r == ["image"]:
                return {"path": cardbuild.save_image(app.dir, b.get("data", ""))}
            if r == ["password"]:
                app.set_password(b.get("old", ""), b.get("new", ""))
                return {"ok": True, "message": "Password changed. Please log in again."}
            # bookings
            if r == ["bookings"]:
                return app.booking.create(dict(b, accept_policy=True), "instant" if b.get("staff_id", "any") != "any" or app.shop()["modules"].get("auto_booking") else "request")
            if len(r) == 3 and r[0] == "bookings":
                bid, act = r[1], r[2]
                if act == "confirm":
                    return app.booking.confirm(bid, b.get("staff_id", ""))
                if act == "move":
                    return app.booking.move(bid, b.get("date", ""), b.get("time", ""), b.get("staff_id", ""))
                if act == "done":
                    return app.mark_done(bid, b.get("price_paid"))
                if act in ("cancelled", "no_show", "declined"):
                    return app.booking.set_status(bid, act, reason=b.get("reason", ""))
                if act == "paid":                 # the owner took the deposit by hand (cash, card reader, bank)
                    return app.booking.payment_result(bid, True, source="owner")
                if act == "payment-failed":
                    return app.booking.payment_result(bid, False, source="owner")
                if act == "alert-done":
                    return {"cleared": app.booking.clear_alert(bid)}
                if act == "gcal":
                    app.on("gcal")
                    bk = app.booking.get(bid)
                    staff = next((s["name"] for s in app.shop()["staff"] if s["id"] == bk["staff_id"]), "")
                    return app.cm.run(SCOPE, "google_calendar", "add_event", {"event": calendar.google_event(app.shop(), bk, staff)})
            if r == ["sms"]:
                app.on("reminders", "review_requests")
                return app.cm.run(SCOPE, "twilio_sms", "send", {"to": b.get("to", ""), "text": b.get("text", "")})
            # queue
            if r == ["queue", "call"]:
                app.on("walkin_queue")
                return app.queue.call_next(b.get("chair", ""))
            if r == ["queue", "skip"]:
                app.on("walkin_queue")
                return app.queue.skip(b.get("no", ""))
            if r == ["queue", "status"]:
                app.on("walkin_queue")
                return app.queue.set_status(b.get("no", ""), b.get("status", ""))
            if r == ["queue", "open"]:
                app.on("walkin_queue")
                return app.queue.set_open(bool(b.get("on")))
            if r == ["queue", "add"]:
                app.on("walkin_queue")
                return app.queue.join(b.get("name", ""), b.get("service_id", ""), b.get("barber", "any"), b.get("phone", ""))
            # loyalty / vouchers / packages
            if r and r[0] == "loyalty":
                app.on("loyalty")
                if r[1:] == ["new"]:
                    return app.loyalty.new_card(b.get("name", ""), b.get("phone", ""))
                if r[1:] == ["stamp"]:
                    return app.loyalty.stamp(b.get("code", ""), int(b.get("n") or 1), b.get("note", ""))
                if r[1:] == ["redeem"]:
                    return app.loyalty.redeem(b.get("code", ""))
            if r and r[0] == "vouchers":
                app.on("vouchers")
                if r[1:] == ["issue"]:
                    return app.vouchers.issue(b.get("amount"), b.get("buyer", ""), b.get("for", ""), b.get("months"), bool(b.get("paid", True)))
                if r[1:] == ["redeem"]:
                    return app.vouchers.redeem(b.get("code", ""), b.get("amount"))
                if r[1:] == ["void"]:
                    return app.vouchers.void(b.get("code", ""))
            if r and r[0] == "packages":
                app.on("packages")
                if r[1:] == ["sell"]:
                    return app.packages.sell(b.get("plan_id", ""), b.get("client", ""), b.get("phone", ""))
                if r[1:] == ["use"]:
                    return app.packages.use(b.get("code", ""))
            if r and r[0] == "products":
                app.on("retail")
                act = r[1] if len(r) > 1 else ""
                if act == "receive":
                    return app.retail.receive(b.get("id", ""), int(b.get("qty") or 0))
                if act == "sell":
                    res = app.retail.sell(b.get("id", ""), int(b.get("qty") or 1))
                    if b.get("staff_id") and b.get("amount") and app.shop()["modules"].get("rota"):
                        app.rota.add_takings(b["staff_id"], app.now().date().isoformat(), b["amount"], "retail", b.get("id", ""))
                    return res
                if act == "count":
                    return app.retail.set_count(b.get("id", ""), int(b.get("qty") or 0))
                if act == "barcode":
                    if not app.cm:
                        raise ValueError("Connectors folder is missing.")
                    r1 = app.cm.run(SCOPE, "open_beauty_facts", "barcode", {"barcode": b.get("barcode", "")})
                    if not (r1.get("result") or {}).get("found"):
                        r2 = app.cm.run(SCOPE, "open_food_facts", "barcode", {"barcode": b.get("barcode", "")})
                        if (r2.get("result") or {}).get("found"):
                            return r2["result"]
                    return r1.get("result") or {"found": False, "message": r1.get("message") or "Lookup didn't work just now - type the details in."}
            if r and r[0] == "clients":
                app.on("client_records")
                if r[1:] == ["save"]:
                    return app.clients.save(b)
                if r[1:] == ["patch-test"]:
                    return app.clients.add_patch_test(b.get("id", ""), b.get("product", ""), b.get("result", ""), b.get("tested_on", ""))
                if len(r) == 3 and r[1] == "erase":
                    return app.clients.erase(r[2])
            if r and r[0] == "rota":
                app.on("rota")
                if r[1:] == ["shift"]:
                    return app.rota.add_shift(b.get("staff_id", ""), b.get("date", ""), b.get("start", ""), b.get("end", ""))
                if r[1:] == ["remove"]:
                    return app.rota.remove_shift(b.get("id", ""))
                if r[1:] == ["takings"]:
                    return app.rota.add_takings(b.get("staff_id", ""), b.get("date", ""), b.get("amount"), b.get("kind", "service"))
            if r == ["referrals", "new"]:
                app.on("referrals")
                return app.referrals.create(b.get("owner", ""), b.get("phone", ""))
            if r == ["suppliers", "search"]:
                app.on("supplier_finder")
                shop = app.shop()
                settings = {"max_web_queries": 4}
                if app.cm:
                    brave = app.cm.store.creds(SCOPE, "brave_search").get("api_key")
                    if brave:
                        settings["brave_api_key"] = brave
                return suppliers.run(app.card().get("supplier_search", {}), b.get("postcode") or shop.get("postcode", ""),
                                     settings, app.fetcher, None, int(b.get("radius_m") or 5000), b.get("text", ""))
            if r == ["suppliers", "save"]:
                app.on("supplier_finder")
                cur = app.shop()
                item = {k: str((b.get("result") or {}).get(k) or "")[:400] for k in ("title", "url", "address", "phone", "source", "checked_at", "label")}
                if not item["title"] or not item["url"].startswith(("http://", "https://")):
                    raise ValueError("A supplier needs a title and a web link.")
                if all(s.get("url") != item["url"] for s in cur.get("suppliers", [])):
                    cur["suppliers"] = cur.get("suppliers", []) + [item]
                    cardbuild.save_shop(app.dir, cur)
                return {"ok": True, "suppliers": app.shop()["suppliers"]}
            # connectors
            if not app.cm:
                raise ValueError("Connectors folder (lib/connectors) is missing.")
            if len(r) == 3 and r[0] == "connectors":
                cid, act = r[1], r[2]
                if act == "credentials":
                    return {"ok": True, "saved": app.cm.store.save_creds(SCOPE, cid, b.get("values") or {})}
                if act == "test":
                    return app.cm.test(SCOPE, cid)
                if act == "enable":
                    return {"enabled": app.cm.store.set_enabled(SCOPE, cid, bool(b.get("on")))}
            raise KeyError("Not found")

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
        shop["admin"] = {"password_hash": cardbuild.hash_password(pw)}
        cardbuild.save_shop(app.dir, shop)
        print("Password saved (only a scrambled version is stored).")
        return
    if a.build:
        cardbuild.save_shop(app.dir, app.shop())
        print("Rebuilt the public files in", app.dir / "site")
        return
    httpd = ThreadingHTTPServer((a.host, a.port), make_handler(app))
    print(f"{app.shop()['name']} — shop app running.")
    print(f"  Customers:   http://localhost:{a.port}/")
    print(f"  Owner admin: http://localhost:{a.port}/admin")
    print(f"  Queue board: http://localhost:{a.port}/queue   (if the walk-in queue is switched on)")
    print("Press Ctrl+C to stop.")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
