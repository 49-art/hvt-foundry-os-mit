# DR-2026-11-21-01 — Licence split: an MIT edition (public) and a proprietary edition (private)

Document ID: DR-2026-11-21-01  
Title: Licence split — MIT edition (public) and proprietary edition (private)  
Version: 1.0  
Status: Approved  
Owner: CEO Office  
Reviewed By: Travis Lee Swift (Tony Adams), Founder and human owner — CEO Office, instruction of 21 Nov 2026  
Drafted By: Claude (AI executor) on the owner's instruction — a draft carries no weight of its own (HVT-0001 Art. IV); this record carries the owner's instruction  
Dependencies: LICENSE; README ("License"); DR-2026-09-25-01; DR-2026-09-25-02 §4; DR-2026-11-20-01; DR-2026-11-20-12  

---

## 1. What was said

On 21 November 2026 the owner said, word for word:

> **"put it in 2 repos, 1 with mit added to name in git and the other propriety. then people can improve the mit repo. while i carry on with my version. we will see who comes out best then. after give me links to mit repo to publish"**

## 2. Background: where MIT came from

The MIT licence was never decided on its own before this record.

1. The README in the source record (HVT_Foundry_Full_Record.pdf) says, under the heading "License": "MIT — see LICENSE. Contributions and forks welcome."
2. DR-2026-09-25-01 copied that README word for word.
3. DR-2026-09-25-02 §4 then created a LICENSE file to match: MIT, "Copyright (c) 2026 Travis Lee Swift / HVT Foundation".
4. The 20 Nov 2026 completion pass (DR-2026-11-20-02) approved DR-2026-09-25-02 together with everything else.

## 3. Decision

1. The HVT Foundry OS, as handed over after the 20 Nov 2026 completion pass (DR-2026-11-20-01 … -12), is split into two repositories:

| Repository | Licence | Visibility | Purpose |
|---|---|---|---|
| 49-art/hvt-foundry-os-mit | MIT | Public | Anyone may use, copy, change and improve it |
| 49-art/hvt-foundry-os-mine | Proprietary — all rights reserved | Private | The owner's own version, developed separately |

2. **Both repositories start from the same first commit**, "Snapshot as received: HVT Foundry OS, 20 Nov 2026 completion pass". That snapshot is unchanged from the bundle handed over.
3. **What changed in each repository after that snapshot:**
   - *MIT edition:* only this record was added. LICENSE and README are unchanged.
   - *Proprietary edition:* this record was added; LICENSE was replaced with an all-rights-reserved notice; the README "License" section was updated to match. The MIT LICENSE text is kept in that repository's first commit, so nothing is deleted (Art. V.4).
4. **The shared snapshot stays under MIT for everyone**, because it is public in the MIT edition. Only work added to the proprietary edition after 21 Nov 2026 is proprietary.
5. **The two editions develop separately.** Nothing moves between them automatically. Bringing a public contribution into the proprietary edition is the owner's decision each time. Code taken from the MIT edition keeps its MIT notice wherever it is used.

## 4. Left open (flagged, not resolved)

1. **Who legally owns the code.** The copyright line names "Travis Lee Swift / HVT Foundation". Whether it should be one of them, or HVT Innovations as the commercial arm, is not decided. The line is unchanged in both editions.
2. **Shop app ownership notes.** The Studio puts a note in every shop app saying the shop may copy, change, host or hand on its app with no licence fee to HVT Innovations (studio/card_app.py, studio/shop_app.py; HVT Foundry principle "Every customer asset belongs to the customer"). This is unchanged in both editions. Whether the proprietary edition keeps it is the owner's decision.
3. **Contribution rules for the public repository.** Who reviews and accepts outside pull requests is not set.

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-11-21 | Logged on the owner's instruction of 21 Nov 2026. |
