"""Every connector, tested with a FAKE network (no real internet, no real keys).
python3 -m pytest studio/test_connectors.py -q"""
import base64
import json
import sys
import urllib.parse
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import connectors as C  # noqa: E402
from connectors import custom_api  # noqa: E402
from netutil import NetError  # noqa: E402

CATALOGUE_ONLY = {"evri", "stuart", "uber_direct", "deliveroo", "uber_eats", "just_eat"}
LIVE_TESTED = {"postcodes_io", "overpass_osm", "open_food_facts", "frankfurter", "whatsapp_link", "custom_api"}


class Fake:
    """Returns canned JSON for the first matching URL fragment and records every request."""
    def __init__(self, routes=None, default=b"{}"):
        self.routes, self.default, self.calls = routes or {}, default, []

    def __call__(self, url, method="GET", headers=None, data=None, timeout=20, contact=""):
        self.calls.append({"url": url, "method": method, "headers": dict(headers or {}), "data": data})
        for frag, resp in self.routes.items():
            if frag in url:
                if isinstance(resp, Exception):
                    raise resp
                return 200, {}, (resp if isinstance(resp, bytes) else json.dumps(resp).encode())
        return 200, {}, self.default

    def form(self, i=-1):
        return dict(urllib.parse.parse_qsl(self.calls[i]["data"].decode()))

    def json(self, i=-1):
        return json.loads(self.calls[i]["data"])


def creds_for(cls):
    c = {k["key"]: "test_value_123456" for k in cls.credentials}
    c.update({"site_url": "https://shop.example.com", "shop_domain": "demo.myshopify.com", "phone": "07700900123",
              "from_number": "+447700900999", "merchant_code": "MTEST01"})
    return {k: v for k, v in c.items() if k in {x["key"] for x in cls.credentials}}


REG = C.registry()


# ---------------------------------------------------------------- whole catalogue
def test_catalogue_has_standard_fields_and_honest_statuses():
    cat = C.catalogue()
    assert len(cat) >= 27
    for d in cat:
        for k in ("id", "name", "category", "cost_type", "what_it_does", "credentials", "docs_url", "status", "actions"):
            assert k in d, (d["id"], k)
        assert d["status"] in C.STATUSES
        assert d["cost_type"] in ("free", "open source", "free key", "paid"), d["id"]
        if d["pricing"] and d["pricing"].get("checked"):
            assert d["pricing"]["url"].startswith("https://")
        if d["status"] == "working-tested":
            assert d["live_tested_on"] or d["id"] == "custom_api" or d["status_note"]
    ids = {d["id"] for d in cat}
    assert LIVE_TESTED <= ids and CATALOGUE_ONLY <= ids
    for must in ("stripe", "square", "sumup", "shopify", "woocommerce", "whatsapp_cloud", "twilio_sms", "xero",
                 "companies_house", "shippo", "easypost", "royal_mail_click_drop", "google_business_profile", "brave_search", "duckduckgo"):
        assert must in ids


@pytest.mark.parametrize("cid", sorted(set(REG) - {"custom_api"}))
def test_every_connector_test_button_never_crashes_and_uses_https(cid):
    cls = REG[cid]
    for fake in (Fake(), Fake(default=b"not json"), Fake({"": NetError("offline", "No internet connection.")}),
                 Fake({"": NetError("auth", "401", 401)})):
        r = C._safe_test(cls(creds_for(cls), fake))
        assert isinstance(r, dict) and "ok" in r and r.get("message"), cid
        assert all(c["url"].startswith("https://") for c in fake.calls), cid
    if cid in CATALOGUE_ONLY:
        assert r["ok"] is False and "No code" in r["message"]


@pytest.mark.parametrize("cid", sorted(cid for cid, c in REG.items() if any(k.get("required") for k in c.credentials)))
def test_keyed_connectors_ask_for_the_key_before_calling_out(cid):
    fake = Fake()
    r = C._safe_test(REG[cid]({}, fake))
    assert r["ok"] is False and fake.calls == []


def test_auth_failure_message_is_plain():
    r = C._safe_test(REG["stripe"]({"secret_key": "sk_test_x"}, Fake({"": NetError("auth", "401", 401)})))
    assert r["ok"] is False and "key" in r["message"].lower()


