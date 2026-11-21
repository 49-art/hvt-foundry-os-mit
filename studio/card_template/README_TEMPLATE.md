# {name} — your shop's own app

**This app belongs to {name}.** The files, the content and the name are yours. There is no lock-in and no
licence fee to HVT Innovations to keep using it. Built from the HVT Foundry **{card}** card template.

## What's in this folder

| Folder / file | What it is |
|---|---|
| `site/` | The app customers use (works on phones, installs to the home screen, works offline). |
| `site/queue.html` | The walk-in queue board for a TV or tablet (if the queue is switched on). |
| `admin/` | Your owner page: prices, team, photos, bookings, modules on/off, everything. |
| `data/shop.json` | Your shop information and a scrambled copy of your password. |
| `data/card.json` | The card template: every module this app can switch on. |
| `data/private/` | Bookings, client records, vouchers, loyalty cards, rota. **Private. Back it up. Never share it.** |
| `server.py` | The small program that runs the app, the booking engine and the admin page. |
| `lib/` | The engines (booking, queue, loyalty…) and optional connectors (payments, SMS, calendar). |

Private things are never put in `site/` and never in an exported zip: your password, client records,
bookings, vouchers, suppliers and any keys you add (`data/shop.secrets.json`).

## Start it (3 steps)

1. Install Python 3 (free) from https://www.python.org/downloads/ (Windows: tick "Add python.exe to PATH").
2. Double-click `Start shop app (Mac).command` or `Start shop app (Windows).bat` (or type `python3 server.py`).
3. Open **http://localhost:8080** (the app), **http://localhost:8080/admin** (your owner page) and
   **http://localhost:8080/queue** (the queue board). Forgot the password? Run `python3 server.py --set-password`.

## Putting it online — what works where (plain truth)

* **Running `server.py`** (on a shop computer, a small always-on PC, or any host that runs Python):
  everything works — live booking, no-double-booking, queue, loyalty, vouchers, admin.
* **Uploading only the `site/` folder** to a free static host: customers still see the full app (services,
  prices, team, gallery, reviews, hours, map, WhatsApp/call buttons). Booking falls back to a WhatsApp
  message with the service, day and time filled in; the live queue, stamp and voucher checks need `server.py`.

Making `server.py` reachable from the internet (a host or a tunnel) is a set-up step HVT does with you;
it is not done automatically.

## Modules

Open **admin → Modules** to switch features on or off. Each shows its honest status: **working** (no key
needed), **needs key** (add your own account key in admin → Connectors), **link only**, or **unverified**,
plus any vendor price we checked, with the date and source. Nothing is ever sent to customers without you
pressing a button.

## Client records and GDPR

If you switch on client records: allergy and patch-test details are health data. The app only stores them
with the client's consent tick (it records when and the wording), keeps them on this computer only, and lets
you export or erase a client's record when they ask. This is a safeguard, not legal advice — see the ICO's
guidance for small businesses.
