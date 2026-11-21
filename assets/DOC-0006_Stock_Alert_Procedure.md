# DOC-0006 — Stock Alert Procedure (capability specification + Engine Search record)

Document ID: DOC-0006  
Title: Stock Alert Procedure — capability specification for "Stock / inventory tracking (mobile notifications)"  
Version: 1.0  
Previous version: 0.2  
Status: Approved  
Previous status (v0.2): Approved by Founder (Travis Lee Swift), 18 Oct 2026 — interim: the rules also ask for a Chief Architect review, and nobody holds that role yet  
Approval record: DR-2026-11-20-02 (earlier: DR-2026-10-18-01)  
Owner: Architecture Office  
Reviewed By: CEO Office for the vacant Chief Architect role — Tony Adams, 20 Nov 2026 (EXC-2026-11-20-01, DR-2026-11-20-02)  
Dependencies: HVT-0001 Art. II, III.1, VIII, X, XIII.3.e; DR-2026-09-04-10; DR-2026-09-04-10a; DR-2026-09-04-12; HVT-0006-OVL-0001; ENG-0003; SLC-0002; WSH-0001; PRB-0004  
Drafted by: AI executor (Grok Bot) on instruction from Travis Lee Swift, 2026-09-25. Carries no institutional weight until reviewed (HVT-0001 Art. IV.3, V.3).

---

## 1. Why this document exists

DR-2026-09-04-10a lists "DOC-0006 Stock Alert Procedure" as an optional Draft that may be written under Architecture Office authority, and DOC-0008 treats DOC-0006 as a reserved procedure ID. This Draft fills that slot.

It is the written specification for the BUT-0001 capability gap "Stock / inventory tracking (mobile notifications)" (PRB-0004 Manual stock; WSH-0001 "Owner wants stock alerts on phone").

## 2. What this document is NOT

- It is **not an Engine** and does **not** register, reserve or code ENG-0005. ENG-0005 Local Stock Ledger is on **HOLD** under DR-2026-09-04-12 ("Not refused. Not registered. Not coded."). Reopening it needs a new DR (the next number, DR-13, has not been started).
- It does **not** change the Engine Search result recorded in DR-2026-09-04-10 (Approved). It restates that search and adds fresh vendor evidence dated 2026-09-25.
- It does **not** adopt StockItem (STI-) into HVT-0004 (DR-2026-09-04-12, "Explicitly not in this stamp").
- It does **not** choose between paths S1 and S3 for the owner. That choice belongs to the owner (WSH-0001 stays Configured, "awaiting owner plan: Square vs sheet").

## 3. Capability specification (HVT-0001 Art. III.1 terms)

| Item | Specification |
|---|---|
| Capability | Tell the salon owner, on their phone, when a product they sell or use is running low. |
| Inputs | A list of stock items; a current count for each; a "reorder when at or below" number for each. Who counts and when is the owner's choice. |
| Outputs | A low-stock message the owner can see on their phone (email or app notification), naming the item and the count. |
| Decision logic | Alert when count ≤ reorder number. No automatic reordering, no automatic purchase, no payment action. |
| Failure modes | Counts not updated → alert is wrong or missing. Alert goes to an inbox the owner does not read. Tool changes its plan terms. In each case the owner is told plainly; nothing is ordered on their behalf. |
| Ownership | The stock list, counts and reorder numbers are a **Customer Asset** (Art. VIII 8.1; WSH-0001 customer_asset_flag = true). They stay exportable and never become an HVT asset. |
| Human authority | The owner decides what to reorder (Art. X). HVT tooling only surfaces the signal. |

## 4. Engine Search record (HVT-0001 Art. II.2, in the four-step a → b → c → d form used by DR-2026-09-04-10)

Art. II.2 asks: (a) does an existing engine solve this, in whole or in part? (b) can one be extended, parameterized or composed? (c) only if both are "no", with evidence, may new functionality be authorized. DR-10 added a connectors / owner-owned / free step before the build question. Art. II.3 requires the result to be logged in the registry — see HVT-0003 v0.5 Draft §4A.

This restates the search already approved in DR-2026-09-04-10 (Search 1). Evidence rows marked 2026-09-25 were re-checked for this Draft.

