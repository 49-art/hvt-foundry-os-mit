"""
Build a shop's public app files from its data (standard library only).

Used by HVT Foundry Studio when it generates a shop app, and by the shop's own
server.py whenever the owner saves changes in the admin page. The public files
in site/ never contain the owner's password, suppliers or any keys.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import struct
import zlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

RTL = {"ar", "fa", "ur", "ps", "ckb", "prs", "he"}
LANG_NAMES = {"en": "English", "ro": "Română", "pl": "Polski", "ar": "العربية", "tr": "Türkçe", "kmr": "Kurmancî",
              "ckb": "کوردی", "hi": "हिन्दी", "ur": "اردو", "bn": "বাংলা", "ta": "தமிழ்", "pa": "ਪੰਜਾਬੀ", "fr": "Français",
              "so": "Soomaali", "am": "አማርኛ", "zh": "中文", "pt": "Português", "bg": "Български", "lt": "Lietuvių",
              "uk": "Українська", "el": "Ελληνικά", "fa": "فارسی", "prs": "دری", "ps": "پښتو"}
DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
PBKDF2_ITER = 240_000


# ------------------------------------------------------------------ passwords
def hash_password(pw: str) -> str:
    if not pw or len(pw) < 6:
        raise ValueError("Password must be at least 6 characters.")
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode("utf-8"), bytes.fromhex(salt), PBKDF2_ITER).hex()
    return f"pbkdf2_sha256${PBKDF2_ITER}${salt}${h}"


def verify_password(pw: str, stored: str) -> bool:
    try:
        algo, it, salt, h = stored.split("$")
        if algo != "pbkdf2_sha256":
            return False
        calc = hashlib.pbkdf2_hmac("sha256", (pw or "").encode("utf-8"), bytes.fromhex(salt), int(it)).hex()
        return hmac.compare_digest(calc, h)
    except (ValueError, AttributeError):
        return False


# ---------------------------------------------------------------- validation
def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (name or "").lower()).strip("-")
    return s[:40] or "shop-" + secrets.token_hex(3)


def _txt(v, n=400) -> str:
    return str(v or "").strip()[:n]


def _ml(v, langs, n=400) -> Dict[str, str]:
    """Multi-language text: dict lang->text (a plain string goes to the first language)."""
    if isinstance(v, str):
        v = {langs[0]: v}
    return {k: _txt(t, n) for k, t in (v or {}).items() if k in langs and _txt(t, n)}


def clean_shop(d: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and tidy owner-entered shop data. Raises ValueError with a plain message."""
    name = _txt(d.get("name"), 80)
    if not name:
        raise ValueError("The shop needs a name.")
    langs = [l for l in (d.get("languages") or ["en"]) if l in LANG_NAMES][:4] or ["en"]
    col = d.get("colours") or {}
    colours = {}
    for k, default in (("primary", "#3D2C8D"), ("accent", "#F29E4C"), ("bg", "#FAF6F0"), ("text", "#1C1433")):
        v = col.get(k) or default
        if not HEX.match(v):
            raise ValueError(f"Colour {k} must look like #A1B2C3.")
        colours[k] = v
    hours = []
    by_day = {h.get("day"): h for h in (d.get("hours") or []) if isinstance(h, dict)}
    for day in DAYS:
        h = by_day.get(day, {})
        closed = bool(h.get("closed"))
        o, c = _txt(h.get("open"), 5), _txt(h.get("close"), 5)
        for t in (o, c):
            if t and not re.fullmatch(r"[0-2]\d:[0-5]\d", t):
                raise ValueError("Opening times must look like 08:30.")
        hours.append({"day": day, "open": o, "close": c, "closed": closed or not (o and c)})
    products = []
    for i, p in enumerate((d.get("products") or [])[:300]):
        pname = _ml(p.get("name"), langs, 120)
        if not pname:
            continue
        price = _txt(p.get("price"), 12).replace("£", "")
        if price and not re.fullmatch(r"\d{1,5}(\.\d{1,2})?", price):
            raise ValueError(f"Price for '{list(pname.values())[0]}' must be a number like 3.50.")
        link = _txt(p.get("pay_link"), 300)
        if link and not link.startswith("https://"):
            raise ValueError("Pay links must start with https://")
        products.append({"id": _txt(p.get("id"), 20) or f"p{i + 1}", "name": pname, "price": price,
                         "unit": _txt(p.get("unit"), 20), "category": _txt(p.get("category"), 60),
                         "description": _ml(p.get("description"), langs, 300), "pay_link": link,
                         "in_stock": p.get("in_stock", True) is not False, "barcode": re.sub(r"\D", "", str(p.get("barcode") or ""))[:14]})
    logo = d.get("logo") or ""
    if logo and not re.match(r"^data:image/(png|jpeg|webp|svg\+xml);base64,", logo):
        raise ValueError("Logo must be a PNG, JPG, WEBP or SVG picture.")
    if len(logo) > 900_000:
        raise ValueError("Logo picture is too big. Please use one under about 600 KB.")
    phone = re.sub(r"[^\d+ ]", "", _txt(d.get("phone"), 30))
    wa = re.sub(r"[^\d+]", "", _txt(d.get("whatsapp"), 30))
    feats = d.get("features") or {}
    out = {
        "name": name, "tagline": _ml(d.get("tagline"), langs, 160), "languages": langs,
        "default_language": d.get("default_language") if d.get("default_language") in langs else langs[0],
        "colours": colours, "logo": logo, "hours": hours, "hours_note": _ml(d.get("hours_note"), langs, 200),
        "address": _txt(d.get("address"), 200), "postcode": _txt(d.get("postcode"), 10).upper(),
        "lat": d.get("lat"), "lon": d.get("lon"),
        "phone": phone, "whatsapp": wa, "announcement": _ml(d.get("announcement"), langs, 240),
        "announcement_on": bool(d.get("announcement_on", True)),
        "products": products, "currency": "GBP",
        "features": {"whatsapp_order": bool(feats.get("whatsapp_order", bool(wa))), "pay_links": bool(feats.get("pay_links", True)),
                     "barcode_lookup": bool(feats.get("barcode_lookup", True))},
        "suppliers": [s for s in (d.get("suppliers") or []) if isinstance(s, dict)][:200],
        "demo": bool(d.get("demo")),
        "admin": {"password_hash": (d.get("admin") or {}).get("password_hash", "")},
        "made_with": "Built with HVT Foundry Studio (HVT Innovations). This app and its content belong to the shop.",
    }
    return out