# ---------------------------------------------------------------- free, live-tested ones
def test_postcodes_io():
    f = Fake({"postcodes.io": {"result": {"postcode": "HA3 5AA", "latitude": 51.590353, "longitude": -0.332695,
                                          "admin_district": "Harrow", "region": "London"}}})
    assert REG["postcodes_io"]({}, f).run("lookup", {"postcode": "HA3 5AA"})["area"] == "Harrow"


def test_overpass_nearby_and_tag_injection_refused():
    f = Fake({"overpass": {"elements": [{"type": "node", "id": 9, "tags": {"name": "Post Office"}}]}})
    r = REG["overpass_osm"]({}, f).run("nearby", {"lat": "51.59", "lon": "-0.33", "tag": "amenity=post_office"})
    assert r["items"][0]["url"] == "https://www.openstreetmap.org/node/9"
    assert '["amenity"="post_office"]' in f.form()["data"]
    with pytest.raises(C.ConnectorError):
        REG["overpass_osm"]({}, f).run("nearby", {"lat": 1, "lon": 1, "tag": 'shop="x"];out;'})


def test_open_food_facts_found_and_missing():
    f = Fake({"5900259128843": {"status": 1, "product": {"product_name": "Chips", "brands": "Lay's", "countries": "Poland"}},
              "123456789": {"status": 0}})
    c = REG["open_food_facts"]({}, f)
    assert c.run("barcode", {"barcode": "5900259128843"})["brands"] == "Lay's"
    assert c.run("barcode", {"barcode": "123456789"})["found"] is False
    with pytest.raises(C.ConnectorError):
        c.run("barcode", {"barcode": "12"})


def test_frankfurter_convert():
    f = Fake({"frankfurter": {"amount": 100.0, "base": "GBP", "date": "2026-09-25", "rates": {"RON": 613.23, "PLN": 508.08}}})
    r = REG["frankfurter"]({}, f).run("convert", {"amount": "100", "from": "gbp", "to": "RON,PLN"})
    assert r["rates"]["RON"] == 613.23 and "symbols=RON,PLN" in f.calls[0]["url"]
    with pytest.raises(C.ConnectorError):
        REG["frankfurter"]({}, f).run("convert", {"to": "LEI!"})


def test_whatsapp_click_to_chat_link():
    r = REG["whatsapp_link"]({"phone": "07700 900123"}, Fake()).run("link", {"text": "2 x baklava"})
    assert r["url"] == "https://wa.me/447700900123?text=2%20x%20baklava"


# ---------------------------------------------------------------- keyed ones: request shape matches vendor docs
def test_stripe_payment_link_two_calls_bearer_and_pence():
    f = Fake({"/v1/prices": {"id": "price_1"}, "/v1/payment_links": {"id": "plink_1", "url": "https://buy.stripe.com/test_x", "livemode": False}})
    r = REG["stripe"]({"secret_key": "sk_test_abc"}, f).run("payment_link", {"name": "Baklava box", "price": "12.50"})
    assert r["url"] == "https://buy.stripe.com/test_x"
    assert f.calls[0]["headers"]["Authorization"] == "Bearer sk_test_abc"
    assert f.form(0) == {"currency": "gbp", "unit_amount": "1250", "product_data[name]": "Baklava box"}
    assert f.form(1)["line_items[0][price]"] == "price_1"
    with pytest.raises(C.ConnectorError):
        REG["stripe"]({"secret_key": "k"}, f).run("payment_link", {"name": "x", "price": "-1"})


def test_square_payment_link_version_header_and_sandbox():
    f = Fake({"/v2/locations": {"locations": [{"id": "L1", "name": "Shop"}]},
              "payment-links": {"payment_link": {"id": "pl", "url": "https://square.link/u/abc"}}})
    r = REG["square"]({"access_token": "t", "environment": "sandbox"}, f).run("payment_link", {"name": "Deposit", "price": "10"})
    assert r["url"] == "https://square.link/u/abc"
    assert all(c["url"].startswith("https://connect.squareupsandbox.com") for c in f.calls)
    assert f.calls[-1]["headers"]["Square-Version"] == "2026-09-16"
    body = f.json()
    assert body["quick_pay"]["price_money"] == {"amount": 1000, "currency": "GBP"} and body["quick_pay"]["location_id"] == "L1"


