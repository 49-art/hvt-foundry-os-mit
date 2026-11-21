"""
Build a card-based shop app's public files from its data (standard library only).

Used by HVT Foundry Studio when it generates a shop app from a card template,
and by the shop's own server.py whenever the owner saves in the admin page.

data/shop.json      – everything the owner edits (+ the scrambled admin password)
data/card.json      – the card template this app was built from (modules, presets, schema)
data/private/       – bookings, clients, vouchers… (never public, never in a zip)
site/content.json   – what customers see: no password, no suppliers, no keys, no private data
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import shopbuild
from shopbuild import LANG_NAMES, RTL, DAYS, HEX, _write, hash_password, verify_password, slugify  # noqa: F401

IMG_PATH = re.compile(r"^img/[A-Za-z0-9_\-]{1,40}\.(png|jpg|webp|svg)$")
DATA_IMG = re.compile(r"^data:image/(png|jpeg|webp|svg\+xml);base64,")
MAX_IMG = 2_500_000        # characters of base64 (~1.8 MB picture)
PUBLIC_KEYS = ["card_id", "card_version", "variant", "preset", "colours", "fonts", "pattern", "radius", "name", "tagline",
               "languages", "default_language", "logo", "hero_images", "hours", "closed_dates", "hours_note", "address",
               "postcode", "lat", "lon", "phone", "whatsapp", "google_place_id", "offer", "offer_on", "instagram", "tiktok",
               "platform_links", "policy_text", "policy_required", "access_info", "loyalty", "services", "staff",
               "gallery", "before_after", "reviews", "packages", "products", "branches", "demo", "made_with", "vouchers",
               "staff_word", "staff_word_plural", "demo_note"]


def load_card(app_dir) -> Dict[str, Any]:
    return json.loads((Path(app_dir) / "data" / "card.json").read_text(encoding="utf-8"))


def _txt(v, n=400) -> str:
    return str(v if v is not None else "").strip()[:n]


def _ml(v, langs, n=400) -> Dict[str, str]:
    if isinstance(v, str):
        v = {langs[0]: v}
    return {k: _txt(t, n) for k, t in (v or {}).items() if k in langs and _txt(t, n)}


def _money(v, label) -> str:
    s = _txt(v, 12).replace("£", "")
    if s and not re.fullmatch(r"\d{1,5}(\.\d{1,2})?", s):
        raise ValueError(f"{label} must be a number like 25 or 25.50.")
    return s


def _url(v, label) -> str:
    s = _txt(v, 400)
    if s and not s.startswith("https://"):
        raise ValueError(f"{label} must start with https://")
    return s


def save_image(app_dir: Path, data_url: str) -> str:
    """Store an uploaded picture in site/img/ and return its path. Refuses anything that isn't a picture."""
    m = DATA_IMG.match(data_url or "")
    if not m:
        raise ValueError("Pictures must be PNG, JPG, WEBP or SVG.")
    if len(data_url) > MAX_IMG:
        raise ValueError("That picture is too big. Please use one under about 1.8 MB.")
    raw = base64.b64decode(data_url.split(",", 1)[1])
    ext = {"jpeg": "jpg", "svg+xml": "svg"}.get(m.group(1), m.group(1))
    if ext == "svg" and re.search(rb"<script|on\w+\s*=|javascript:", raw, re.I):
        raise ValueError("That SVG picture contains script, so it can't be used.")
    name = f"img/{hashlib.sha256(raw).hexdigest()[:16]}.{ext}"
    _write(Path(app_dir) / "site" / name, raw, True)
    return name


def _img(v, app_dir, label, required=False) -> str:
    v = _txt(v, MAX_IMG + 100)
    if not v:
        if required:
            raise ValueError(f"{label}: add a picture.")
        return ""
    if DATA_IMG.match(v):
        if app_dir is None:
            raise ValueError("Pictures can only be uploaded in the shop app.")
        return save_image(app_dir, v)
    if not IMG_PATH.match(v):
        raise ValueError(f"{label}: unknown picture.")
    return v


