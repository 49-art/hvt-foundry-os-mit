Document ID: BUT-0004
Title: BusinessType card — Independent specialist retailer
Version: 0.1
Status: Approved
Owner: Architecture Office
Reviewed By: Raj (CEO Office) — signed off 2026-09-04
             Stan Lee Design review: deferred (hibernation)
Live instance: none
Depends on: DR-10, DR-12
ENG-0005: held

Filed: artifacts/governance/BUT-0004_independent_specialist_retailer.md
ID reserved by DR-2026-09-04-12. Signed off by Raj 2026-09-04
as an Approved BusinessType card (classification only).
No live instance. No site.

Howard flags (not silently closed):
- “Specialist goods” is Market Industry prose. No MKT ID.
  Sector Retail still has no SEC-0002.
- PRB-0005 reused from BUT-0001 (slow checkout). Shared
  Problem is allowed; do not mint a parallel checkout Problem.
- ENG-0002 is a filter (appointment yes/no), not a Search.
- Instagram is named as Customer Asset (Art. VIII). Foundry
  does not take the account. No Instagram Engine.
- “Public surface that is not a template” is Design + Brand
  Intake (DR-12), not a new Engine and not job-to-build-a-site.
- Breadth of examples (fabric, records, phone parts, bridal)
  may later need Business Model splits (BUM-). Not split here.

============================================================
WHAT THIS SHOP IS
============================================================
One person (or a few) selling a craft they know better than
a chain: fabric, tools, records, hair and beauty supply,
phone repair parts, bridal, books, a single import brand.
The UK high street still has these. They are not “retail
generic.”

This card also covers the specialist next door to a
community grocer — same street, different gravity.

Typical picture
- The owner IS the catalogue
- Slow days, high-knowledge sales
- Instagram / WhatsApp more real than a shop site
- Stock is odd sizes and brands, not supermarket SKUs
- They already hate website builders

Classification
  Sector:          Retail
  Market Industry: Specialist goods
  Business Type:   Independent specialist retailer
  Business Model:  Counter + advice. Sometimes appointment
                   for long jobs (bridal, repair, colour
                   match). Sometimes mail to regulars.

============================================================
PROBLEMS
============================================================
  PRB-0016  “The thing a customer wants is in a box I forgot
             I had, or it isn’t, and I only find out when
             they are standing there.”
  PRB-0017  “My brands look cheap if the page looks like
             Canva.”
  PRB-0018  “I have no time to keep a site, but I need
             people to know I am open and what I know.”
  PRB-0019  “Empty midweek. Regulars don’t get told when
             the good shipment landed.”
  PRB-0005  Slow checkout if they still write paper receipts
            (same family as salon checkout)

============================================================
WHAT WE ALREADY HAVE
============================================================
  ENG-0001  Customer — the regular who asks for a brand
  ENG-0002  Booking — ON when the sale is an appointment
            (repair slot, fitting). OFF when it is walk-in.
  ENG-0003  Commerce — existing card
  DR-10 alerts for the lines they bother to list
  GBP + WhatsApp for presence and replies

============================================================
GAPS
============================================================
  - Brand-accurate product names (owner’s list)
  - A public surface that is not a template
    = Brand Intake + Stan Lee veto, not a new Engine
  - Shipment-landed message to regulars
    = ENG-0001 + WhatsApp. Procedure, not Engine
  - ENG-0005 held

============================================================
CONNECTORS TO PREFER
============================================================
  1. Phone camera + sheet of what is actually on the shelf
  2. WhatsApp Business app
  3. Instagram they already run (Customer Asset — do not
     take the account)
  4. Google Business Profile
  5. Existing payments
  6. Companies House optional

============================================================
SIZING FILTERS
============================================================
  size:     one room
  budget:   low to mid
  skill:    uneven — expert in the craft, beginner in admin
  country:  UK
  appointment: yes / no  (turns ENG-0002 on or off)

============================================================
BRAND INTAKE
============================================================
  - Fascia and one photo of the real counter
  - Three brands they would be ashamed to see next to
    fake stock photography
  - Whether they take appointments
  - The sentence they say when someone walks in
    (that sentence is the homepage, if any homepage exists)

STAN LEE TEST
  Logo-swap test. Inter-and-teal test.
  If it looks like Manus / Canva “boutique template,” reject.

USED BY: none
MATURITY: Draft schema