def test_sumup_checkout():
    f = Fake({"/v0.1/checkouts": {"id": "c1", "status": "PENDING", "amount": 18.0}})
    r = REG["sumup"]({"api_key": "sup_sk_x", "merchant_code": "M1"}, f).run("checkout", {"name": "Order", "price": "18"})
    assert r["status"] == "PENDING" and f.json()["merchant_code"] == "M1" and f.json()["currency"] == "GBP"


def test_shopify_graphql_and_bad_domain():
    f = Fake({"graphql.json": {"data": {"products": {"nodes": [{"title": "Cozonac", "totalInventory": 4,
                                                               "variants": {"nodes": [{"price": "7.99"}]}}]}}}})
    c = REG["shopify"]({"shop_domain": "demo.myshopify.com", "access_token": "shpat_x"}, f)
    assert c.run("products", {})["items"] == [{"name": "Cozonac", "stock": 4, "price": "7.99"}]
    assert "/admin/api/2026-07/graphql.json" in f.calls[0]["url"] and f.calls[0]["headers"]["X-Shopify-Access-Token"] == "shpat_x"
    with pytest.raises(C.ConnectorError):
        REG["shopify"]({"shop_domain": "evil.com", "access_token": "x"}, f).run("products", {})
    assert C._safe_test(REG["shopify"]({"shop_domain": "demo.myshopify.com", "access_token": "x"},
                                       Fake({"": {"errors": [{"message": "Invalid API key"}]}})))["ok"] is False


def test_woocommerce_basic_auth_https_only_and_set_stock():
    f = Fake({"/products/5": {"id": 5, "name": "Zacusca", "stock_quantity": 24}, "/products?": [{"id": 5, "name": "Zacusca", "price": "3.49", "stock_quantity": 2}]})
    c = REG["woocommerce"]({"site_url": "https://shop.example.com/", "consumer_key": "ck_1", "consumer_secret": "cs_2"}, f)
    assert c.run("products", {})["items"][0]["price"] == "3.49"
    assert f.calls[0]["headers"]["Authorization"] == "Basic " + base64.b64encode(b"ck_1:cs_2").decode()
    assert c.run("set_stock", {"product_id": "5", "stock": "24"})["stock"] == 24 and f.calls[-1]["method"] == "PUT"
    assert C._safe_test(REG["woocommerce"]({"site_url": "http://x", "consumer_key": "a", "consumer_secret": "b"}, f))["ok"] is False


def test_twilio_sms_form_and_uk_number():
    f = Fake({"Messages.json": {"sid": "SM1", "status": "queued"}})
    r = REG["twilio_sms"]({"account_sid": "AC1", "auth_token": "t", "from_number": "+447700900999"}, f).run("send", {"to": "07700 900123", "text": "Ready"})
    assert r["status"] == "queued" and f.form()["To"] == "+447700900123" and "/Accounts/AC1/Messages.json" in f.calls[0]["url"]


def test_whatsapp_cloud_send_text():
    f = Fake({"/messages": {"messages": [{"id": "wamid.1"}]}})
    r = REG["whatsapp_cloud"]({"access_token": "t", "phone_number_id": "123"}, f).run("send_text", {"to": "07700900123", "text": "hi"})
    assert r["message_ids"] == ["wamid.1"] and f.json()["to"] == "447700900123" and f.json()["messaging_product"] == "whatsapp"


def test_companies_house_basic_key_and_links():
    f = Fake({"search/companies": {"items": [{"title": "EXAMPLE LTD", "company_number": "01234567", "company_status": "active"}]}})
    r = REG["companies_house"]({"api_key": "chkey"}, f).run("search", {"q": "example"})
    assert r["items"][0]["url"].endswith("/company/01234567")
    assert f.calls[0]["headers"]["Authorization"] == "Basic " + base64.b64encode(b"chkey:").decode()


def test_brave_connector_header():
    f = Fake({"api.search.brave.com": {"web": {"results": [{"title": "t", "url": "https://x.org", "description": "d"}]}}})
    assert REG["brave_search"]({"api_key": "BSA1"}, f).run("search", {"q": "x"})["results"][0]["url"] == "https://x.org"
    assert f.calls[0]["headers"]["X-Subscription-Token"] == "BSA1"


