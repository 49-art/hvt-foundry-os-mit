# DR-2026-09-04-10a — Application of Approved Engine Search outcomes to BUT-0001 / WSH-0001 (overlay, not in-place rewrite)

Document ID: DR-2026-09-04-10a  
Title: Application of Approved Engine Search outcomes to BUT-0001 / WSH-0001 (overlay, not in-place rewrite)  
Version: 1.0  
Status: Draft  
Owner: Architecture Office  
Reviewed By: pending Raj  
Dependencies: DR-2026-09-04-10 (Approved), HVT-0001 Art. II.3, Art. V, Art. VII, HVT-0003, HVT-0004 v0.1, HVT-0006 v0.4 §2.3, BUT-0001, PRB-0004, WSH-0001  

---

### WHAT CHANGED

Raj stamped DR-2026-09-04-10 Approved on 2026-09-04 and ordered a durable copy.

This record applies the six stamp-actions without:
- creating ENG-0005 or ENG-0006
- rewriting HVT-0006 source in the pack zip / PDF
- adopting new HVT-0004 status types (job B still open)

Durable files:
- artifacts/decisions/DR-2026-09-04-10_Engine_Search_Stock_and_Review.md
- artifacts/decisions/DR-2026-09-04-10a_Apply_Search_Outcomes_BUT-0001.md
- artifacts/governance/HVT-0006_BUT-0001_capability_overlay.md

### ID COLLISION (item 1 from Howard review)

Standing overview job A still uses informal name “DR-10” for agent registration + Article XIV.6.

Raj approved Document ID DR-2026-09-04-10 as this Engine Search. Consequence of the stamp, not a silent pick:
- Engine Search keeps DR-2026-09-04-10
- Job A, when named, must take the next ID (proposed DR-2026-09-04-11). Do not reuse -10.

### STATUS VOCABULARY (item 7 from Howard review)

“Configured-by-connector” and “Configured (awaiting owner plan)” are prose on the overlay. They are not added to HVT-0004’s canonical type or field list in this pass. Job B remains the adoption pass for types + relationships.

### MUTATIONS RECORDED (overlay)

1. BUT-0001 required_capabilities “Stock / inventory tracking” Prior (HVT-0006 §2.3): GAP — no Engine registered, Engine Search pending (Art. II) Now: Engine Search completed = PARTIAL MATCH foundry_engine: none status_prose: Configured-by-connector (pending owner plan) default_order: S1 Square inventory+alerts if already on Square → else S3 sheet + WhatsApp/email → else reopen Search related: ENG-0003 sale event only, WSH-0001, PRB-0004 fulfilment_layer: HVT-0007 catalog / owner estate, not a new Tier 2 Engine HVT-0007 §6 chain tension (required capability with no Foundry Engine) remains flagged, not closed.

2. BUT-0001 optional_capabilities “Review & reply management” Prior: GAP — Engine Search pending Now: Engine Search completed = PARTIAL MATCH foundry_engine: none (compose ENG-0001 + ENG-0002) status_prose: Configured-by-connector default_order: R1 GBP read+reply → R2 WhatsApp Business app private follow-up → R3 optional one-shot ask after completed booking do_not: auto-reply public reviews without owner sign-off (Art. X)
3. WSH-0001 remains linked to PRB-0004 (not a new feature request) resolution: DR-2026-09-04-10 status_prose: Configured (awaiting owner plan: Square vs sheet)

4. ENG-0005 / ENG-0006 not created

### OPEN_ITEMS (appended)

- Confirm owner POS (Square / Stripe / neither)
- Verify Square alert-on-phone on that plan (SLC-0002 field detail still unverified)
- Optional: draft DOC-0006 Stock Alert Procedure (Documentation asset, Art. XIII.3.e)
- Optional: draft DOC-0007 Review Reply Procedure
- Optional: PRB-0006 Unanswered reviews (schema only)
- Optional: Pronto as SLC-0009 only if Raj asks
- Art. II.3: log Search results on HVT-0003 without issuing Engine IDs (registry row still missing)
- Whether “required capability, connector-only” is an allowed terminal state on a BUT card vs HVT-0007 §6
- Jobs A, B, D not started
- Article XIV.6 not written
- INT vs SLC relationship still held open
- Stripe country 170+ vs 46+ both retained
- Six+ SLC field cards unverified
- Referral income deferred

### WHAT WAS REJECTED

- In-place edit of HVT-0006 v0.4 inside the pack (Art. V: no document is amended by another document’s side effect)
- New Object Model status enums
- Installing Pronto
- Building the decrement adapter now
- Running ENG-0004
- Treating vendor plan prices / Reviews API as Verified

### WHAT IT SUPERSEDES / DEPENDS ON

Supersedes: the GAP / “Engine Search pending” prose on BUT-0001 stock and review lines, by overlay only. Does not supersede HVT-0006 as a document (still v0.4 Draft).

Depends on: DR-2026-09-04-10 Approved.

### AUTHORITY

Stamp authority: CEO Office (Raj) on DR-2026-09-04-10. Application drafting: Architecture Office.

Status: Draft (application record). The Search itself is Approved. The overlay wording waits if Raj wants different card language. Owner: Architecture Office Reviewed By: pending Raj
