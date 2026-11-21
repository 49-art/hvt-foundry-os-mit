# BUT-0006 — BusinessType card — Local clinic / practitioner rooms

Document ID: BUT-0006  
Title: BusinessType card — Local clinic / practitioner rooms  
Version: 1.0  
Previous version: 0.2  
Status: Approved  
Previous status (v0.2): Approved by Founder (Travis Lee Swift), 18 Oct 2026; pending Raj and Stan Lee  
Approval record: DR-2026-11-20-10 (earlier: DR-2026-10-18-01)  
Owner: Architecture Office  
Reviewed By: Raj (CEO Office) — Tony Adams, 20 Nov 2026 (DR-2026-11-20-10). Stan Lee Design review: deferred (hibernation), not waived  
Live instance: none  
Depends on: DR-10, DR-12, HVT-0001 Art. VIII, Art. X  
ENG-0005: held  
Note: Foundry does not practise medicine. We assemble diary, people, payments, messages. Clinical records stay on the clinician’s lawful system (Art. VIII).  

---

Filed: artifacts/governance/BUT-0006_local_clinic_practitioner_rooms.md Not an Approved BusinessType. No site. No clinical system.

Howard flags (not closed):
- Sector Services already has SEC-0001. Market Industry “Local health & care rooms” has no MKT ID (not MKT-0001 Personal Care). Do not collapse clinic into salon.
- PRB-0024 overlaps PRB-0001 (missed appointments) and empty-slot family. Share vs new ID open.
- PRB-0028 overlaps optional review gap / proposed PRB-0006.
- Tier 3 clinic suites (Cliniko, Jane, Mindbody, Fresha, Dentally, Phorest) unverified. Do not register as SLC on this card. Do not rip out if already owned (Art. VIII).
- “WhatsApp not clinical advice” is an Art. X / Legal boundary, not an Architecture invention. Legal office not yet staffed on the working list.
- Consumables stock = DR-10 path, not a clinic ERP, not ENG-0005.

### WHAT THIS PRACTICE IS

A high-street or parade-room practice: physio, dentist rooms, osteopath, aesthetic clinic, counselling rooms, GP-adjacent private rooms. Time is the stock. Trust is the product. Paper diaries still exist.

Typical picture
- Practitioner + receptionist, or practitioner alone
- Slots on a wall calendar or a branded diary app
- Recall letters they never send
- No-shows cost more than software
- They are frightened of “patient data in a new app”

Classification Sector: Services Market Industry: Local health & care rooms Business Type: Local clinic / practitioner Business Model: Appointment + fee. Packages / courses of treatment common.

### PROBLEMS

- PRB-0024 No-shows and empty slots PRB-0025 Recall / “you’re due back” never goes out PRB-0026 Diary in one place, payments in another, notes in a third — or on paper PRB-0027 New patients cannot book without phoning during the appointment they are interrupting PRB-0028 Reviews sit unanswered; fear of one bad star

### SHELF (show all)

Tier 4: the diary they already use; the notes system they are legally tied to; their card machine Tier 1: Google Calendar; GBP; WhatsApp Business app (human, not clinical advice on WhatsApp) Tier 2: ENG-0002 booking + reminders ENG-0001 people / recall list ENG-0003 payments / packages DR-10 review path — owner replies, no auto-clinical Tier 3: Cliniko, Jane, Mindbody, Fresha, Dentally, Phorest-class clinic suites — alternatives on the shelf. Do not rip them out if already owned. Never: Foundry-hosted clinical notes as a “feature”

### GAPS

Lawful medical record = out of scope (correct gap) Insurance / NHS pathways = out of scope unless Search Stock of consumables (needles, product) = DR-10 path or held ledger, not a clinic ERP

### MINIMUM PATH

Keep their notes system. ENG-0002 or their existing clinic suite for slots. Reminders on a channel they already read. Payments on the account they already have. GBP hours + review replies.

STAN LEE TEST No stock-photo white coats, no fake five-star row, no “wellness serenity” template. Rooms look like their rooms.

USED BY: none MATURITY: Draft schema


## Resolution — v1.0, 20 Nov 2026 (DR-2026-11-20-08 / -10)

- **Status:** Approved card v1.0 — classification only. Live instance: none. Overlay: HVT-0006-OVL-0006.
- **Classification IDs:** MKT-0006 under SEC-0001 Services.
- **Problems:** PRB-0024, PRB-0025, PRB-0026, PRB-0027, PRB-0028 (minted in the graph; overlaps recorded with family_of).
- **Business Model:** Appointment + fee; packages / courses of treatment common. **complexity_score:** 2 (computed, DR-2026-11-20-07 §7).
- **ENG-0002:** on — time is the stock. **ENG-0005:** authorised on trigger (DR-2026-11-20-05) — not a recommended engine.
- **Howard flags:** each one closed in DR-2026-11-20-10 §3 (table).
- **Stan Lee:** Design review deferred (hibernation), not waived — Brand Intake + veto before any public surface.
- **MATURITY (supersedes the line above):** Approved card v1.0.

## Version history (added 2026-10-18)

| Version | Date | Change |
|---|---|---|
| 0.1 | (earlier) | Status was: Draft |
| 0.2 | 2026-10-18 | Approved by Founder (Travis Lee Swift), 18 Oct 2026; pending Raj and Stan Lee. Founder approval recorded. The record names Raj and Stan Lee as sign-off. Text unchanged from v0.1. Founder's words: “APPROVE EVERYTHING IN THE WAY YOU FEEL IT SHOULD BE.” See DR-2026-10-18-01. |
| 1.0 | 2026-11-20 | Approved. Approved card v1.0 (classification only). Owner's instruction, 20 Nov 2026: “can you complete all decisions waiting and complete it.” See DR-2026-11-20-10. |
