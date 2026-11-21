# DR-2026-11-20-10 — BusinessType cards BUT-0002…0007 at v1.0; capability overlays HVT-0006-OVL-0002…0007; index HVT-0006-Q-0001 v1.0

Document ID: DR-2026-11-20-10  
Title: BusinessType cards BUT-0002…0007 Approved v1.0 (classification only); capability overlays OVL-0002…0007 issued; index v1.0  
Version: 1.0  
Status: Approved  
Owner: CEO Office (approval) / Architecture Office (cards)  
Reviewed By: Tony Adams (Raj), CEO Office — 20 Nov 2026. Stan Lee Design review: deferred (hibernation), per the DR-2026-09-04-14 precedent  
Dependencies: DR-2026-09-04-12; DR-2026-09-04-14; DR-2026-11-20-01; DR-2026-11-20-04 §1.3; DR-2026-11-20-05; DR-2026-11-20-07; DR-2026-11-20-08; HVT-0006-OVL-0001  

---

## 1. Cards

| Card | Was | Now | Notes |
|---|---|---|---|
| BUT-0002 CEE grocer-deli | v0.1 "Approved" (Raj, 2026-09-04) | **v1.0 Approved** | Version normalised to the 0.x → 1.0 rule. Howard flags closed (§3) |
| BUT-0003 Neighbourhood grocery + owner-stated trust rules | v0.1 "Approved" | **v1.0 Approved** | Not "the Muslim shop". Foundry stores the owner's sentence and does not certify it |
| BUT-0004 Independent specialist retailer | v0.1 "Approved" | **v1.0 Approved** | |
| BUT-0005 Independent high-street retail | v0.2 Approved by Founder; pending Raj + Stan Lee | **v1.0 Approved** | Routing rule fixed (DR-2026-11-20-08 §3) |
| BUT-0006 Local clinic / practitioner rooms | v0.2 …pending Raj + Stan Lee | **v1.0 Approved** | Clinical notes OUT OF SCOPE, permanently |
| BUT-0007 Carpenter / small building trades | v0.2 …pending Raj + Stan Lee | **v1.0 Approved** | Quote→deposit→schedule is a Workflow candidate, not an Engine |

All six are **approved as classification only**. There are no live instances and no sites. Stan Lee's Design review is deferred, not waived. Any owner-facing surface for any of these types still needs Brand Intake and his veto.

## 2. Capability overlays (HVT-0006 overlay pattern of OVL-0001)

HVT-0006-OVL-0002 … HVT-0006-OVL-0007, one per card, **v1.0 Approved**. Each one lists required and optional capabilities, the covering Engine or connector path with its Search reference, the ENG-0002 filter, the out-of-scope lines and the wishes slot. The machine-readable copy is the `card` block on each BUT object in graph/foundry_graph.json. That block is what the ENG-0004 ladder (`foundry_os`) reads.

## 3. Howard flags on the cards, closed

| Flag | Decision |
|---|---|
| PRB-0006 never minted (BUT-0002) | Minted as "Reviews sit unanswered" (DR-2026-11-20-08) |
| No SEC-0002 / MKT IDs (all retail cards, BUT-0006, BUT-0007) | Minted: SEC-0002, SEC-0003, MKT-0002…0007 |
| ENG-0002 "conditional" vs "same engines as BUT-0001 until a Search" (BUT-0002) | **The filter wins.** ENG-0002 is not a recommended engine on BUT-0002/0003/0004/0005. It is a filter, switched on by the owner's answer, and no Search is needed to switch off an Engine a shop doesn't need |
| Dual-type 0002 + 0003 (BUT-0003); offcuts 0007 → 0004/0005 (BUT-0007) | Allowed via primary + also_business_types (DR-2026-11-20-08 §3) |
| Shared PRB-0007 / PRB-0005 | Shared IDs confirmed. No duplicates |
| PRB overlaps (0020/0019, 0021/0010, 0024/0001+0002, 0028/0006) | Kept as their own IDs, linked with family_of |
| Product marks on StockItem only if ENG-0005 (BUT-0003) | StockItem schema adopted. Instances only after the ENG-0005 trigger. Until then the sheet column is the Customer Asset |
| Instagram as Customer Asset (BUT-0004) | Confirmed. No Instagram Engine, and the Foundry never takes the account |
| BUM- splits for BUT-0004 breadth | First BUM- minted when a real repair or bridal shop needs different Workflows (DR-2026-11-20-07 §6) |
| Tier 3 names unverified (BUT-0005/6/7) | Shown as "unverified candidate" on the shelf. Not registered (DR-2026-11-20-09 §6) |
| "Cali" nickname (BUT-0005) | Retired: it means "Tier 3 premium" (DR-2026-11-20-03) |
| DOC-0008 Draft pointer on the BUT-0005 shelf | DOC-0008 is now v1.0 Approved |
| Legal office unstaffed; "WhatsApp is not clinical advice" (BUT-0006) | The boundary is adopted as a card rule now (Art. X). Legal review is a live-human item (DR-2026-11-20-12) |
| Lead-marketplace lock-in (BUT-0007) | Shelf label "lead door — warn lock-in" |

## 4. Index

HVT-0006-Q-0001 → **v1.0 Approved**. It now indexes BUT-0001…0007 and OVL-0001…0007.

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-11-20 | Logged. |
