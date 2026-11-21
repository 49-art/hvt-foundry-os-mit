# Where a shop's app can live (hosting options)

Written 18 Oct 2026. Prices are only given where they were read on the company's own pricing page, with the date. Anything else says **price not checked**. Prices change: check again before you quote a shop.

## The two ways a shop's app can run

| Way | What works | What doesn't |
|---|---|---|
| **Full app** (needs a computer that stays on, "a server") | Live booking with no double-booking, deposits, walk-in queue and TV board, owner admin page, reminders | Needs hosting, and someone to look after it |
| **Static copy** (just files, no server) | The good-looking app, prices, opening times, call / WhatsApp / directions, and "send your booking request by WhatsApp" | No live booking (requests only, the shop confirms by hand), no queue, no admin page, no packages or retail stock |

The static copy is inside every exported zip, in the `static_copy/` folder.

## Options

| Option | Price (as read on the page) | Source and date checked | Good for | Notes |
|---|---|---|---|---|
| **The shop's own PC or laptop**, left on in the shop | No hosting fee | — | Trying it out; a shop that already keeps a PC on | Only reachable from outside the shop with extra setup (a tunnel). If the PC is off, booking stops. |
| **Render** (web service) | Hobby workspace $0 plus compute. Smallest paid instance ("less than 1 CPU", 512 MB) **$7 a month**. Disk **$0.25 per GB a month**. A free instance exists, with limits. | render.com/pricing, 18 Oct 2026 | One always-on shop app | The app keeps its bookings in a file, so it needs a disk on Render (the free instance has no lasting disk). |
| **PythonAnywhere** | Developer plan **$10 a month** (1 web app, 1 always-on task, 5 GB). Free plan has restricted internet access. | pythonanywhere.com/pricing, 18 Oct 2026 | People who want a simple dashboard | Needs a small adapter (WSGI) that **is not written yet**. On the free plan, payment and text-message services may be blocked. |
| **Hetzner** (rent a small server) | **Price not checked** | — | Running many shops' apps on one server | Needs someone comfortable with Linux. |
| **Cloudflare Pages** (static copy only) | Free plan | From the 26 Sept 2026 theory test (not re-checked) | The WhatsApp-request version | Check the current free-plan limits before relying on it. |

Other costs the shop pays directly to those companies (not to HVT):

- Stripe: UK cards **1.5% + 20p** (stripe.com/gb/pricing, checked 25 Sept 2026).
- Square: free plan £0 a month plus card fees (squareup.com/gb/en/pricing, checked 25 Sept 2026).
- SumUp, Twilio text messages, WhatsApp Business messages: **price not checked**.

## What HVT charges (Travis's own figures, not market-checked)

About **£3,000** for the build and starter setup, then **£20–25 a week** retainer. Decide, and tell the owner, whether hosting is inside the retainer or paid by the shop.

## Open question for Travis

Who hosts each shop's always-on app, and who pays for it. Nothing has been bought or set up.