def clean_list(schema: List[Dict[str, Any]], items, langs, card, staff_ids=None, app_dir=None, prefix="x", limit=300):
    out = []
    opts = card.get("service_options", {})
    for i, it in enumerate((items or [])[:limit]):
        if not isinstance(it, dict):
            continue
        row = {"id": re.sub(r"[^A-Za-z0-9_-]", "", _txt(it.get("id"), 24)) or f"{prefix}{i + 1}"}
        skip = False
        for f in schema:
            k, t, lab = f["key"], f["type"], f["label"]
            v = it.get(k, f.get("default"))
            if t == "breaks":
                if isinstance(v, list):
                    v = ", ".join(f"{b.get('start')}-{b.get('end')}" for b in v if isinstance(b, dict))
                v = _txt(v, 120)
            elif t == "text":
                v = _txt(v, 120)
            elif t == "text_long":
                v = _txt(v, 1200)
            elif t == "ml_text":
                v = _ml(v, langs, 300)
            elif t == "int":
                try:
                    v = int(v if v not in (None, "") else f.get("default", 0))
                except (TypeError, ValueError):
                    raise ValueError(f"{lab} must be a whole number.")
                if not f.get("min", -10**9) <= v <= f.get("max", 10**9):
                    raise ValueError(f"{lab} must be between {f.get('min')} and {f.get('max')}.")
            elif t == "money":
                v = _money(v, lab)
            elif t in ("choice", "choice_or_text"):
                allowed = [o[0] if isinstance(o, list) else o for o in opts.get(f.get("options_from"), [])]
                v = _txt(v, 60)
                if t == "choice" and v and v not in allowed:
                    raise ValueError(f"{lab}: choose one of {', '.join(allowed)}.")
            elif t == "multichoice":
                allowed = [o[0] for o in opts.get(f.get("options_from"), [])]
                v = [x for x in (v or []) if x in allowed]
            elif t == "bool":
                v = bool(v)
            elif t == "image":
                v = _img(v, app_dir, lab, f.get("required", False))
            elif t == "url":
                v = _url(v, lab)
            elif t == "tags":
                if isinstance(v, str):
                    v = [x.strip() for x in v.split(",")]
                v = [_txt(x, 60) for x in (v or []) if _txt(x, 60)][:20]
            elif t == "staff_refs":
                v = [x for x in (v or []) if staff_ids is None or x in staff_ids]
            elif t == "barcode":
                v = re.sub(r"\D", "", str(v or ""))[:14]
            elif t == "commission":
                v = v or {}
                c = {}
                for kk in ("service_percent", "retail_percent"):
                    try:
                        x = float(v.get(kk) or 0)
                    except (TypeError, ValueError):
                        raise ValueError("Commission must be a percentage like 40.")
                    if not 0 <= x <= 100:
                        raise ValueError("Commission must be between 0 and 100 percent.")
                    c[kk] = x
                v = c
            if f.get("required") and v in ("", {}, [], None):
                if t in ("ml_text", "text") and not any(it.values()):
                    skip = True
                    break
                raise ValueError(f"{lab} is needed ({prefix} {i + 1}).")
            if f.get("required_true") and v is not True:
                raise ValueError(f"{lab} — tick it before the photos can be shown.")
            row[k] = v
        if not skip:
            out.append(row)
    return out


def _hours(raw):
    hours, by_day = [], {h.get("day"): h for h in (raw or []) if isinstance(h, dict)}
    for day in DAYS:
        h = by_day.get(day, {})
        o, c = _txt(h.get("open"), 5), _txt(h.get("close"), 5)
        for t in (o, c):
            if t and not re.fullmatch(r"[0-2]\d:[0-5]\d", t):
                raise ValueError("Opening times must look like 08:30.")
        if o and c and c <= o:
            raise ValueError(f"On {day}, closing time must be after opening time.")
        hours.append({"day": day, "open": o, "close": c, "closed": bool(h.get("closed")) or not (o and c)})
    return hours


