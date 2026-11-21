Document ID: HVT-0006-OVL-0001
Title: BUT-0001 capability overlay after DR-2026-09-04-10
Version: 0.1
Status: Draft
Owner: Architecture Office
Reviewed By: pending Raj
Dependencies: HVT-0006 v0.4 Draft, DR-2026-09-04-10 Approved,
              DR-2026-09-04-10a

This overlay sits beside HVT-0006 §2.3. It does not replace
the taxonomy document. Where this file and HVT-0006 disagree
on stock / review fulfilment status, this file wins for those
two capabilities only, because it carries the Approved Search.

Unchanged on BUT-0001:
  name, sector, common_problems, booking / payments / customer
  coverage, recommended_engines, integrations list, deployment,
  pricing_bands, time_to_deploy, complexity_score (still
  unvalidated), staff rota still unmodeled.

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

Art. II.3 note: HVT-0003 still needs Search-result rows
(PARTIAL MATCH × 2) with no new Engine IDs.
