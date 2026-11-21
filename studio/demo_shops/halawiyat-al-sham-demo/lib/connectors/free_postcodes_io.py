"""postcodes.io — UK postcode lookup. Free, open source (MIT), no key."""
import urllib.parse
from . import Connector, ConnectorError


class PostcodesIO(Connector):
    id = "postcodes_io"
    name = "postcodes.io"
    category = "Location"
    cost_type = "open source"
    what_it_does = "Turns a UK postcode into a map position and area name. Used by the live search."
    credentials = []
    docs_url = "https://postcodes.io/docs"
    pricing = {"text": "Free, no key needed.", "url": "https://postcodes.io/", "checked": "2026-09-26"}
    status = "working-tested"
    live_tested_on = "2026-09-26"
    actions = {"lookup": {"label": "Look up a postcode", "params": [{"key": "postcode", "label": "Postcode", "example": "HA3 5AA"}]}}
    shop_features = ["Map link from the shop's postcode"]

    def test_connection(self):
        r = self.act_lookup({"postcode": "HA3 5AA"})
        return {"ok": True, "message": f"Working: HA3 5AA is in {r['area']} ({r['lat']:.4f}, {r['lon']:.4f})."}

    def act_lookup(self, p):
        pc = (p.get("postcode") or "").strip()
        if not pc:
            raise ConnectorError("Type a postcode.")
        d = self.get_json("https://api.postcodes.io/postcodes/" + urllib.parse.quote(pc))
        r = d.get("result") or {}
        return {"postcode": r.get("postcode"), "lat": r.get("latitude"), "lon": r.get("longitude"),
                "area": r.get("admin_district"), "ward": r.get("admin_ward"), "region": r.get("region")}