def clean_shop(card: Dict[str, Any], d: Dict[str, Any], app_dir=None) -> Dict[str, Any]:
    """Validate and tidy owner-entered data against the card. Raises ValueError with a plain message."""
    import cards_runtime as cr
    name = _txt(d.get("name"), 80)
    if not name:
        raise ValueError("The shop needs a name.")
    langs = [l for l in (d.get("languages") or ["en"]) if l in LANG_NAMES][:4] or ["en"]
    pre = next((p for p in card["presets"] if p["id"] == d.get("preset")), card["presets"][0])
    variant = next((v for v in card["variants"] if v["id"] == d.get("variant")), None) or \
        next((v for v in card["variants"] if v["id"] == pre.get("variant")), card["variants"][0])
    colours = dict(pre["colours"])
    for k, v in (d.get("colours") or {}).items():
        if k in colours and v:
            if not HEX.match(v):
                raise ValueError(f"Colour {k} must look like #A1B2C3.")
            colours[k] = v
    schema = card["content_schema"]
    staff = clean_list(schema["staff"], d.get("staff"), langs, card, app_dir=app_dir, prefix="s")
    staff_ids = {s["id"] for s in staff}
    raw_staff = {s.get("id"): s for s in (d.get("staff") or []) if isinstance(s, dict)}
    for s in staff:                                         # per-person working days (optional)
        days = (raw_staff.get(s["id"]) or {}).get("days")
        if isinstance(days, dict):
            s["days"] = {k: (v if (v is None or v == "shop" or (isinstance(v, dict) and re.fullmatch(r"[0-2]\d:[0-5]\d", str(v.get("start", ""))) and re.fullmatch(r"[0-2]\d:[0-5]\d", str(v.get("end", ""))))) else "shop")
                         for k, v in days.items() if k in DAYS}
    modules = cr.resolve(card, d.get("modules") or {})
    phone = re.sub(r"[^\d+ ]", "", _txt(d.get("phone"), 30))
    wa = re.sub(r"[^\d+]", "", _txt(d.get("whatsapp"), 30))
    logo = d.get("logo") or ""
    if logo and not IMG_PATH.match(logo):
        logo = _img(logo, app_dir, "Logo")
    place = re.sub(r"[^A-Za-z0-9_\-]", "", _txt(d.get("google_place_id"), 120))
    loyalty = d.get("loyalty") or {}
    try:
        stamps = int(loyalty.get("stamps_needed") or 6)
    except (TypeError, ValueError):
        raise ValueError("Stamps needed must be a whole number.")
    if not 2 <= stamps <= 30:
        raise ValueError("Stamps needed must be between 2 and 30.")
    bk = dict(card.get("booking_defaults") or {})
    nsd = _money((d.get("booking") or {}).get("no_show_deposit") or "10", "Deposit after a no-show")
    for k, v in (d.get("booking") or {}).items():
        if k in bk:
            try:
                bk[k] = max(0, min(int(v), 1440))
            except (TypeError, ValueError):
                raise ValueError(f"Booking setting {k} must be a whole number.")
    if bk.get("slot_minutes", 15) < 5:
        raise ValueError("Slots must be at least 5 minutes.")
    bk["no_show_deposit"] = nsd
    closed = [x for x in (d.get("closed_dates") or []) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(x))][:100]
    pl = d.get("platform_links") or {}
    policy_text = _ml(d.get("policy_text"), langs, 1200)
    out = {
        "card_id": card["card_id"], "card_version": card["version"], "variant": variant["id"],
        "staff_word": variant.get("staff_word", "Stylist"), "staff_word_plural": variant.get("staff_word_plural", "Stylists"),
        "preset": pre["id"], "colours": colours, "fonts": {"display": pre.get("font_display"), "body": pre.get("font_body")},
        "pattern": pre.get("pattern", "arches"), "radius": pre.get("radius", "16px"),
        "name": name, "tagline": _ml(d.get("tagline"), langs, 160), "languages": langs,
        "default_language": d.get("default_language") if d.get("default_language") in langs else langs[0],
        "logo": logo, "hero_images": [_img(x, app_dir, "Hero photo") for x in (d.get("hero_images") or [])[:5] if x],
        "hours": _hours(d.get("hours")), "closed_dates": closed, "hours_note": _ml(d.get("hours_note"), langs, 200),
        "address": _txt(d.get("address"), 200), "postcode": _txt(d.get("postcode"), 10).upper(),
        "lat": d.get("lat") if isinstance(d.get("lat"), (int, float)) else None,
        "lon": d.get("lon") if isinstance(d.get("lon"), (int, float)) else None,
        "phone": phone, "whatsapp": wa, "email": _txt(d.get("email"), 120), "google_place_id": place,
        "offer": _ml(d.get("offer"), langs, 200), "offer_on": bool(d.get("offer_on", True)),
        "instagram": _url(d.get("instagram"), "Instagram link"), "tiktok": _url(d.get("tiktok"), "TikTok link"),
        "platform_links": {k: _url(pl.get(k), f"{k.title()} link") for k in ("fresha", "treatwell", "booksy")},
        "policy_text": policy_text, "policy_required": bool(modules.get("policy") and policy_text),
        "policy_short": _txt(d.get("policy_short"), 160),
        "access_info": _ml(d.get("access_info"), langs, 600),
        "loyalty": {"stamps_needed": stamps, "reward": _txt(loyalty.get("reward"), 120) or "A free visit"},
        "vouchers": {"valid_months": max(1, min(int((d.get("vouchers") or {}).get("valid_months") or 12), 60)),
                     "amounts": [a for a in ((d.get("vouchers") or {}).get("amounts") or ["20", "40", "60"]) if re.fullmatch(r"\d{1,4}", str(a))][:6],
                     "pay_link": _url((d.get("vouchers") or {}).get("pay_link"), "Voucher pay link")},
        "walkin": {"max_waiting": max(1, min(int((d.get("walkin") or {}).get("max_waiting") or 25), 200)),
                   "default_minutes": max(5, min(int((d.get("walkin") or {}).get("default_minutes") or 30), 240))},
        "booking": bk,
        "messages": {k: _txt((d.get("messages") or {}).get(k), 500) for k in ("reminder", "review")},
        "services": clean_list(schema["services"], d.get("services"), langs, card, staff_ids, app_dir, "v"),
        "staff": staff,
        "gallery": clean_list(schema["gallery"], d.get("gallery"), langs, card, app_dir=app_dir, prefix="g", limit=60),
        "before_after": clean_list(schema["before_after"], d.get("before_after"), langs, card, app_dir=app_dir, prefix="ba", limit=40),
        "reviews": clean_list(schema["reviews"], d.get("reviews"), langs, card, prefix="r", limit=60),
        "packages": clean_list(schema["packages"], d.get("packages"), langs, card, prefix="pk", limit=40),
        "products": clean_list(schema["products"], d.get("products"), langs, card, app_dir=app_dir, prefix="p"),
        "branches": clean_list(schema["branches"], d.get("branches"), langs, card, prefix="b", limit=20),
        "modules": modules,
        "suppliers": [s for s in (d.get("suppliers") or []) if isinstance(s, dict)][:200],
        "deposit_provider": d.get("deposit_provider") if d.get("deposit_provider") in ("stripe", "square", "sumup") else "",
        "public_url": _url(d.get("public_url"), "Public web address"),
        "demo": bool(d.get("demo")),
        "demo_note": _txt(d.get("demo_note"), 200) if d.get("demo") else "",
        "admin": {"password_hash": (d.get("admin") or {}).get("password_hash", "")},
        "made_with": "Built with HVT Foundry Studio (HVT Innovations). This app and its content belong to the shop.",
    }
    _check_times(out)
    return out


