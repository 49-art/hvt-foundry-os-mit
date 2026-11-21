"""
"Shop's own app" generator for HVT Foundry Studio.

Turns the shop details entered in the Studio into a standalone folder the shop
owns: a Progressive Web App (installs on a phone, works offline) + a tiny
standard-library server with an owner admin page + optional connectors.
It can be exported as a zip with the shop's name on it. Keys/secrets are never
put in the zip.
"""
from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path
from typing import Any, Dict, Optional

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "shop_template"
import sys
sys.path.insert(0, str(TEMPLATE))
import shopbuild  # noqa: E402

LIB_FILES = ["netutil.py", "live_search.py", "communities.py"]
EXCLUDE_NAMES = {"__pycache__", ".DS_Store"}
SECRET_SUFFIXES = (".secrets.json",)


def generate(shop_input: Dict[str, Any], out_dir: Path | str, password: Optional[str] = None,
             existing_hash: str = "") -> Dict[str, Any]:
    """Create or refresh the app folder. Returns the cleaned shop (without the hash)."""
    out = Path(out_dir)
    shop = dict(shop_input)
    if password:
        shop["admin"] = {"password_hash": shopbuild.hash_password(password)}
    elif existing_hash:
        shop["admin"] = {"password_hash": existing_hash}
    shop = shopbuild.clean_shop(shop)
    if not shop["admin"]["password_hash"]:
        raise ValueError("Set an owner password for the admin page (6+ characters).")
    out.mkdir(parents=True, exist_ok=True)
    for item in ("site", "admin"):
        dst = out / item
        dst.mkdir(parents=True, exist_ok=True)
        for f in (TEMPLATE / item).iterdir():
            if f.is_file():
                shutil.copy2(f, dst / f.name)
    for f in ("server.py", "shopbuild.py", "Start shop app (Mac).command", "Start shop app (Windows).bat"):
        shutil.copy2(TEMPLATE / f, out / f)
    lib = out / "lib"
    if lib.exists():
        shutil.rmtree(lib)
    lib.mkdir()
    for f in LIB_FILES:
        shutil.copy2(HERE / f, lib / f)
    shutil.copytree(HERE / "connectors", lib / "connectors", ignore=shutil.ignore_patterns("__pycache__"))
    (out / "README.md").write_text((TEMPLATE / "README_TEMPLATE.md").read_text(encoding="utf-8").replace("{name}", shop["name"]),
                                   encoding="utf-8")
    (out / "OWNERSHIP.txt").write_text(
        f"This app, its files and its content belong to {shop['name']}.\n"
        "The shop may copy, change, host or hand it to anyone it chooses. No licence fee is due to HVT Innovations to keep using it.\n"
        "The code inside is standard Python and JavaScript with no outside libraries.\n", encoding="utf-8")
    saved = shopbuild.save_shop(out, shop)
    return public_summary(saved)


def public_summary(shop: Dict[str, Any]) -> Dict[str, Any]:
    s = {k: v for k, v in shop.items() if k != "admin"}
    s["password_set"] = bool(shop.get("admin", {}).get("password_hash"))
    return s


def export_zip(app_dir: Path | str, zip_path: Path | str) -> Dict[str, Any]:
    """Zip the app folder for the shop. Skips secrets, caches and __pycache__."""
    app_dir, zip_path = Path(app_dir), Path(zip_path)
    shop = shopbuild.load_shop(app_dir)
    top = shopbuild.slugify(shop["name"]) + "-app"
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    skipped, n = [], 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(app_dir.rglob("*")):
            rel = f.relative_to(app_dir)
            if any(p in EXCLUDE_NAMES for p in rel.parts) or not f.is_file():
                continue
            if f.name.endswith(SECRET_SUFFIXES) or f.name.endswith(".tmp") or "cache" in f.name:
                skipped.append(str(rel))
                continue
            info = zipfile.ZipInfo(f"{top}/{rel.as_posix()}")
            info.external_attr = (0o755 if f.suffix in (".command", ".py") else 0o644) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, f.read_bytes())
            n += 1
    return {"zip": str(zip_path), "files": n, "skipped_secrets": skipped, "top_folder": top}
