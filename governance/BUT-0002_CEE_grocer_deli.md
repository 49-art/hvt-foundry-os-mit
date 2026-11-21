# BUT-0002 — BusinessType card — Central / Eastern European grocer-deli

Document ID: BUT-0002  
Title: BusinessType card — Central / Eastern European grocer-deli  
Version: 1.0  
Previous version: 0.1  
Status: Approved  
Previous status (v0.1): Approved  
Approval record: DR-2026-11-20-10  
Owner: Architecture Office  
Reviewed By: Raj (CEO Office) — Tony Adams, 20 Nov 2026 (DR-2026-11-20-10). Stan Lee Design review: deferred (hibernation), not waived  
Stan Lee Design review: deferred (hibernation)  
Live instance: none  
Depends on: HVT-0006, DR-10 Approved, DR-12 Approved  
ENG-0005: held — do not reference as registered  

---

Filed: artifacts/governance/BUT-0002_CEE_grocer_deli.md ID reserved by DR-2026-09-04-12. Signed off by Raj 2026-09-04 as an Approved BusinessType card (classification only). No live instance. No site. Design veto still applies to any future owner-facing surface when Stan Lee returns.

Howard flags (not silently closed):
- PRB-0001–0005 are BUT-0001 salon problems.
- PRB-0006 (optional unanswered reviews) was never minted. This card starts at PRB-0007. Gap at 0006 left open.
- SEC-0001 in HVT-0006 is Services. Retail is named in the type list but no SEC-0002 / MKT-0002 IDs exist yet. “Food & household import retail” is a proposed Market Industry name, not a registered MKT row.
- ENG-0002 listed as conditional. Inherited “same engines as BUT-0001 until Search” from DR-12 still sits beside “do not force a booking diary.” Flag, do not pick.

### WHAT THIS SHOP IS

The counter on a UK high street that sells the food people actually want from home: Polish, Romanian, Lithuanian, Bulgarian, or mixed Central / Eastern European import. Not a Tesco with a “world food” aisle. Not a salon with a flag on the homepage.

Typical picture
- Family or small partnership
- One room + stock room
- Queue at the till, not an app
- Products named in Polish / Romanian first
- Cash still common; card if they already have it
- WhatsApp used like a phone, not like a CRM

Classification Sector: Retail Market Industry: Food & household import retail Business Type: Central / Eastern European grocer-deli Business Model: Counter + basket. Sometimes a small hot-food / bakery case. Rarely delivery as the main trade.

How it is NOT BUT-0001 Hair salon sells time. This shop sells tins, bread, meat, sweets, and brands the owner is proud to put in the window. Same customer engine can hold people. Same commerce engine can take a card. The product list is the centre of gravity.

### PROBLEMS (owner language first)

- PRB-0007 “I don’t know what is about to run out until the regular asks and I’ve sold the last one.”
- PRB-0008 “English software spells the products wrong and the customers stop recognising them.”
- PRB-0009 “Suppliers change price and pack size. I find out when the delivery arrives.”
- PRB-0010 “Card / till / notebook don’t match. End of week is a fight.”
- PRB-0011 “New people walk past because the shop looks shut or generic online. Regulars already know.”

### WHAT WE ALREADY HAVE (do not rebuild)

ENG-0001 Customer — regulars, families, phone numbers ENG-0002 Booking — only if they do trays / cakes to order. Most of these shops do NOT need a booking diary as the main tool. Do not force one. ENG-0003 Commerce — card payments they already use DR-10 stock path: if they use Square → Square alerts else sheet + WhatsApp / email to the owner’s phone Review path (DR-10): Google Business Profile + WhatsApp replies

### GAPS (honest)

- Multi-source product list (sheet + supplier + till) = ENG-0005 HELD. Do not invent it on this card.
- Supplier price lists we are not allowed to scrape
- Language / script on tickets and WhatsApp
- Community calendar (Polish / Orthodox / national days) is not in the English bank-holiday list

### CONNECTORS TO PREFER (free / already-owned first)

1. Whatever till they already have
2. Google Sheet of SKUs in their language
3. WhatsApp Business app
4. Google Business Profile (name in their language)
5. Companies House only if they want the legal name on the pack (free, optional)
6. Card: Stripe or Square they already own — never force a new account

### SIZING FILTERS (Configurator later)

size: one counter / one stock room budget: low — hours matter more than software skill: phone + WhatsApp, not a back office country: UK language: at least one non-English counter language

### BRAND INTAKE (required before any public surface)

- Photo of the actual fascia
- Languages spoken at the counter
- Three product names that must stay un-anglicised (example shape: Pączki, zacuscă, kielbasa — owner picks)
- Brands they are proud to show
- What must never look like a London template grocer

STAN LEE TEST If you can swap the logo and it becomes “European Mini Mart #14,” reject it.

USED BY: none MATURITY OF THIS CARD: Draft schema


## Resolution — v1.0, 20 Nov 2026 (DR-2026-11-20-08 / -10)

- **Status:** Approved card v1.0 — classification only. Live instance: none. Overlay: HVT-0006-OVL-0002.
- **Classification IDs:** MKT-0002 under SEC-0002 Retail.
- **Problems:** PRB-0007, PRB-0008, PRB-0009, PRB-0010, PRB-0011 (minted in the graph; overlaps recorded with family_of).
- **Business Model:** Counter + basket; sometimes a small hot-food / bakery case; rarely delivery as the main trade. **complexity_score:** 3 (computed, DR-2026-11-20-07 §7).
- **ENG-0002:** conditional — trays / cakes to order only. **ENG-0005:** authorised on trigger (DR-2026-11-20-05) — not a recommended engine.
- **Howard flags:** each one closed in DR-2026-11-20-10 §3 (table).
- **Stan Lee:** Design review deferred (hibernation), not waived — Brand Intake + veto before any public surface.
- **MATURITY (supersedes the line above):** Approved card v1.0.

## Version history (added 2026-11-20)

| Version | Date | Change |
|---|---|---|
| 0.1 | (earlier) | Status was: Approved |
| 1.0 | 2026-11-20 | Approved. Approved card v1.0 (classification only). Owner's instruction, 20 Nov 2026: “can you complete all decisions waiting and complete it.” See DR-2026-11-20-10. |
