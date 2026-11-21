"""Build the two DEMO card apps for the Hair Salon / Barber card (not real shops).

Everything here is invented for demonstration and labelled "(demo)": shop names, staff
labels, prices, offers, example reviews and products. Phone numbers are from Ofcom's
drama range (07700 900xxx), which is never given to real people. Pictures are drawn
from simple shapes by demo_content.picture() - there are no photos of real people.
There is no real address; the map section shows that.

Run:   python3 demo_shops/make_card_demos.py            (demo owner password: demo-owner-2026)
Then:  SHOP_DEMO_NOW=2026-10-24T10:30 python3 demo_shops/card_demo_luxury/server.py --port 8081
       SHOP_DEMO_NOW=2026-10-24T10:30 python3 demo_shops/card_demo_barber/server.py --port 8082

SHOP_DEMO_NOW makes a DEMO shop act as if it were Saturday 24 Oct 2026 at 10:30, so the
screens look like a working morning whatever time you open them. It is ignored by real shops,
and the demo banner says the clock is set.
"""
import os
import importlib.util
import shutil
import sys
from datetime import timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import card_app  # noqa: E402
from demo_content import picture  # noqa: E402

DEMO_PASSWORD = "demo-owner-2026"
CARD = "CARD-HAIR-01"
DEMO_NOW = "2026-10-24T10:30"
DEMO_NOTE = "Demo clock set to Sat 24 Oct 2026, 10:30. Bookings, queue and alerts are invented."


def week(o, c, sun=None, closed=("mon",)):
    out = []
    for d in ("mon", "tue", "wed", "thu", "fri", "sat", "sun"):
        if d in closed:
            continue
        if d == "sun":
            if sun:
                out.append({"day": d, "open": sun[0], "close": sun[1]})
            continue
        out.append({"day": d, "open": o, "close": c})
    return out


