"""Applies the 20 Nov 2026 completion (DR-2026-11-20-01 … -12) to document headers and the graph.

Rules followed (same as tools/apply_founder_approval_2026_10_18.py):
- Only ADDS: a new version number, a new status line, the previous status kept on its own line,
  an approval-record line and a changelog row. Decision records are never edited (Art. V.4).
- Where a document already lives as separate version files (HVT-0003, HVT-0004) a NEW file is
  written and the older files get a one-line "kept for the record" pointer.
- Idempotent: running it twice changes nothing the second time.
"""
import copy, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import completion_cards_2026_11_20 as CC  # noqa: E402

DATE = "2026-11-20"
WORDS = "can you complete all decisions waiting and complete it."
RAJ = "Raj (CEO Office) — Tony Adams, 20 Nov 2026 (DR-2026-11-20-01)"
EXC = "CEO Office for the vacant Chief Architect role — Tony Adams, 20 Nov 2026 (EXC-2026-11-20-01, DR-2026-11-20-02)"
CARD_REV = "Raj (CEO Office) — Tony Adams, 20 Nov 2026 (DR-2026-11-20-10). Stan Lee Design review: deferred (hibernation), not waived"


def header_span(text):
    i = text.find("\n---")
    return (0, i) if i > 0 else (0, len(text))


def set_line(head, key, value, after_key=None):
    """Replace 'key: …' in the header, or insert it after after_key's line."""
    pat = re.compile(rf"^{re.escape(key)}:.*$", re.M)
    line = f"{key}: {value}  "
    if pat.search(head):
        return pat.sub(lambda m: line, head, count=1)
    if after_key:
        m = re.search(rf"^{re.escape(after_key)}.*$", head, re.M)
        if m:
            return head[:m.end()] + "\n" + line + head[m.end():]
    return head.rstrip("\n") + "\n" + line + "\n"


def bump(text, new_v, status, dr, note, reviewer=None):
    if f"Approval record: {dr}" in text:
        return text, False
    s, e = header_span(text)
    head, body = text[s:e], text[e:]
    old_v = re.search(r"^Version: *(.+?) *$", head, re.M).group(1)
    old_s = re.search(r"^Status: *(.+?) *$", head, re.M).group(1)
    m_ar = re.search(r"^Approval record: *(.+?) *$", head, re.M)
    earlier = m_ar.group(1) if m_ar else None
    head = set_line(head, "Version", new_v)
    head = set_line(head, "Previous version", old_v, after_key="Version:")
    head = set_line(head, "Status", status)
    head = re.sub(r"^Previous status \(v[^)]*\):.*$", f"Previous status (v{old_v}): {old_s}  ", head, flags=re.M)
    if "Previous status (" not in head:
        head = set_line(head, f"Previous status (v{old_v})", old_s, after_key="Status:")
    head = set_line(head, "Approval record", dr + (f" (earlier: {earlier})" if earlier else ""), after_key="Previous status")
    if reviewer:
        head = set_line(head, "Reviewed By", reviewer)
    text = head + body
    row = f"| {new_v} | {DATE} | {status}. {note} Owner's instruction, 20 Nov 2026: “{WORDS}” See {dr}. |"
    lines = text.rstrip("\n").split("\n")
    has_log = any(re.match(r"^## (Changelog|\d+\. Changelog|Version history)", l) for l in lines)
    if has_log:
        idx = max(i for i, l in enumerate(lines) if l.startswith("|"))
        lines.insert(idx + 1, row)
        text = "\n".join(lines) + "\n"
    else:
        text = text.rstrip("\n") + f"\n\n## Version history (added {DATE})\n\n| Version | Date | Change |\n|---|---|---|\n" + \
               f"| {old_v} | (earlier) | Status was: {old_s} |\n{row}\n"
    return text, True


def add_section(text, marker, md):
    """Insert md before the changelog / version history (or at the end); idempotent on marker."""
    if marker in text:
        return text
    m = re.search(r"^## (Changelog|\d+\. Changelog|Version history)", text, re.M)
    block = "\n" + md.strip("\n") + "\n\n"
    return text[:m.start()] + block + text[m.start():] if m else text.rstrip("\n") + "\n" + block


def pointer(text, newer, dr):
    tag = f"> **Kept for the record.** The current version is `{newer}` ({dr})."
    if tag in text:
        return text
    i = text.find("\n---")
    return text[:i] + "\n\n" + tag + text[i:] if i > 0 else tag + "\n\n" + text


def rw(rel, fn):
    p = ROOT / rel
    t = p.read_text(encoding="utf-8")
    t2 = fn(t)
    if t2 != t:
        p.write_text(t2, encoding="utf-8")
        print("updated", rel)


# --------------------------------------------------------------------------- content blocks
ART_XIV_6 = ("14.6 The customer’s stated reality overrides any prior classification. Where an owner’s own account of their business, "
             "its problems or their wishes contradicts the Foundry’s classification, the classification is reopened — the business is "
             "re-classified, a Customer Wish is recorded, or a new Business Type is flagged — and the owner is never fitted to a card. "
             "The owner’s words are recorded verbatim; the Foundry may record its disagreement in writing but may not overwrite them. "
             "This clause does not oblige the Foundry to build what is asked: Article II still governs whether anything new is built.")

