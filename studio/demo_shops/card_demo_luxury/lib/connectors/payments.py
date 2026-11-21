"""Card payments: Stripe, Square, SumUp. Code written against official docs (checked 2026-09-26,
deposit / webhook parts re-checked 2026-10-18). Need the owner's own keys. Not run against the
real services here: we have no keys. The signature checks are tested with made-up secrets.

How a deposit is confirmed (the app never trusts the customer's own phone for this):
  * Stripe - Stripe sends "checkout.session.completed" to /api/pay/stripe. We check the
    Stripe-Signature header ("t=...,v1=...": HMAC-SHA256 of "t.body" with the endpoint's
    whsec_ secret; reject if older than 5 minutes) and match the payment link id.
  * Square - Square sends "payment.updated" to /api/pay/square. We check the
    x-square-hmacsha256-signature header (base64 HMAC-SHA256 of notification URL + raw
    body, with the subscription's signature key) and match the order id.
  * SumUp - SumUp posts the checkout id to /api/pay/sumup. The message itself is not
    trusted: we ask SumUp for that checkout's status (PAID / FAILED / EXPIRED / PENDING).
  * Any shop - the owner can press "Mark deposit paid" in the admin page.
"""
import base64
import hashlib
import hmac
import json
import time
import uuid
from . import Connector, ConnectorError


def _pence(v) -> int:
    try:
        p = round(float(v) * 100)
    except (TypeError, ValueError):
        raise ConnectorError("Price must be a number, e.g. 3.50")
    if p <= 0:
        raise ConnectorError("Price must be more than zero.")
    return p


class Stripe(Connector):
    id = "stripe"
    name = "Stripe (payment links)"
    category = "Payments"
    cost_type = "paid"
    what_it_does = "Makes a 'Pay now' link for a product or deposit. The shop app shows it as a Pay button. Money goes to the owner's own Stripe account."
    credentials = [{"key": "secret_key", "label": "Stripe secret key (sk_test_… to try, sk_live_… for real)", "secret": True, "required": True,
                    "help": "dashboard.stripe.com → Developers → API keys. Use a test key first; a restricted key with Payment Links + Prices write is safer."},
                   {"key": "webhook_secret", "label": "Webhook signing secret (whsec_…) - for deposits", "secret": True, "required": False,
                    "help": "Stripe Workbench → Webhooks → your endpoint (…/api/pay/stripe, event checkout.session.completed) → reveal secret."}]
    docs_url = "https://docs.stripe.com/api/payment-link/create"
    pricing = {"text": "No monthly fee; standard UK cards 1.5% + 20p (from the 25 Sept 2026 fact-check).",
               "url": "https://stripe.com/gb/pricing", "checked": "2026-09-25"}
    status = "code-ready-needs-key"
    status_note = "POST /v1/prices and /v1/payment_links confirmed in Stripe's API reference on 2026-09-26. Works with a free test-mode key; not tested here (no key)."
    actions = {"payment_link": {"label": "Make a payment link", "params": [
        {"key": "name", "label": "What it's for", "example": "Baklava box (1kg)"},
        {"key": "price", "label": "Price in £", "example": "12.50"}]},
        "deposit_link": {"label": "Make a deposit link for a booking", "params": [
            {"key": "ref", "label": "Booking ref", "example": "K7Q2PD"}, {"key": "price", "label": "Deposit in £", "example": "30"}]}}
    shop_features = ["Pay button on products (Stripe payment link)"]
    BASE = "https://api.stripe.com/v1"

    def _h(self):
        self.need("secret_key")
        return {"Authorization": "Bearer " + self.creds["secret_key"]}

    def test_connection(self):
        d = self.get_json(self.BASE + "/balance", headers=self._h())
        mode = "LIVE" if d.get("livemode") else "test"
        return {"ok": True, "message": f"Working: connected to a Stripe account in {mode} mode."}

    def act_payment_link(self, p):
        if not p.get("name"):
            raise ConnectorError("Say what the payment is for.")
        price = self.send_json(self.BASE + "/prices", headers=self._h(), form={
            "currency": "gbp", "unit_amount": _pence(p.get("price")), "product_data[name]": p["name"][:250]})
        link = self.send_json(self.BASE + "/payment_links", headers=self._h(), form={
            "line_items[0][price]": price["id"], "line_items[0][quantity]": 1})
        return {"url": link.get("url"), "id": link.get("id"), "livemode": link.get("livemode")}

    def act_deposit_link(self, p):
        """One payment link per booking, so the payment can be matched back to it."""
        return self.act_payment_link({"name": f"Deposit {p.get('ref', '')} - {p.get('name', '')}"[:250], "price": p.get("price")})


