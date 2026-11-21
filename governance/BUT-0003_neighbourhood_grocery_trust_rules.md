# BUT-0003 — BusinessType card — Neighbourhood grocery with owner-stated dietary / trust rules

Document ID: BUT-0003  
Title: BusinessType card — Neighbourhood grocery with owner-stated dietary / trust rules  
Version: 1.0  
Previous version: 0.1  
Status: Approved  
Previous status (v0.1): Approved  
Approval record: DR-2026-11-20-10  
Owner: Architecture Office  
Reviewed By: Raj (CEO Office) — Tony Adams, 20 Nov 2026 (DR-2026-11-20-10). Stan Lee Design review: deferred (hibernation), not waived  
Stan Lee Design review: deferred (hibernation)  
Live instance: none  
Depends on: DR-10, DR-12  
ENG-0005: held  

---

Filed: artifacts/governance/BUT-0003_neighbourhood_grocery_trust_rules.md ID reserved by DR-2026-09-04-12. Signed off by Raj 2026-09-04 as an Approved BusinessType card (classification only). No live instance. No site.

Howard flags (not silently closed):
- A shop “can be this type and also a grocer-deli” is a multi-type instance question. HVT-0006 spine is usually one BusinessType. Whether one premises may carry BUT-0002 AND BUT-0003 is open for job B / HVT-0006, not decided here.
- “Neighbourhood grocery” is proposed Market Industry prose. No MKT-0003 / SEC-0002 minted.
- PRB-0007 shared with BUT-0002. Shared Problem objects are allowed in principle (HVT-0006 solves is many-to-many). Do not mint a second stock-out Problem for this type.
- Trust rule is owner-stated, stored, not certified. Foundry must not become a halal / slaughter certifier.
- Product marks planned on StockItem only if DR-13 stamps ENG-0005. Until then the sheet column is the Customer Asset (Art. VIII).

### WHAT THIS SHOP IS

A UK neighbourhood grocery where trust is the product: halal, specific slaughter / supplier rules, or another rule the OWNER states. Foundry does not invent the rule and does not invent a religion.

This is NOT “the Muslim shop.” A shop can be this type and also a grocer-deli. Dietary / trust marks sit on the owner and on products, not as a costume on the homepage.

Typical picture
- Regulars who ask “who is the supplier?” before they ask the price
- Meat / groceries / household mix
- Community language at the counter (may be more than one)
- Prayer time / Friday / Ramadan hours may matter
- WhatsApp groups do more work than a website

Classification Sector: Retail Market Industry: Neighbourhood grocery Business Type: Grocery with owner-stated trust rules Business Model: Counter retail. Trust rule is part of the offer, written in the owner’s words.

### PROBLEMS

- PRB-0012 “If one product is wrong on the rule, I lose the family, not one sale.”
- PRB-0013 “Hours change around community calendar. Google still shows last winter.”
- PRB-0014 “I need to know which lines I can put next to which. A normal stock app doesn’t care.”
- PRB-0015 “Reviews and rumours travel in the community faster than the Google star.”
- PRB-0007 Stock-outs still hurt (shared with BUT-0002)

### WHAT WE ALREADY HAVE

ENG-0001 Customer — families, not just ticket names ENG-0003 Commerce — existing card / cash ENG-0002 only if they take pre-orders for large packs or catering. Default = off. DR-10 stock alerts DR-10 review path — plus: never auto-reply a trust complaint. Owner speaks. Art. X.

### GAPS

- A field for the owner’s rule, in their words
- Product marks (owner-stated) — planned on StockItem when / if ENG-0005 is ever authorised. Until then a column on the sheet is enough
- Calendar that is not only UK bank holidays
- ENG-0005 held

### CONNECTORS TO PREFER

1. Owner’s existing till
2. Sheet with a “rule / mark” column the owner controls
3. WhatsApp Business app (human replies)
4. Google Business Profile — hours kept honest
5. Existing payments account only

### SIZING FILTERS

size: one shop budget: low skill: phone first country: UK trust: owner writes the rule; Foundry stores it, Foundry does not certify it

### BRAND INTAKE

- Fascia photo
- The trust rule in one sentence, owner’s words
- Languages
- Three product names that must not be “translated away”
- What a generic ‘world food’ template would get wrong

STAN LEE TEST No stock-photo prayer, no stock-photo spice pile, no “exotic” copy. If the rule is not in the owner’s sentence, the surface is rejected.

USED BY: none MATURITY: Draft schema


## Resolution — v1.0, 20 Nov 2026 (DR-2026-11-20-08 / -10)

- **Status:** Approved card v1.0 — classification only. Live instance: none. Overlay: HVT-0006-OVL-0003.
- **Classification IDs:** MKT-0003 under SEC-0002 Retail.
- **Problems:** PRB-0012, PRB-0013, PRB-0014, PRB-0015, PRB-0007 (minted in the graph; overlaps recorded with family_of).
- **Business Model:** Counter retail; the owner's trust rule is part of the offer, in the owner's words. **complexity_score:** 3 (computed, DR-2026-11-20-07 §7).
- **ENG-0002:** default off — pre-order / catering only. **ENG-0005:** authorised on trigger (DR-2026-11-20-05) — not a recommended engine.
- **Howard flags:** each one closed in DR-2026-11-20-10 §3 (table).
- **Stan Lee:** Design review deferred (hibernation), not waived — Brand Intake + veto before any public surface.
- **MATURITY (supersedes the line above):** Approved card v1.0.

## Version history (added 2026-11-20)

| Version | Date | Change |
|---|---|---|
| 0.1 | (earlier) | Status was: Approved |
| 1.0 | 2026-11-20 | Approved. Approved card v1.0 (classification only). Owner's instruction, 20 Nov 2026: “can you complete all decisions waiting and complete it.” See DR-2026-11-20-10. |
