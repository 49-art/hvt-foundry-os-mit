"""Open Food Facts — product/barcode lookup. Free, open database (ODbL), no key."""
import re
from . import Connector, ConnectorError


class OpenFoodFacts(Connector):
    id = "open_food_facts"
    name = "Open Food Facts"
    category = "Stock"
    cost_type = "open source"
    what_it_does = ("Type or scan a barcode and get the product name, brand and where it's sold. "
                    "Handy for adding imported stock to the shop's list quickly.")
    docs_url = "https://openfoodfacts.github.io/openfoodfacts-server/api/"
    pricing = {"text": "Free, no key. Please send a real app name (we do).", "url": "https://world.openfoodfacts.org/data",
               "checked": "2026-09-26"}
    status = "working-tested"
    live_tested_on = "2026-09-26"
    actions = {"barcode": {"label": "Look up a barcode", "params": [{"key": "barcode", "label": "Barcode", "example": "5900259128843"}]}}
    shop_features = ["Barcode lookup when adding products (owner admin)"]

    def test_connection(self):
        r = self.act_barcode({"barcode": "5900259128843"})
        return {"ok": True, "message": f"Working: barcode 5900259128843 = {r.get('brands') or '?'} {r.get('product_name') or ''}".strip()}

    def act_barcode(self, p):
        code = re.sub(r"\D", "", str(p.get("barcode") or ""))
        if not 6 <= len(code) <= 14:
            raise ConnectorError("A barcode is 8 to 14 digits.")
        d = self.get_json(f"https://world.openfoodfacts.org/api/v2/product/{code}.json"
                          "?fields=product_name,brands,countries,quantity,categories,image_front_small_url")
        if d.get("status") != 1:
            return {"found": False, "barcode": code, "message": "Not in Open Food Facts yet."}
        pr = d.get("product") or {}
        return {"found": True, "barcode": code, "product_name": pr.get("product_name"), "brands": pr.get("brands"),
                "quantity": pr.get("quantity"), "countries": pr.get("countries"), "image": pr.get("image_front_small_url"),
                "source_url": f"https://world.openfoodfacts.org/product/{code}"}
