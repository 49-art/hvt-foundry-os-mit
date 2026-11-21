"""Shop's own app: build, public content, RTL, password, zip, and the shop's server.
python3 -m pytest studio/test_shop_app.py -q"""
import importlib.util
import json
import threading
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

import pytest

import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "demo_shops"))
import shop_app  # noqa: E402
from shop_app import shopbuild  # noqa: E402
from make_demos import ARABIC, ROMANIAN  # noqa: E402

SUPPLIER = {"title": "Secret Wholesale Ltd", "url": "https://www.openstreetmap.org/node/1", "checked_at": "2026-09-26T08:00:00+01:00"}


@pytest.fixture
def ar_app(tmp_path):
    shop_app.generate(dict(ARABIC, suppliers=[SUPPLIER]), tmp_path / "ar", password="owner-pass-1")
    return tmp_path / "ar"


def test_password_hashing():
    h = shopbuild.hash_password("abcdef")
    assert h != "abcdef" and shopbuild.verify_password("abcdef", h) and not shopbuild.verify_password("abcdeg", h)
    with pytest.raises(ValueError):
        shopbuild.hash_password("123")


def test_rtl_manifest_icons_and_html(ar_app):
    site = ar_app / "site"
    c = json.loads((site / "content.json").read_text(encoding="utf-8"))
    assert c["dir"] == {"ar": "rtl", "en": "ltr"} and c["default_language"] == "ar" and c["demo"] is True
    html = (site / "index.html").read_text(encoding="utf-8")
    assert 'lang="ar"' in html and 'dir="rtl"' in html
    m = json.loads((site / "manifest.webmanifest").read_text(encoding="utf-8"))
    assert m["name"] == "Halawiyat Al-Sham (demo)" and m["theme_color"] == ARABIC["colours"]["primary"]
    assert m["display"] == "standalone" and {i["sizes"] for i in m["icons"]} >= {"192x192", "512x512"}
    for i in m["icons"]:
        assert (site / i["src"]).read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_public_content_hides_password_hash_and_suppliers(ar_app):
    pub = (ar_app / "site" / "content.json").read_text(encoding="utf-8")
    assert "Secret Wholesale" not in pub and "pbkdf2" not in pub and "password" not in pub
    private = shopbuild.load_shop(ar_app)
    assert private["suppliers"][0]["title"] == "Secret Wholesale Ltd"
    assert private["admin"]["password_hash"].startswith("pbkdf2")


def test_validation_messages():
    with pytest.raises(ValueError):
        shopbuild.clean_shop({"name": ""})
    with pytest.raises(ValueError):
        shopbuild.clean_shop({"name": "x", "colours": {"primary": "red"}})
    with pytest.raises(ValueError):
        shopbuild.clean_shop({"name": "x", "products": [{"name": {"en": "a"}, "price": "£abc"}]})
    with pytest.raises(ValueError):
        shopbuild.clean_shop({"name": "x", "products": [{"name": {"en": "a"}, "pay_link": "http://insecure"}]})
    with pytest.raises(ValueError):
        shop_app.generate({"name": "No password"}, Path("/tmp/never-used-hvt"), password=None)


def test_zip_leaves_out_secrets_and_caches(ar_app):
    (ar_app / "data").mkdir(exist_ok=True)
    (ar_app / "data" / "shop.secrets.json").write_text('{"credentials": {"stripe": {"secret_key": "sk_live_SHOULDNOTSHIP"}}}')
    (ar_app / "lib" / "__pycache__").mkdir(exist_ok=True)
    (ar_app / "lib" / "__pycache__" / "x.pyc").write_bytes(b"x")
    info = shop_app.export_zip(ar_app, ar_app.parent / "out.zip")
    names = zipfile.ZipFile(info["zip"]).namelist()
    assert not any("secrets" in n or "__pycache__" in n for n in names)
    assert any(n.endswith("site/index.html") for n in names) and any(n.endswith("server.py") for n in names)
    assert any(n.endswith("lib/connectors/payments.py") for n in names)
    assert "data/shop.secrets.json" in info["skipped_secrets"]
    blob = b"".join(zipfile.ZipFile(info["zip"]).read(n) for n in names)
    assert b"SHOULDNOTSHIP" not in blob


def _load_server(app_dir):
    spec = importlib.util.spec_from_file_location(f"shopserver_{app_dir.name}", app_dir / "server.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_shop_server_login_admin_and_public_pages(tmp_path):
    shop_app.generate(dict(ROMANIAN, suppliers=[SUPPLIER]), tmp_path / "ro", password="owner-pass-1")
    mod = _load_server(tmp_path / "ro")
    calls = []

    def fake(url, method="GET", headers=None, data=None, timeout=20, contact=""):
        calls.append(url)
        return 200, {}, json.dumps({"status": 1, "product": {"product_name": "Chips", "brands": "Lay's"}}).encode()
    app = mod.App(tmp_path / "ro", fetcher=fake)
    httpd = mod.ThreadingHTTPServer(("127.0.0.1", 0), mod.make_handler(app))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{httpd.server_address[1]}"

    def req(path, body=None, cookie=""):
        r = urllib.request.Request(base + path, method="POST" if body is not None else "GET",
                                   data=json.dumps(body).encode() if body is not None else None,
                                   headers={"Content-Type": "application/json", "Cookie": cookie})
        try:
            with urllib.request.urlopen(r) as resp:
                return resp.status, resp.read(), resp.headers
        except urllib.error.HTTPError as e:
            return e.code, e.read(), e.headers
    try:
        code, body, _ = req("/")
        assert code == 200 and b'lang="ro"' in body
        code, body, _ = req("/content.json")
        assert b"Secret Wholesale" not in body
        assert req("/api/admin/shop")[0] == 401
        assert req("/api/login", {"password": "wrong"})[0] == 403
        code, _, h = req("/api/login", {"password": "owner-pass-1"})
        assert code == 200
        cookie = h["Set-Cookie"].split(";")[0]
        code, body, _ = req("/api/admin/shop", cookie=cookie)
        shop = json.loads(body)
        assert code == 200 and shop["suppliers"][0]["title"] == "Secret Wholesale Ltd" and "password_hash" not in json.dumps(shop)
        shop["products"][0]["price"] = "5.25"
        assert req("/api/admin/shop", shop, cookie=cookie)[0] == 200
        assert '"5.25"' in (tmp_path / "ro" / "site" / "content.json").read_text(encoding="utf-8")
        code, body, _ = req("/api/admin/connectors/open_food_facts/run", {"action": "barcode", "params": {"barcode": "5900259128843"}}, cookie=cookie)
        assert code == 200 and json.loads(body)["result"]["brands"] == "Lay's" and "openfoodfacts" in calls[0]
        code, body, _ = req("/api/admin/connectors/stripe/credentials", {"values": {"secret_key": "sk_test_ABCDEFGH1234"}}, cookie=cookie)
        assert json.loads(body)["saved"] == {"secret_key": "••••1234"}
        code, body, _ = req("/api/admin/connectors", cookie=cookie)
        assert b"sk_test_ABCDEFGH1234" not in body
        for _ in range(5):
            req("/api/login", {"password": "bad"})
        assert b"Too many" in req("/api/login", {"password": "owner-pass-1"})[1]     # rate limited
    finally:
        httpd.shutdown(); httpd.server_close()