LUX_COL = {"primary": "#1F1A17", "accent": "#C9A46A", "bg": "#F6EFE6", "text": "#1F1A17"}
LUXURY = {
    "name": "Maison Aurelle Salon (demo)", "preset": "luxury", "variant": "salon",
    "languages": ["en", "ar", "fr"],
    "tagline": {"en": "Colour, cut and care - an invented salon for the demo",
                "ar": "صالون تجريبي - محتوى للعرض فقط", "fr": "Salon fictif pour la démonstration"},
    "hours": week("09:30", "19:00", sun=("11:00", "16:00")),
    "hours_note": {"en": "Late opening Thursday (demo)"},
    "address": "No real address - demo shop", "postcode": "",
    "phone": "07700 900456", "whatsapp": "+447700900456", "email": "",
    "offer": {"en": "(demo) 15% off a first colour appointment - example offer text"}, "offer_on": True,
    "hero_images": [picture("dryer", LUX_COL, "demo image"), picture("scissors", LUX_COL, "demo image", variant=1)],
    "services": [
        {"id": "cut", "name": {"en": "Cut & blow-dry (demo)"}, "category": "Cuts", "duration_min": 60, "price_from": "55", "audience": "women", "hair_types": ["straight", "wavy", "curly"], "deposit": "10"},
        {"id": "mcut", "name": {"en": "Men's restyle (demo)"}, "category": "Cuts", "duration_min": 45, "price_from": "40", "audience": "men"},
        {"id": "balay", "name": {"en": "Balayage (demo)"}, "category": "Colour", "duration_min": 180, "price_from": "150", "audience": "anyone", "deposit": "30", "price_note": {"en": "Price depends on length (demo)"},
         "segments": "60 active, 45 processing, 75 active", "needs_patch_test": True},
        {"id": "roots", "name": {"en": "Root colour (demo)"}, "category": "Colour", "duration_min": 90, "price_from": "70", "audience": "anyone",
         "segments": "30 active, 30 processing, 30 active", "needs_patch_test": True},
        {"id": "silk", "name": {"en": "Silk press (demo)"}, "category": "Styling", "duration_min": 90, "price_from": "65", "audience": "anyone", "hair_types": ["curly", "coily"]},
        {"id": "bridal", "name": {"en": "Bridal trial (demo)"}, "category": "Occasion", "duration_min": 120, "price_from": "90", "audience": "women", "staff_ids": ["s1"]},
        {"id": "treat", "name": {"en": "Bond repair treatment (demo)"}, "category": "Treatments", "duration_min": 45, "price_from": "35", "audience": "anyone"},
    ],
    "staff": [
        {"id": "s1", "name": "Demo Stylist A", "role": {"en": "Creative director (demo)"}, "bio": {"en": "Invented profile for the demo - colour and bridal."}, "specialities": ["Balayage", "Bridal"], "commission": {"service": 40, "retail": 10}, "breaks": "13:00-13:30"},
        {"id": "s2", "name": "Demo Stylist B", "role": {"en": "Senior stylist (demo)"}, "bio": {"en": "Invented profile for the demo - curls and silk press."}, "specialities": ["Curly cuts", "Silk press"], "commission": {"service": 35, "retail": 10}, "breaks": "13:30-14:00"},
        {"id": "s3", "name": "Demo Stylist C", "role": {"en": "Stylist (demo)"}, "bio": {"en": "Invented profile for the demo."}, "specialities": ["Men's cuts"], "commission": {"service": 30, "retail": 10}, "breaks": "14:00-14:30"},
    ],
    "gallery": [{"image": picture(ic, LUX_COL, "demo image", variant=i), "caption": {"en": "demo image"}}
                for i, ic in enumerate(["scissors", "dryer", "bottle", "brush", "chair", "comb"])],
    "before_after": [{"before": picture("comb", LUX_COL, "before (demo)", variant=2), "after": picture("dryer", LUX_COL, "after (demo)", variant=3),
                      "caption": {"en": "Example pair (demo) - shapes only"}, "consent": True}],
    "reviews": [{"author": "Example review (demo)", "stars": 5, "text": "Invented text to show how reviews look. Not a real customer.", "source": "demo - not a real review"},
                {"author": "Example review 2 (demo)", "stars": 4, "text": "Invented text. A real shop only shows reviews it actually received.", "source": "demo - not a real review"}],
    "packages": [{"name": {"en": "Blow-dry club - 5 visits (demo)"}, "uses": 5, "price": "120", "valid_days": 180}],
    "products": [{"name": {"en": "Repair shampoo 250ml (demo)"}, "price": "18", "barcode": "", "image": picture("bottle", LUX_COL, "demo image", 600, 600)},
                 {"name": {"en": "Heat protect spray (demo)"}, "price": "16", "barcode": "", "image": picture("bottle", LUX_COL, "demo image", 600, 600, 1)}],
    "policy_text": {"en": "(demo) Please give 24 hours' notice to cancel or move. Example wording only - each shop writes its own."},
    "policy_short": "24 hours' notice please (demo)",
    "access_info": {"en": "(demo) Example: step-free entrance, quiet appointments on request."},
    "loyalty": {"stamps_needed": 8, "reward": "A free treatment (demo)"},
    "vouchers": {"valid_months": 12, "amounts": ["25", "50", "100"]},
    "booking": {"slot_minutes": 15, "buffer_minutes": 10, "min_notice_minutes": 120, "max_days_ahead": 60,
                "hold_minutes": 10, "late_cancel_hours": 24, "no_show_grace_minutes": 15, "deposit_after_no_shows": 1,
                "no_show_deposit": "10", "patch_test_gap_hours": 48},
    "modules": {"auto_booking": True, "deposits": True, "reminders": True, "gcal": True, "loyalty": True, "vouchers": True,
                "packages": True, "retail": True, "before_after": True, "client_records": True, "review_requests": True,
                "accessibility": True, "policy": True, "analytics": True, "rota": True},
    "demo": True, "demo_note": DEMO_NOTE,
}