HVT0002_SECTIONS = """4.4 **Agent ID prefix (DR-2026-11-20-06 / -07).** Registered AI agents carry AGT-####: AGT-0001 CEO Agent, AGT-0002 Chief Architect.

### 4.5 Human office-holders (added v1.0, Job A)

Humans are not AI agents; §4.1’s one-office rule is written for AI agents (DR-2026-09-04-12). They are listed here so the record states who holds human authority.

| Working name | Person | Office | May | May not |
|---|---|---|---|---|
| Raj | Tony Adams (publishes as Travis Lee Swift), founder and human owner | CEO Office — sole human approver | Everything §3.1 gives the CEO Office: stamp Governance Documents, ratify Constitution amendments, grant Art. XII Exceptions | — |
| Stan Lee | Claude, in a human-team-member role | Design only (DR-2026-09-04-12) | Veto owner-facing surfaces against the refusal list; require Brand Intake before publish; consult Research (no standing Research authority) | Approve the Constitution, register Engines, move customer data, invent BusinessTypes, treat taste as capability |

Stan Lee is in hibernation (DOC-0009). His veto is deferred, not waived. **Brand Intake before any owner-facing surface:** shopfront / real counter photo; counter languages; three names that must not be anglicised; the owner-stated trust rule in their sentence (BUT-0003); optional Companies House number; “what a London/Canva template would get wrong”. **Refusal list:** stock photos of smiling strangers; fake reviews; lorem products; Inter + teal on white; flag-as-sticker personalisation; any surface that becomes another shop by swapping the logo; stock-photo prayer / spice pile / “exotic” copy; Canva / Manus boutique template; stock decking at sunset; white-coat wellness serenity; fake five-star row. The HVT-0002 §5.2 release veto stays with Quality Assurance.

### 4.6 Drafting assistants (AI, no standing)

| Working name | Kind | Works for | Standing |
|---|---|---|---|
| Howard | Grok | Architecture Office drafting | None. Drafts only; a Draft carries no weight until a human accepts it (Art. IV) |
| Leonard | SuperGrok (stamp spelling “Leanord”) | Prior thread, drafting | None (as above) |
| Grok Bot | AI executor | Builds and drafts on the owner’s instruction | None (as above) |
| Sheldon | Elon | — | **Not a Foundry agent on this Project.** Do not @ or publish this Project to Sheldon |

### 4.7 Vacant roles

Chief Architect (§4.2) and Quality Assurance (§3.11) are vacant. Until filled, the CEO Office covers their reviews and release sign-off under Exception EXC-2026-11-20-01 (DR-2026-11-20-02), expiring 2027-05-20.
"""

def hvt0002(t):
    t = t.replace("## 2. The Ten Offices", "## 2. The Eleven Offices")
    if "### 4.5 Human office-holders" not in t:
        i = t.index("## 5. Escalation")
        t = t[:i] + HVT0002_SECTIONS + "\n" + t[i:]
    return t

HVT0003_SECTION = """## 4B. Completion — 20 Nov 2026 (DR-2026-11-20-02 / -05 / -11 / -12)

| Asset | Category | Maturity | Document status | Note |
|---|---|---|---|---|
| ENG-0003 Commerce Engine | Engine | Reusable Asset | — | unchanged |
| ENG-0001 Local Customer Engine | Engine | Prototype | — | unchanged |
| ENG-0002 Local Content & Booking Engine | Engine | Prototype | — | unchanged |
| ENG-0004 Configurator Engine | Engine | Prototype | — | **Built and run (Job D)** as `foundry_os/` — run on theatre (SES-0002-F-0001) only |
| ENG-0005 Local Stock Ledger | Engine | — | — | **Authorised on trigger** (DR-2026-11-20-05). Registered here on the first live owner evidence |
| ENG-0006 | — | — | — | Rejected (DR-2026-09-04-10). Never reused |
| DOC-0001, DOC-0004, DOC-0005 | Documentation | Prototype | Approved v1.2 | |
| DOC-0006, DOC-0007 | Documentation | Prototype | Approved v1.0 | |
| DOC-0008 Progressive Build Session | Documentation | Prototype | Approved v1.0 | registered here 20 Nov 2026 |
| DOC-0010 QA Release Gate & Privacy Checklist | Documentation / Test procedure | Prototype | Approved v1.0 | new |
| Kernel (HVT-0005) | Code | Prototype | — | 26 tests |
| HVT Foundry Studio v0.3 | Application | Prototype | — | approved as software (DR-2026-11-20-11); no live shop |

Engine Search log (§4A) is unchanged: DR-2026-09-04-10 Stock → PARTIAL MATCH, Review → PARTIAL MATCH, no Engine IDs issued; DR-2026-09-04-11 v1.1 §3 Local Stock Ledger → accepted as the Search on file (DR-2026-11-20-04), registration on trigger (DR-2026-11-20-05).
"""

