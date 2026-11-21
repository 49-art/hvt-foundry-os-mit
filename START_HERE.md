# Start here (updated 20 Nov 2026)

Everything waiting on Raj and Stan Lee was decided on 20 Nov 2026: see `decisions/DR-2026-11-20-01` … `-12`.

```
python3 -m pytest -q            # 210 tests
python3 -m foundry_os status    # ENG-0004 Configurator (Prototype) + governance verifier
python3 -m foundry_os ladder foundry_os/examples/mina_theatre_SES-0002-F-0001.json
```

What still needs a real person is listed in OPEN_ITEMS.md.

---

# START HERE — HVT Foundry Studio

HVT Foundry Studio is an app you use on a tablet or laptop while you sit with a high-street business owner. It takes you through the **High-Street Tablet Design Loop** (DOC-0005) step by step. It runs on your own computer. **New in v0.2 (26 Sept 2026):** live search for suppliers and more (in the owner's own language), a real phone app for each shop, and connectors to outside services. Those parts use the internet, but only when you press Search, Test or Run. Everything else works offline. Read **studio/REAL_LIFE_GUIDE.md** for using it in real shops.

**New in v0.3 (18 Oct 2026):**

- **Founder approval.** On 18 Oct 2026 Travis said "APPROVE EVERYTHING IN THE WAY YOU FEEL IT SHOULD BE." What that approved, and what still waits for Raj, Stan Lee or the Chief Architect, is in `decisions/DR-2026-10-18-01_Founder_Approval.md`.
- **Card apps (Hair Salon / Barber).** A new **Card apps** screen. Pick a look, switch modules on or off, and build the shop's own app: booking with no double-booking, deposits, a walk-in queue with a TV board, and a WhatsApp version that needs no server. Every module shows an honest status. This part is still **Draft** (DR-2026-09-26-09), waiting for Travis to look at it.
- **Two demo shops** (invented, marked "(demo)"): a luxury salon and an urban barber. Screenshots: `studio_shots_v3/` in the governance pack.
- **Where a shop's app can live:** `studio/HOSTING_OPTIONS.md`.

## Start it in 3 steps

1. **Get Python 3** (free). Mac: most Macs already have it. If not, download it from https://www.python.org/downloads/. Windows: download it from the same page, and tick **"Add python.exe to PATH"** during install.
2. **Unzip** `HVT_Foundry_Studio_v3.zip` anywhere, for example on your Desktop.
3. **Double-click the start file** in the unzipped folder:
   - Mac: `Start HVT Foundry Studio (Mac).command`. The first time, macOS may block it: right-click it, choose **Open**, then **Open** again.
   - Windows: `Start HVT Foundry Studio (Windows).bat`

   Your browser opens at **http://localhost:8000**. If it doesn't, type that address into your browser yourself.

If you prefer typing, open a terminal in the unzipped folder and type `python3 studio/app.py`.

To stop the app, close the black terminal window (or press Ctrl+C in it). Your work is saved automatically in `studio/data/studio_state.json`.

**Using it on an iPad:** start it on a laptop with `python3 studio/app.py --host 0.0.0.0`. Then, on the iPad (on the same Wi-Fi), open `http://<the laptop's IP address>:8000`. Only do this on a network you trust, and **set a Studio password in Settings first** (it has none until you set one).

## What you'll see

| Screen | What it's for |
|---|---|
| **Boot** | The kernel checks its 4 safety gates. You'll see green PASS and red REFUSED. The red ones are *meant* to be refused; that proves the checks work. |
| **Sessions** | Start a session (SES-0004, SES-0005, …) for the kind of business in front of you. Hair Salon has full data. The other types show what's known and list the gaps. |
| Session **Step 2: Classify** | If the owner says "that's not quite us", type what they said. The owner's word wins. |
| Session **Step 3: Configure** | Pick size, budget and tech skill. The app shows the Foundry engines and the outside tools (Stripe, Square, …). Each tool has a label: **verified**, **partly** or **unverified**, based on the 25 Sept 2026 fact-check. |
| Session **Step 4: Owner review** | A plain-English summary to show the owner. They can say yes or no. |
| Session **Step 5: Wishes** | Type what the owner wants **in their own words**. |
| Session **Step 6: Close** | Locks the session. Wishes go to the review queue. |
| **Review queue** | Back at base, decide each wish: (a) re-configure with what exists, (b) log a formal Engine Search, or (c) out of scope for now. You can then offer the owner an updated setup in a follow-up session. |
| **Find for my business** | Live search: tap what the owner needs (suppliers, stock, money, delivery, storage), their community and postcode. Web + map results, each with its link, source and time checked, labelled "found live, not checked by us". Save the good ones to the shop. |
| **Shop's own app** (from a session) | Build the shop's installable phone app: their name, colours, up to 4 languages (Arabic/Farsi/Urdu right-to-left), hours, products and prices, owner password. Preview it, then download the zip the owner keeps. |
| **Connectors** | Free/open-source/paid services (postcodes, maps, barcodes, exchange rates, Stripe, Square, SumUp, Shopify, WooCommerce, WhatsApp, Twilio, Companies House, couriers…) plus "add any API". Each shows whether it is working-tested, code-ready-needs-key or unverified. |
| **Settings** | Brave Search key (for web results), Studio password. |
| **Audit log** | Every check and action, with who was allowed to do it and why. It includes buttons that try forbidden things, so you can watch them get refused. |

## Important things to know

- **Everything the app produces is "pending human review".** The founder approval of 18 Oct 2026 covers the governance documents listed in DR-2026-10-18-01, not what the app makes for a shop.
- **The owner saying "yes" is their own choice.** It is not a Foundry approval of anything.
- **Nothing is ever deleted.** Changes add a new version on top of the old one.
- **Sessions made here are practice/draft records.** They are kept in `studio/data/`, not in the official graph file. The first *official* live session (SES-0003) still waits on Raj's stamp on DOC-0008.
- **Size and tech-skill choices don't narrow the list yet.** The documents don't contain that information for any tool, so the app records your choice and says so instead of guessing. Budget does work, using only prices checked on the vendors' own websites.
- QuickBooks facts could not be checked, so it is marked **unverified** everywhere.

## For whoever maintains it

- Python standard library only. No installs are needed to run it. Tests need `pytest`.
- Run the tests from the project folder: `python3 -m pytest kernel/test_kernel.py studio/` (189 tests on 18 Oct 2026; the network is simulated).
- Real live run: `python3 studio/live_sample.py` writes `studio/LIVE_SEARCH_SAMPLE_OUTPUT.txt`.
- Demo shop apps (clearly marked demo, invented prices): `python3 studio/demo_shops/make_demos.py`, then `python3 server.py` inside a demo folder (password `demo-owner-2026`).
- Walk through the whole loop without a browser: start the app, then run `bash studio/curl_walkthrough.sh`
- Code: `studio/app.py` (web server), `studio/studio_core.py` (the loop logic), `studio/factcheck.py` (vendor fact-check data from DR-2026-09-25-04), `studio/static/` (screens).
- Design choices: see `decisions/DR-2026-09-25-07_HVT_Foundry_Studio.md`, `decisions/DR-2026-09-26-08_Studio_Live_Search_Shop_Apps_Connectors.md` and `decisions/DR-2026-09-26-09_Salon_Barber_Card_App_Template.md`.
- Card demo shops: `python3 studio/demo_shops/make_card_demos.py`, then `python3 server.py` inside a demo folder.
- Card code: `studio/cards/`, `studio/card_app.py`, `studio/card_template/`, `studio/engines/` (booking, walk-in queue, clients, messages).
- New code: `studio/live_search.py`, `studio/communities.py`, `studio/connectors/` (one file per service group), `studio/shop_app.py` + `studio/shop_template/`, `studio/static/find.js`.
