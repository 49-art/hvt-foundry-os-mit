# DOC-0010 — QA Release Gate and Privacy Checklist (one shop, one release)

Document ID: DOC-0010  
Title: QA Release Gate and Privacy Checklist — what must be true before anything a real shop or its customers will see goes live  
Version: 1.0  
Status: Approved  
Owner: Quality Assurance (covered by the CEO Office under EXC-2026-11-20-01 until 2027-05-20)  
Reviewed By: Tony Adams, CEO Office — 20 Nov 2026 (DR-2026-11-20-02, DR-2026-11-20-11)  
Dependencies: HVT-0001 Art. IV, VIII, X; HVT-0002 §3.11, §5.2, §5.3; DR-2026-09-04-12; DOC-0008; DR-2026-11-20-02  

---

Use this once per release, for one named shop. File the filled copy as `releases/<shop>-<date>.md`. If any box is NO, the release does not ship (HVT-0002 §5.2). Only a logged Art. XII Exception from the CEO Office can override that (§5.3).

## 1. Model first (Art. XIV)

- [ ] The shop is classified (BUT-####) in a closed, real-owner session (SES-0003 or later). The session record is filed.
- [ ] Every feature in the release traces to a Problem the owner named, or a Wish in their words.

## 2. Brand gate (DR-2026-09-04-12)

- [ ] Brand Intake is complete for this type: fascia / real counter photo, counter languages, three names that must not be anglicised, the owner's trust sentence if BUT-0003, and "what a template would get wrong".
- [ ] Stan Lee's Design veto was asked and **not** used, or the surface is a diary/WhatsApp path that needs no veto (rung 7 SKIP).
- [ ] Refusal list clear: no stock photos of strangers, no fake reviews, no lorem products, no Inter + teal on white, no flag-as-sticker, logo-swap test passes.

## 3. Privacy and customer assets (Art. VIII, X)

- [ ] Customer data, stock lists and photos live on the **owner's** accounts or in the owner's app data folder. The owner holds the export zip.
- [ ] API keys are stored masked and local to the owner's app. No key is sent to the Foundry.
- [ ] Nothing auto-replies to a public review. A trust complaint (BUT-0003) or clinical question (BUT-0006) is always answered by a human.
- [ ] No clinical notes are stored (BUT-0006).
- [ ] A UK GDPR basis is written down for every personal field collected (name, phone, allergies/patch tests only with consent).

## 4. Evidence

- [ ] `python3 -m pytest -q` passes in full on the release commit (record the count).
- [ ] `python3 -m foundry_os verify` passes.
- [ ] Each connector used was run with the owner's real key on their account. Otherwise it is switched off.
- [ ] Reversible: the owner can switch the app off and keep everything (read-back line from DOC-0008 rung 5).

## 5. Sign-off

QA signer (name, office): ________ Date: ________ Shop: ________ Release: ________ Result: PASS / FAIL

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-11-20 | Issued (DR-2026-11-20-02, DR-2026-11-20-11). The next free documentation ID after this is DOC-0011. DOC-0002 and DOC-0003 are not in this repository; they are treated as issued elsewhere and are never reused. |
