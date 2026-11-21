"""
Card app generator for HVT Foundry Studio.

    card template (studio/cards/defs/*.json)  +  the shop's details and module choices
        →  the shop's own app folder (PWA + admin + engines + server), exportable as a zip.

Keys and private data are never exported: the zip skips data/private/, *.secrets.json and caches.
"""
from __future__ import annotations

import json
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, Optional

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "card_template"
SHOP_TEMPLATE = HERE / "shop_template"
for p in (str(TEMPLATE), str(SHOP_TEMPLATE), str(HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)
import cardbuild  # noqa: E402
import cards  # noqa: E402

LIB_FILES = ["netutil.py", "live_search.py", "communities.py"]
EXCLUDE_DIRS = {"__pycache__", ".DS_Store", "private"}
SECRET_SUFFIXES = (".secrets.json",)


def generate(card_id: str, shop_input: Dict[str, Any], out_dir: Path | str, password: Optional[str] = None,
             existing_hash: str = "") -> Dict[str, Any]:
    """Create or refresh a card app folder. Returns the public summary (no password hash)."""
    card = cards.load_card(card_id)
    out = Path(out_dir)
    shop = dict(shop_input)
    if password:
        shop["admin"] = {"password_hash": cardbuild.hash_password(password)}
    elif existing_hash:
        shop["admin"] = {"password_hash": existing_hash}
    if not _has_data_images(shop):                             # early, friendly validation before copying files
        cardbuild.clean_shop(card, dict(shop, admin={"password_hash": "x"}))
    if not (shop.get("admin") or {}).get("password_hash"):
        raise ValueError("Set an owner password for the admin page (6+ characters).")
    out.mkdir(parents=True, exist_ok=True)
    for item in ("site", "admin"):
        dst = out / item
        dst.mkdir(parents=True, exist_ok=True)
        for f in (TEMPLATE / item).iterdir():
            if f.is_file():
                shutil.copy2(f, dst / f.name)
    for f in ("server.py", "cardbuild.py", "Start shop app (Mac).command", "Start shop app (Windows).bat"):
        shutil.copy2(TEMPLATE / f, out / f)
    shutil.copy2(SHOP_TEMPLATE / "shopbuild.py", out / "shopbuild.py")
    lib = out / "lib"
    if lib.exists():
        shutil.rmtree(lib)
    lib.mkdir()
    for f in LIB_FILES:
        shutil.copy2(HERE / f, lib / f)
    shutil.copy2(HERE / "cards" / "__init__.py", lib / "cards_runtime.py")
    shutil.copytree(HERE / "connectors", lib / "connectors", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(HERE / "engines", lib / "engines", ignore=shutil.ignore_patterns("__pycache__"))
    (out / "data").mkdir(exist_ok=True)
    (out / "data" / "private").mkdir(exist_ok=True)
    (out / "data" / "card.json").write_text(json.dumps(card, ensure_ascii=False, indent=1), encoding="utf-8")
    name = shop.get("name") or "Shop"
    (out / "README.md").write_text((TEMPLATE / "README_TEMPLATE.md").read_text(encoding="utf-8")
                                   .replace("{name}", name).replace("{card}", card["title"]), encoding="utf-8")
    (out / "OWNERSHIP.txt").write_text(
        f"This app, its files and its content belong to {name}.\n"
        "The shop may copy, change, host or hand it to anyone it chooses. No licence fee is due to HVT Innovations to keep using it.\n"
        "The code inside is standard Python and JavaScript with no outside libraries.\n", encoding="utf-8")
    saved = cardbuild.save_shop(out, shop)
    return public_summary(saved)


def _has_data_images(shop: Dict[str, Any]) -> bool:
    return "data:image/" in json.dumps(shop)[:5_000_000]


def public_summary(shop: Dict[str, Any]) -> Dict[str, Any]:
    s = {k: v for k, v in shop.items() if k not in ("admin", "suppliers")}
    s["password_set"] = bool(shop.get("admin", {}).get("password_hash"))
    return s


def export_zip(app_dir: Path | str, zip_path: Path | str) -> Dict[str, Any]:
    """Zip the app for the shop. Skips data/private/, secrets, caches and __pycache__."""
    app_dir, zip_path = Path(app_dir), Path(zip_path)
    shop = cardbuild.load_shop(app_dir)
    top = cardbuild.slugify(shop["name"]) + "-app"
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    skipped, n = [], 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(app_dir.rglob("*")):
            rel = f.relative_to(app_dir)
            if not f.is_file() or "__pycache__" in rel.parts or f.name == ".DS_Store":
                continue
            if "private" in rel.parts or f.name.endswith(SECRET_SUFFIXES) or f.name.endswith(".tmp") or "cache" in f.name:
                skipped.append(str(rel))
                continue
            info = zipfile.ZipInfo(f"{top}/{rel.as_posix()}")
            info.external_attr = (0o755 if f.suffix in (".command", ".py") else 0o644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, f.read_bytes())
            n += 1
        z.writestr(f"{top}/data/private/README.txt", "Private data (bookings, clients, vouchers) is created here when the app runs. It is never exported.\n")
        # A simple static copy for free static hosting, for when there is no always-on server (theory test B21):
        # customer pages only, booking by WhatsApp request, nothing that needs the server.
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            info_static = cardbuild.write_static_site(app_dir, Path(tmp) / "static_copy")
            for f in sorted((Path(tmp) / "static_copy").rglob("*")):
                if f.is_file():
                    z.writestr(f"{top}/static_copy/{f.relative_to(Path(tmp) / 'static_copy').as_posix()}", f.read_bytes())
                    n += 1
        z.writestr(f"{top}/static_copy/README.txt",
                   "Simple copy of the customer app for free static hosting (no server needed).\n"
                   "Booking becomes a WhatsApp REQUEST: customers are only booked when the shop replies.\n"
                   "Left out because they need the shop's server: " + (", ".join(info_static["left_out"]) or "nothing") + ".\n"
                   "There is no admin page in this copy. Change details in the full app, then export again.\n")
    return {"zip": str(zip_path), "files": n, "skipped_private": skipped, "top_folder": top,
            "static_copy_left_out": info_static["left_out"]}


def demo_preview(card_id: str, preset_id: str, out_dir: Path | str, choices: Optional[Dict[str, bool]] = None) -> Dict[str, Any]:
    """A throw-away preview app for the Studio screen: sample '(demo)' content in the chosen preset."""
    card = cards.load_card(card_id)
    pre = cards.preset(card, preset_id)
    import demo_content
    shop = demo_content.sample_shop(card, pre, choices or {})
    return generate(card_id, shop, out_dir, password="preview-only-" + preset_id)