BAR_COL = {"primary": "#111111", "accent": "#FFD23F", "bg": "#1B1B1B", "text": "#F4F4F4"}
BARBER = {
    "name": "Kerbside Cuts Barbers (demo)", "preset": "urban_barber", "variant": "barber",
    "languages": ["en", "tr", "pl"],
    "tagline": {"en": "Walk in or book - an invented barbershop for the demo",
                "tr": "Demo berber - yalnızca gösterim", "pl": "Fikcyjny barber - tylko demo"},
    "hours": week("09:00", "20:00", sun=("10:00", "16:00"), closed=()),
    "address": "No real address - demo shop", "postcode": "",
    "phone": "07700 900789", "whatsapp": "+447700900789",
    "offer": {"en": "(demo) Tuesday: kids cut + dad cut deal - example offer text"}, "offer_on": True,
    "hero_images": [picture("razor", BAR_COL, "demo image"), picture("chair", BAR_COL, "demo image", variant=1)],
    "services": [
        {"id": "fade", "name": {"en": "Skin fade (demo)"}, "category": "Cuts", "duration_min": 40, "price_from": "22", "audience": "men", "hair_types": ["any"]},
        {"id": "sciss", "name": {"en": "Scissor cut (demo)"}, "category": "Cuts", "duration_min": 30, "price_from": "18", "audience": "men"},
        {"id": "beard", "name": {"en": "Beard shape-up (demo)"}, "category": "Beard & shave", "duration_min": 20, "price_from": "12", "audience": "men"},
        {"id": "shave", "name": {"en": "Hot towel shave (demo)"}, "category": "Beard & shave", "duration_min": 30, "price_from": "20", "audience": "men"},
        {"id": "combo", "name": {"en": "Fade + beard (demo)"}, "category": "Cuts", "duration_min": 55, "price_from": "30", "audience": "men"},
        {"id": "kids", "name": {"en": "Kids cut (demo)"}, "category": "Kids", "duration_min": 25, "price_from": "14", "audience": "children"},
        {"id": "design", "name": {"en": "Hair design / lines (demo)"}, "category": "Extras", "duration_min": 15, "price_from": "5", "audience": "anyone"},
    ],
    "staff": [
        {"id": "b1", "name": "Demo Barber 1", "role": {"en": "Head barber (demo)"}, "bio": {"en": "Invented profile for the demo - fades and designs."}, "specialities": ["Fades", "Designs"], "commission": {"service": 50, "retail": 10}},
        {"id": "b2", "name": "Demo Barber 2", "role": {"en": "Barber (demo)"}, "bio": {"en": "Invented profile for the demo - beards and shaves."}, "specialities": ["Hot towel shave"], "commission": {"service": 45, "retail": 10}},
        {"id": "b3", "name": "Demo Barber 3", "role": {"en": "Barber (demo)"}, "bio": {"en": "Invented profile - walk-ins only in this demo."}, "bookable": False, "commission": {"service": 40, "retail": 10}},
    ],
    "gallery": [{"image": picture(ic, BAR_COL, "demo image", variant=i), "caption": {"en": "demo image"}}
                for i, ic in enumerate(["razor", "comb", "chair", "scissors"])],
    "reviews": [{"author": "Example review (demo)", "stars": 5, "text": "Invented text to show how reviews look. Not a real customer.", "source": "demo - not a real review"}],
    "products": [{"name": {"en": "Matte clay 100ml (demo)"}, "price": "12", "image": picture("bottle", BAR_COL, "demo image", 600, 600)},
                 {"name": {"en": "Beard oil 30ml (demo)"}, "price": "10", "image": picture("bottle", BAR_COL, "demo image", 600, 600, 1)}],
    "loyalty": {"stamps_needed": 6, "reward": "6th cut free (demo)"},
    "walkin": {"max_waiting": 20, "default_minutes": 30},
    "booking": {"slot_minutes": 10, "buffer_minutes": 0, "min_notice_minutes": 30, "max_days_ahead": 21},
    "modules": {"walkin_queue": True, "auto_booking": True, "loyalty": True, "retail": True, "rota": True,
                "referrals": True, "supplier_finder": True, "analytics": True, "reminders": True, "review_requests": True},
    "demo": True, "demo_note": DEMO_NOTE,
}