def _check_times(shop: Dict[str, Any]) -> None:
    """Turn break and processing-time text into checked values (plain error if mistyped)."""
    try:
        from engines.booking import parse_breaks, parse_segments
    except ImportError:                           # pragma: no cover - engines folder missing
        return
    from engines.store import EngineError
    for s in shop["staff"]:
        try:
            br = parse_breaks(s.get("breaks") or "")
        except EngineError as e:
            raise ValueError(f"{s['name']}: {e}")
        s["breaks"] = [{"start": f"{b['start'] // 60:02d}:{b['start'] % 60:02d}", "end": f"{b['end'] // 60:02d}:{b['end'] % 60:02d}",
                        "flexible": bool(s.get("break_flexible", True))} for b in br]
    for v in shop["services"]:
        if v.get("segments"):
            try:
                parse_segments(v["segments"], int(v.get("duration_min") or 30))
            except EngineError as e:
                raise ValueError(f"{(v.get('name') or {}).get(shop['default_language'], v['id'])}: {e}")


# ------------------------------------------------------------------ public
def public_content(shop: Dict[str, Any], card: Dict[str, Any]) -> Dict[str, Any]:
    """What customers see. Sections for switched-off modules are left out entirely."""
    on = shop["modules"]
    c = {k: shop.get(k) for k in PUBLIC_KEYS}
    c["modules"] = {m["id"]: True for m in card["modules"] if on.get(m["id"]) and m.get("public")}
    if on.get("auto_booking"):
        c["booking_mode"] = "instant"
    elif on.get("booking_request"):
        c["booking_mode"] = "request"
    else:
        c["booking_mode"] = ""
    drop = {"gallery": "gallery", "before_after": "before_after", "reviews": "reviews", "packages": "packages",
            "products": "retail", "branches": "multi_branch", "staff": "staff"}
    for key, mod in drop.items():
        if not on.get(mod):
            c[key] = [] if key != "staff" else [{"id": s["id"], "name": s["name"]} for s in shop["staff"]]
    c["staff"] = [{k: v for k, v in s.items() if k not in ("commission", "days_off")} for s in c["staff"]]
    if not on.get("deposits"):
        c["services"] = [dict(s, pay_link="", deposit="") for s in c["services"]]
        c["products"] = [dict(p, pay_link="") for p in c["products"]]
        c["packages"] = [dict(p, pay_link="") for p in c["packages"]]
        c["vouchers"] = dict(c["vouchers"], pay_link="")
    if not on.get("social_links"):
        c["instagram"] = c["tiktok"] = ""
    if not on.get("platform_links"):
        c["platform_links"] = {}
    if not on.get("policy"):
        c["policy_text"], c["policy_required"] = {}, False
    if not on.get("accessibility"):
        c["access_info"] = {}
    if not on.get("offers"):
        c["offer_on"] = False
    if not on.get("reviews"):
        c["google_place_id"] = ""
    c["review_link"] = f"https://search.google.com/local/writereview?placeid={shop['google_place_id']}" if c.get("google_place_id") else ""
    c["dir"] = {l: ("rtl" if l in RTL else "ltr") for l in shop["languages"]}
    c["lang_names"] = {l: LANG_NAMES.get(l, l) for l in shop["languages"]}
    c["map_url"] = shopbuild.map_url(shop)
    c["service_options"] = card.get("service_options", {})
    c["built_at"] = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    c["needs_server_modules"] = sorted(m["id"] for m in card["modules"] if m.get("needs_server"))
    return c


