# DR-2026-09-04-10 — Decision Record — Engine Search (Art. II) for Stock / inventory and Review / reply on BUT-0001

Document ID: DR-2026-09-04-10  
Title: Decision Record — Engine Search (Art. II) for Stock / inventory and Review / reply on BUT-0001  
Version: 1.0  
Status: Approved  
Owner: Architecture Office (Howard / Leonard drafting)  
Reviewed By: Raj (CEO Office) — stamped 2026-09-04  
Dependencies: HVT-0001 Art. II, Art. VI.4, Art. VIII, Art. X, Art. XIV HVT-0003, HVT-0006 §2.3, HVT-0007 BUT-0001, PRB-0004, PRB-0005, WSH-0001 ENG-0001, ENG-0002, ENG-0003, SLC-0001–0008  

---

Application record: DR-2026-09-04-10a Durable path: artifacts/decisions/DR-2026-09-04-10_Engine_Search_Stock_and_Review.md

### DECISION (APPROVED)

1. STOCK — result: PARTIAL MATCH. No new Engine. Fulfilment = owner-owned / free connector first, then paid Square inventory if they already take cards on Square. Foundry work if any = a thin Commerce adapter later, not ENG-0005.

2. REVIEW — result: PARTIAL MATCH. No new Engine. Fulfilment = Google Business Profile (free) + WhatsApp Business app (free tier) + optional post-visit ask from ENG-0002. Foundry work if any = a procedure + optional connector card, not ENG-0006.

3. WSH-0001 (“owner wants stock alerts on phone”) stays linked to PRB-0004. Status move: Engine Search Required → Configured (connector path), pending owner plan.

4. Explicitly rejected Registering ENG-0005 Stock Engine or ENG-0006 Review Engine in this pass.

### SEARCH METHOD (Art. II.2 + proposed HVT-0007 practice)

Constitution Art. II.2 as written is (a) existing engine, (b) extend / parameterise / compose; only if both are no, with evidence, may new functionality be authorised.

This Search also applied a catalog step before authorising a new Engine (Architecture Office practice, not Art. II.2 text). Logged so it is not later cited as already constitutional.

For each gap we asked, in order: a. Does a registered Engine already solve this in whole or part? b. Can an existing Engine be extended / parameterised / composed? c. Can Tier 4 (owner already owns it) or Tier 1 (free / open) or a free tier of Tier 3 cover it? d. Only if a–c are no, with evidence, may a new Engine be authorised.

### SEARCH 1 — STOCK / INVENTORY

Problem: PRB-0004 Manual stock Capability: required on BUT-0001 Wish: WSH-0001 stock alerts on phone

a. Existing Engine? ENG-0003 Commerce = payments, receipts, memberships. It is not an inventory ledger. Stripe itself is not stock software. A Stripe App exists for quantity caps; that is a marketplace add-on, not ENG-0003. Partial at best: decrement after sale is a Commerce event, the catalogue is not.

ENG-0001 Customer = people, not SKUs. ENG-0002 Booking = time slots, not colour tubes.

b. Extend an existing Engine? Yes, later, as a Package on ENG-0003: “on payment success, decrement SKU.” That is an adapter, not a fifth Engine. Do not build it until we know where the SKU list lives (Square item library vs sheet vs owner notebook).
c. Connectors / owner-owned / free? Path S1 — owner already on Square (SLC-0002) Square Item Library + low-stock alerts exist. Alerts can email after close of day. Free plan: basic item library and alerts reported for small sellers. Deeper history / counting / barcode often sits on paid Square plans (~$49/mo cited in market writeups). Phone: Square Dashboard / POS app. This matches WSH-0001 if they already take Square. Status of SLC-0002: still unverified at field level. Confirm on the owner’s actual plan before promising alerts.

Path S2 — owner on Stripe only (SLC-0001) Stripe does not give salon-grade stock-on-phone. Do not pretend it does. Use S3 or move catalog to Square / a sheet. Do not force a new payments account (Art. VIII).

Path S3 — zero new vendor (Tier 4 + free) Google Sheet or Apple Numbers of SKUs. Low-stock = a row + WhatsApp / email to the owner’s phone. Ugly. Works in minutes. Leaves a reusable procedure (Documentation asset), not an Engine. This is the default if they have no POS inventory today.

Path S4 — open source (Tier 1) Pronto (salon booking + POS + inventory + WhatsApp/Telegram low-stock alerts, self-host or free cloud start) is a candidate Solution Component, not a Foundry Engine. Register only if Raj wants a Tier 1 option on the card. Do not install it “because it is cool.” Vendor facts above: unverified.

d. New Engine authorised? NO in this pass. Evidence: S1 or S3 covers a one-location salon’s required capability (“know when colour / foil / product is low, on my phone”) without Foundry writing stock logic. If a second BusinessType (retail) proves S1/S3 cannot generalise, reopen Search. Do not pre-build for that day.

