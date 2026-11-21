# HVT-0006-OVL-0001 — BUT-0001 capability overlay after DR-2026-09-04-10

Document ID: HVT-0006-OVL-0001  
Title: BUT-0001 capability overlay after DR-2026-09-04-10  
Version: 1.0  
Previous version: 0.2  
Status: Approved  
Previous status (v0.2): Approved by Founder (Travis Lee Swift), 18 Oct 2026; pending Raj  
Approval record: DR-2026-11-20-04 (earlier: DR-2026-10-18-01)  
Owner: Architecture Office  
Reviewed By: Raj (CEO Office) — Tony Adams, 20 Nov 2026 (DR-2026-11-20-01)  
Dependencies: HVT-0006 v0.4 Draft, DR-2026-09-04-10 Approved, DR-2026-09-04-10a  

---

This overlay sits beside HVT-0006 §2.3. It does not replace the taxonomy document. Where this file and HVT-0006 disagree on stock / review fulfilment status, this file wins for those two capabilities only, because it carries the Approved Search.

Unchanged on BUT-0001: name, sector, common_problems, booking / payments / customer coverage, recommended_engines, integrations list, deployment, pricing_bands, time_to_deploy, complexity_score (still unvalidated), staff rota still unmodeled.

```yaml
BusinessType:
  id: BUT-0001
  name: Hair Salon
  required_capabilities:
    - Appointment booking             # covered: ENG-0002
    - Payment processing              # covered: ENG-0003
    - Customer records / loyalty      # covered: ENG-0001
    - Stock / inventory tracking
        search: DR-2026-09-04-10
        search_result: PARTIAL MATCH
        foundry_engine: none
        status_prose: Configured-by-connector (pending owner plan)
        default_order:
          - S1 Square inventory + alerts if owner already on Square (SLC-0002 unverified)
          - S2 Stripe-only is not stock-on-phone; do not force a new payments account (Art. VIII)
          - S3 else sheet + WhatsApp/email procedure
          - else reopen Engine Search
        related: [ENG-0003, WSH-0001, PRB-0004]
        do_not_register: ENG-0005
  optional_capabilities:
    - Review & reply management
        search: DR-2026-09-04-10
        search_result: PARTIAL MATCH
        foundry_engine: none
        compose: [ENG-0001, ENG-0002]
        status_prose: Configured-by-connector
        default_order:
          - R1 Google Business Profile read + reply
          - R2 WhatsApp Business app private follow-up
          - R3 optional one-shot ask after completed booking
        do_not: auto-reply public reviews without owner sign-off
        do_not_register: ENG-0006
    - Staff rota / timesheets         # not yet modeled — unchanged
  wishes:
    - WSH-0001
        text: owner wants stock alerts on phone
        lands_on: PRB-0004
        resolution: DR-2026-09-04-10
        status_prose: Configured (awaiting owner plan: Square vs sheet)
```

Art. II.3 note: HVT-0003 still needs Search-result rows (PARTIAL MATCH × 2) with no new Engine IDs.


## Completion — v1.0, 20 Nov 2026 (DR-2026-11-20-04)

Signed off by the CEO Office with the card wording exactly as filed. “Required capability, connector-only” is an allowed terminal state when a Search is on file and a procedure document is named (DR-2026-11-20-04 §1.3) — here DR-2026-09-04-10 + DOC-0006 / DOC-0007 (both v1.0). The Square-vs-sheet choice is the salon owner’s at the session (Art. VIII); WSH-0001 stays “Configured (awaiting owner plan)”, which is correct. ENG-0005: authorised on trigger (DR-2026-11-20-05), still not a recommended engine.

## Version history (added 2026-10-18)

| Version | Date | Change |
|---|---|---|
| 0.1 | (earlier) | Status was: Draft |
| 0.2 | 2026-10-18 | Approved by Founder (Travis Lee Swift), 18 Oct 2026; pending Raj. Founder approval recorded. Reviewer named in the record is Raj, so it stays pending Raj. Text unchanged from v0.1. Founder's words: “APPROVE EVERYTHING IN THE WAY YOU FEEL IT SHOULD BE.” See DR-2026-10-18-01. |
| 1.0 | 2026-11-20 | Approved. Signed off; wording unchanged. Owner's instruction, 20 Nov 2026: “can you complete all decisions waiting and complete it.” See DR-2026-11-20-04. |
