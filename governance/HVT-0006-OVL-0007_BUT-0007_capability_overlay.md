Document ID: HVT-0006-OVL-0007  
Title: BUT-0007 capability overlay — Building & joinery  
Version: 1.0  
Status: Approved  
Owner: Architecture Office  
Reviewed By: Raj (CEO Office) — Tony Adams, 20 Nov 2026 (DR-2026-11-20-10)  
Dependencies: BUT-0007 v1.0, HVT-0006 v1.0, HVT-0006-OVL-0001 (pattern), DR-2026-09-04-10, DR-2026-11-20-05, DR-2026-11-20-10  

---

This overlay sits beside the BUT-0007 card, following the HVT-0006-OVL-0001 pattern. It does not replace the card. The machine-readable copy is the `card` block on BUT-0007 in graph/foundry_graph.json, which the ENG-0004 ladder (`foundry_os`) reads.

```yaml
BusinessType:
  id: BUT-0007
  market_industry: MKT-0007
  business_model: Quoted job + deposit + schedule; some day-rate; some small retail of offcuts / furniture if they have a shop
  required_capabilities:
    - name: Customers / sites
      foundry_engine: ENG-0001
    - name: Survey / fit-day slots
      foundry_engine: ENG-0002
    - name: Deposits and balances
      foundry_engine: ENG-0003
    - name: Quote → accept → deposit → schedule
      foundry_engine: none
      path: Procedure; Workflow candidate (WKF-), not an Engine
  optional_capabilities:
    - name: Job photos
      foundry_engine: none
      path: Google Drive folder per job — photos stay the owner's (Art. VIII)
    - name: Timber / ironmongery stock
      foundry_engine: none
      path: DR-10 path: merchant account + sheet (ENG-0005 on trigger only)
    - name: Which jobs made money
      foundry_engine: none
      path: GAP — site costing / CIS / multi-crew ERP not session 1
  recommended_engines: [ENG-0001, ENG-0002, ENG-0003]
  eng_0002: on — survey and fit days
  eng_0005: authorised on trigger (DR-2026-11-20-05) — not recommended
  out_of_scope: ["Full site costing / CIS / multi-crew ERP in session 1"]
  complexity_score: 2
  wishes: []   # filled only from a real owner's words (SES-0003+)
```

Brand gate: Rung 7: Brand Intake + Stan Lee Design veto before ANY public surface (DR-2026-09-04-12). SKIP for diary + WhatsApp paths.
Stan Lee test: No stock decking at sunset. Their last job, their hands, their van signwriting. Else reject.

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-11-20 | Issued and approved (DR-2026-11-20-10). |