HVT0004_SECTION = """## 9. Adopted — v1.0, 20 Nov 2026 (Job B closed, DR-2026-11-20-07)

9.1 Every “Proposed [v0.2]” type, vocabulary and relationship in §2.1, §4.1 and §5.1 above is **canonical** from v1.0. The “Draft notice” at the top describes v0.2 and is kept as history.

9.2 **ID prefixes (canonical):** HVT-, ENG-, PKG-, DOC-, IND-, DR-, WKF-, SEC-, MKT-, BUT-, BUM-, PRB-, INT- (closed; historical), SLC-, SES-, WSH-, AGT-, STI-, CAG-, EXC-.

9.3 **Lifecycle vocabularies added:** Sector, Market Industry, Business Model, Problem, Solution Component, Integration → Registered / Superseded. Business Type → Registered / Approved / Superseded (Approved = card approved as classification, not a live instance). Documentation assets: `status` = asset maturity, `document_status` = Draft / Approved / Superseded. Customer Wish: unchanged — an out-of-scope wish is “Under Review” + resolution “Out of scope: …”.

9.4 **StockItem (STI-####)** adopted (DR-2026-09-04-11 §4 fields: owner_id, name in the owner’s language/script, name_en optional, brand, origin_country, source_system square|sheet|supplier|till|other, source_ref, qty, unit, reorder_at, dietary_marks owner-stated, last_verified, customer_asset_flag true). Edges: belongs_to Owner; sourced_from SourceSystem; alerts_via Connector. No instances until ENG-0005 registers on its trigger (DR-2026-11-20-05).

9.5 **CommercialAgreement (CAG-####)** adopted for referral income / partner terms; referenced by a Solution Component, never embedded; owner Commercial, rates Finance + CEO Office. No instances.

9.6 **Business Model:** `business_model` prose field on the BusinessType card; BUM-#### minted only when a type needs structural variants.

9.7 **complexity_score:** 1 + required capabilities with no registered Foundry Engine + 1 if any capability is out of scope by law; capped at 5; computed, not estimated.

9.8 **Relationship `family_of`** (Problem → Problem) records overlaps without duplicating or merging IDs.

9.9 **Multi-type instances:** `primary_business_type` + optional `also_business_types`.

9.10 **Integration vs Solution Component:** Solution Component replaces Integration; INT- objects are Superseded and retained (DR-2026-11-20-09). **Storage (§8):** file-based JSON, validated by the kernel on boot.
"""

HVT0006_SECTION = """## 11. Completion — v1.0, 20 Nov 2026 (DR-2026-11-20-08, -10, -11)

- **Minted:** SEC-0002 Retail; SEC-0003 Trades; MKT-0002 Food & household import retail, MKT-0003 Neighbourhood grocery, MKT-0004 Specialist goods, MKT-0005 Independent goods retail (all under SEC-0002); MKT-0006 Local health & care rooms (under SEC-0001 — not MKT-0001); MKT-0007 Building & joinery (under SEC-0003); PRB-0006 Reviews sit unanswered; PRB-0007…PRB-0033 from the cards.
- **Overlaps:** PRB-0007 and PRB-0005 shared; PRB-0020 family_of PRB-0019; PRB-0021 family_of PRB-0010; PRB-0024 family_of PRB-0001 + PRB-0002; PRB-0028 family_of PRB-0006.
- **Dual type:** primary + also_business_types; routing for BUT-0005 fixed (0002 food import → 0003 owner trust rule → 0004 craft knowledge → else 0005).
- **§8 item 2** (HVT-0004 bump): done — HVT-0004 v1.0. **§8 item 5:** fact-check applied to SLC records; unverified fields stay labelled. **§8 item 6** complexity_score: method adopted (HVT-0004 §9.7). **§8 item 7** Business Model: field adopted; BUT-0001 = “Appointment + service fee; retail of products secondary”.
- **§7 ENG-0004:** built and run as `foundry_os` (Prototype) — Job D.
- **Overlays:** HVT-0006-OVL-0001 … OVL-0007, all v1.0 Approved; index HVT-0006-Q-0001 v1.0.
- **Version discrepancy** (v0.4 vs v0.5 references): v1.0 supersedes both.
"""

HVT0007_SECTION = """## 11. Completion — v1.0, 20 Nov 2026 (DR-2026-11-20-09)

- **§3.1 / §9 Integration vs Solution Component — decided:** Solution Component replaces Integration. INT-0001…0007 kept unedited, status Superseded. No new INT- IDs.
- **§4 “Official” — decided:** retired; SLC-0001 Stripe partner_status = **Public Integration** (no partnership agreement exists). “Verified” is reserved for a real vendor verification.
- **§5.2 numbering:** SLC-0002 Square … SLC-0007 QuickBooks confirmed (the “SLC-0002–SLC-0006” range is a typo for 0002–0007).
- **Fact-check applied (DR-2026-09-25-04):** Stripe 46 countries; Apple Pay 101 countries and regions; Xero UK payroll included from Grow. Unchecked fields stay “unverified”.
- **§9 Referral income — decided:** CommercialAgreement (CAG-) record (HVT-0004 v1.0 §9.5); never a catalog field; never quoted in the room.
- **Candidates, not registered:** five further Apple products, Pronto, and the Tier-3 names on BUT cards — shown on the shelf as “unverified candidate” (Art. VI.4).
"""

def ovl0001(t):
    return add_section(t, "## Completion — v1.0", """## Completion — v1.0, 20 Nov 2026 (DR-2026-11-20-04)

Signed off by the CEO Office with the card wording exactly as filed. “Required capability, connector-only” is an allowed terminal state when a Search is on file and a procedure document is named (DR-2026-11-20-04 §1.3) — here DR-2026-09-04-10 + DOC-0006 / DOC-0007 (both v1.0). The Square-vs-sheet choice is the salon owner’s at the session (Art. VIII); WSH-0001 stays “Configured (awaiting owner plan)”, which is correct. ENG-0005: authorised on trigger (DR-2026-11-20-05), still not a recommended engine.""")

