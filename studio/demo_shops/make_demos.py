"""Build the two DEMO shop apps (not real shops).

Everything here is invented for demonstration: names, prices, phone numbers
(Ofcom's drama range 07700 900xxx), and products. Every app shows a "demo" banner.
The Romanian and Arabic wording was written carefully but has NOT been checked
by a native speaker.

Run:  python3 demo_shops/make_demos.py      (demo password for both: demo-owner-2026)
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import shop_app  # noqa: E402

DEMO_PASSWORD = "demo-owner-2026"
WEEK = lambda o, c, sun=("10:00", "16:00"): [{"day": d, "open": o, "close": c} for d in ("mon", "tue", "wed", "thu", "fri", "sat")] + \
    [{"day": "sun", "open": sun[0], "close": sun[1]}]

ROMANIAN = {
    "name": "Magazin Carpați (demo)",
    "languages": ["ro", "en"],
    "tagline": {"ro": "Gusturi de acasă, în Harrow", "en": "A taste of home, in Harrow"},
    "announcement": {"ro": "DEMO — prețuri de exemplu, nu este un magazin real.",
                     "en": "DEMO — example prices, not a real shop."},
    "colours": {"primary": "#002B7F", "accent": "#FCD116", "bg": "#FFF8E7", "text": "#1B1B3A"},
    "phone": "07700 900123", "whatsapp": "+447700900123",
    "address": "Demo address (not a real shop), Harrow", "postcode": "HA3 5AA",
    "hours": WEEK("08:00", "21:00"),
    "products": [
        {"name": {"ro": "Telemea de oaie", "en": "Sheep's cheese (telemea)"}, "price": "4.99", "unit": "400 g", "category": "Lactate / Dairy"},
        {"name": {"ro": "Zacuscă de legume", "en": "Vegetable spread (zacuscă)"}, "price": "3.49", "unit": "300 g", "category": "Conserve / Jars"},
        {"name": {"ro": "Mici", "en": "Mici (grilling rolls)"}, "price": "6.50", "unit": "1 kg", "category": "Carne / Meat"},
        {"name": {"ro": "Pâine de casă", "en": "Homestyle bread"}, "price": "2.20", "unit": "1 loaf", "category": "Brutărie / Bakery"},
        {"name": {"ro": "Cozonac cu nucă", "en": "Walnut sweet bread (cozonac)"}, "price": "7.99", "unit": "500 g", "category": "Brutărie / Bakery"},
        {"name": {"ro": "Apă minerală", "en": "Mineral water"}, "price": "1.10", "unit": "1.5 L", "category": "Băuturi / Drinks"},
    ],
    "features": {"whatsapp_order": True, "pay_links": True, "barcode_lookup": True},
    "demo": True,
}

ARABIC = {
    "name": "Halawiyat Al-Sham (demo)",
    "languages": ["ar", "en"],
    "tagline": {"ar": "حلويات شرقية طازجة كل يوم", "en": "Fresh Middle Eastern sweets, every day"},
    "announcement": {"ar": "تجريبي — أسعار للعرض فقط، ليس متجراً حقيقياً.",
                     "en": "DEMO — example prices, not a real shop."},
    "colours": {"primary": "#0B6E4F", "accent": "#C8A951", "bg": "#FBF5E9", "text": "#20160C"},
    "phone": "07700 900456", "whatsapp": "+447700900456",
    "address": "Demo address (not a real shop), Harrow", "postcode": "HA3 5AA",
    "hours": WEEK("10:00", "22:00", ("12:00", "22:00")),
    "products": [
        {"name": {"ar": "بقلاوة بالفستق", "en": "Pistachio baklava"}, "price": "12.00", "unit": "500 g", "category": "Baklava"},
        {"name": {"ar": "كنافة نابلسية", "en": "Nabulsi kunafa"}, "price": "4.50", "unit": "1 slice", "category": "Kunafa"},
        {"name": {"ar": "معمول بالتمر", "en": "Date maamoul"}, "price": "6.00", "unit": "12 pieces", "category": "Biscuits"},
        {"name": {"ar": "بسبوسة", "en": "Basbousa (semolina cake)"}, "price": "3.00", "unit": "1 piece", "category": "Cakes"},
        {"name": {"ar": "علبة هدية مشكلة", "en": "Mixed gift box"}, "price": "25.00", "unit": "1 kg", "category": "Gifts"},
    ],
    "features": {"whatsapp_order": True, "pay_links": True, "barcode_lookup": False},
    "demo": True,
}

if __name__ == "__main__":
    for shop, folder in ((ROMANIAN, "magazin-carpati-demo"), (ARABIC, "halawiyat-al-sham-demo")):
        s = shop_app.generate(shop, HERE / folder, password=DEMO_PASSWORD)
        print("built", HERE / folder, "languages", s["languages"])
