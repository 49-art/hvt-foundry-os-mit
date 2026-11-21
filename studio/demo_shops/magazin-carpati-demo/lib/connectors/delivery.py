"""Delivery and couriers: Shippo and EasyPost (multi-carrier), Royal Mail Click & Drop, and catalogue-only entries."""
from . import Connector, ConnectorError, basic


def _addr(p, prefix):
    return {k: (p.get(f"{prefix}_{k}") or "").strip() for k in ("name", "street1", "city", "zip")}


class Shippo(Connector):
    id = "shippo"
    name = "Shippo (compare couriers)"
    category = "Delivery"
    cost_type = "paid"
    what_it_does = "Compares parcel prices from several couriers for one parcel and can buy labels (carriers depend on the owner's Shippo account)."
    credentials = [{"key": "api_token", "label": "Shippo API token (shippo_test_… or shippo_live_…)", "secret": True, "required": True,
                    "help": "apps.goshippo.com → Settings → API. Test tokens are free."}]
    docs_url = "https://docs.goshippo.com/shippoapi/public-api/"
    pricing = {"text": "Price not checked today — see Shippo's pricing page. UK carrier coverage not checked.", "url": "https://goshippo.com/pricing", "checked": None}
    status = "code-ready-needs-key"
    status_note = "api.goshippo.com and 'ShippoToken' auth confirmed in the public API docs on 2026-09-26. Not tested here (no token)."
    actions = {"rates": {"label": "Compare parcel prices", "params": [
        {"key": "from_zip", "label": "From postcode", "example": "HA3 5AA"}, {"key": "to_zip", "label": "To postcode", "example": "N15 4QL"},
        {"key": "weight_kg", "label": "Weight kg", "example": "2"}]}}

    def _h(self):
        self.need("api_token")
        return {"Authorization": "ShippoToken " + self.creds["api_token"]}

    def test_connection(self):
        d = self.get_json("https://api.goshippo.com/addresses/?results=1", headers=self._h())
        return {"ok": True, "message": "Working: Shippo accepted the token."}

    def act_rates(self, p):
        try:
            w = float(p.get("weight_kg") or 1)
        except ValueError:
            raise ConnectorError("Weight must be a number.")
        body = {"address_from": {"zip": p.get("from_zip"), "country": "GB", "city": p.get("from_city") or "London", "street1": p.get("from_street1") or "", "name": "Shop"},
                "address_to": {"zip": p.get("to_zip"), "country": "GB", "city": p.get("to_city") or "London", "street1": p.get("to_street1") or "", "name": "Customer"},
                "parcels": [{"length": "30", "width": "20", "height": "15", "distance_unit": "cm", "weight": str(w), "mass_unit": "kg"}],
                "async": False}
        d = self.send_json("https://api.goshippo.com/shipments/", headers=self._h(), body=body)
        return {"rates": [{"carrier": r.get("provider"), "service": (r.get("servicelevel") or {}).get("name"),
                           "amount": r.get("amount"), "currency": r.get("currency"), "days": r.get("estimated_days")} for r in d.get("rates", [])]}


class EasyPost(Connector):
    id = "easypost"
    name = "EasyPost (addresses and couriers)"
    category = "Delivery"
    cost_type = "paid"
    what_it_does = "Checks delivery addresses and compares courier prices (carriers depend on the owner's EasyPost account)."
    credentials = [{"key": "api_key", "label": "EasyPost API key (test or production)", "secret": True, "required": True,
                    "help": "easypost.com → Account → API keys. Test keys are free."}]
    docs_url = "https://docs.easypost.com/docs/addresses"
    pricing = {"text": "Price not checked today — see EasyPost's pricing page.", "url": "https://www.easypost.com/pricing", "checked": None}
    status = "code-ready-needs-key"
    status_note = "api.easypost.com/v2 endpoints confirmed in the official docs on 2026-09-26. Not tested here (no key)."
    actions = {"check_address": {"label": "Check an address", "params": [
        {"key": "street1", "label": "Street", "example": "10 High Street"}, {"key": "city", "label": "Town", "example": "Harrow"},
        {"key": "zip", "label": "Postcode", "example": "HA3 5AA"}]}}

    def _h(self):
        self.need("api_key")
        return {"Authorization": basic(self.creds["api_key"], "")}

    def test_connection(self):
        self.get_json("https://api.easypost.com/v2/addresses?page_size=1", headers=self._h())
        return {"ok": True, "message": "Working: EasyPost accepted the key."}

    def act_check_address(self, p):
        d = self.send_json("https://api.easypost.com/v2/addresses", headers=self._h(), body={
            "address": {"street1": p.get("street1"), "city": p.get("city"), "zip": p.get("zip"), "country": "GB"}, "verify": True})
        v = ((d.get("verifications") or {}).get("delivery") or {})
        return {"id": d.get("id"), "deliverable": v.get("success"), "errors": [e.get("message") for e in v.get("errors", [])]}


class RoyalMailClickDrop(Connector):
    id = "royal_mail_click_drop"
    name = "Royal Mail Click & Drop"
    category = "Delivery"
    cost_type = "paid"
    what_it_does = "Sends parcel orders into the owner's Royal Mail Click & Drop account, ready to print labels."
    credentials = [{"key": "api_key", "label": "Click & Drop API key", "secret": True, "required": True,
                    "help": "Click & Drop → Settings → Integrations → Click & Drop API (may need an OBA/business account)."}]
    docs_url = "https://business.parcel.royalmail.com/"
    pricing = {"text": "Price not checked today.", "url": "https://www.royalmail.com/business", "checked": None}
    status = "unverified"
    status_note = "We could not find/read Royal Mail's public API reference from our box on 2026-09-26. Endpoint from our knowledge only."
    actions = {"list_orders": {"label": "List recent orders", "params": []}}

    def _h(self):
        self.need("api_key")
        return {"Authorization": "Bearer " + self.creds["api_key"]}

    def test_connection(self):
        self.act_list_orders({})
        return {"ok": True, "message": "Working: Click & Drop accepted the key."}

    def act_list_orders(self, p):
        d = self.get_json("https://api.parcel.royalmail.com/api/v1/orders", headers=self._h())
        return {"orders": d if isinstance(d, list) else d.get("orders", d)}


class _CatalogueOnly(Connector):
    status = "unverified"
    actions = {}

    def test_connection(self):
        raise ConnectorError("No code for this one yet: it needs a business/partner account and its API docs aren't public enough to build against. "
                             "Listed so you know it exists.")


class Evri(_CatalogueOnly):
    id = "evri"
    name = "Evri"
    category = "Delivery"
    cost_type = "paid"
    what_it_does = "Parcel courier with many local drop-off shops. Business API needs an Evri business account."
    docs_url = "https://www.evri.com/business"
    status_note = "Catalogue only. Business API access is by account; not built or tested."


class Stuart(_CatalogueOnly):
    id = "stuart"
    name = "Stuart (same-day courier)"
    category = "Delivery"
    cost_type = "paid"
    what_it_does = "On-demand same-day delivery in London and other UK cities."
    docs_url = "https://stuart.com/"
    status_note = "Catalogue only. Needs a Stuart business account for API keys; not built or tested."


class UberDirect(_CatalogueOnly):
    id = "uber_direct"
    name = "Uber Direct"
    category = "Delivery"
    cost_type = "paid"
    what_it_does = "Uber couriers deliver the shop's own orders (not the Uber Eats marketplace)."
    docs_url = "https://developer.uber.com/docs/deliveries/overview"
    status_note = "Catalogue only. Needs Uber approval for API access; not built or tested."