def static_content(shop: Dict[str, Any], card: Dict[str, Any]) -> Dict[str, Any]:
    """Customer content for a STATIC copy (no always-on server - e.g. free static hosting).
    Anything that needs the server is left out, and booking becomes a WhatsApp request
    that says plainly it is not booked until the shop replies. Theory test B21."""
    c = public_content(shop, card)
    need = set(c.pop("needs_server_modules", []))
    dropped = sorted(k for k in c["modules"] if k in need and k not in ("booking_request",))
    for k in dropped:
        c["modules"].pop(k, None)
    if c.get("booking_mode"):
        c["booking_mode"] = "whatsapp_request" if (shop.get("whatsapp") or shop.get("phone")) else ""
        c["modules"]["booking_request"] = bool(c["booking_mode"])
    c["services"] = [dict(s, deposit="") for s in c["services"]]       # deposits need the server; fixed pay links still show
    c["static_copy"] = True
    c["static_note"] = ("This is the simple copy of the app (no live booking). Booking requests go by WhatsApp; "
                        "you're only booked when the shop replies.")
    c["static_dropped"] = dropped
    return c


def write_static_site(app_dir: Path | str, out_dir: Path | str) -> Dict[str, Any]:
    """Write a static copy of the customer app (site/ only, no admin, no server, no private data)."""
    import shutil
    app_dir, out_dir = Path(app_dir), Path(out_dir)
    shop, card = load_shop(app_dir), load_card(app_dir)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    shutil.copytree(app_dir / "site", out_dir, ignore=shutil.ignore_patterns("queue.html", "__pycache__"))
    content = static_content(shop, card)
    _write(out_dir / "content.json", json.dumps(content, ensure_ascii=False, indent=1))
    return {"folder": str(out_dir), "booking_mode": content["booking_mode"], "left_out": content["static_dropped"]}


