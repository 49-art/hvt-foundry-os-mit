# DR-2026-11-20-05 — ENG-0005 Local Stock Ledger: path A, authorised on trigger; Pronto not registered

Document ID: DR-2026-11-20-05  
Title: ENG-0005 Local Stock Ledger — path A chosen, Prototype authorised on a stated trigger; Pronto (SLC-0009 candidate) not registered  
Version: 1.0  
Status: Approved  
Owner: CEO Office (decision) / Architecture Office (execution)  
Reviewed By: Tony Adams (Raj), CEO Office — 20 Nov 2026 (DR-2026-11-20-01)  
Dependencies: HVT-0001 Art. II, III.4, VIII, X; DR-2026-09-04-10; DR-2026-09-04-11 v1.1 §3–§4; DR-2026-09-04-12 (iii); DR-2026-11-20-04; SES-0002-F-0001; DOC-0006  

---

## 1. The question that was waiting

DR-2026-09-04-12 (iii) put ENG-0005 on HOLD until Raj chose **A** (accept the DR-11 v1.1 §3 Search and issue a one-page Engine-only paper: "ENG-0005 Prototype authorised; charter = v1.1 §3; prefix STI-") or **B** (order a standalone Search).

## 2. Decision: path A, with a stated trigger

1. **Path A is chosen.** The DR-11 v1.1 §3 a→b→c→d Search is accepted as the Art. II Search (DR-2026-11-20-04 §1.4). The ENG-0005 charter is **v1.1 §3 exactly**: StockItem records (STI-), an ingest adapter interface (square | sheet | supplier | till | other), qty / reorder_at / last_verified, low-stock alerts sent to the DR-10 alert path, and queries by owner, brand, origin and owner-stated mark. **Out of scope:** POs, multi-warehouse, forecasting/MRP, forcing a new POS or payments account, scraping, and owning the owner's list (rows are Customer Assets, Art. VIII).
2. **The trigger.** The only evidence of the two-source gap so far is theatre (SES-0002-F-0001, fictional). Art. II exists to stop Engines arriving on adjacent good ideas, so **ENG-0005 is entered in the graph and HVT-0003 at maturity Prototype on the day a real owner, in a live session (SES-0003 or later), states the two-source stock gap in their own words.** The Architecture Office then files a one-page Engine-only DR that cites this record and the session. **No further CEO Office stamp is needed.** Until the trigger, DR-10 is the path exactly as stamped: Square alerts, or a sheet plus WhatsApp (DOC-0006).
3. The HOLD wording is replaced everywhere by **"authorised on trigger (DR-2026-11-20-05)"**. ENG-0005 is still not a recommended engine on any card. Nobody may promise it in the room (DOC-0008 rung 6: "Logged. Not built today.").
4. The STI- prefix and the StockItem schema are adopted into HVT-0004 v1.0 now (DR-2026-11-20-07). No StockItem instances exist yet.
5. The software includes a check. `foundry_os` (ENG-0004 ladder, DR-2026-11-20-11) reports `eng_0005_trigger: true` only when a **live** intake states the two-source gap. For theatre it reports `false`.

## 3. Pronto (possible SLC-0009, DR-10 path S4)

**Not registered.** The sheet path (S3) already is the free Tier 1 option, and Pronto's facts are unverified. No SLC ID is reserved for it. SLC-0009 stays unissued until something is actually registered.

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-11-20 | Logged. HOLD lifted to "authorised on trigger". |