def map_url(shop: Dict[str, Any]) -> str:
    from urllib.parse import quote
    if shop.get("lat") and shop.get("lon"):
        return f"https://www.openstreetmap.org/?mlat={shop['lat']}&mlon={shop['lon']}#map=18/{shop['lat']}/{shop['lon']}"
    q = ", ".join(x for x in [shop.get("address"), shop.get("postcode")] if x)
    return "https://www.openstreetmap.org/search?query=" + quote(q) if q else ""


def public_content(shop: Dict[str, Any]) -> Dict[str, Any]:
    """What customers see. No password hash, no suppliers, no keys."""
    keep = ["name", "tagline", "languages", "default_language", "colours", "hours", "hours_note", "address",
            "postcode", "phone", "whatsapp", "announcement", "announcement_on", "products", "currency", "features", "demo", "made_with"]
    c = {k: shop.get(k) for k in keep}
    c["dir"] = {l: ("rtl" if l in RTL else "ltr") for l in shop["languages"]}
    c["lang_names"] = {l: LANG_NAMES.get(l, l) for l in shop["languages"]}
    c["map_url"] = map_url(shop)
    c["logo"] = "logo." + _logo_ext(shop["logo"]) if shop.get("logo") else ""
    c["built_at"] = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    if not c["features"].get("pay_links"):
        c["products"] = [dict(p, pay_link="") for p in c["products"]]
    return c


def _logo_ext(data_url: str) -> str:
    m = re.match(r"^data:image/(png|jpeg|webp|svg\+xml);", data_url or "")
    return {"jpeg": "jpg", "svg+xml": "svg"}.get(m.group(1), m.group(1)) if m else "png"


# ---------------------------------------------------------------- PNG icons
_FONT = {  # 5x7 bitmap capitals, rows top->bottom, 5 bits each
    "A": "01110 10001 10001 11111 10001 10001 10001", "B": "11110 10001 10001 11110 10001 10001 11110",
    "C": "01111 10000 10000 10000 10000 10000 01111", "D": "11110 10001 10001 10001 10001 10001 11110",
    "E": "11111 10000 10000 11110 10000 10000 11111", "F": "11111 10000 10000 11110 10000 10000 10000",
    "G": "01111 10000 10000 10111 10001 10001 01111", "H": "10001 10001 10001 11111 10001 10001 10001",
    "I": "11111 00100 00100 00100 00100 00100 11111", "J": "00111 00010 00010 00010 00010 10010 01100",
    "K": "10001 10010 10100 11000 10100 10010 10001", "L": "10000 10000 10000 10000 10000 10000 11111",
    "M": "10001 11011 10101 10101 10001 10001 10001", "N": "10001 11001 10101 10011 10001 10001 10001",
    "O": "01110 10001 10001 10001 10001 10001 01110", "P": "11110 10001 10001 11110 10000 10000 10000",
    "Q": "01110 10001 10001 10001 10101 10010 01101", "R": "11110 10001 10001 11110 10100 10010 10001",
    "S": "01111 10000 10000 01110 00001 00001 11110", "T": "11111 00100 00100 00100 00100 00100 00100",
    "U": "10001 10001 10001 10001 10001 10001 01110", "V": "10001 10001 10001 10001 10001 01010 00100",
    "W": "10001 10001 10001 10101 10101 10101 01010", "X": "10001 10001 01010 00100 01010 10001 10001",
    "Y": "10001 10001 01010 00100 00100 00100 00100", "Z": "11111 00001 00010 00100 01000 10000 11111",
}