def _server(app_dir: Path):
    spec = importlib.util.spec_from_file_location(f"srv_{app_dir.name}", app_dir / "server.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.App(app_dir)


def _next_open(app, n=1):
    days = [d for d in app.booking.open_days(21) if not d.get("closed")]
    return days[n]["date"] if len(days) > n else days[-1]["date"]


def _try(what, fn):
    try:
        return fn()
    except Exception as e:  # noqa: BLE001
        print(f"  seed {what} skipped:", e)


def seed_luxury(app):
    """Invented bookings and records so the admin screens aren't empty. All names say (demo)."""
    from datetime import datetime
    today = app.now().date().isoformat()
    d1, d2 = _next_open(app, 1), _next_open(app, 2)
    cl = app.clients.save({"name": "Client B (demo)", "phone": "07700 900002", "consent": True,
                           "allergies": "None recorded (demo)", "hair_notes": "Invented record for the demo."})
    app.clients.add_patch_test(cl["id"], "Demo colour range (demo)", "clear", (app.now().date() - timedelta(days=5)).isoformat())
    app.clients.save({"name": "Client A (demo)", "phone": "07700 900001", "consent": True,
                      "allergies": "None recorded (demo)", "hair_notes": "Invented record for the demo."})
    # Client A's cut needs a £10 deposit. No payment firm is connected in the demo, so it comes in as a request;
    # the owner took the deposit at the desk, pressed "Deposit paid", then "Confirm".
    a = _try("request", lambda: app.book({"service_id": "cut", "staff_id": "s2", "date": today, "time": "12:30", "name": "Client A (demo)",
                                          "phone": "07700 900001", "accept_policy": True}))
    if a:
        bid = app.booking.get(a["ref"])["id"]
        app.booking.payment_result(bid, True, source="owner")
        app.booking.confirm(bid)
    for req in ({"service_id": "roots", "staff_id": "s1", "date": today, "time": "14:00", "name": "Client B (demo)", "phone": "07700 900002"},
                {"service_id": "treat", "staff_id": "any", "date": d1, "time": "14:00", "name": "Client C (demo)", "phone": "07700 900003"},
                {"service_id": "mcut", "staff_id": "s3", "date": d2, "time": "11:00", "name": "Client D (demo)", "phone": "07700 900004"}):
        _try("booking", lambda req=req: app.booking.create(dict(req, accept_policy=True), "instant"))
    # a booking that came in while no payment firm is connected: a request, deposit to take by hand
    _try("request", lambda: app.book({"service_id": "balay", "staff_id": "s1", "date": d2, "time": "11:00", "name": "Client B (demo)",
                                      "phone": "07700 900002", "accept_policy": True}))
    # the late-payment case, played out with the demo clock: held 20 minutes ago, hold ran out,
    # the time was re-booked, then the (demo) payment arrived -> refund due + alert for the owner
    real_now = app.booking.now
    app.booking.now = lambda: real_now() - timedelta(minutes=20)
    e = _try("held", lambda: app.booking.create({"service_id": "cut", "staff_id": "s3", "date": d1, "time": "15:00", "name": "Client E (demo)",
                                                   "phone": "07700 900005", "accept_policy": True}, "instant"))
    app.booking.now = real_now
    _try("rebook", lambda: app.booking.create({"service_id": "mcut", "staff_id": "s3", "date": d1, "time": "15:00", "name": "Client F (demo)",
                                                "phone": "07700 900006", "accept_policy": True}, "instant"))
    if e:
        _try("late payment", lambda: app.booking.payment_result(e["id"], True, source="demo"))
    c = app.loyalty.new_card("Client A (demo)", "07700 900001")
    app.loyalty.stamp(c["code"], 3, "demo")
    app.vouchers.issue("50", buyer="Client B (demo)", for_name="Friend (demo)")


def seed_barber(app):
    today = app.now().date().isoformat()
    # booked appointments in the same chairs, so the walk-in waits include them
    _try("booking", lambda: app.booking.create({"service_id": "combo", "staff_id": "b1", "date": today, "time": "11:00", "name": "Client D (demo)", "phone": "07700 900004"}, "instant"))
    _try("booking", lambda: app.booking.create({"service_id": "fade", "staff_id": "b2", "date": today, "time": "11:10", "name": "Client G (demo)", "phone": "07700 900007"}, "instant"))
    for name, svc, who, ph in (("Sam (demo)", "fade", "any", "07700 900011"), ("J. (demo)", "beard", "any", "07700 900012"),
                               ("Kai (demo)", "combo", "b1", "07700 900013"), ("R. (demo)", "kids", "any", "07700 900014")):
        _try("queue", lambda name=name, svc=svc, who=who, ph=ph: app.queue.join(name, svc, who, ph))
    t = _try("call", lambda: app.queue.call_next("b3"))
    if t:
        _try("chair", lambda: app.queue.set_status(t["no"], "in_chair"))
    d1 = _next_open(app, 1)
    _try("booking", lambda: app.booking.create({"service_id": "fade", "staff_id": "b1", "date": d1, "time": "12:00", "name": "Client D (demo)", "phone": "07700 900004"}, "instant"))
    c = app.loyalty.new_card("Client D (demo)", "07700 900004")
    app.loyalty.stamp(c["code"], 4, "demo")
    app.referrals.create("Client D (demo)", "07700 900004")


def build(fresh=True):
    os.environ["SHOP_DEMO_NOW"] = DEMO_NOW
    out = {}
    for folder, shop, seed in (("card_demo_luxury", LUXURY, seed_luxury), ("card_demo_barber", BARBER, seed_barber)):
        d = HERE / folder
        if fresh and d.exists():
            shutil.rmtree(d)
        card_app.generate(CARD, shop, d, password=DEMO_PASSWORD)
        seed(_server(d))
        out[folder] = str(d)
        print("built", folder)
    return out


if __name__ == "__main__":
    build()