| Step | Question | Finding |
|---|---|---|
| a. Existing Engine? | Does a registered Engine already provide stock alerts? | **No.** None of ENG-0001 to ENG-0004 provides stock alerts (DR-10). |
| b. Extend an Engine? | Can an existing Engine be extended within its purpose? | **At most a small extension, later.** DR-10: "Foundry work if any = a thin Commerce adapter later, not ENG-0005." Nothing is approved or built. |
| c. Existing vendor / Solution Component? | Does a catalogued component already do this? | **Yes, partly — path S1.** SLC-0002 Square: low-stock alerts can be set per item/variation in the Square Dashboard; Square emails a low-stock report **90 minutes after each location's closing time** (source: squareup.com/help/gb/en/article/8333-create-inventory-alerts, checked 2026-09-25). The article names no plan restriction, but whether it works on the owner's actual Square plan (Free vs Plus) is **still unverified** — DR-10 already says "confirm on owner's plan". The alert is an email, so it reaches the phone only if that email is on the phone. |
| d. New Engine? | Only if a–c fail. | **Not justified.** Result: **PARTIAL MATCH** (same as DR-10). No ENG-0005 / ENG-0006 registration. |

**Search result: PARTIAL MATCH — unchanged.** Paths as recorded in DR-10: **S1** owner already on Square (SLC-0002) — Square item library + low-stock alerts; **S2** owner on Stripe only (SLC-0001) — Stripe does not give salon-grade stock-on-phone, so use S3 (do not force a new payments account, Art. VIII); **S3** zero new vendor — a Google Sheet or Apple Numbers list, with a WhatsApp/email to the owner's phone when a row is low (the default if the owner has no POS stock today). DR-10 also names **S4** — Pronto, an open-source (Tier 1) candidate Solution Component: "Register only if Raj wants a Tier 1 option on the card… Vendor facts above: unverified." It is not registered and its facts were not checked for this Draft.

## 5. Procedure — path S1 (owner already uses Square for stock)

Steps below come from the Square help article cited above. Screens may differ; follow Square's own current help if they do.

1. In the Square Dashboard, open **Items** and choose the item (or variation) to watch.
2. Turn on stock tracking for it if it is not already on, and set the **low stock alert** number.
3. Make sure the Square account email is one the owner reads on their phone.
4. Square sends a low-stock email after closing time (90 minutes after close, per location).
5. Record in the owner's session notes (SES-) which items are watched. The list itself is the owner's data.

Before recommending S1: confirm on the owner's real plan that low-stock alerts are available (open item).

## 6. Procedure — path S3 (owner has no POS stock, is on Stripe only (S2), or prefers a sheet)

1. The owner keeps a simple sheet (Google Sheets or Apple Numbers, per DR-10 — or whatever they already use): columns *Item*, *Count*, *Reorder at*, *Supplier*, *Last counted*.
2. The owner (or staff) updates *Count* on a regular day they choose.
3. Any row where *Count* ≤ *Reorder at* is marked (e.g. by colour) so it is obvious on the phone app.
4. When a row is low, a WhatsApp or email to the owner's phone flags it (DR-10 S3). The owner decides what to reorder. Nothing is ordered automatically.
5. The sheet is a Customer Asset: it stays in the owner's own account and can be exported at any time.

This path needs no new software and no HVT code. It is what DR-11 §3 described as the "local" alternative, **without** building ENG-0005.

## 7. Things this procedure must never do

- Place orders, pay suppliers or move money (Art. X; ENG-0003 boundaries).
- Store the owner's stock data inside an HVT asset (Art. VIII).
- Claim a vendor feature that has not been checked on the owner's plan.

## 8. Open items (carried, not closed)

- Square low-stock alert availability on the owner's actual plan — **unverified**.
- Pronto (S4) — unregistered, unverified; registering it is Raj's call (DR-10).
- Owner's choice of S1 vs S3 — **pending the owner** (WSH-0001 stays Configured).
- ENG-0005 remains **HOLD** (DR-2026-09-04-12). Any change needs a new DR and Raj's stamp.
- This document needs Chief Architect review before it is more than a Draft.

## Changelog

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-09-25 | Draft created by AI executor on instruction from Travis Lee Swift. Restates DR-2026-09-04-10 Search 1 with 2026-09-25 vendor evidence. Not reviewed. |
| 0.2 | 2026-10-18 | Approved by Founder (Travis Lee Swift), 18 Oct 2026 — interim: the rules also ask for a Chief Architect review, and nobody holds that role yet. Approved by the founder as interim. Chief Architect review still to do (role vacant). Text unchanged from v0.1. Founder's words: “APPROVE EVERYTHING IN THE WAY YOU FEEL IT SHOULD BE.” See DR-2026-10-18-01. |
| 1.0 | 2026-11-20 | Approved. Chief Architect review done by the CEO Office under EXC-2026-11-20-01. Text unchanged. Owner's instruction, 20 Nov 2026: “can you complete all decisions waiting and complete it.” See DR-2026-11-20-02. |
