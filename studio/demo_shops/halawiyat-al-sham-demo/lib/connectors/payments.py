"""Card payments: Stripe, Square, SumUp. Code written against official docs (checked 2026-09-26). Need the owner's own keys."""
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
                    "help": "dashboard.stripe.com → Developers → API keys. Use a test key first; a restricted key with Payment Links + Prices write is safer."}]
    docs_url = "https://docs.stripe.com/api/payment-link/create"
    pricing = {"text": "No monthly fee; standard UK cards 1.5% + 20p (from the 25 Sept 2026 fact-check).",
               "url": "https://stripe.com/gb/pricing", "checked": "2026-09-25"}
    status = "code-ready-needs-key"
    status_note = "POST /v1/prices and /v1/payment_links confirmed in Stripe's API reference on 2026-09-26. Works with a free test-mode key; not tested here (no key)."
    actions = {"payment_link": {"label": "Make a payment link", "params": [
        {"key": "name", "label": "What it's for", "example": "Baklava box (1kg)"},
        {"key": "price", "label": "Price in £", "example": "12.50"}]}}
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


class Square(Connector):
    id = "square"
    name = "Square"
    category = "Payments"
    cost_type = "paid"
    what_it_does = "Checks the owner's Square account and makes quick 'Pay now' links. Good if the shop already has a Square card reader."
    credentials = [{"key": "access_token", "label": "Square access token", "secret": True, "required": True,
                    "help": "developer.squareup.com → Applications → your app → Credentials. Sandbox token to try first."},
                   {"key": "environment", "label": "sandbox or production", "secret": False, "required": False, "help": "Type sandbox while testing."},
                   {"key": "location_id", "label": "Location ID (optional — first location is used)", "secret": False, "required": False}]
    docs_url = "https://developer.squareup.com/reference/square/checkout-api/create-payment-link"
    pricing = {"text": "Free plan £0 a month plus card fees (from the 25 Sept 2026 fact-check).",
               "url": "https://squareup.com/gb/en/pricing", "checked": "2026-09-25"}
    status = "code-ready-needs-key"
    status_note = "GET /v2/locations and POST /v2/online-checkout/payment-links confirmed in Square's reference on 2026-09-26. Not tested here (no token)."
    actions = {"payment_link": {"label": "Make a payment link", "params": [
        {"key": "name", "label": "What it's for", "example": "Cake order deposit"}, {"key": "price", "label": "Price in £", "example": "10"}]}}
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
        return {"url": pl.get("url"), "id": pl.get("id")}


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
        {"key": "name", "label": "What it's for", "example": "Order 1042"}, {"key": "price", "label": "Price in £", "example": "18.00"}]}}
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