def test_duckduckgo_block_is_reported():
    r = C._safe_test(REG["duckduckgo"]({}, Fake({"duckduckgo": b"<html>anomaly</html>"})))
    assert r["ok"] is False and "robot" in r["message"]


def test_shippo_rates_and_easypost_address():
    f = Fake({"shipments": {"rates": [{"provider": "Evri", "servicelevel": {"name": "Standard"}, "amount": "3.50", "currency": "GBP", "estimated_days": 2}]}})
    r = REG["shippo"]({"api_token": "shippo_test_x"}, f).run("rates", {"from_zip": "HA3 5AA", "to_zip": "N15 4QL", "weight_kg": "2"})
    assert r["rates"][0]["carrier"] == "Evri" and f.calls[0]["headers"]["Authorization"] == "ShippoToken shippo_test_x"
    f2 = Fake({"addresses": {"id": "adr_1", "verifications": {"delivery": {"success": True, "errors": []}}}})
    assert REG["easypost"]({"api_key": "EZTK"}, f2).run("check_address", {"street1": "1 High St", "city": "Harrow", "zip": "HA3 5AA"})["deliverable"] is True


def test_unverified_xero_gbp_royal_mail_code_paths():
    f = Fake({"connect/token": {"access_token": "xt"}, "Organisation": {"Organisations": [{"Name": "Demo Ltd", "CountryCode": "GB", "BaseCurrency": "GBP"}]}})
    assert REG["xero"]({"client_id": "a", "client_secret": "b"}, f).run("organisation", {})["name"] == "Demo Ltd"
    assert f.calls[1]["headers"]["Authorization"] == "Bearer xt"
    f = Fake({"accounts": {"accounts": [{"accountName": "Shop", "name": "accounts/1"}]}})
    assert REG["google_business_profile"]({"access_token": "t"}, f).run("accounts", {})["items"][0]["id"] == "accounts/1"
    f = Fake({"orders": [{"orderIdentifier": 1}]})
    assert REG["royal_mail_click_drop"]({"api_key": "k"}, f).run("list_orders", {})["orders"] == [{"orderIdentifier": 1}]


def test_unknown_action_refused():
    with pytest.raises(C.ConnectorError):
        REG["frankfurter"]({}, Fake()).run("delete_everything", {})


# ---------------------------------------------------------------- credentials: local, masked, never exported
def test_credential_store_masks_ignores_masked_and_removes_empty(tmp_path):
    s = C.CredentialStore(tmp_path)
    m = s.save_creds("shop", "stripe", {"secret_key": "sk_test_1234567890"})
    assert m == {"secret_key": "••••7890"}
    s.save_creds("shop", "stripe", {"secret_key": "••••7890"})                     # form sent back masked -> unchanged
    assert s.creds("shop", "stripe")["secret_key"] == "sk_test_1234567890"
    s.save_creds("shop", "square", {"access_token": "tok_abcdefghij", "environment": "sandbox"})
    assert s.masked("shop", "square") == {"access_token": "••••ghij", "environment": "sandbox"}   # non-secret shown
    s.save_creds("shop", "stripe", {"secret_key": ""})
    assert s.creds("shop", "stripe") == {}
    assert (tmp_path / "shop.secrets.json").exists()
    with pytest.raises(C.ConnectorError):
        s.creds("../etc", "x")


def test_manager_list_never_shows_raw_secret(tmp_path):
    s = C.CredentialStore(tmp_path)
    s.save_creds("studio", "companies_house", {"api_key": "REALSECRETKEY999"})
    s.set_enabled("studio", "companies_house", True)
    items = {d["id"]: d for d in C.ConnectorManager(s, Fake()).list("studio")}
    assert "REALSECRETKEY999" not in json.dumps(items)
    assert items["companies_house"]["enabled"] is True


# ---------------------------------------------------------------- custom API + OpenAPI
DEF = {"label": "Rates", "base_url": "https://api.example.org/v1/", "auth_type": "api_key_header", "header_name": "X-Key",
       "actions": [{"name": "latest", "method": "GET", "path": "/latest"},
                   {"name": "item", "method": "GET", "path": "/items/{id}"},
                   {"name": "add", "method": "POST", "path": "/items", "body_template": '{"name": "{name}", "qty": 1}'}]}


