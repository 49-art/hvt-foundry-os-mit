# DR-2026-11-20-11 — HVT Foundry Studio work of 18 Oct approved; Job D: ENG-0004 built and run as the `foundry_os` ladder; Studio housekeeping decisions

Document ID: DR-2026-11-20-11  
Title: Studio approvals (DR-2026-09-26-09, Studio v0.3); Job D — ENG-0004 Configurator built and run; Studio decisions  
Version: 1.0  
Status: Approved  
Owner: CEO Office (approval) / Architecture Office (Studio, ENG-0004)  
Reviewed By: Tony Adams (Raj), CEO Office — 20 Nov 2026; Chief Architect review under EXC-2026-11-20-01  
Dependencies: DR-2026-09-25-07; DR-2026-09-26-08; DR-2026-09-26-09; DR-2026-10-18-01 §6; DR-2026-11-20-02; HVT-0006 §7; DOC-0005; DOC-0008; DOC-0010  

---

## 1. Approvals

- **DR-2026-09-26-09 (Salon / Barber card app template) and its 3 Studio actions** (preview_card_template, build_card_app, export_card_app): **Approved.**
- **Studio v0.3** (shop apps, card template, connectors, live search): **Approved** as software. **No demo shop or card app is a live surface.** A real shop's app needs Brand Intake, the Stan Lee veto, and a DOC-0010 QA release for that shop.
- **All 17 Studio actions** (8 from DR-2026-09-25-07, 6 from DR-2026-09-26-08, 3 from DR-2026-09-26-09) now cite "Approved — DR-2026-11-20-11". They stay additions to the **Architecture Office only**, through the kernel's labelled extension, and **the CEO Agent is still refused every Studio action.**

## 2. Job D: ENG-0004 Configurator

- Built as `foundry_os/` (stdlib only). It runs the DOC-0008 eight-rung ladder against the graph: classify, problems (owner words verbatim), shelf (all four tiers shown), match, quote (type of take only, no rates), gaps, Brand gate, and deploy week. It also produces a session record and a governance verifier, and is run from a CLI (`python3 -m foundry_os …`).
- **Run on theatre:** the SES-0002-F-0001 "Mina" intake reproduces the filed outcome: BUT-0001; no-shows / empty slots / regulars / stock / reviews; DR-10 S3 sheet path because the till is not Square; quotes Q1–Q3 zero; gap = two-source stock with `eng_0005_trigger: false` (theatre); Brand SKIP; Stan Lee not needed.
- **Maturity stays Prototype.** It has been run on theatre only, and promotion needs real use (Art. III).
- The Studio's built-in configurator (DOC-0005 step 3) and the ladder read the same graph cards, so there is one source of truth.

## 3. Studio housekeeping decisions (OPEN_ITEMS B2/B3)

| Item | Decision |
|---|---|
| "Out of scope" wish status (HVT-0006 §9.2) | No new status. The Studio keeps "Under Review" with the resolution text "Out of scope: …" (HVT-0004 v1.0 §9.3) |
| Size / technical-ability filters | These stay **recorded, not applied** until real data exists. They are never faked |
| Studio sessions → graph | A session enters the graph only when it is a **real-owner** session (SES-0003 onward), closed, and exported by the Architecture Office. Theatre and local drafts stay local |
| Brave Search API key | **Not bought.** No spend. Live search uses OpenStreetMap plus a free web fallback, and the result is labelled when web search is unavailable. This can be revisited with a one-line CEO Office decision |
| Hosting each shop's always-on app | **The owner's own account (Art. VIII). The Foundry hosts nothing by default.** Options stay in studio/HOSTING_OPTIONS.md. No Foundry-paid hosting |
| Data protection (saved suppliers, API keys) | DOC-0010 §3 privacy checklist must pass before any real customer data is stored. Keys stay masked and local, as now |
| Native-language search phrases | Kept and labelled "unchecked by a native speaker" until checked (live-human item) |
| Chairs counted separately from staff | One stylist = one chair, as now. A chair resource is added only when a real salon needs it |
| Vendor records in the graph | Updated with the DR-2026-09-25-04 findings (DR-2026-11-20-09 §4) |

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-11-20 | Logged. |
