Document ID: HVT-0006-OVL-0005  
Title: BUT-0005 capability overlay — Independent goods retail  
Version: 1.0  
Status: Approved  
Owner: Architecture Office  
Reviewed By: Raj (CEO Office) — Tony Adams, 20 Nov 2026 (DR-2026-11-20-10)  
Dependencies: BUT-0005 v1.0, HVT-0006 v1.0, HVT-0006-OVL-0001 (pattern), DR-2026-09-04-10, DR-2026-11-20-05, DR-2026-11-20-10  

---

This overlay sits beside the BUT-0005 card, following the HVT-0006-OVL-0001 pattern. It does not replace the card. The machine-readable copy is the `card` block on BUT-0005 in graph/foundry_graph.json, which the ENG-0004 ladder (`foundry_os`) reads.

```yaml
BusinessType:
  id: BUT-0005
  market_industry: MKT-0005
  business_model: Walk-in basket; optional click-and-collect
  required_capabilities:
    - name: Customer records — regulars
      foundry_engine: ENG-0001
    - name: Payment processing — payments they have
      foundry_engine: ENG-0003
    - name: Stock / reorder alerts
      foundry_engine: none
      path: DR-10 path: S1 Square alerts if already on Square; else S3 sheet + WhatsApp/email to the owner's phone (DOC-0006 v1.0) — the twenty lines that actually run out
      search: DR-2026-09-04-10  # PARTIAL MATCH
  optional_capabilities:
    - name: Click-and-collect
      foundry_engine: none
      path: Tier 3 candidate only if they already sell online (Shopify-class); else GAP
    - name: Appointments (personal shopping, repairs)
      foundry_engine: ENG-0002
      path: OFF unless they do appointments
    - name: Review & reply management
      foundry_engine: none
      path: GBP read + reply in the owner's voice; WhatsApp Business private follow-up; never auto-reply (DOC-0007 v1.0)
      search: DR-2026-09-04-10  # PARTIAL MATCH
  recommended_engines: [ENG-0001, ENG-0003]
  eng_0002: off unless appointments (personal shopping, repairs)
  eng_0005: authorised on trigger (DR-2026-11-20-05) — not recommended
  out_of_scope: []
  complexity_score: 2
  wishes: []   # filled only from a real owner's words (SES-0003+)
```

Brand gate: Rung 7: Brand Intake + Stan Lee Design veto before ANY public surface (DR-2026-09-04-12). SKIP for diary + WhatsApp paths.
Stan Lee test: Logo-swap / Inter-teal / fake lifestyle stock. Reject.

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-11-20 | Issued and approved (DR-2026-11-20-10). |