def test_custom_api_validate_and_call_with_each_auth_type(tmp_path):
    d = custom_api.validate_definition(DEF)
    assert d["base_url"] == "https://api.example.org/v1"
    f = Fake({"/items/": {"id": "a b"}, "/latest": {"ok": 1}, "/items": {"created": True}})
    c = custom_api.CustomAPI({"secret": "K1"}, f, definition=DEF, slug="rates")
    assert c.run("latest", {"base": "GBP"})["json"] == {"ok": 1}
    assert f.calls[0]["url"] == "https://api.example.org/v1/latest?base=GBP" and f.calls[0]["headers"]["X-Key"] == "K1"
    c.run("item", {"id": "a b/../x"})
    assert f.calls[1]["url"] == "https://api.example.org/v1/items/a%20b%2F..%2Fx"          # placeholders are escaped
    c.run("add", {"name": 'Cozonac "big"'})
    assert json.loads(f.calls[2]["data"]) == {"name": 'Cozonac "big"', "qty": 1}
    for auth, expect in (("bearer", "Bearer K1"), ("basic", "Basic " + base64.b64encode(b"u:K1").decode())):
        f2 = Fake()
        custom_api.CustomAPI({"secret": "K1", "username": "u"}, f2, definition=dict(DEF, auth_type=auth)).run("latest", {})
        assert f2.calls[0]["headers"]["Authorization"] == expect
    with pytest.raises(C.ConnectorError):
        custom_api.CustomAPI({}, Fake(), definition=DEF).run("latest", {})        # key missing
    for bad in ({"base_url": "ftp://x"}, dict(DEF, auth_type="magic"), dict(DEF, actions=[{"name": "x", "method": "TRACE"}])):
        with pytest.raises(C.ConnectorError):
            custom_api.validate_definition(bad)


def test_custom_api_saved_per_scope_and_run_through_manager(tmp_path):
    s = C.CredentialStore(tmp_path)
    s.save_custom_def("SES-0001", "rates", custom_api.validate_definition(DEF))
    s.save_creds("SES-0001", "custom:rates", {"secret": "SECRETVALUE123"})
    f = Fake({"/latest": {"rates": {"EUR": 1.16}}})
    m = C.ConnectorManager(s, f)
    ids = [d["id"] for d in m.list("SES-0001")]
    assert "custom:rates" in ids and "custom:rates" not in [d["id"] for d in m.list("studio")]
    assert m.run("SES-0001", "custom:rates", "latest", {})["result"]["json"]["rates"]["EUR"] == 1.16
    assert "SECRETVALUE123" not in json.dumps(m.list("SES-0001"))


OPENAPI3 = {"openapi": "3.0.0", "info": {"title": "Frankfurter API", "version": "2"}, "servers": [{"url": "https://api.frankfurter.dev/v2"}],
            "components": {"securitySchemes": {"k": {"type": "apiKey", "in": "header", "name": "X-API-Key"}}},
            "paths": {"/rates": {"get": {"operationId": "getRates", "summary": "Latest rates"}},
                      "/currencies": {"get": {"summary": "List"}, "post": {"summary": "Add"}}}}
SWAGGER2 = {"swagger": "2.0", "info": {"title": "Old", "version": "1"}, "host": "api.old.example", "basePath": "/v1", "schemes": ["https"],
            "securityDefinitions": {"b": {"type": "basic"}}, "paths": {"/things/{id}": {"get": {}}}}


def test_openapi_import_lists_endpoints_and_auth():
    r = custom_api.parse_openapi(json.dumps(OPENAPI3))
    assert r["title"] == "Frankfurter API" and r["base_url"] == "https://api.frankfurter.dev/v2"
    assert r["auth_type"] == "api_key_header" and r["header_name"] == "X-API-Key"
    assert {(e["method"], e["path"]) for e in r["endpoints"]} == {("GET", "/rates"), ("GET", "/currencies"), ("POST", "/currencies")}
    r2 = custom_api.parse_openapi(SWAGGER2)
    assert r2["base_url"] == "https://api.old.example/v1" and r2["auth_type"] == "basic"
    for bad in ("not json", {"paths": {}}, "openapi: 3.0.0"):
        with pytest.raises(C.ConnectorError):
            custom_api.parse_openapi(bad)
