"""Online shops the owner may already have: Shopify and WooCommerce."""
import re
import urllib.parse
from . import Connector, ConnectorError, basic


class Shopify(Connector):
    id = "shopify"
    name = "Shopify"
    category = "Online shop"
    cost_type = "paid"
    what_it_does = "Reads products and stock from the owner's existing Shopify shop, so the shop app can show the same list."
    credentials = [{"key": "shop_domain", "label": "Shop address (yourshop.myshopify.com)", "secret": False, "required": True},
                   {"key": "access_token", "label": "Admin API access token (shpat_…)", "secret": True, "required": True,
                    "help": "Shopify admin → Settings → Apps and sales channels → Develop apps → create app → read_products → install → token."}]
    docs_url = "https://shopify.dev/docs/api/admin-graphql"
    pricing = {"text": "Price not checked today — see Shopify's UK pricing page.", "url": "https://www.shopify.com/uk/pricing", "checked": None}
    status = "code-ready-needs-key"
    status_note = "GraphQL Admin API endpoint /admin/api/2026-07/graphql.json confirmed on shopify.dev on 2026-09-26. Not tested here (no shop)."
    actions = {"products": {"label": "List products", "params": []}}
    VERSION = "2026-07"

    def _url(self):
        self.need("shop_domain", "access_token")
        d = self.creds["shop_domain"].strip().replace("https://", "").replace("http://", "").strip("/")
        if not re.fullmatch(r"[A-Za-z0-9-]+\.myshopify\.com", d):
            raise ConnectorError("Shop address must look like yourshop.myshopify.com")
        return f"https://{d}/admin/api/{self.VERSION}/graphql.json"

    def _q(self, query):
        d = self.send_json(self._url(), headers={"X-Shopify-Access-Token": self.creds["access_token"]}, body={"query": query})
        if d.get("errors"):
            raise ConnectorError("Shopify said: " + str(d["errors"])[:300])
        return d.get("data") or {}

    def test_connection(self):
        d = self._q("{ shop { name currencyCode } }")
        return {"ok": True, "message": f"Working: connected to '{d['shop']['name']}' ({d['shop']['currencyCode']})."}

    def act_products(self, p):
        d = self._q("{ products(first: 50) { nodes { title totalInventory variants(first: 1) { nodes { price } } } } }")
        return {"items": [{"name": n["title"], "stock": n.get("totalInventory"),
                           "price": ((n.get("variants") or {}).get("nodes") or [{}])[0].get("price")}
                          for n in d.get("products", {}).get("nodes", [])]}


class WooCommerce(Connector):
    id = "woocommerce"
    name = "WooCommerce (WordPress)"
    category = "Online shop"
    cost_type = "open source"
    what_it_does = "Reads products and stock from a WordPress + WooCommerce shop (free, open-source plugin) and can update stock numbers."
    credentials = [{"key": "site_url", "label": "Website address (https://…)", "secret": False, "required": True},
                   {"key": "consumer_key", "label": "Consumer key (ck_…)", "secret": True, "required": True,
                    "help": "WordPress admin → WooCommerce → Settings → Advanced → REST API → Add key."},
                   {"key": "consumer_secret", "label": "Consumer secret (cs_…)", "secret": True, "required": True}]
    docs_url = "https://woocommerce.github.io/woocommerce-rest-api-docs/"
    pricing = {"text": "The plugin is free and open source; the owner pays for their own web hosting.",
               "url": "https://wordpress.org/plugins/woocommerce/", "checked": "2026-09-26"}
    status = "code-ready-needs-key"
    status_note = "/wp-json/wc/v3 endpoints confirmed in the official REST API docs on 2026-09-26. Not tested here (no shop)."
    actions = {"products": {"label": "List products", "params": []},
               "set_stock": {"label": "Set stock for a product", "params": [
                   {"key": "product_id", "label": "Product ID", "example": "123"}, {"key": "stock", "label": "New stock number", "example": "24"}]}}

    def _base(self):
        self.need("site_url", "consumer_key", "consumer_secret")
        u = self.creds["site_url"].strip().rstrip("/")
        if not u.startswith("https://"):
            raise ConnectorError("Use the https:// address (WooCommerce keys must not be sent over plain http).")
        return u + "/wp-json/wc/v3"

    def _h(self):
        return {"Authorization": basic(self.creds["consumer_key"], self.creds["consumer_secret"])}

    def test_connection(self):
        d = self.get_json(self._base() + "/products?per_page=1", headers=self._h())
        return {"ok": True, "message": f"Working: WooCommerce answered ({len(d)} product shown as a sample)."}

    def act_products(self, p):
        d = self.get_json(self._base() + "/products?per_page=50", headers=self._h())
        return {"items": [{"id": x.get("id"), "name": x.get("name"), "price": x.get("price"), "stock": x.get("stock_quantity")} for x in d]}

    def act_set_stock(self, p):
        try:
            pid, stock = int(p.get("product_id")), int(p.get("stock"))
        except (TypeError, ValueError):
            raise ConnectorError("Product ID and stock must be whole numbers.")
        d = self.send_json(f"{self._base()}/products/{pid}", method="PUT", headers=self._h(),
                           body={"manage_stock": True, "stock_quantity": stock})
        return {"id": d.get("id"), "name": d.get("name"), "stock": d.get("stock_quantity")}
