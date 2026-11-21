# Finishing notes — 25 September 2026 (plain English)

## What was finished

- **The repository now exists.** Every document from your 109-page PDF is now its own file, in the folders your README describes. The wording was not changed.
- **The Foundry Kernel code is written and working.** It checks four things in order: the Constitution is Approved, the data file loads, only real Agents get registered, and each Agent only does what its Office is allowed to do. The demo shows it saying "no" three times, as it should. **23 tests, all 23 pass.** (Your README says 17; the extra 6 check the pilot data.)
- **The data file (graph/foundry_graph.json) is built** from the Hair Salon pilot in your documents: 72 records, from the Constitution down to the salon owner's wish for stock alerts on their phone.
- **Vendor records were checked** against the vendors' own websites (25 Sep 2026). Most facts checked out. Some were out of date. For example, Apple Pay now works in 101 countries, not "70+". Stripe is available to businesses in 46 countries, not 170+. Xero includes payroll from its Grow plan in the UK. QuickBooks could not be checked.
- **The stock and review gaps are written up** as two draft how-to documents (DOC-0006 and DOC-0007).
- **A draft of the updated Object Model (HVT-0004 v0.2)** puts all the extra record types from HVT-0006 and HVT-0007 in one place, ready for one approval.
- **Every change is logged** as a Decision Record (DR-2026-09-25-01 to -06), all marked Draft.

## Added later the same night: HVT Foundry Studio

A working app on top of the kernel, for sitting with a business owner on a tablet. See **START_HERE.md** for how to start it (double-click the start file, then open http://localhost:8000). It walks through the whole DOC-0005 loop, saves everything, never deletes anything, and marks every output "pending human review". Tests: 47 of 47 pass (26 kernel tests + 21 app tests).

## Added 26 September 2026: Studio v0.2 (live search, shop apps, connectors)

- **Find for my business.** A live search in English and the owner's own language, for suppliers, stock, money help, delivery and storage. It uses the real map (OpenStreetMap) and web search. Every result has its link and the time it was checked, and is marked "found live, not checked by us".
- **The shop's own app.** A phone app for each shop with their name, colours, languages (including right-to-left) and prices. It has an owner-only admin page with a password, and the owner keeps the zip.
- **Connectors.**
  - 27 services in the catalogue, plus "add any API" (which can read OpenAPI files).
  - 5 connectors were tested live today: postcodes.io, OpenStreetMap, Open Food Facts, Frankfurter exchange rates and the WhatsApp order link, plus the Custom API.
  - The paid ones are written from the vendors' docs but need the owner's keys.
- **Tests:** 139 of 139 pass (47 old + 92 new). See studio/REAL_LIFE_GUIDE.md and decisions/DR-2026-09-26-08.
- **Not working from our computer:** DuckDuckGo web search (it blocked us). No Brave key yet. OpenStreetMap is sometimes busy.

## Added 18 October 2026: founder approval, and Studio v0.3 (the Salon / Barber card)

**Founder approval.** You said: "APPROVE EVERYTHING IN THE WAY YOU FEEL IT SHOULD BE." It's written down word for word in `decisions/DR-2026-10-18-01_Founder_Approval.md`.

- Documents with no one else named are now **Approved by Founder**. These are HVT-0002, HVT-0006, HVT-0007, the BusinessType queue, DOC-0001, DOC-0004 and DOC-0005.
- Where the rules ask for the Chief Architect, your approval stands **for now** (interim), because nobody holds that role. These are HVT-0003, HVT-0004, DOC-0006 and DOC-0007.
- Where a named person must sign (Raj, Stan Lee), the item says **"Approved by Founder; pending Raj"** (or Stan Lee). Nobody's signature was copied.
- Every changed document got a new version. Old versions are kept. Nothing was deleted.
- The CEO Agent is still refused every Studio action.

**The Salon / Barber card.**

- A shop gets a good app straight away. It can switch extra parts on or off, and each part says honestly whether it is working, needs a key, or needs a server.
- **Booking:**
  - A stylist can't be double-booked.
  - A time can be held while a deposit is paid.
  - All six problems the theory test found are fixed.
  - If the phone has no signal, the app says clearly "you are NOT booked".
- **The walk-in queue** works out waits chair by chair, using how long each service takes.
- **No server?** A copy of the app takes booking requests by WhatsApp instead.
- **Two demo shops**, clearly marked "(demo)". Phone and tablet screenshots were taken of both.
- **Tests:** 189 of 189 pass. That's the 142 from before plus 47 new ones, including all 29 theory-test cases.
- **This new card work is still Draft.** You hadn't seen it when you gave the approval. One line from you approves it.

## One important thing the README gets wrong

The README says the stock and review gaps still need a formal Engine Search. In fact that search was done and **approved by Raj on 4 September** (DR-2026-09-04-10). The answer was: no new Engine. Use Square or a simple sheet for stock alerts, and Google and WhatsApp for reviews. ENG-0005 (the stock ledger) is on hold by Raj's decision. So I did **not** write new Engine code or Engine specs. I wrote the two how-to documents instead. Your own records had already reserved them (DOC-0006 and DOC-0007).

## What was not done on purpose

- Nothing was marked Approved. Nobody's stamp was used.
- No Agents, people or chats were created. Nobody was contacted.
- ENG-0005 was not coded, because it is on hold.
- Facts that could not be checked are still marked unverified.

## What still needs you

See **OPEN_ITEMS.md**. The top three:

1. Raj's stamp on DOC-0008. Until then, the first live salon session (SES-0003) cannot run.
2. Raj's decision on the overlay (HVT-0006-OVL-0001) and DR-10a.
3. Your call on "Integration vs. Solution Component", which you asked the team to hold off on.
