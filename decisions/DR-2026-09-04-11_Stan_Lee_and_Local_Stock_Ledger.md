# DR-2026-09-04-11 — Decision Record — Ratify DR-2026-09-04-10; register Stan Lee; Art. II Search for a Local Stock Ledger; UK community types; personalisation as Customer Asset + Design veto

Document ID: DR-2026-09-04-11  
Title: Decision Record — Ratify DR-2026-09-04-10; register Stan Lee; Art. II Search for a Local Stock Ledger; UK community types; personalisation as Customer Asset + Design veto  
Version: 1.1  
Status: Draft — superseded for execution-intent by DR-2026-09-04-12 Approved  
Owner: Architecture Office  
Reviewed By: Stan Lee (assessment received); split via DR-12 (Approved)  
Supersedes: DR-2026-09-04-11 v1.0 (same ID, Draft — not executed; v1.0 text was not present in this Project filesystem)  
Depends on: DR-2026-09-04-10 (Approved by Raj 2026-09-04) HVT-0001 Art. II, III, V, VI.4, VIII, X, XIII, XIV HVT-0002 §4.1–4.3, HVT-0004, HVT-0006, HVT-0007 BUT-0001, PRB-0004, WSH-0001  

---

Howard review of this text is in the chat Decision Record of 2026-09-

04. This file is the received v1.1 wording plus filesystem header only. Not Approved. ENG-0005 not registered.

Change from v1.0 (Stan Lee):
- StockItem given ID prefix STI-
- ENG-0005 now has a full Art. II a→b→c→d Search, same bar as DR-10
- Fallback layers named honestly (git is not in this chat)

### 0. FALLBACK — WHAT THIS THREAD CAN AND CANNOT PROMISE

Constitutional fallback (this thread, always): Article V. Never delete. Supersede and link. v1.0 of this DR remains readable. v1.1 replaces it if stamped. DR-10 remains Approved and is not rewritten by this document.

Technical fallback (git): Leonard has no Foundry repository in this window. If Howard / Grok Bot committed DR-10 on the account computer, that commit is their restorable point. Leonard cannot see it and will not pretend to. Standing order if a repo exists: one commit per stamped DR. Uncommitted Drafts are not restorable points.

If Raj says “undo 11”: supersede 11 with a new DR that restores the DR-10 stock posture. That is a defined operation.

### 1. WHAT RAJ ALREADY LOCKED (UNCHANGED)

DR-2026-09-04-10 stands:
- No Review Engine.
- Review = GBP + WhatsApp app + optional one-shot ask.
- WSH-0001 stays on PRB-0004.
- Stock is not warehouse / MRP / multi-site purchasing software.

v1.0 tried to reopen “where the SKU list lives.” v1.1 runs that reopening through Art. II instead of asserting it.

### 2. STAN LEE

Agent: Stan Lee Office: Design + Research (dual, Design primary) Authority: HVT-0002 §4.3 — add the row before the agent acts. Row is Draft until HVT-0002 itself is bumped (still A). May: Reject owner-facing surfaces that match the generic signature list. Demand Brand Intake before publish. May not: Approve Constitution, register Engines, move customer data, treat taste as an Engine.

His two gaps on v1.0 are accepted. That is Design + Research doing the job, not decoration.

### 3. ART. II SEARCH — LOCAL STOCK LEDGER (this is the section v1.0 skipped)

Capability required: One product record the owner cares about, written from whatever source they already have, alerted to their phone, still theirs (Art. VIII). Not: purchase orders, multi-warehouse, forecasting, MRP.

a. Does a registered Engine already solve this? ENG-0001 Customer — people, not SKUs. No. ENG-0002 Booking — slots, not colour tubes or tins. No. ENG-0003 Commerce — payment, receipt, membership. A successful payment can be a signal that qty should drop. It is not a catalogue, not a source adapter, not an alert ledger. Partial event only. Not a match. ENG-0004 Configurator — matches businesses to capability. It does not store products. No.

b. Can an existing Engine be extended / parameterised / composed? Composition already decided in DR-10: Square alerts if they live in Square else sheet + WhatsApp else reopen. That composition covers ALERTS for one shop on one source. It does not cover:

