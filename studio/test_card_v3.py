"""Salon / barber card v3: the shop app server with holds, deposits (Stripe / Square / SumUp with a FAKE
network and made-up secrets), refund alerts, the walk-in queue, the static WhatsApp copy and the export.
python3 -m pytest studio/test_card_v3.py -q"""
import base64
import hashlib
import hmac
import json
import sys
import threading
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timedelta
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import card_app  # noqa: E402
import cards  # noqa: E402
import demo_content  # noqa: E402

SAT = "2026-10-03"
WEEK = [{"day": d, "open": "09:00", "close": "18:00"} for d in ("mon", "tue", "wed", "thu", "fri", "sat")] + [{"day": "sun", "closed": True}]
CALLS = []


class Clock:
    def __init__(self):
        self.t = datetime(2026, 10, 1, 9, 0)

    def __call__(self):
        return self.t


def fake(url, method="GET", headers=None, data=None, timeout=20, contact=""):
    CALLS.append((method, url, data))
    if url.endswith("/v1/prices"):
        return 200, {}, b'{"id": "price_1"}'
    if url.endswith("/v1/payment_links"):
        return 200, {}, json.dumps({"id": f"plink_{len(CALLS)}", "url": f"https://buy.stripe.com/test_{len(CALLS)}"}).encode()
    if url.endswith("/v2/locations"):
        return 200, {}, b'{"locations": [{"id": "L1", "name": "Demo"}]}'
    if url.endswith("/v2/online-checkout/payment-links"):
        return 200, {}, b'{"payment_link": {"id": "PL1", "order_id": "ORDER1", "url": "https://square.link/u/demo"}}'
    if url.endswith("/v0.1/checkouts") and method == "POST":
        return 200, {}, b'{"id": "chk1", "status": "PENDING", "hosted_checkout_url": "https://checkout.sumup.com/pay/chk1"}'
    if "openbeautyfacts.org/api/v2/product/5201279101411" in url:
        return 200, {}, json.dumps({"status": 1, "product": {"product_name": "Hydra shampoo", "brands": "APIVITA", "quantity": "500ml"}}).encode()
    if "facts.org/api/v2/product/" in url:
        from netutil import NetError
        raise NetError("http", "The service answered with an error (404).", 404, "")
    if "/v0.1/checkouts/chk1" in url:
        return 200, {}, b'{"id": "chk1", "status": "PAID"}'
    return 200, {}, b"{}"


