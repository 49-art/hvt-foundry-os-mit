"""OpenStreetMap Overpass API — nearby places. Free, open data (ODbL), no key."""
import urllib.parse
from . import Connector, ConnectorError


class OverpassOSM(Connector):
    id = "overpass_osm"
    name = "OpenStreetMap (Overpass)"
    category = "Location"
    cost_type = "open source"
    what_it_does = "Finds real places near the shop from OpenStreetMap: wholesalers, storage, couriers, banks, community shops."
    docs_url = "https://wiki.openstreetmap.org/wiki/Overpass_API"
    pricing = {"text": "Free public service with fair-use limits; please don't hammer it (the Studio caches for 24 hours).",
               "url": "https://wiki.openstreetmap.org/wiki/Overpass_API", "checked": "2026-09-26"}
    status = "working-tested"
    live_tested_on = "2026-09-26"
    actions = {"nearby": {"label": "Places near a point", "params": [
        {"key": "lat", "label": "Latitude", "example": "51.5903"}, {"key": "lon", "label": "Longitude", "example": "-0.3327"},
        {"key": "tag", "label": "OSM tag (key=value)", "example": "shop=wholesale"},
        {"key": "radius_m", "label": "Radius in metres", "example": "3000"}]}}

    def test_connection(self):
        r = self.act_nearby({"lat": 51.590353, "lon": -0.332695, "tag": "amenity=post_office", "radius_m": 1500})
        return {"ok": True, "message": f"Working: {r['count']} post office(s) within 1.5 km of HA3 5AA."}

    def act_nearby(self, p):
        try:
            lat, lon = float(p["lat"]), float(p["lon"])
            radius = max(100, min(int(p.get("radius_m") or 2000), 15000))
        except (KeyError, ValueError, TypeError):
            raise ConnectorError("Latitude, longitude and radius must be numbers.")
        k, _, v = (p.get("tag") or "shop=wholesale").partition("=")
        if not k or any(c in k + v for c in '"\\;()[]'):
            raise ConnectorError("Tag must look like key=value, e.g. shop=wholesale.")
        q = f'[out:json][timeout:25];nwr(around:{radius},{lat},{lon})["{k}"="{v}"];out center tags 50;'
        d = self.send_json("https://overpass-api.de/api/interpreter", form={"data": q}, timeout=40)
        items = [{"name": (e.get("tags") or {}).get("name", "(no name)"),
                  "url": f"https://www.openstreetmap.org/{e['type']}/{e['id']}"} for e in d.get("elements", [])]
        return {"count": len(items), "items": items}