two sources at once (till + supplier list) the same product object on a salon and a grocer names in a language Square’s US item library will mangle brand / origin / dietary mark as first-class fields Foundry being able to query “what does this owner stock?” without logging into Square Parameterising ENG-0003 with “also keep a list of SKUs” would overload Commerce into a second Engine in disguise and tie the ledger to payments. A Polish counter that takes cash would have no ledger. Reject that composition.

c. Can Tier 4 / Tier 1 / free Tier 3 cover the ledger? Square item library = good source, bad canonical store. Owner-plan dependent. English-first. Not portable if they leave Square (Art. VIII.3). Google Sheet = good source, bad canonical store. No ID discipline. No graph. No Configurator query. Pronto / other OSS POS = another source, still a vendor catalogue, not a Foundry object. Stripe = payments. Still not a catalogue. None of these give the Foundry a queryable, portable, multi-source product object that stays a Customer Asset.

Therefore connectors remain INGEST and ALERT paths. They are not the ledger.

d. New Engine authorised? YES — Prototype only, narrow charter.

Name: ENG-0005 Local Stock Ledger Engine Maturity: Prototype (Art. III.3.a as cited in received text — Howard flags: III.3.a is the two-context Reusable test; Prototype is Art. III.4). Not Reusable until two live BusinessTypes use it (salon + one community shop). Used By starts empty.

In scope:

StockItem records (prefix STI-) ingest adapter interface (square | sheet | supplier | till | other) qty, reorder_at, last_verified emit low-stock toward the DR-10 alert path query by owner, brand, origin, dietary mark

Out of scope (explicit, this is how 11 does not reverse 10):

purchasing / POs multi-warehouse / transfers forecasting / MRP forcing a new POS or payments account scraping a wholesaler we are not allowed to read owning the owner’s product list (customer_asset_flag) If Raj refuses ENG-0005, fallback is DR-10 as stamped: alerts only, no Foundry product object.

### 4. OBJECT — STOCKITEM

ID prefix: STI- # Stan Lee gap 1, closed Example: STI-0001

StockItem id STI-#### owner_id customer name owner’s language / script name_en optional brand origin_country source_system square | sheet | supplier | till | other source_ref qty unit reorder_at dietary_marks owner-stated (halal, none, …) last_verified customer_asset_flag true

Relationship words to adopt in the HVT-0004 bump (B): StockItem belongs_to Owner StockItem sourced_from SourceSystem StockItem alerts_via Connector (DR-10 path) CommerceEvent may decrement StockItem (adapter, later)

### 5. COMMUNITY TYPES AND PERSONALISATION (unchanged in substance; tightened)

No “Foreign Shop” type. No “Muslim theme pack.”

Queue (schema only, Draft cards): BUT-0002 Central / Eastern European grocer-deli BUT-0003 Neighbourhood grocery with owner-stated dietary / trust rules BUT-0004 Independent specialist retailer

Dietary / trust marks live on StockItem and on the owner, not as a single BusinessType label.

Brand Intake is required before any owner-facing surface: shopfront photo counter languages three product names that must not be anglicised optional UK Companies House number (free public connector) “what must never look English-generic”

Stan Lee refusal list (procedural, not a vibe): stock photos of smiling strangers fake reviews lorem products Inter + teal on white flag-as-sticker personalisation any surface that becomes another shop by swapping the logo

### 6. DECISION (PROPOSED)

1. Keep DR-10 locked.
2. Register Stan Lee as Draft agent (Design primary).
3. Authorise ENG-0005 Local Stock Ledger Engine at Prototype under the Art. II Search in §3. Not a warehouse suite.
4. Adopt StockItem / STI- into the next HVT-0004 bump.
5. Queue BUT-0002 / 0003 / 0004 as Draft cards.
6. Brand Intake + Stan Lee veto on deploy pack.
7. Reject: global live feed of “all latest products,” generic site factory, one ethnic template.

### 7. OPEN ITEMS

- Legal bound on supplier ingest.
- Scripts in the object model (not English-only names).
- HVT-0002 bump still required before Stan Lee is fully authorised (that is still original job A).
- Git commit discipline lives with whoever has the repo.
- ENG-0005 code does not exist. This DR authorises the charter, not a merge.

### AUTHORITY

Art. II Search completed in §3 (proposed). Art. V: v1.1 supersedes v1.0 of the same ID. Art. VIII: ledger schema Foundry, rows Customer Asset. Art. XIV: types and ledger before any site.

Status: Draft. No institutional weight until Raj stamps v1.1.
