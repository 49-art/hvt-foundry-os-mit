Document ID: HVT-0006-OVL-0002  
Title: BUT-0002 capability overlay — Food & household import retail  
Version: 1.0  
Status: Approved  
Owner: Architecture Office  
Reviewed By: Raj (CEO Office) — Tony Adams, 20 Nov 2026 (DR-2026-11-20-10)  
Dependencies: BUT-0002 v1.0, HVT-0006 v1.0, HVT-0006-OVL-0001 (pattern), DR-2026-09-04-10, DR-2026-11-20-05, DR-2026-11-20-10  

---

This overlay sits beside the BUT-0002 card, following the HVT-0006-OVL-0001 pattern. It does not replace the card. The machine-readable copy is the `card` block on BUT-0002 in graph/foundry_graph.json, which the ENG-0004 ladder (`foundry_os`) reads.

```yaml
BusinessType:
  id: BUT-0002
  market_industry: MKT-0002
  business_model: Counter + basket; sometimes a small hot-food / bakery case; rarely delivery as the main trade
  required_capabilities:
    - name: Customer records — regulars and families
      foundry_engine: ENG-0001
    - name: Payment processing — card they already use
      foundry_engine: ENG-0003
    - name: Stock / reorder alerts
      foundry_engine: none
      path: DR-10 path: S1 Square alerts if already on Square; else S3 sheet + WhatsApp/email to the owner's phone (DOC-0006 v1.0)
      search: DR-2026-09-04-10  # PARTIAL MATCH
    - name: Product names in the owner's language
      foundry_engine: none
      path: Google Sheet of SKUs in their language — Customer Asset (Art. VIII); procedure, not an Engine
  optional_capabilities:
    - name: Review & reply management
      foundry_engine: none
      path: GBP read + reply in the owner's voice; WhatsApp Business private follow-up; never auto-reply (DOC-0007 v1.0)
      search: DR-2026-09-04-10  # PARTIAL MATCH
    - name: Trays / cakes to order
      foundry_engine: ENG-0002
      path: conditional — only if they take orders
    - name: Supplier price / pack-size changes
      foundry_engine: none
      path: GAP — supplier lists we are not allowed to scrape; owner's own notes only
    - name: Community calendar (Polish / Orthodox / national days)
      foundry_engine: none
      path: GAP — owner sets honest hours on GBP; no calendar product
  recommended_engines: [ENG-0001, ENG-0003]
  eng_0002: conditional — trays / cakes to order only
  eng_0005: authorised on trigger (DR-2026-11-20-05) — not recommended
  out_of_scope: ["Scraping supplier price lists"]
  complexity_score: 3
  wishes: []   # filled only from a real owner's words (SES-0003+)
```

Brand gate: Rung 7: Brand Intake + Stan Lee Design veto before ANY public surface (DR-2026-09-04-12). SKIP for diary + WhatsApp paths.
Stan Lee test: If you can swap the logo and it becomes 'European Mini Mart #14', reject.

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-11-20 | Issued and approved (DR-2026-11-20-10). |