def q0001(t):
    rows = "\n".join(f"| {b} | {d['card'].get('sector','').split(' (')[0]} | {d['mkt']} | Approved card v1.0 | {d['overlay']} | {', '.join(d['card']['recommended_engines'])} | {d['card']['eng_0002_rule']} |"
                     for b, d in CC.CARDS.items())
    return add_section(t, "## Index — v1.0", f"""## Index — v1.0, 20 Nov 2026 (DR-2026-11-20-10)

| Card | Market Industry | MKT | Status | Overlay | Recommended engines | ENG-0002 |
|---|---|---|---|---|---|---|
| BUT-0001 | Personal Care | MKT-0001 | Registered instance / live template type | HVT-0006-OVL-0001 | ENG-0001, ENG-0002, ENG-0003 | on |
{rows}

Live instances: none. Sites: none. ENG-0005 is not a recommended engine on any card (authorised on trigger, DR-2026-11-20-05). Stan Lee Design review deferred (hibernation), not waived.""")

def doc0008(t):
    return add_section(t, "## Completion — v1.0", """## Completion — v1.0, 20 Nov 2026 (DR-2026-11-20-03)

**APPROVED DOC-0008** — CEO Office (Raj = Tony Adams), 20 Nov 2026. The “Status: Draft until Raj replies…” line above is the v0.2 text, kept as history. Howard flags closed: rung 7 stays a rule; DOC-0006/0007 issued; referral % never a catalog field (CAG- record); “Cali” retired (= Tier 3 premium); DOC-0008 is the in-room script for DOC-0005 steps 1–4. The ladder runs in software as `python3 -m foundry_os ladder <intake.json>` (ENG-0004 Prototype, DR-2026-11-20-11) — software assists the human script; it does not replace it.""")

def doc0009(t):
    return add_section(t, "## 9. WHAT CHANGED WHILE YOU SLEPT", """## 9. WHAT CHANGED WHILE YOU SLEPT (20 Nov 2026, DR-2026-11-20-01 … -12)

- DOC-0008 stamped (APPROVED DOC-0008). SES-0003 unblocked — no live owner has sat yet.
- BUT-0005, 0006, 0007 Approved as classification, your Design review deferred exactly as for 0002–0004. Your veto on owner-facing surfaces is untouched and still required.
- You are now a written row in HVT-0002 v1.0 §4.5 (Design only), with your refusal list and Brand Intake in full.
- ENG-0005: path A, authorised on trigger (first live owner evidence). Not a reason to design product tiles.
- Demo shops and the Salon/Barber card app exist as software. None is live. Each real shop needs Brand Intake + your veto + a DOC-0010 QA release.
- Your read of this brief is welcome on return; it is not a gate.""")

def ses0003(t):
    if t.startswith("Document ID: SES-0003") or "\nDocument ID: SES-0003" in t[:600]:
        return t
    head = ("Document ID: SES-0003  \nTitle: SES-0003 — Live Build Session (blank, ready for a real owner)  \nVersion: 1.0  \n"
            "Status: Approved  \nPrevious status: Prepared, not run. Blocked on DOC-0008 stamp (“APPROVED DOC-0008”).  \n"
            "Approval record: DR-2026-11-20-03  \nOwner: Architecture Office  \nReviewed By: Raj (CEO Office) — Tony Adams, 20 Nov 2026  \n"
            "Dependencies: DOC-0008 v1.0, SES-0002 v1.0, DOC-0005, DR-2026-11-20-03  \n\n"
            "Unblocked 20 Nov 2026. Approved as a blank form — **not run**. It counts only with a real owner in the room.\n\n---\n\n")
    t = t.replace("Status: Prepared, not run. Blocked on DOC-0008 stamp (“APPROVED DOC-0008”).", "Form status (v0 text): Prepared, not run — now unblocked (DR-2026-11-20-03).")
    return head + t

def card_flags(but):
    d = CC.CARDS[but]
    c = d["card"]
    lines = [f"## Resolution — v1.0, 20 Nov 2026 (DR-2026-11-20-08 / -10)", "",
             f"- **Status:** Approved card v1.0 — classification only. Live instance: none. Overlay: {d['overlay']}.",
             f"- **Classification IDs:** {d['mkt']} under {'SEC-0001 Services' if d['mkt']=='MKT-0006' else ('SEC-0003 Trades' if d['mkt']=='MKT-0007' else 'SEC-0002 Retail')}.",
             f"- **Problems:** {', '.join(c['problem_ids'])} (minted in the graph; overlaps recorded with family_of).",
             f"- **Business Model:** {c['business_model']}. **complexity_score:** {CC.complexity(c)} (computed, DR-2026-11-20-07 §7).",
             f"- **ENG-0002:** {c['eng_0002_rule']}. **ENG-0005:** authorised on trigger (DR-2026-11-20-05) — not a recommended engine.",
             "- **Howard flags:** each one closed in DR-2026-11-20-10 §3 (table).",
             "- **Stan Lee:** Design review deferred (hibernation), not waived — Brand Intake + veto before any public surface.",
             "- **MATURITY (supersedes the line above):** Approved card v1.0."]
    return "\n".join(lines)