def _rgb(h: str):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def make_icon_png(size: int, bg: str, accent: str, letters: str) -> bytes:
    """A square app icon: shop colour, accent ring, up to 2 initials. Pure Python PNG."""
    B, A, W = _rgb(bg), _rgb(accent), (255, 255, 255)
    letters = "".join(ch for ch in letters.upper() if ch in _FONT)[:2]
    cx = cy = size / 2
    r_out, r_in = size * 0.40, size * 0.34
    px = size / (7 * 3.3) if letters else 0              # font pixel size
    glyph_w = (5 * len(letters) + (len(letters) - 1)) * px
    gx0, gy0 = cx - glyph_w / 2, cy - 3.5 * px
    rows = []
    for y in range(size):
        row = bytearray([0])
        for x in range(size):
            d = ((x + .5 - cx) ** 2 + (y + .5 - cy) ** 2) ** .5
            c = B
            if r_in <= d <= r_out:
                c = A
            if letters:
                gx, gy = (x + .5 - gx0) / px, (y + .5 - gy0) / px
                if 0 <= gy < 7 and gx >= 0:
                    idx, col = int(gx) // 6, int(gx) % 6
                    if idx < len(letters) and col < 5 and _FONT[letters[idx]].split()[int(gy)][col] == "1":
                        c = W
            row += bytes(c)
        rows.append(bytes(row))
    raw = zlib.compress(b"".join(rows), 9)

    def chunk(t, data):
        return struct.pack(">I", len(data)) + t + data + struct.pack(">I", zlib.crc32(t + data) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", raw) + chunk(b"IEND", b""))


def initials(name: str) -> str:
    words = [w for w in re.findall(r"[A-Za-z]+", name or "") if w.lower() not in ("the", "and", "of", "demo")]
    return "".join(w[0] for w in words[:2]).upper() or ""


# ------------------------------------------------------------------ writing
def manifest(shop: Dict[str, Any]) -> Dict[str, Any]:
    lang = shop["default_language"]
    return {"name": shop["name"], "short_name": shop["name"][:12], "lang": lang,
            "dir": "rtl" if lang in RTL else "ltr", "start_url": "./", "scope": "./", "display": "standalone",
            "background_color": shop["colours"]["bg"], "theme_color": shop["colours"]["primary"],
            "description": (shop.get("tagline") or {}).get(lang, shop["name"]),
            "icons": [{"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
                      {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]}


def _write(p: Path, data, binary=False):
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    (tmp.write_bytes(data) if binary else tmp.write_text(data, encoding="utf-8"))
    os.replace(tmp, p)


def write_site(app_dir: Path | str, shop: Dict[str, Any]) -> Dict[str, Any]:
    """(Re)build site/content.json, manifest, icons, logo and the service worker version."""
    app_dir = Path(app_dir)
    site = app_dir / "site"
    content = public_content(shop)
    _write(site / "content.json", json.dumps(content, ensure_ascii=False, indent=1))
    _write(site / "manifest.webmanifest", json.dumps(manifest(shop), ensure_ascii=False, indent=1))
    ini = initials(shop["name"])
    for s in (192, 512):
        _write(site / "icons" / f"icon-{s}.png", make_icon_png(s, shop["colours"]["primary"], shop["colours"]["accent"], ini), True)
    for old in site.glob("logo.*"):
        old.unlink()
    if shop.get("logo"):
        _write(site / content["logo"], base64.b64decode(shop["logo"].split(",", 1)[1]), True)
    sw = (site / "sw.js")
    if sw.exists():
        version = hashlib.sha256(json.dumps(content, sort_keys=True).encode()).hexdigest()[:10]
        txt = re.sub(r'const VERSION = "[^"]*";', f'const VERSION = "{version}";', sw.read_text(encoding="utf-8"))
        txt = re.sub(r"const LOGO = [^;]*;", f"const LOGO = {json.dumps(content['logo'])};", txt)
        _write(sw, txt)
    idx = site / "index.html"
    if idx.exists():   # bake name, colours and language into the first paint (works before JS loads)
        lang = shop["default_language"]
        t = idx.read_text(encoding="utf-8")
        t = re.sub(r'<html[^>]*>', f'<html lang="{lang}" dir="{"rtl" if lang in RTL else "ltr"}">', t, count=1)
        t = re.sub(r"<title>.*?</title>", "<title>" + _esc(shop["name"]) + "</title>", t, count=1)
        t = re.sub(r'<meta name="theme-color" content="[^"]*">', f'<meta name="theme-color" content="{shop["colours"]["primary"]}">', t)
        _write(idx, t)
    return content


def _esc(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load_shop(app_dir: Path | str) -> Dict[str, Any]:
    return json.loads((Path(app_dir) / "data" / "shop.json").read_text(encoding="utf-8"))


def save_shop(app_dir: Path | str, shop: Dict[str, Any]) -> Dict[str, Any]:
    shop = clean_shop(shop)
    shop["updated_at"] = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    _write(Path(app_dir) / "data" / "shop.json", json.dumps(shop, ensure_ascii=False, indent=1))
    write_site(app_dir, shop)
    return shop
