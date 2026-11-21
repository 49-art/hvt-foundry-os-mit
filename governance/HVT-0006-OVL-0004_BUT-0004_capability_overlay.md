Document ID: HVT-0006-OVL-0004  
Title: BUT-0004 capability overlay — Specialist goods  
Version: 1.0  
Status: Approved  
Owner: Architecture Office  
Reviewed By: Raj (CEO Office) — Tony Adams, 20 Nov 2026 (DR-2026-11-20-10)  
Dependencies: BUT-0004 v1.0, HVT-0006 v1.0, HVT-0006-OVL-0001 (pattern), DR-2026-09-04-10, DR-2026-11-20-05, DR-2026-11-20-10  

---

This overlay sits beside the BUT-0004 card, following the HVT-0006-OVL-0001 pattern. It does not replace the card. The machine-readable copy is the `card` block on BUT-0004 in graph/foundry_graph.json, which the ENG-0004 ladder (`foundry_os`) reads.

```yaml
BusinessType:
  id: BUT-0004
  market_industry: MKT-0004
  business_model: Counter + advice; sometimes appointments for long jobs (bridal, repair, colour match); sometimes mail to regulars
  required_capabilities:
    - name: Customer records — the regular who asks for a brand
      foundry_engine: ENG-0001
    - name: Payment processing — existing card
      foundry_engine: ENG-0003
    - name: Stock / reorder alerts
      foundry_engine: none
      path: DR-10 path: S1 Square alerts if already on Square; else S3 sheet + WhatsApp/email to the owner's phone (DOC-0006 v1.0) — for the lines they bother to list (phone camera + sheet)
      search: DR-2026-09-04-10  # PARTIAL MATCH
  optional_capabilities:
    - name: Appointments (repair slot, fitting)
      foundry_engine: ENG-0002
      path: ON when the sale is an appointment, OFF when walk-in
    - name: Shipment-landed message to regulars
      foundry_engine: ENG-0001
      path: ENG-0001 + WhatsApp Business — procedure, not an Engine
    - name: Public surface that is not a template
      foundry_engine: none
      path: Brand Intake + Stan Lee veto (Design), not an Engine
    - name: Review & reply management
      foundry_engine: none
      path: GBP read + reply in the owner's voice; WhatsApp Business private follow-up; never auto-reply (DOC-0007 v1.0)
      search: DR-2026-09-04-10  # PARTIAL MATCH
  recommended_engines: [ENG-0001, ENG-0003]
  eng_0002: filter — on if appointments, off if walk-in
  eng_0005: authorised on trigger (DR-2026-11-20-05) — not recommended
  out_of_scope: ["Taking the owner's Instagram account"]
  complexity_score: 2
  wishes: []   # filled only from a real owner's words (SES-0003+)
```

Brand gate: Rung 7: Brand Intake + Stan Lee Design veto before ANY public surface (DR-2026-09-04-12). SKIP for diary + WhatsApp paths.
Stan Lee test: Logo-swap test. Inter-and-teal test. Manus / Canva 'boutique template' fails.

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-11-20 | Issued and approved (DR-2026-11-20-10). |