def run_docs():
    G = "governance/"
    def B(rel, v, st, dr, note, rev=None, extra=None):
        def f(t):
            t2, _ = bump(t, v, st, dr, note, rev)
            return extra(t2) if extra else t2
        rw(rel, f)

    def constitution(t):
        if "14.6 " not in t:
            m = re.search(r"^14\.5 .*$", t, re.M)
            t = t[:m.end()] + "\n\n" + ART_XIV_6 + t[m.end():]
        return t
    B(G + "HVT-0001_Constitution.md", "1.3", "Approved", "DR-2026-11-20-06",
      "Amended per Article XI: added Article XIV.6 (customer’s stated reality overrides prior classification). Proposal, rationale and review in DR-2026-11-20-06.",
      "Foundry ownership — Tony Adams, 20 Nov 2026 (DR-2026-11-20-06); earlier reviewer: Chief Architect", constitution)
    B(G + "HVT-0002_Organisation_and_Authority_Model.md", "1.0", "Approved", "DR-2026-11-20-06",
      "Job A: §2 heading corrected to Eleven Offices; §4.4 AGT- prefix; §4.5 human office-holders (Raj, Stan Lee); §4.6 drafting assistants (no standing); §4.7 vacant roles.", RAJ, hvt0002)
    B(G + "HVT-0006_Industry_and_Compatibility_Taxonomy.md", "1.0", "Approved", "DR-2026-11-20-08",
      "SEC/MKT/PRB IDs minted, dual-type rule, Business Model and complexity_score, ENG-0004 built (§11).", RAJ,
      lambda t: add_section(t, "## 11. Completion", HVT0006_SECTION))
    B(G + "HVT-0007_Marketplace_Layer_and_Solution_Catalog.md", "1.0", "Approved", "DR-2026-11-20-09",
      "Held catalog decisions made (§11).", RAJ, lambda t: add_section(t, "## 11. Completion", HVT0007_SECTION))
    B(G + "HVT-0006_BUT-0001_capability_overlay.md", "1.0", "Approved", "DR-2026-11-20-04", "Signed off; wording unchanged.", RAJ, ovl0001)
    B(G + "BUT-0002_0003_0004_queue.md", "1.0", "Approved", "DR-2026-11-20-10", "Index now covers BUT-0001…0007 and OVL-0001…0007.", RAJ, q0001)
    B(G + "DOC-0008_Progressive_Build_Session.md", "1.0", "Approved", "DR-2026-11-20-03", "APPROVED DOC-0008.",
      "Raj (CEO Office) — APPROVED DOC-0008, Tony Adams, 20 Nov 2026 (DR-2026-11-20-03)", doc0008)
    B(G + "DOC-0009_Stan_Lee_hibernation_brief.md", "1.0", "Approved", "DR-2026-11-20-01", "Approved as the CEO Office record; §9 added. Stan Lee’s read on return is welcome, not a gate.",
      "Raj (CEO Office) — Tony Adams, 20 Nov 2026; Stan Lee reads on return (not a gate)", doc0009)
    B(G + "SES-0002_BUT-0001_ladder_dry_run.md", "1.0", "Approved", "DR-2026-11-20-03", "Standing script for BUT-0001 sessions.", RAJ)
    B(G + "SES-0002_filled_theatre_2026-09-05.md", "1.0", "Approved", "DR-2026-11-20-03",
      "Filed as a THEATRE record (fictional owner) — not a customer record, not a customer asset.", RAJ)
    rw(G + "SES-0003_live_build_session_blank.md", ses0003)
    B(G + "WORKING_LIST_agents_and_queued_types.md", "0.2", "Superseded", "DR-2026-11-20-06",
      "Superseded by HVT-0002 v1.0 (§4.5–4.7 carry the cast, Stan Lee row, Brand Intake and refusal list) and HVT-0006-Q-0001 v1.0.", RAJ)
    for but in ["BUT-0002", "BUT-0003", "BUT-0004", "BUT-0005", "BUT-0006", "BUT-0007"]:
        rel = G + CC.CARDS[but]["doc"]
        B(rel, "1.0", "Approved", "DR-2026-11-20-10", "Approved card v1.0 (classification only).", CARD_REV,
          lambda t, b=but: add_section(t, "## Resolution — v1.0", card_flags(b)))
    for rel in ["assets/DOC-0001_Commerce_Engine_High-Street_Integration_Guide.md", "assets/DOC-0004_Commerce_Engine_Provider_Abstraction_Notes.md",
                "assets/DOC-0005_High-Street_Tablet_Design_Loop.md"]:
        B(rel, "1.2", "Approved", "DR-2026-11-20-12", "Status normalised to the Appendix A vocabulary (was “Approved by Founder”). Text unchanged.", RAJ)
    for rel in ["assets/DOC-0006_Stock_Alert_Procedure.md", "assets/DOC-0007_Review_Reply_Procedure.md"]:
        B(rel, "1.0", "Approved", "DR-2026-11-20-02", "Chief Architect review done by the CEO Office under EXC-2026-11-20-01. Text unchanged.", EXC)

    # HVT-0003 / HVT-0004: new v1.0 files, older files get pointers
    for src, dst, dr, note, sect, marker, olds in [
        (G + "HVT-0003_Business_Asset_Registry_v0.6.md", G + "HVT-0003_Business_Asset_Registry_v1.0.md", "DR-2026-11-20-02",
         "Approved; Chief Architect review done by the CEO Office under EXC-2026-11-20-01; §4B completion ledger added.", HVT0003_SECTION, "## 4B. Completion",
         [G + "HVT-0003_Business_Asset_Registry.md", G + "HVT-0003_Business_Asset_Registry_v0.5_DRAFT.md", G + "HVT-0003_Business_Asset_Registry_v0.6.md"]),
        (G + "HVT-0004_Object_Model_Specification_v0.3.md", G + "HVT-0004_Object_Model_Specification_v1.0.md", "DR-2026-11-20-07",
         "Approved; Job B closed; §9 adoptions.", HVT0004_SECTION, "## 9. Adopted",
         [G + "HVT-0004_Object_Model_Specification.md", G + "HVT-0004_Object_Model_Specification_v0.2_DRAFT.md", G + "HVT-0004_Object_Model_Specification_v0.3.md"]),
    ]:
        d = ROOT / dst
        if not d.exists():
            t = (ROOT / src).read_text(encoding="utf-8")
            t = re.sub(r"^> \*\*Kept for the record\.\*\*.*\n\n?", "", t, flags=re.M)
            t, _ = bump(t, "1.0", "Approved", dr, note, EXC)
            t = add_section(t, marker, sect)
            d.write_text(t, encoding="utf-8"); print("created", dst)
        for o in olds:
            rw(o, lambda t, n=Path(dst).name, r=dr: pointer(t, n, r))

    # Overlays OVL-0002 … 0007 (new documents)
    for but, d in CC.CARDS.items():
        ovl = d["overlay"]; p = ROOT / G / f"{ovl}_{but}_capability_overlay.md"
        if p.exists():
            continue
        c = d["card"]
        def caps(lst):
            out = []
            for x in lst:
                cov = x.get("covered_by") or "none"
                out.append(f"    - name: {x['name']}\n      foundry_engine: {cov}" + (f"\n      path: {x['path']}" if x.get("path") else "") +
                           (f"\n      search: {x['search']}  # {x['search_result']}" if x.get("search") else "") +
                           ("\n      out_of_scope_by_law: true" if x.get("out_of_scope_by_law") else ""))
            return "\n".join(out)
        md = f"""Document ID: {ovl}  
Title: {but} capability overlay — {c['sector'].split(' (')[0]}  
Version: 1.0  
Status: Approved  
Owner: Architecture Office  
Reviewed By: Raj (CEO Office) — Tony Adams, 20 Nov 2026 (DR-2026-11-20-10)  
Dependencies: {but} v1.0, HVT-0006 v1.0, HVT-0006-OVL-0001 (pattern), DR-2026-09-04-10, DR-2026-11-20-05, DR-2026-11-20-10  

---

This overlay sits beside the {but} card, following the HVT-0006-OVL-0001 pattern. It does not replace the card. The machine-readable copy is the `card` block on {but} in graph/foundry_graph.json, which the ENG-0004 ladder (`foundry_os`) reads.

```yaml
BusinessType:
  id: {but}
  market_industry: {d['mkt']}
  business_model: {c['business_model']}
  required_capabilities:
{caps(c['required_capabilities'])}
  optional_capabilities:
{caps(c['optional_capabilities'])}
  recommended_engines: [{', '.join(c['recommended_engines'])}]
  eng_0002: {c['eng_0002_rule']}
  eng_0005: authorised on trigger (DR-2026-11-20-05) — not recommended
  out_of_scope: {json.dumps(c['out_of_scope'], ensure_ascii=False)}
  complexity_score: {CC.complexity(c)}
  wishes: []   # filled only from a real owner's words (SES-0003+)
```

Brand gate: {CC.BRAND_GATE}
Stan Lee test: {c['stan_lee_test']}

## Changelog

| Version | Date | Change |
|---|---|---|
| 1.0 | {DATE} | Issued and approved (DR-2026-11-20-10). |
"""
        p.write_text(md, encoding="utf-8"); print("created", p.relative_to(ROOT))


