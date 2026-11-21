"""Open Beauty Facts — barcode lookup for cosmetics and hair products. Free, open database (ODbL), no key."""
import re
from netutil import NetError
from . import Connector, ConnectorError


class OpenBeautyFacts(Connector):
    id = "open_beauty_facts"
    name = "Open Beauty Facts"
    category = "Stock"
    cost_type = "open source"
    what_it_does = ("Type or scan the barcode on a shampoo, conditioner, hair dye or styling product and get its name, "
                    "brand and size, to add retail products to the salon's shop quickly. Many salon-only brands are "
                    "not in the database yet; then the owner types the details.")
    docs_url = "https://openfoodfacts.github.io/openfoodfacts-server/api/"
    pricing = {"text": "Free, no key. Please send a real app name (we do).", "url": "https://world.openbeautyfacts.org/",
               "checked": "2026-09-26"}
    status = "working-tested"
    live_tested_on = "2026-09-26"
    status_note = "Barcode 5201279101411 returned 'APIVITA Hyaluronic Hydra moisturizing shampoo, 500ml' from our box on 2026-09-26, and again on 2026-10-19 (00:04 UK time). An unknown barcode answers 404, which the app now shows as 'not found - type the details in'."
    actions = {"barcode": {"label": "Look up a barcode", "params": [{"key": "barcode", "label": "Barcode", "example": "5201279101411"}]}}
    shop_features = ["Barcode lookup when adding retail hair products (owner admin)"]

    def test_connection(self):
        r = self.act_barcode({"barcode": "5201279101411"})
        return {"ok": True, "message": f"Working: barcode 5201279101411 = {r.get('brands') or '?'} {r.get('product_name') or ''}".strip()}

    def act_barcode(self, p):
        code = re.sub(r"\D", "", str(p.get("barcode") or ""))
        if not 6 <= len(code) <= 14:
            raise ConnectorError("A barcode is 8 to 14 digits.")
        try:
            d = self.get_json(f"https://world.openbeautyfacts.org/api/v2/product/{code}.json"
                          "?fields=product_name,brands,quantity,categories,image_front_small_url")
        except NetError as e:
            if e.status != 404:
                raise
            d = {"status": 0}                       # 404 = not in the database (checked live 2026-10-19)
        if d.get("status") != 1:
            return {"found": False, "barcode": code, "message": "Not in Open Beauty Facts yet — type the details in."}
        pr = d.get("product") or {}
        return {"found": True, "barcode": code, "product_name": pr.get("product_name"), "brands": pr.get("brands"),
                "quantity": pr.get("quantity"), "categories": pr.get("categories"), "image": pr.get("image_front_small_url"),
                "source_url": f"https://world.openbeautyfacts.org/product/{code}"}