def verify_stripe(body: bytes, header: str, secret: str, tolerance: int = 300, now: float = None) -> dict:
    """Check a Stripe webhook. Returns the event, or raises ConnectorError."""
    if not secret:
        raise ConnectorError("No Stripe webhook secret saved.")
    parts = {}
    for item in (header or "").split(","):
        k, _, v = item.strip().partition("=")
        parts.setdefault(k, []).append(v)
    try:
        ts = int(parts.get("t", [""])[0])
    except ValueError:
        raise ConnectorError("Stripe signature header is missing its time.")
    want = hmac.new(secret.encode(), f"{ts}.".encode() + body, hashlib.sha256).hexdigest()
    if not any(hmac.compare_digest(want, v) for v in parts.get("v1", [])):
        raise ConnectorError("Stripe signature doesn't match.")
    if abs((now or time.time()) - ts) > tolerance:
        raise ConnectorError("Stripe message is too old.")
    return json.loads(body.decode("utf-8"))


def stripe_outcome(event: dict):
    """(payment link id, paid?) from a Stripe event, or None if it isn't about a payment link."""
    obj = (event.get("data") or {}).get("object") or {}
    if event.get("type") == "checkout.session.completed" and obj.get("payment_link"):
        return obj["payment_link"], obj.get("payment_status") == "paid", event.get("id", "")
    if event.get("type") == "checkout.session.async_payment_failed" and obj.get("payment_link"):
        return obj["payment_link"], False, event.get("id", "")
    return None


class Square(Connector):
    id = "square"
    name = "Square"
    category = "Payments"
    cost_type = "paid"
    what_it_does = "Checks the owner's Square account and makes quick 'Pay now' links. Good if the shop already has a Square card reader."
    credentials = [{"key": "access_token", "label": "Square access token", "secret": True, "required": True,
                    "help": "developer.squareup.com → Applications → your app → Credentials. Sandbox token to try first."},
                   {"key": "environment", "label": "sandbox or production", "secret": False, "required": False, "help": "Type sandbox while testing."},
                   {"key": "location_id", "label": "Location ID (optional — first location is used)", "secret": False, "required": False},
                   {"key": "signature_key", "label": "Webhook signature key - for deposits", "secret": True, "required": False,
                    "help": "Developer Console → Webhooks → your subscription (event payment.updated) → Signature key."},
                   {"key": "notification_url", "label": "Webhook notification URL (exactly as typed in Square)", "secret": False, "required": False,
                    "help": "e.g. https://your-shop-address/api/pay/square"}]
    docs_url = "https://developer.squareup.com/reference/square/checkout-api/create-payment-link"
    pricing = {"text": "Free plan £0 a month plus card fees (from the 25 Sept 2026 fact-check).",
               "url": "https://squareup.com/gb/en/pricing", "checked": "2026-09-25"}
    status = "code-ready-needs-key"
    status_note = "GET /v2/locations and POST /v2/online-checkout/payment-links confirmed in Square's reference on 2026-09-26. Not tested here (no token)."
    actions = {"payment_link": {"label": "Make a payment link", "params": [
        {"key": "name", "label": "What it's for", "example": "Cake order deposit"}, {"key": "price", "label": "Price in £", "example": "10"}]},
        "deposit_link": {"label": "Make a deposit link for a booking", "params": [
            {"key": "ref", "label": "Booking ref", "example": "K7Q2PD"}, {"key": "price", "label": "Deposit in £", "example": "30"}]}}
    shop_features = ["Pay button on products (Square payment link)"]
    VERSION = "2026-09-16"   # Square-Version shown in Square's reference on 2026-09-26

    def _base(self):
        env = (self.creds.get("environment") or "production").lower()
        return "https://connect.squareupsandbox.com" if env.startswith("sand") else "https://connect.squareup.com"

    def _h(self):
        self.need("access_token")
        return {"Authorization": "Bearer " + self.creds["access_token"], "Square-Version": self.VERSION}

    def _location(self):
        if self.creds.get("location_id"):
            return self.creds["location_id"]
        locs = self.get_json(self._base() + "/v2/locations", headers=self._h()).get("locations") or []
        if not locs:
            raise ConnectorError("This Square account has no locations.")
        return locs[0]["id"]

    def test_connection(self):
        locs = self.get_json(self._base() + "/v2/locations", headers=self._h()).get("locations") or []
        return {"ok": True, "message": f"Working: {len(locs)} Square location(s): " + ", ".join(l.get("name", "?") for l in locs[:3])}

    def act_payment_link(self, p):
        if not p.get("name"):
            raise ConnectorError("Say what the payment is for.")
        d = self.send_json(self._base() + "/v2/online-checkout/payment-links", headers=self._h(), body={
            "idempotency_key": str(uuid.uuid4()),
            "quick_pay": {"name": p["name"][:255], "price_money": {"amount": _pence(p.get("price")), "currency": "GBP"},
                          "location_id": self._location()}})
        pl = d.get("payment_link") or {}
        return {"url": pl.get("url"), "id": pl.get("id"), "order_id": pl.get("order_id")}

    def act_deposit_link(self, p):
        r = self.act_payment_link({"name": f"Deposit {p.get('ref', '')} - {p.get('name', '')}"[:255], "price": p.get("price")})
        return dict(r, id=r.get("order_id") or r.get("id"))       # Square's payment message carries the order id