Proposed fulfillment on BUT-0001 required_capabilities.stock: status: Configured-by-connector (pending owner plan) default_order: 1. Owner’s existing Square inventory + alerts 2. Else sheet + WhatsApp/email alert procedure 3. Else Engine Search reopened foundry_engine: none related: ENG-0003 (sale event only), WSH-0001, PRB-0004

What stays open on Stock
- Verify Square free-vs-paid inventory on the actual owner plan.
- Confirm alert destination is phone-usable (app / email-to-phone), not “dashboard only.”
- Whether ENG-0003 later gets a decrement adapter (Package, not Engine).
- Whether Pronto is catalogued as SLC-0009 (Tier 1 candidate only).

### SEARCH 2 — REVIEW / REPLY

Problem: not a numbered PRB as “reviews” on the five-problem list; flagged as optional_capabilities on BUT-0001. Capability: optional

a. Existing Engine? ENG-0001 holds the customer. It does not hold Google reviews. ENG-0002 can trigger “how was your cut?” after the slot. That is composition, not a Review Engine.

b. Extend an existing Engine? Yes: ENG-0002 post-visit message + ENG-0001 customer phone. The review itself lives on Google. Foundry should not own it.

c. Connectors / free? Path R1 — Google Business Profile (free) Owner already has (or should have) a GBP. Official Reviews API can list and reply. Owner can also reply in the Google app on the phone. This is the public review surface that matters on the high street. Do not pay a “review platform” to wrap Google. API operational detail: unverified; pilot may be app-only.

Path R2 — WhatsApp Business app (free) Owner replies to complaints in the same chat they already use. WhatsApp Cloud API automation is a paid / approved path. Default = human replies in the free app (Art. X: keep judgment on a bad review with the owner, not an auto-reply bot).

Path R3 — post-visit ask After ENG-0002 completes a slot, send the GBP review link via WhatsApp or SMS. One ask. No nag loop. Negative private reply → owner handles. Do not auto-push unhappy clients onto Google.

d. New Engine authorised? NO. Evidence: the capability is “see and answer public reviews, and sometimes ask for one.” Google + WhatsApp + booking completion event cover it. A Foundry Review Engine would duplicate Google and violate “solutions not vendors” by becoming a review product.

Proposed fulfillment on BUT-0001 optional_capabilities.review_reply: status: Configured-by-connector default_order: 1. Google Business Profile (read + reply) 2. WhatsApp Business app for private follow-up

3. Optional one-shot ask after completed booking foundry_engine: none (compose ENG-0001 + ENG-0002) do_not: auto-reply public reviews without owner sign-off

What stays open on Review
- GBP API vs owner-taps-in-app for v1 (app is enough for pilot).
- Whether a Problem object PRB-0006 “unanswered reviews” should be added (schema only) so the card is queryable.
- WhatsApp Business Platform pricing if anyone later wants automated asks. Pilot uses the free app.

### WHAT THIS IMPROVES

- Stops the overview’s two red gaps being “fixed” by fake engines.
- Gives WSH-0001 a legal landing: Square alerts or sheet+phone, not “build stock software.”
- Gives the Configurator (when D is done) something to emit besides “GAP.”
- Keeps first deploy inside minutes: turn on Square alerts or open a sheet, open GBP, done.
- Leaves Foundry stronger only if we extract assets: two Search records (this DR), and later a Stock connector procedure + a Review procedure (Documentation, not Engines).

### WHAT THIS DOES NOT DO

- Does not deploy.
- Does not verify SLC field-level prices/countries.
- Does not run ENG-0004.
- Does not promote ENG-0001 / ENG-0002 to Reusable.
- Does not install Pronto.
- Does not write Article XIV.6 (that is still A).
- Does not create ENG-0005 or ENG-0006.

### ACTIONS TAKEN ON STAMP (see DR-2026-09-04-10a)

1. BUT-0001 required_capabilities.stock recorded as connector path pending owner plan (overlay; HVT-0006 source text not rewritten in place). 2. optional_capabilities.review recorded as R1–R3 stack.
3. WSH-0001.resolution set to this DR. Status prose: Configured (awaiting owner plan: Square vs sheet). Status strings are prose, not new HVT-0004 types (job B).
4. ENG-0005 and ENG-0006 not created.
5. OPEN_ITEMS appended in 10a.
6. Art. II.3 registry row still outstanding on HVT-0003 (Search result log without a new Engine ID).

### AUTHORITY

Issued under HVT-0001 Art. II (mandatory Search before build), Art. VI.4 (solutions not vendors), Art. VIII (do not force a new payments account), Art. X (do not auto-judge a bad review), Art. XIV (model first), HVT-0002 §3.2 Architecture Office Search authority.

Status: Approved by Raj, 2026-09-04. Changelog:
- 1.0 Draft issued as Search text.
- 1.0 Approved; durable copy written; application in 10a.