# ----------------------------------------------------------- pattern art
def pattern_svg(pattern: str, col: Dict[str, str], w=1200, h=800) -> str:
    """Neutral generated artwork for when the shop has no photos yet. Shapes only — never people."""
    p, a, bg = col["primary"], col["accent"], col.get("surface", col["bg"])
    defs, body = "", ""
    if pattern == "stripes":
        defs = f'<pattern id="pt" width="80" height="80" patternUnits="userSpaceOnUse" patternTransform="rotate(35)"><rect width="80" height="80" fill="{p}"/><rect width="18" height="80" fill="{a}"/><rect x="30" width="8" height="80" fill="{bg}" opacity=".85"/></pattern>'
        body = f'<rect width="{w}" height="{h}" fill="url(#pt)"/><rect width="{w}" height="{h}" fill="{p}" opacity=".55"/>'
    elif pattern == "weave":
        defs = f'<pattern id="pt" width="120" height="120" patternUnits="userSpaceOnUse"><rect width="120" height="120" fill="{p}"/><path d="M0 30h60v30H0zM60 60h60v30H60z" fill="{a}" opacity=".85"/><path d="M30 0v60h30V0zM90 60v60h30V60z" fill="{bg}" opacity=".18"/><circle cx="90" cy="30" r="10" fill="{a}"/><circle cx="30" cy="90" r="10" fill="{bg}" opacity=".5"/></pattern>'
        body = f'<rect width="{w}" height="{h}" fill="url(#pt)"/>'
    elif pattern == "pinstripe":
        defs = f'<pattern id="pt" width="36" height="36" patternUnits="userSpaceOnUse"><rect width="36" height="36" fill="{p}"/><rect x="17" width="2" height="36" fill="{a}" opacity=".7"/></pattern>'
        body = f'<rect width="{w}" height="{h}" fill="url(#pt)"/><circle cx="{w * .78}" cy="{h * .45}" r="{h * .33}" fill="none" stroke="{a}" stroke-width="10" opacity=".8"/>'
    elif pattern == "tiles":
        star = "M60 0l14 46 46 14-46 14-14 46-14-46L0 60l46-14z"
        defs = f'<pattern id="pt" width="120" height="120" patternUnits="userSpaceOnUse"><rect width="120" height="120" fill="{p}"/><path d="{star}" fill="{a}" opacity=".8"/><circle cx="60" cy="60" r="12" fill="{bg}" opacity=".9"/></pattern>'
        body = f'<rect width="{w}" height="{h}" fill="url(#pt)"/>'
    elif pattern == "paisley":
        drop = "M40 10c22 0 34 22 26 42-7 18-30 26-44 14-14-12-6-30 8-30 10 0 14 10 8 16"
        defs = f'<pattern id="pt" width="110" height="110" patternUnits="userSpaceOnUse"><rect width="110" height="110" fill="{p}"/><path d="{drop}" fill="none" stroke="{a}" stroke-width="3" opacity=".9"/><circle cx="84" cy="88" r="5" fill="{a}"/></pattern>'
        body = f'<rect width="{w}" height="{h}" fill="url(#pt)"/>'
    else:  # arches
        arches = "".join(f'<path d="M{x} {h} V{h * .45} a{90} {90} 0 0 1 180 0 V{h}" fill="none" stroke="{a}" stroke-width="3" opacity="{op}"/>'
                         for x, op in ((80, .9), (330, .5), (580, .75), (830, .4), (1080, .6)))
        body = f'<rect width="{w}" height="{h}" fill="{p}"/>{arches}<circle cx="{w * .8}" cy="{h * .25}" r="120" fill="{a}" opacity=".25"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice">'
            f'<defs>{defs}</defs>{body}</svg>')