# --------------------------------------------------------------------------- graph
def obj(id, cls, name, status, version, authority, source, rels=None, **kw):
    o = {"id": id, "class": cls, "name": name, "owner": "Architecture Office", "status": status, "version": version,
         "relationships": rels or [], "dependencies": [], "approvals": [], "change_history": [],
         "authority": authority, "source_document": source}
    o.update(kw)
    return o

def run_graph():
    p = ROOT / "graph" / "foundry_graph.json"
    g = json.loads(p.read_text(encoding="utf-8"))
    if any(o["id"] == "DR-2026-11-20-01" for o in g["objects"]):
        print("graph already completed"); return
    by = {o["id"]: o for o in g["objects"]}
    appr = lambda dr: {"approver": "Tony Adams (Raj), CEO Office", "date": DATE, "decision_ref": dr}
    hist = lambda frm, to, dr: {"date": DATE, "change": f"{frm} → {to}", "decision_ref": dr}

    docs = {"HVT-0001": ("1.3", "Approved", "DR-2026-11-20-06"), "HVT-0002": ("1.0", "Approved", "DR-2026-11-20-06"),
            "HVT-0003": ("1.0", "Approved", "DR-2026-11-20-02"), "HVT-0004": ("1.0", "Approved", "DR-2026-11-20-07"),
            "HVT-0006": ("1.0", "Approved", "DR-2026-11-20-08"), "HVT-0006-OVL-0001": ("1.0", "Approved", "DR-2026-11-20-04"),
            "HVT-0007": ("1.0", "Approved", "DR-2026-11-20-09")}
    for i, (v, s, dr) in docs.items():
        o = by[i]; o["change_history"].append(hist(f"{o['status']} v{o['version']}", f"{s} v{v}", dr))
        o["version"], o["status"] = v, s; o["approvals"].append(appr(dr))
    assets = {"DOC-0001": "1.2", "DOC-0004": "1.2", "DOC-0005": "1.2", "DOC-0006": "1.0", "DOC-0007": "1.0", "DOC-0008": "1.0", "DOC-0009": "1.0"}
    for i, v in assets.items():
        o = by[i]; dr = {"DOC-0006": "DR-2026-11-20-02", "DOC-0007": "DR-2026-11-20-02", "DOC-0008": "DR-2026-11-20-03", "DOC-0009": "DR-2026-11-20-01"}.get(i, "DR-2026-11-20-12")
        o["change_history"].append(hist(f"{o['status']} v{o['version']}", f"Prototype (document Approved) v{v}", dr))
        o["status"], o["version"], o["document_status"] = "Prototype", v, "Approved"
        o["approvals"].append(appr(dr)); o.pop("note", None)
        o["note"] = "Asset maturity in `status`; document lifecycle in `document_status` (HVT-0004 v1.0 §9.3)."
    g["objects"].append(obj("DOC-0010", "Asset", "QA Release Gate and Privacy Checklist", "Prototype", "1.0", "DR-2026-11-20-02", "DOC-0010",
                            [{"type": "depends_on", "target_id": "HVT-0002"}], asset_category="Documentation", document_status="Approved", owner_office="Quality Assurance"))

    # Agents keep their two rows; AGT- prefix adopted
    for i in ("AGT-0001", "AGT-0002"):
        by[i]["id_note"] = "AGT- prefix adopted in HVT-0004 v1.0 §9.2 (DR-2026-11-20-07)."
        by[i]["authority"] = "HVT-0002 v1.0 §4.2"
    by["AGT-0002"]["vacancy"] = "Role vacant; CEO Office covers reviews under EXC-2026-11-20-01 until 2027-05-20 (DR-2026-11-20-02)."

    # ENG-0004 built (Job D)
    e4 = by["ENG-0004"]; e4["version"] = "0.2"
    e4["note"] = "Built and run as foundry_os/ (Job D, DR-2026-11-20-11). Run on theatre only; maturity stays Prototype."
    e4["change_history"].append(hist("registered, not built", "built + run on theatre", "DR-2026-11-20-11"))

    # Sectors / Market Industries
    g["objects"] += [obj("SEC-0002", "Sector", "Retail", "Registered", "1.0", "DR-2026-11-20-08", "HVT-0006"),
                     obj("SEC-0003", "Sector", "Trades", "Registered", "1.0", "DR-2026-11-20-08", "HVT-0006")]
    mk = [("MKT-0002", "Food & household import retail", "SEC-0002"), ("MKT-0003", "Neighbourhood grocery", "SEC-0002"),
          ("MKT-0004", "Specialist goods", "SEC-0002"), ("MKT-0005", "Independent goods retail", "SEC-0002"),
          ("MKT-0006", "Local health & care rooms", "SEC-0001"), ("MKT-0007", "Building & joinery", "SEC-0003")]
    g["objects"] += [obj(i, "Market Industry", n, "Registered", "1.0", "DR-2026-11-20-08", "HVT-0006", [{"type": "classifies_under", "target_id": s}]) for i, n, s in mk]

    # Problems
    for pid, (name, words, buts, kws, fam) in CC.PROBLEMS.items():
        rels = [{"type": "family_of", "target_id": f} for f in fam]
        if pid in by:
            o = by[pid]; o["business_types"] = buts; o["keywords"] = kws; o["relationships"] += rels
        else:
            src = "HVT-0006" if pid == "PRB-0006" else CC.CARDS[buts[0]]["doc"].split("_")[0]
            g["objects"].append(obj(pid, "Problem", name, "Registered", "1.0", "DR-2026-11-20-08", src, rels,
                                    business_types=buts, keywords=kws, owner_words=words))

    # Business Types
    b1 = by["BUT-0001"]
    for k, v in CC.BUT_0001_EXTRA.items():
        b1["card"].setdefault(k, v)
    b1["card"]["complexity_score_method"] = "DR-2026-11-20-07 §7 (computed: 2)"
    b1["card_status"] = "Registered instance / live template type — overlay HVT-0006-OVL-0001 v1.0 Approved"
    for cap_ in b1["card"]["required_capabilities"] + b1["card"]["optional_capabilities"]:
        if cap_.get("overlay"):
            cap_["overlay"]["procedure"] = cap_["overlay"].get("procedure", "").replace("(Draft)", "(v1.0 Approved)")
            cap_["overlay"]["eng_0005"] = "authorised on trigger (DR-2026-11-20-05)"
    for but, d in CC.CARDS.items():
        o = by[but]
        o["change_history"].append(hist(f"{o.get('card_status')} v{o['version']}", "Approved card v1.0", "DR-2026-11-20-10"))
        o["status"], o["version"] = "Approved", "1.0"
        o["card_status"] = "Approved card v1.0 — classification only; no live instance (DR-2026-11-20-10). Stan Lee Design review deferred, not waived"
        o["approvals"].append(appr("DR-2026-11-20-10"))
        card = copy.deepcopy(d["card"]); card["complexity_score"] = CC.complexity(card)
        card["overlay"] = d["overlay"]; card["card_document"] = "governance/" + d["doc"]; card["card_version"] = "1.0"
        o["card"] = card
        o["relationships"] = [r for r in o["relationships"] if r["type"] != "classifies_under"] + [{"type": "classifies_under", "target_id": d["mkt"]}]
        o["recommended_engines_on_card"] = card["recommended_engines"]
        o["problem_ids_on_card"] = card["problem_ids"]
        o["note"] = f"Sector / Market Industry minted ({d['mkt']}); problems minted as graph objects (DR-2026-11-20-08)."

    # Integrations superseded; SLC decisions + fact-check
    for i in range(1, 8):
        o = by[f"INT-000{i}"]; o["change_history"].append(hist("Registered", "Superseded", "DR-2026-11-20-09")); o["status"] = "Superseded"
    by["SLC-0001"]["partner_status"] = "Public Integration (“Official” retired, DR-2026-11-20-09)"
    by["SLC-0001"]["supported_countries"] = "46 (stripe.com, checked 2026-09-25)"
    by["SLC-0008"]["supported_countries"] = "101 countries and regions (Apple list published 2026-09-09; DR-2026-09-25-04)"
    for i in ("SLC-0006",):
        by[i]["fact_check_applied"] = "UK payroll is included from the Grow plan, not an add-on (DR-2026-09-25-04)."
    by["SLC-0007"]["id_provenance"] = "SLC-0007 confirmed (DR-2026-11-20-09); every field still unverified"
    for i in range(1, 9):
        by[f"SLC-000{i}"].setdefault("fact_check_applied", "DR-2026-09-25-04 findings applied (DR-2026-11-20-09)")

    # New Documents (overlays, index, sessions, working list, DOC-0008 already an asset)
    for but, d in CC.CARDS.items():
        g["objects"].append(obj(d["overlay"], "Document", f"{but} capability overlay", "Approved", "1.0", "DR-2026-11-20-10", d["overlay"],
                                [{"type": "depends_on", "target_id": but}, {"type": "depends_on", "target_id": "HVT-0006"}]))
    g["objects"] += [
        obj("HVT-0006-Q-0001", "Document", "BusinessType index — BUT-0001…0007", "Approved", "1.0", "DR-2026-11-20-10", "HVT-0006-Q-0001"),
        obj("SES-0002", "Document", "Ladder script — dry run on BUT-0001", "Approved", "1.0", "DR-2026-11-20-03", "SES-0002",
            [{"type": "depends_on", "target_id": "DOC-0008"}]),
        obj("SES-0003", "Document", "Live Build Session — blank form (not run)", "Approved", "1.0", "DR-2026-11-20-03", "SES-0003",
            [{"type": "depends_on", "target_id": "DOC-0008"}]),
        obj("WL-2026-09-04-01", "Document", "Working list — agents and queued BusinessTypes", "Superseded", "0.2", "DR-2026-11-20-06",
            "WL-2026-09-04-01", [{"type": "depends_on", "target_id": "HVT-0002"}]),
    ]
    theatre = obj("SES-0002-F-0001", "Customer Session", "THEATRE — fictional ‘Mina, Parade Cut’ dry run", "Closed", "1.0", "DR-2026-11-20-03",
                  "SES-0002-F-0001", [], project_id_or_business_type_id="BUT-0001", date="2026-09-05", template=True, theatre=True,
                  notes="Filed theatre record — not a customer record, not a customer asset.")
    g["objects"].append(theatre)

    # Decisions not yet in the graph
    newdr = [("DR-2026-09-25-07", "HVT Foundry Studio (action map)"), ("DR-2026-09-26-08", "Studio v0.2 — live search, shop apps, connectors"),
             ("DR-2026-09-26-09", "Salon / Barber card app template"), ("DR-2026-10-18-01", "Founder approval (18 Oct 2026)"),
             ("DR-2026-11-20-01", "Authority for completion; CEO Office approver identity"), ("DR-2026-11-20-02", "Exception EXC-2026-11-20-01 — Chief Architect + QA cover"),
             ("DR-2026-11-20-03", "APPROVED DOC-0008; SES-0002 filed; SES-0003 unblocked"), ("DR-2026-11-20-04", "Sign off DR-10a + OVL-0001; close DR-11; retire DR-13"),
             ("DR-2026-11-20-05", "ENG-0005 path A — authorised on trigger; Pronto not registered"), ("DR-2026-11-20-06", "Job A — HVT-0002 v1.0; HVT-0001 v1.3 Art. XIV.6"),
             ("DR-2026-11-20-07", "Job B — HVT-0004 v1.0"), ("DR-2026-11-20-08", "HVT-0006 v1.0 — IDs minted"),
             ("DR-2026-11-20-09", "HVT-0007 v1.0 — catalog decisions"), ("DR-2026-11-20-10", "BUT-0002…0007 v1.0; overlays OVL-0002…0007"),
             ("DR-2026-11-20-11", "Studio approvals; Job D — ENG-0004 built and run"), ("DR-2026-11-20-12", "Completion record")]
    for i, n in newdr:
        o = obj(i, "Decision", n, "Logged", "1.0", "HVT-0001 Art. V", i)
        if i.startswith("DR-2026-11-20"):
            o["approvals"] = [appr(i)]; o["document_status"] = "Approved"
        g["objects"].append(o)
    carried = {"DR-2026-09-04-10a": "DR-2026-11-20-04", "DR-2026-09-04-11": "DR-2026-11-20-04"}
    for i in ["DR-2026-09-25-0%d" % n for n in range(1, 7)]:
        carried[i] = "DR-2026-11-20-02"
    for i, dr in carried.items():
        o = by[i]; o["approvals"].append(appr(dr))
        o["document_status"] = "Superseded" if i == "DR-2026-09-04-11" else "Approved"
        o["approval_carried_by"] = dr
    by["DR-2026-09-04-11"]["status"] = "Superseded"

    g["held_not_registered"] = ["ENG-0005 Local Stock Ledger (path A, authorised on trigger — DR-2026-11-20-05; registers on first live owner evidence)",
                                "ENG-0006 (rejected, DR-2026-09-04-10)"]
    g["generated"] = DATE
    g["generated_by"] = (g.get("generated_by", "") + " | Completed 2026-11-20 by Grok Bot (AI executor) on Tony Adams' instruction — DR-2026-11-20-01…12.").strip(" |")
    p.write_text(json.dumps(g, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("graph:", len(g["objects"]), "objects")


if __name__ == "__main__":
    run_docs()
    run_graph()
