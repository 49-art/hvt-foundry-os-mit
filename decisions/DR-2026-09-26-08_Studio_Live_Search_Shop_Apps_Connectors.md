# DR-2026-09-26-08 — Decision Record — Studio v0.2: live search, shop's own apps, connectors

Document ID: DR-2026-09-26-08  
Title: Decision Record — HVT Foundry Studio v0.2 (live search, shop apps, connectors)  
Version: 0.1  
Status: Draft  
Owner: Architecture Office  
Reviewed By: pending — not reviewed (Chief Architect review required)  
Drafted By: AI executor (Grok Bot) on instruction from Travis Lee Swift, 2026-09-26  
Dependencies: DR-2026-09-25-07; DOC-0005; HVT-0001 Art. IV, V, VIII; HVT-0002 §3.2, §4.2; DR-2026-09-25-04  
Supersedes (in part): DR-2026-09-25-07, only where it said the Studio "does not need the internet and does not send anything anywhere"  

---

## Decision

Extend HVT Foundry Studio with three things:

1. **Find for my business.** A live search, run only when the user presses the button, for suppliers, stock, finance, delivery and storage.
   - It searches in English and in the owner's community language(s).
   - It uses postcodes.io, the OpenStreetMap Overpass API, and a web search provider: Brave Search API with a key, SerpAPI with a key, or DuckDuckGo HTML without a key.
2. **The shop's own app.** A per-shop installable web app (PWA) that the shop owns (Art. VIII). It has an owner-only admin page with a password and a private supplier list.
3. **Connectors.** One small module per outside service, all with the same interface. Keys are stored per scope, masked, and never exported. There is also a no-code Custom API with OpenAPI import.

## Action taken

- **Six new actions** were added to the Studio action map, for the **Architecture Office only**, through the same labelled `extra_authority` mechanism:
  - `run_live_search`
  - `save_search_result`
  - `build_shop_app`
  - `export_shop_app`
  - `update_studio_settings`
  - `manage_connector`

  Each is tagged "(DR-2026-09-26-08, Draft)". The CEO Agent (AGT-0001) is refused all six; this is tested. **kernel/foundry_kernel.py was not changed.**
- **Honesty rules built into the code:**
  - Every search result carries its URL, source, query language and checked time, and the label "found live, not checked by us".
  - Saving a result without a URL or checked time is refused.
  - Saved results are stored with `verified: false`.
  - Native-language phrases are marked "not yet checked by a native speaker".
  - When a service is blocked, offline or busy, the app says so in plain words and never fills the gap.
  - Each connector declares its status: working-tested, code-ready-needs-key or unverified.
- **Settings** (search keys, provider order, Studio password hash) and connector secrets are kept in `studio/data/`. They are excluded by `.gitignore` and by the zip exporters. Settings changes are logged by field name only, never with the key values.
- **Tests.** 92 new tests, all using a simulated network:
  - test_live_search.py (13)
  - test_connectors.py (66)
  - test_shop_app.py (6)
  - test_studio_v2.py (7)

  With the original 47: **139 passed** on 2026-09-26.

## Rationale

Travis asked for real-world use: live results for shop owners in their own language, an app each shop owns, and a way to plug in free, open-source and paid services. The kernel discipline is kept: every new action is authorised at Gate 4 and logged, and everything stays "pending human review".

## Authority

Prepared on Travis Lee Swift's direct instruction. It is a Draft: under HVT-0001 Art. IV and V.3 it has no institutional weight until reviewed. **The six new Studio actions extend what the Architecture Office's agent may do in software. That extension is itself pending Chief Architect review.** No one's approval or stamp is claimed.

## Traceability and open points

- The Studio now **contacts outside services**, but only when a person presses Search, Test or Run. It sends a descriptive User-Agent and caches results for 24 hours.
- DuckDuckGo was blocked from the build box on 2026-09-26. No Brave key was available. The web search was tested with a simulated network only.
- WhatsApp Cloud API, Xero, Google Business Profile and Royal Mail Click & Drop are **unverified**, because their docs could not be read on 2026-09-26. Evri, Stuart, Uber Direct, Deliveroo, Uber Eats and Just Eat are catalogue entries with no code.
- Storing third-party business details (saved suppliers) and API keys needs a data-protection review. Not done.
- Owner-facing design still awaits Stan Lee's review.
