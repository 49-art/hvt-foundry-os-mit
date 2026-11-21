# Real-life guide: HVT Foundry Studio v0.3 on the high street

Plain English. Written 26 September 2026. Every price has its source page and the date it was checked. Where something could not be checked, it says so.

---

## 1. What you now have

- **The Studio** (this app). You use it on a laptop or tablet while you sit with a shop owner. It has new screens:
  - **Find for my business.** A live search for suppliers, stock, money help, delivery and storage, run in English *and* in the owner's own language. It searches the web and the map.
  - **Shop's own app.** Builds a real phone app for the shop, with the shop's name, colours, languages and prices.
  - **Connectors.** Plugs the Studio or a shop into outside services: free ones, open-source ones and paid ones.
  - **Settings.** Holds your search keys and the Studio password.
- **Each shop's own app.** It is a folder the shop owns. It has:
  - a public page that customers add to their phone's home screen
  - an owner-only admin page with a password
  - the connectors
- **All results are live, never made up.** Every search result shows its link, where it came from, and the time it was checked. It is labelled **"found live, not checked by us"**. Nothing is presented as recommended or checked.

## 2. Running it

### On your laptop (easiest, free)
1. Install Python 3 from https://www.python.org/downloads/ (Windows: tick "Add python.exe to PATH").
2. Unzip `HVT_Foundry_Studio_v3.zip`.
3. Double-click `Start HVT Foundry Studio (Mac).command` or `(Windows).bat`. Your browser opens at http://localhost:8000.

### On a tablet in a shop
- **Option A (no hosting):** run it on your laptop with `python3 studio/app.py --host 0.0.0.0`. Then open `http://<laptop IP>:8000` on the tablet. The laptop and tablet must be on the same Wi-Fi (your phone hotspot works). **Set a Studio password in Settings first.**
- **Option B (online, so you only need the tablet):** host it. See section 3.

The live search needs internet. Without internet the rest of the Studio still works, and the search screen tells you plainly that you're offline.

## 3. Putting the Studio online (optional)

The Studio saves its data to a file, so the host must keep files between restarts.

| Host | What it costs | Notes | Source (checked 26 Sept 2026) |
|---|---|---|---|
| **PythonAnywhere** | "Developer" plan **$10/month** | The free "Beginner" plan only lets apps reach a list of approved sites on the internet. The live search needs open internet, so use a paid plan. | https://www.pythonanywhere.com/pricing/ |
| **Render** | Paid web service from **$7/month** (0.5 CPU, 512 MB), plus a persistent disk at **$0.25 per GB per month** | The free web service loses its files when it restarts, so add a disk. | https://render.com/pricing |

How (Render, in outline):
1. Put the project in a **private** GitHub repository. The `.gitignore` already keeps keys, secrets and shop data out.
2. On Render, create a new Web Service from that repository.
   - Start command: `python3 studio/app.py --host 0.0.0.0 --port $PORT --no-browser`
   - Mount a disk at `studio/data`.
3. Add environment variables: `BRAVE_SEARCH_API_KEY` (optional), plus anything else you need.
4. **Open the Studio and set a Studio password in Settings straight away.** Until you do, anyone with the link can use it.

Not checked: Railway, Fly.io and others.

## 4. Publishing a shop's own app so customers can use it

The shop's public page is plain files: HTML, CSS, JavaScript, a manifest and icons. It needs no server.

| Where | Cost | Notes | Source (checked 26 Sept 2026) |
|---|---|---|---|
| **Cloudflare Pages** (recommended) | Free plan | 500 builds a month, 100 custom domains per project, up to 20,000 files, 25 MiB per file. | https://developers.cloudflare.com/pages/platform/limits/ (page updated 5 Sept 2026) |
| Netlify | Free plan with 300 credits. A production deploy costs 15 credits, and bandwidth costs 20 credits per GB. Personal plan $9/month. | Credits run out if you update the app often. | https://www.netlify.com/pricing/ |
| GitHub Pages | Free, but **not suitable** | GitHub's own limits page says Pages is not meant for running an online business or e-commerce. | https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits |

Steps (Cloudflare Pages, "direct upload"):
1. In the Studio, build the shop's app, then press **Download the owner's app (zip)**. Unzip it.
2. On Cloudflare go to Workers & Pages → Create → Pages → **Upload assets**. Upload the **`site`** folder only.
3. You get an address like `magazin-carpati.pages.dev`. Put it on a QR code at the till.
4. After the owner changes prices in their admin page, upload the `site` folder again. It is rebuilt automatically every time they save.

**The owner-only admin page and the supplier list are never in `site/`.** The admin runs on the owner's own laptop: double-click `Start shop app (Mac).command` or `(Windows).bat`, then go to http://localhost:8080/admin.

**Add to home screen:**
- iPhone: open the address in Safari → Share → **Add to Home Screen**.
- Android: open it in Chrome → **Install app** (or menu → Add to Home screen).

After the first visit the app works offline.

**Own domain (for example magazincarpati.co.uk):** optional. Cloudflare Registrar charges .co.uk at cost. A third-party price tracker (https://cfdomainpricing.com/, updated 26 Sept 2026) lists **.co.uk at about US$5.30 a year**. That is not Cloudflare's own page, so **treat it as unverified** and check the price at purchase. Other registrars' prices were not checked (Namecheap blocked our check).

## 5. The door-to-door flow (how a visit goes)

1. **Open a session** for the shop type (for example "Central / Eastern European grocer-deli").
2. **Find for my business.** Tap what they need (Suppliers, Stock, Money, Delivery, Storage, or "Anything else"). Tap their community, type their postcode and press **Search live now**.
   - Show them results in their own language.
   - Tap **Save to this shop** on the ones they like. Saved results go into their private supplier list.
3. **Shop's own app.**
   - Type their name. Let *them* choose the colours; there are ideas from their heritage, or any colour they like.
   - Choose up to 4 languages, enter hours and a few products with *their* prices.
   - They choose their admin password.
   - Press **Build**. Show them the phone preview.
4. **Connectors** (if they want them): payment links (Stripe / Square / SumUp), a WhatsApp order button, a barcode lookup, exchange rates.
5. **Download the zip** and give it to them. It belongs to them (Constitution Art. VIII).

**Your pricing (Travis's own figures, not market-checked):** about **£3,000** for the build and starter setup, then **£20–25 a week** retainer for updates, publishing and support. Say clearly what the retainer covers. Also tell the owner that paid outside services (Stripe fees, Brave searches, WhatsApp Business messages and so on) are billed by those companies directly to them.

## 6. Web search keys (Settings screen)

The map search (OpenStreetMap) and postcode lookup are free and need no key. For **web** results:

- **Brave Search API (recommended).** https://api-dashboard.search.brave.com
  - Sign up and choose a plan. **Search is $5 per 1,000 requests, prepaid.** The page shows "free $5 credits every month" on some plans, but it is not clear from the page whether that applies to Search. Brave's FAQ says a credit card is needed even for the free plan. (Source: https://api-dashboard.search.brave.com/app/plans and https://brave.com/search/api/, checked 26 Sept 2026.)
  - Copy the key into **Settings → Brave Search API key**.
  - The Studio uses at most 6 searches per button press (you can change this). Results are kept for 24 hours, so repeating a search costs nothing.
- **SerpAPI** (optional; uses Bing): paste a key if you have one. The price was not checked today.
- **DuckDuckGo** (no key) is tried last. **It did not work from our cloud build computer on 26 Sept 2026**: DuckDuckGo asked it to prove it wasn't a robot. It may work from a home or phone connection, but that is not tested. When it's blocked, the Studio says so in plain words.

## 7. Connectors: what each one does and how to get its key

**Status words:**
- **working-tested**: we called the real service on 26 Sept 2026 and it worked.
- **code-ready-needs-key**: written from the vendor's official docs (checked on 26 Sept 2026). It works once a key is added, but it has *not* been tested with a real key.
- **unverified**: we could not read the official docs today, or the service needs a partner account. It is a starting point only.

**Where keys are kept:** the Studio's keys are in `studio/data/connectors/studio.secrets.json`. Each shop's keys are in `data/shop.secrets.json` in its app folder, or in the Studio per session. They stay on that computer. They are **never** put into a zip or git, and on screen they show masked (••••1234).

**Try test keys first** (Stripe `sk_test_…`, Square sandbox, Shippo `shippo_test_…`).

| Connector | Type | Cost | Status | How to get the key (plain steps) |
|---|---|---|---|---|
| postcodes.io | Location | Free, open source | working-tested | No key. |
| OpenStreetMap (Overpass) | Map | Free, open data | working-tested | No key. The free servers are sometimes busy (error 504); try again in a minute. |
| Open Food Facts | Stock / barcodes | Free, open data | working-tested | No key. In the shop admin, type a barcode to fill in the product name. |
| Frankfurter exchange rates | Money | Free, open source | working-tested | No key. These are European Central Bank reference rates, not what a bank charges. The ECB does not publish some currencies (AED, SAR, EGP). |
| WhatsApp order button | Messages | Free | working-tested | Just the shop's WhatsApp number. Customers tap it and a message with their basket opens. |
| Custom API | Any | — | working-tested (against frankfurter.dev) | See section 8. |
| Stripe payment links | Payments | No monthly fee. UK cards **1.5% + 20p** (https://stripe.com/gb/pricing, fact-check 25 Sept 2026) | code-ready-needs-key | dashboard.stripe.com → Developers → API keys. Copy the **secret key** (start with `sk_test_`). Safer: create a *restricted key* with write access to Prices and Payment Links. |
| Square payment links | Payments | Free plan **£0/month** plus card fees (https://squareup.com/gb/en/pricing, 25 Sept 2026) | code-ready-needs-key | developer.squareup.com → Applications → your app → Credentials. Copy the **access token**. Type `sandbox` while testing. |
| SumUp checkout | Payments | Not checked today (https://www.sumup.com/en-gb/pricing/) | code-ready-needs-key | me.sumup.com → Settings → For developers → API keys. You also need the merchant code. |
| Shopify | Online shop | Not checked today (https://www.shopify.com/uk/pricing) | code-ready-needs-key | Shopify admin → Settings → Apps and sales channels → Develop apps → create an app with `read_products` → install → copy the Admin API token (`shpat_…`). |
| WooCommerce | Online shop | Plugin is free and open source; the owner pays for hosting | code-ready-needs-key | WordPress admin → WooCommerce → Settings → Advanced → REST API → Add key (Read/Write). Only https sites work. |
| Twilio SMS | Messages | Not checked today (https://www.twilio.com/en-us/sms/pricing/gb) | code-ready-needs-key | console.twilio.com → copy the Account SID and Auth token. You also need a Twilio phone number. |
| Companies House | Checks | Free (needs a free account) | code-ready-needs-key (endpoint answered "401 needs key" on 26 Sept) | developer.company-information.service.gov.uk → register → create an application → REST API key. Use it to check a supplier is a real registered company. |
| Brave Search | Search | $5 per 1,000 searches (above) | code-ready-needs-key (endpoint answered "key required" on 26 Sept) | See section 6. |
| Shippo | Couriers | Not checked today (https://goshippo.com/pricing) | code-ready-needs-key | apps.goshippo.com → Settings → API → test token. UK carrier coverage not checked. |
| EasyPost | Couriers / addresses | Not checked today (https://www.easypost.com/pricing) | code-ready-needs-key | easypost.com → Account → API keys (a test key is available). |
| WhatsApp Business Cloud API | Messages | Meta charges per message; more message types are charged from 1 Oct 2026 (fact-check 25 Sept 2026) | **unverified** | Meta's developer docs would not load for us today. Needs a Meta Business account, an app, a phone number ID and a token. Outside a 24-hour customer chat, only pre-approved templates can be sent. |
| Xero | Accounting | Plans from **£18/month excl. VAT** (fact-check 25 Sept 2026). Custom connections cost extra (not checked) | **unverified** | Xero's developer pages need JavaScript, and we could not read them. You need a Xero "custom connection" client ID and secret. |
| Google Business Profile | Local presence | No charge listed, but Google must approve API access | **unverified** | Needs Google's approval and an OAuth sign-in. |
| Royal Mail Click & Drop | Couriers | Not checked | **unverified** | Click & Drop → Settings → Integrations → API key. The docs could not be read today. |
| Evri, Stuart, Uber Direct, Deliveroo, Uber Eats, Just Eat | Delivery | Paid | **unverified — listed only, no code** | These need a business or partner account, and their APIs aren't public enough to build against. Use their own sign-up pages. |

**In each shop's admin page:** Connectors tab → open a connector → paste the key → **Save keys** → **Test** → **Switch on**. Switched-on features appear in the app. For example, a product's pay link becomes a **Pay** button, and the WhatsApp number becomes an **Order on WhatsApp** button with the basket filled in.

## 8. Adding any other service yourself (Custom API)

For any open-source or paid service with a web API, no code is needed:

1. Connectors → **Add any other service**.
2. Give it a short name and paste its **base address** (for example `https://api.frankfurter.dev/v1`).
3. Choose the login type: none, API key in a header, bearer token, or username + password.
4. Add actions, one per line: `name, METHOD, /path/{placeholder}`. For example: `latest, GET, /latest`.
5. **Or** paste the service's **OpenAPI (Swagger) JSON** and press **Read the OpenAPI file**. It lists the endpoints and fills in the form for you. YAML files must be converted to JSON first.
6. Save, add the key (if it needs one), then press **Test**.

Tested live on 26 Sept 2026: frankfurter.dev v1 `/latest` (GBP → EUR 1.1622, PLN 5.0808, RON 6.1323, TRY 64.847), and an OpenAPI import of https://api.frankfurter.dev/v2/openapi.json (8 endpoints found).

## 8b. Card apps: the Hair Salon / Barber app (new 18 Oct 2026, Draft)

1. In the Studio, open **Card apps**. Pick a look (luxury salon, urban barber, Afro & textured hair, heritage barbershop and more).
2. Switch modules on or off with the owner. Each one says what it really is:
   - **working-tested:** it runs and has tests.
   - **needs a key:** it's written from the company's docs, but needs the shop's own account. Examples: deposits through Stripe, Square or SumUp, text reminders, Google Calendar.
   - **needs a server:** it needs the shop's app running on a computer that stays on. Examples: the walk-in queue, the admin page, live booking.
3. Fill in the shop's details, services (with how long each takes) and staff. Then press **Build**. The owner keeps the zip.
4. **No server yet?** Inside the zip, `static_copy/` is a version that can go on free hosting. Customers send their booking **request** by WhatsApp. It says clearly it is a request, not a booking.
5. Where to run the full app, and what it costs: **studio/HOSTING_OPTIONS.md**.

What to tell the owner, honestly:

- **Payments.** Deposits only work once their own Stripe, Square or SumUp account is connected. Until then, bookings that need a deposit come in as requests, and they take the deposit themselves.
- **No signal.** If a customer's phone has no signal, the app says "you are NOT booked". It sends the request when the signal comes back.
- **The walk-in queue.** The wait times are estimates, based on how long each service takes.

**Your pricing (Travis's own figures, not market-checked):** about **£3,000** for the build and starter setup, then **£20–25 a week** retainer.

## 9. What honestly isn't done

- **No web search results from our build computer.** DuckDuckGo first showed a robot check and then refused connections, and there is no Brave key. The web part is tested with a simulated network only. Map and postcode results are real.
- **Native-language search phrases were written carefully but not checked by native speakers.** Every one is labelled on screen. Please have a speaker check your main communities.
- **OpenStreetMap's free servers are sometimes busy (504 or a timeout).** On 26 Sept a storage search near HA1 1AA timed out twice. We made the search lighter and then it worked (4 self-storage places found). Busy moments can still happen; try again a minute later.
- **Community name matching on the map is rough.** For example, "halal" names match the Arabic community and "Romanian locksmith" once matched Romanian. It is limited to food shops for suppliers and stock, and always labelled "community name match", never "recommended".
- **Paid connectors have not been run with real keys.** WhatsApp Cloud, Xero, Google Business Profile and Royal Mail are unverified.
- **The shop's public app updates when you re-upload `site/`.** There is no automatic publishing yet.
- **Card apps (18 Oct 2026):** payments, texts and Google Calendar never run with real keys; new wording English only; chairs not counted separately from staff; still Draft (DR-2026-09-26-09).
- **Not reviewed:** owner-facing design (Stan Lee), the Studio actions (Chief Architect role vacant; founder-approved interim for the older ones, Draft for the card ones), and any legal or data-protection review of storing supplier details and keys.
