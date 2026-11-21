Document ID: HVT-0006-OVL-0003  
Title: BUT-0003 capability overlay — Neighbourhood grocery  
Version: 1.0  
Status: Approved  
Owner: Architecture Office  
Reviewed By: Raj (CEO Office) — Tony Adams, 20 Nov 2026 (DR-2026-11-20-10)  
Dependencies: BUT-0003 v1.0, HVT-0006 v1.0, HVT-0006-OVL-0001 (pattern), DR-2026-09-04-10, DR-2026-11-20-05, DR-2026-11-20-10  

---

This overlay sits beside the BUT-0003 card, following the HVT-0006-OVL-0001 pattern. It does not replace the card. The machine-readable copy is the `card` block on BUT-0003 in graph/foundry_graph.json, which the ENG-0004 ladder (`foundry_os`) reads.

```yaml
BusinessType:
  id: BUT-0003
  market_industry: MKT-0003
  business_model: Counter retail; the owner's trust rule is part of the offer, in the owner's words
  required_capabilities:
    - name: Customer records — families, not just ticket names
      foundry_engine: ENG-0001
    - name: Payment processing — existing card / cash
      foundry_engine: ENG-0003
    - name: Stock / reorder alerts
      foundry_engine: none
      path: DR-10 path: S1 Square alerts if already on Square; else S3 sheet + WhatsApp/email to the owner's phone (DOC-0006 v1.0) — sheet carries an owner-controlled 'rule / mark' column
      search: DR-2026-09-04-10  # PARTIAL MATCH
    - name: Owner-stated trust rule, stored verbatim
      foundry_engine: none
      path: Owner record + sheet column in the owner's sentence. Foundry stores it; Foundry never certifies it
  optional_capabilities:
    - name: Review & reply management
      foundry_engine: none
      path: GBP read + reply in the owner's voice; WhatsApp Business private follow-up; never auto-reply (DOC-0007 v1.0) — plus: never auto-reply a trust complaint; the owner speaks (Art. X)
      search: DR-2026-09-04-10  # PARTIAL MATCH
    - name: Hours around the community calendar
      foundry_engine: none
      path: GBP hours kept honest by the owner; GAP: no non-UK-bank-holiday calendar product
    - name: Pre-orders / catering
      foundry_engine: ENG-0002
      path: default OFF
  recommended_engines: [ENG-0001, ENG-0003]
  eng_0002: default off — pre-order / catering only
  eng_0005: authorised on trigger (DR-2026-11-20-05) — not recommended
  out_of_scope: ["Certifying halal / slaughter / any trust rule — Foundry stores the owner's sentence only"]
  complexity_score: 3
  wishes: []   # filled only from a real owner's words (SES-0003+)
```

Brand gate: Rung 7: Brand Intake + Stan Lee Design veto before ANY public surface (DR-2026-09-04-12). SKIP for diary + WhatsApp paths.
Stan Lee test: No stock-photo prayer, no stock-photo spice pile, no 'exotic' copy. If the rule is not in the owner's sentence, reject.

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-11-20 | Issued and approved (DR-2026-11-20-10). |