@pytest.fixture
def made(tmp_path):
    card = cards.load_card("CARD-HAIR-01")
    shop = demo_content.sample_shop(card, cards.preset(card, "luxury"),
                                    {"auto_booking": True, "deposits": True, "client_records": True, "walkin_queue": True})
    shop["hours"] = WEEK
    shop["whatsapp"] = "07700900123"
    shop["services"][2].update(deposit="30", needs_patch_test=False, segments="45 active, 45 processing, 30 active")
    shop["staff"][0]["breaks"] = "13:00-13:30"
    card_app.generate("CARD-HAIR-01", shop, tmp_path / "app", password="test-pass-1")
    sys.path.insert(0, str(tmp_path / "app"))
    sys.path.insert(0, str(tmp_path / "app" / "lib"))
    import importlib.util
    spec = importlib.util.spec_from_file_location("shop_server_v3", tmp_path / "app" / "server.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    clock = Clock()
    app = mod.App(tmp_path / "app", fetcher=fake, now=clock)
    return app, mod, clock, tmp_path / "app"


def book(app, svc="v3", who="s1", time_="10:00", phone="07700900501"):
    return app.book({"service_id": svc, "staff_id": who, "date": SAT, "time": time_, "name": "Client (demo)", "phone": phone})


def stripe_on(app):
    app.cm.store.save_creds("shop", "stripe", {"secret_key": "sk_test_fake", "webhook_secret": "whsec_fake"})
    app.cm.store.set_enabled("shop", "stripe", True)


def stripe_msg(link, paid=True, secret="whsec_fake", ts=None, eid="evt_1"):
    body = json.dumps({"id": eid, "type": "checkout.session.completed",
                       "data": {"object": {"payment_link": link, "payment_status": "paid" if paid else "unpaid"}}}).encode()
    ts = ts or int(time.time())
    sig = hmac.new(secret.encode(), f"{ts}.".encode() + body, hashlib.sha256).hexdigest()
    return body, {"Stripe-Signature": f"t={ts},v1={sig}"}


def test_card_is_valid_and_honest():
    card = cards.load_card("CARD-HAIR-01")
    assert cards.validate_card(card) == []
    mods = {m["id"]: m for m in card["modules"]}
    assert mods["deposits"]["status"] == "code-ready-needs-key" and mods["gcal"]["status"] == "code-ready-needs-key"
    assert mods["platform_links"]["status"] == "link-only" and "Approved" not in card["status"]
    assert all("needs_server" in m for m in card["modules"])
    assert card["booking_defaults"]["hold_minutes"] == 10


def test_no_payment_firm_means_request_not_a_fake_hold(made):
    app, *_ = made
    r = book(app)
    assert r["status"] == "requested" and "pay_link" not in r


def test_held_then_signed_stripe_message_confirms(made):
    app, *_ = made
    stripe_on(app)
    r = book(app)
    assert r["status"] == "held" and r["pay_link"].startswith("https://buy.stripe.com/") and r["deposit"] == "30"
    bk = app.booking.get(r["ref"])
    body, h = stripe_msg(bk["deposit"]["link_id"])
    assert app.handle_payment("stripe", body, h)["result"] == "confirmed"
    assert app.booking.get(r["ref"])["status"] == "confirmed"


def test_forged_or_old_stripe_message_is_refused(made):
    app, *_ = made
    stripe_on(app)
    r = book(app)
    link = app.booking.get(r["ref"])["deposit"]["link_id"]
    body, h = stripe_msg(link, secret="whsec_WRONG")
    with pytest.raises(Exception, match="doesn't match"):
        app.handle_payment("stripe", body, h)
    body, h = stripe_msg(link, ts=int(time.time()) - 3600)
    with pytest.raises(Exception, match="too old"):
        app.handle_payment("stripe", body, h)
    assert app.booking.get(r["ref"])["status"] == "held"


def test_late_stripe_payment_after_resale_gives_refund_alert(made):
    app, mod, clock, _ = made
    stripe_on(app)
    r = book(app)
    link = app.booking.get(r["ref"])["deposit"]["link_id"]
    clock.t += timedelta(minutes=12)
    other = book(app, svc="v1", time_="10:00", phone="07700900502")   # 60-min cut, no deposit
    assert other["status"] == "confirmed"
    body, h = stripe_msg(link, eid="evt_late")
    assert app.handle_payment("stripe", body, h)["result"] == "refund due - owner alerted"
    assert app.booking.clashes() == [] and len(app.booking.alerts()) == 1


def test_square_signed_message_confirms(made):
    app, *_ = made
    app.cm.store.save_creds("shop", "square", {"access_token": "EAAA_fake", "signature_key": "sigkey",
                                                "notification_url": "https://shop.example/api/pay/square"})
    app.cm.store.set_enabled("shop", "square", True)
    r = book(app)
    assert r["status"] == "held" and r["pay_link"] == "https://square.link/u/demo"
    body = json.dumps({"event_id": "sq1", "type": "payment.updated",
                       "data": {"object": {"payment": {"order_id": "ORDER1", "status": "COMPLETED"}}}}).encode()
    sig = base64.b64encode(hmac.new(b"sigkey", b"https://shop.example/api/pay/square" + body, hashlib.sha256).digest()).decode()
    with pytest.raises(Exception):
        app.handle_payment("square", body, {"x-square-hmacsha256-signature": "bad"})
    assert app.handle_payment("square", body, {"x-square-hmacsha256-signature": sig})["result"] == "confirmed"


def test_sumup_message_is_checked_with_sumup_before_confirming(made):
    app, *_ = made
    app.cm.store.save_creds("shop", "sumup", {"api_key": "sup_sk_fake", "merchant_code": "MDEMO"})
    app.cm.store.set_enabled("shop", "sumup", True)
    r = book(app)
    assert r["pay_link"] == "https://checkout.sumup.com/pay/chk1"
    CALLS.clear()
    res = app.handle_payment("sumup", b'{"event_type": "CHECKOUT_STATUS_CHANGED", "id": "chk1"}', {})
    assert res["result"] == "confirmed" and any("/v0.1/checkouts/chk1" in c[1] for c in CALLS)


def test_owner_can_mark_deposit_paid_by_hand(made):
    app, *_ = made
    stripe_on(app)
    r = book(app)
    bk = app.booking.get(r["ref"])
    assert app.booking.payment_result(bk["id"], True, source="owner")["booking"]["status"] == "confirmed"


def test_processing_time_lets_a_short_service_fit(made):
    app, *_ = made
    stripe_on(app)
    r = book(app)                                                         # colour 10:00, processing 10:45-11:30
    app.booking.payment_result(app.booking.get(r["ref"])["id"], True)
    times = [s["time"] for s in app.booking.slots("v5", SAT, "s1")["slots"]]   # 30-min men's cut
    assert "10:45" in times and "11:30" not in times


def test_http_slot_taken_gives_409_with_other_times(made):
    app, mod, clock, _ = made
    srv = ThreadingHTTPServer(("127.0.0.1", 0), mod.make_handler(app))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"

    def post(path, obj):
        rq = urllib.request.Request(base + path, data=json.dumps(obj).encode(), headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(rq) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())
    try:
        b = {"service_id": "v1", "staff_id": "s1", "date": SAT, "time": "11:00", "name": "A (demo)", "phone": "07700900601"}
        assert post("/api/book", b)[1]["status"] == "confirmed"
        code, j = post("/api/book", dict(b, phone="07700900602"))
        assert code == 409 and j["slot_taken"] and j["alternatives"]
        code, j = post("/api/pay/stripe", {"id": "x"})
        assert code in (400, 403, 500) and "status" not in j
    finally:
        srv.shutdown()


def test_queue_skip_and_board_through_the_app(made):
    app, mod, clock, _ = made
    clock.t = datetime(2026, 10, 3, 10, 0)
    a = app.queue.join("Tom", "v1", "any", "07000000001")
    app.queue.join("Ali", "v1", "any", "07000000002")
    c = app.queue.call_next("s1")
    assert c["no"] == a["no"]
    assert app.queue.skip(a["no"])["new_position"] == 2                    # only one other waiting
    assert app.queue.board()["checked_at"].startswith("2026-10-03T10:00")


def test_export_zip_has_no_secrets_private_data_or_cache(made, tmp_path):
    app, mod, clock, app_dir = made
    stripe_on(app)
    book(app)
    (app_dir / "lib" / "__pycache__").mkdir(exist_ok=True)
    (app_dir / "lib" / "__pycache__" / "x.pyc").write_bytes(b"x")
    r = card_app.export_zip(app_dir, tmp_path / "out.zip")
    names = zipfile.ZipFile(tmp_path / "out.zip").namelist()
    assert not [n for n in names if "secrets" in n or "__pycache__" in n or n.endswith("bookings.json")]
    assert any(n.endswith("data/private/README.txt") for n in names)
    assert "sk_test_fake" not in b"".join(zipfile.ZipFile(tmp_path / "out.zip").read(n) for n in names).decode("latin-1")


def test_demo_clock_only_for_demo_shops(made, monkeypatch):
    app, mod, clock, app_dir = made
    monkeypatch.setenv("SHOP_DEMO_NOW", "2026-10-24T10:30")
    a2 = mod.App(app_dir, fetcher=fake)
    assert a2.now().strftime("%Y-%m-%d %H:%M") == "2026-10-24 10:30"
    shop = json.loads((app_dir / "data" / "shop.json").read_text())
    shop["demo"] = False
    (app_dir / "data" / "shop.json").write_text(json.dumps(shop))
    a3 = mod.App(app_dir, fetcher=fake)
    from engines.store import now_local
    assert abs((a3.now() - now_local()).total_seconds()) < 5          # real shops always use the real London time


def test_breaks_and_segments_are_checked_when_saving(made):
    app, mod, clock, app_dir = made
    shop = app.shop()
    shop["staff"][0]["breaks"] = "lunchtime"
    with pytest.raises(ValueError, match="13:00-13:30"):
        app.save_shop(shop)
    shop = app.shop()
    shop["services"][0]["segments"] = "10 active, 10 processing"
    with pytest.raises(ValueError, match="add up"):
        app.save_shop(shop)
    assert app.shop()["staff"][0]["breaks"] == [{"start": "13:00", "end": "13:30", "flexible": True}]


def test_barcode_lookup_found_and_not_found(made):
    app, mod, clock, app_dir = made
    srv = ThreadingHTTPServer(("127.0.0.1", 0), mod.make_handler(app))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    app.set_modules({"retail": True})
    try:
        rq = urllib.request.Request(base + "/api/login", data=b'{"password": "test-pass-1"}', headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(rq) as r:
            cookie = r.headers["Set-Cookie"].split(";")[0]

        def look(code):
            rq = urllib.request.Request(base + "/api/admin/products/barcode", data=json.dumps({"barcode": code}).encode(),
                                        headers={"Content-Type": "application/json", "Cookie": cookie}, method="POST")
            with urllib.request.urlopen(rq) as r:
                return json.loads(r.read())
        assert look("5201279101411")["brands"] == "APIVITA"
        miss = look("3600523351640")
        assert miss["found"] is False and "type the details in" in miss["message"]
    finally:
        srv.shutdown()