# ------------------------------------------------------------------ write
def manifest(shop):
    m = shopbuild.manifest(dict(shop, tagline=shop.get("tagline") or {}))
    m["background_color"] = shop["colours"]["bg"]
    return m


def write_site(app_dir: Path | str, shop: Dict[str, Any], card: Dict[str, Any]) -> Dict[str, Any]:
    app_dir = Path(app_dir)
    site = app_dir / "site"
    content = public_content(shop, card)
    _write(site / "content.json", json.dumps(content, ensure_ascii=False, indent=1))
    _write(site / "manifest.webmanifest", json.dumps(manifest(shop), ensure_ascii=False, indent=1))
    _write(site / "img" / "pattern.svg", pattern_svg(shop["pattern"], shop["colours"]))
    ini = shopbuild.initials(shop["name"])
    for s in (192, 512):
        _write(site / "icons" / f"icon-{s}.png", shopbuild.make_icon_png(s, shop["colours"]["primary"], shop["colours"]["accent"], ini), True)
    sw = site / "sw.js"
    if sw.exists():
        imgs = sorted({x for x in [content.get("logo")] + content.get("hero_images", []) if x})
        version = hashlib.sha256(json.dumps(content, sort_keys=True, default=str).encode()).hexdigest()[:10]
        t = re.sub(r'const VERSION = "[^"]*";', f'const VERSION = "{version}";', sw.read_text(encoding="utf-8"))
        t = re.sub(r"const EXTRA = [^;]*;", f"const EXTRA = {json.dumps(imgs)};", t)
        _write(sw, t)
    idx = site / "index.html"
    if idx.exists():
        lang = shop["default_language"]
        t = idx.read_text(encoding="utf-8")
        t = re.sub(r"<html[^>]*>", f'<html lang="{lang}" dir="{"rtl" if lang in RTL else "ltr"}">', t, count=1)
        t = re.sub(r"<title>.*?</title>", "<title>" + shopbuild._esc(shop["name"]) + "</title>", t, count=1)
        t = re.sub(r'<meta name="theme-color" content="[^"]*">', f'<meta name="theme-color" content="{shop["colours"]["primary"]}">', t)
        _write(idx, t)
    return content


def load_shop(app_dir) -> Dict[str, Any]:
    return json.loads((Path(app_dir) / "data" / "shop.json").read_text(encoding="utf-8"))


def save_shop(app_dir, shop: Dict[str, Any]) -> Dict[str, Any]:
    card = load_card(app_dir)
    shop = clean_shop(card, shop, Path(app_dir))
    shop["updated_at"] = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    _write(Path(app_dir) / "data" / "shop.json", json.dumps(shop, ensure_ascii=False, indent=1))
    write_site(app_dir, shop, card)
    return shop
