Document ID: HVT-0006-OVL-0006  
Title: BUT-0006 capability overlay — Local health & care rooms  
Version: 1.0  
Status: Approved  
Owner: Architecture Office  
Reviewed By: Raj (CEO Office) — Tony Adams, 20 Nov 2026 (DR-2026-11-20-10)  
Dependencies: BUT-0006 v1.0, HVT-0006 v1.0, HVT-0006-OVL-0001 (pattern), DR-2026-09-04-10, DR-2026-11-20-05, DR-2026-11-20-10  

---

This overlay sits beside the BUT-0006 card, following the HVT-0006-OVL-0001 pattern. It does not replace the card. The machine-readable copy is the `card` block on BUT-0006 in graph/foundry_graph.json, which the ENG-0004 ladder (`foundry_os`) reads.

```yaml
BusinessType:
  id: BUT-0006
  market_industry: MKT-0006
  business_model: Appointment + fee; packages / courses of treatment common
  required_capabilities:
    - name: Appointment booking + reminders
      foundry_engine: ENG-0002
      path: or their existing clinic suite — do not rip it out (Art. VIII)
    - name: People / recall list
      foundry_engine: ENG-0001
    - name: Payments / packages
      foundry_engine: ENG-0003
      path: on the account they already have
  optional_capabilities:
    - name: Review & reply management
      foundry_engine: none
      path: GBP read + reply in the owner's voice; WhatsApp Business private follow-up; never auto-reply (DOC-0007 v1.0) — owner replies; no clinical content in any reply
      search: DR-2026-09-04-10  # PARTIAL MATCH
    - name: Consumables stock (needles, product)
      foundry_engine: none
      path: DR-10 path (DOC-0006) — not a clinic ERP, not ENG-0005
    - name: Clinical / medical records
      foundry_engine: none
      path: OUT OF SCOPE — clinician's lawful system only (Art. VIII, X)
      out_of_scope_by_law: true
  recommended_engines: [ENG-0001, ENG-0002, ENG-0003]
  eng_0002: on — time is the stock
  eng_0005: authorised on trigger (DR-2026-11-20-05) — not recommended
  out_of_scope: ["Clinical / medical records (lawful system only)", "Insurance / NHS pathways (unless a Search)", "Clinical advice on WhatsApp"]
  complexity_score: 2
  wishes: []   # filled only from a real owner's words (SES-0003+)
```

Brand gate: Rung 7: Brand Intake + Stan Lee Design veto before ANY public surface (DR-2026-09-04-12). SKIP for diary + WhatsApp paths.
Stan Lee test: No stock-photo white coats, no fake five-star row, no 'wellness serenity' template. Rooms look like their rooms. Never design a clinical-notes UI.

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-11-20 | Issued and approved (DR-2026-11-20-10). |