def verify_square(body: bytes, header: str, signature_key: str, notification_url: str) -> dict:
    """Check a Square webhook. Returns the event, or raises ConnectorError."""
    if not signature_key or not notification_url:
        raise ConnectorError("No Square signature key / notification URL saved.")
    want = base64.b64encode(hmac.new(signature_key.encode(), notification_url.encode() + body, hashlib.sha256).digest()).decode()
    if not hmac.compare_digest(want, (header or "").strip()):
        raise ConnectorError("Square signature doesn't match.")
    return json.loads(body.decode("utf-8"))


def square_outcome(event: dict):
    pay = (((event.get("data") or {}).get("object") or {}).get("payment")) or {}
    if not pay.get("order_id"):
        return None
    st = pay.get("status")
    if st == "COMPLETED":
        return pay["order_id"], True, event.get("event_id", "")
    if st in ("FAILED", "CANCELED"):
        return pay["order_id"], False, event.get("event_id", "")
    return None


class SumUp(Connector):
    id = "sumup"
    name = "SumUp"
    category = "Payments"
    cost_type = "paid"
    what_it_does = "Checks the owner's SumUp account and creates online checkouts. Many high-street shops already use SumUp card readers."
    credentials = [{"key": "api_key", "label": "SumUp API key (sup_sk_…)", "secret": True, "required": True,
                    "help": "me.sumup.com → Settings → For developers → API keys."},
                   {"key": "merchant_code", "label": "Merchant code (e.g. MK01A8C2)", "secret": False, "required": True}]
    docs_url = "https://developer.sumup.com/api/checkouts/create"
    pricing = {"text": "Price not checked today — see SumUp's UK pricing page.", "url": "https://www.sumup.com/en-gb/pricing/", "checked": None}
    status = "code-ready-needs-key"
    status_note = "GET /v1/merchants/{merchant_code} and POST /v0.1/checkouts confirmed in SumUp's API reference on 2026-09-26. Not tested here (no key)."
    actions = {"checkout": {"label": "Create an online checkout", "params": [
        {"key": "name", "label": "What it's for", "example": "Order 1042"}, {"key": "price", "label": "Price in £", "example": "18.00"}]},
        "deposit_link": {"label": "Make a deposit pay page for a booking", "params": [
            {"key": "ref", "label": "Booking ref", "example": "K7Q2PD"}, {"key": "price", "label": "Deposit in £", "example": "30"}]},
        "checkout_status": {"label": "Check a checkout's status", "params": [{"key": "id", "label": "Checkout id", "example": "4e42…"}]}}
    BASE = "https://api.sumup.com"

    def _h(self):
        self.need("api_key", "merchant_code")
        return {"Authorization": "Bearer " + self.creds["api_key"]}

    def test_connection(self):
        d = self.get_json(f"{self.BASE}/v1/merchants/{self.creds.get('merchant_code', '')}", headers=self._h())
        name = (d.get("business_profile") or {}).get("name") or (d.get("company") or {}).get("name")
        return {"ok": True, "message": f"Working: SumUp merchant {d.get('merchant_code')} {name or ''}".strip()}

    def act_checkout(self, p):
        h = self._h()
        d = self.send_json(self.BASE + "/v0.1/checkouts", headers=h, body={
            "checkout_reference": f"hvt-{int(time.time())}-{uuid.uuid4().hex[:6]}", "amount": _pence(p.get("price")) / 100,
            "currency": "GBP", "merchant_code": self.creds["merchant_code"], "description": (p.get("name") or "")[:255]})
        return {"id": d.get("id"), "status": d.get("status"), "amount": d.get("amount"),
                "note": "SumUp checkouts are paid through SumUp's card widget or hosted page; see SumUp docs."}

    def act_deposit_link(self, p):
        """A SumUp-hosted pay page (hosted_checkout.enabled, per SumUp's reference, checked 2026-10-18).
        return_url = where SumUp tells our server something changed; we then ask for the status."""
        body = {"checkout_reference": f"dep-{p.get('ref', '')}-{uuid.uuid4().hex[:6]}", "amount": _pence(p.get("price")) / 100,
                "currency": "GBP", "merchant_code": self.creds.get("merchant_code", ""),
                "description": f"Deposit {p.get('ref', '')}"[:255], "hosted_checkout": {"enabled": True}}
        if p.get("callback_url"):
            body["return_url"] = p["callback_url"]
        d = self.send_json(self.BASE + "/v0.1/checkouts", headers=self._h(), body=body)
        return {"id": d.get("id"), "url": d.get("hosted_checkout_url"), "status": d.get("status")}

    def act_checkout_status(self, p):
        """PAID / FAILED / EXPIRED / PENDING (SumUp's reference, checked 2026-10-18)."""
        cid = str(p.get("id") or "")
        if not cid or "/" in cid:
            raise ConnectorError("Checkout id missing.")
        d = self.get_json(f"{self.BASE}/v0.1/checkouts/{cid}", headers=self._h())
        return {"id": d.get("id"), "status": d.get("status")}
