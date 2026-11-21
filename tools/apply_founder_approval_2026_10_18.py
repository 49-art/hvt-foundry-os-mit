"""One-off script (kept for the record): applies the founder approval of 18 Oct 2026
(DR-2026-10-18-01) to document headers. It only ADDS: a new version number, a new status
line, the previous status kept on its own line, and a new changelog row. No text is removed.
Two documents that already had separate Draft files get a new file; the old files stay."""
import re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DR = "DR-2026-10-18-01"
WORDS = "APPROVE EVERYTHING IN THE WAY YOU FEEL IT SHOULD BE."
FA = "Approved by Founder (Travis Lee Swift), 18 Oct 2026"
INTERIM = FA + " — interim: the rules also ask for a Chief Architect review, and nobody holds that role yet"
def pending(who): return f"{FA}; pending {who}"

# (file, new_version, status, plain note for the changelog)
ITEMS = [
    ("governance/HVT-0002_Organisation_and_Authority_Model.md", "0.3", FA, "Approved by the founder. Text unchanged from v0.2."),
    ("governance/HVT-0006_Industry_and_Compatibility_Taxonomy.md", "0.6", FA, "Approved by the founder. Text unchanged from v0.5."),
    ("governance/HVT-0007_Marketplace_Layer_and_Solution_Catalog.md", "0.2", FA, "Approved by the founder. Text unchanged from v0.1. The 'Integration vs Solution Component' point Travis asked to hold stays open (§9)."),
    ("governance/BUT-0002_0003_0004_queue.md", "0.3", FA, "Index approved by the founder. Text unchanged from v0.2."),
    ("assets/DOC-0001_Commerce_Engine_High-Street_Integration_Guide.md", "1.1", FA, "Approved by the founder. Text unchanged from v1.0."),
    ("assets/DOC-0004_Commerce_Engine_Provider_Abstraction_Notes.md", "1.1", FA, "Approved by the founder. Text unchanged from v1.0."),
    ("assets/DOC-0005_High-Street_Tablet_Design_Loop.md", "1.1", FA, "Approved by the founder. Text unchanged from v1.0."),
    ("assets/DOC-0006_Stock_Alert_Procedure.md", "0.2", INTERIM, "Approved by the founder as interim. Chief Architect review still to do (role vacant). Text unchanged from v0.1."),
    ("assets/DOC-0007_Review_Reply_Procedure.md", "0.2", INTERIM, "Approved by the founder as interim. Chief Architect review still to do (role vacant). Text unchanged from v0.1."),
    ("governance/DOC-0008_Progressive_Build_Session.md", "0.3", pending("Raj's stamp (reply APPROVED DOC-0008)"), "Founder approval recorded. The document itself says only Raj's stamp makes it live, so it stays pending Raj. Text unchanged from v0.2."),
    ("governance/HVT-0006_BUT-0001_capability_overlay.md", "0.2", pending("Raj"), "Founder approval recorded. Reviewer named in the record is Raj, so it stays pending Raj. Text unchanged from v0.1."),
    ("governance/SES-0002_BUT-0001_ladder_dry_run.md", "0.2", pending("Raj"), "Founder approval recorded. Reviewer named in the record is Raj. Text unchanged from v0.1."),
    ("governance/BUT-0005_independent_high_street_retail.md", "0.2", pending("Raj and Stan Lee"), "Founder approval recorded. The record names Raj and Stan Lee as sign-off. Text unchanged from v0.1."),
    ("governance/BUT-0006_local_clinic_practitioner_rooms.md", "0.2", pending("Raj and Stan Lee"), "Founder approval recorded. The record names Raj and Stan Lee as sign-off. Text unchanged from v0.1."),
    ("governance/BUT-0007_carpenter_small_building_trades.md", "0.2", pending("Raj and Stan Lee"), "Founder approval recorded. The record names Raj and Stan Lee as sign-off. Text unchanged from v0.1."),
    ("governance/DOC-0009_Stan_Lee_hibernation_brief.md", "0.2", pending("Stan Lee (on his return)"), "Founder approval recorded. The record names Stan Lee as reviewer. Text unchanged from v0.1."),
]
# Documents that already live as separate Draft files: approve into a NEW file, keep the old ones.
NEW_FILES = [
    ("governance/HVT-0003_Business_Asset_Registry_v0.5_DRAFT.md", "governance/HVT-0003_Business_Asset_Registry_v0.6.md", "0.6", INTERIM,
     "v0.5 (proposed) text approved by the founder as interim. HVT-0003 is owned by the Chief Architect (HVT-0002 §4.2), and nobody holds that role yet. Text unchanged from v0.5.",
     ["governance/HVT-0003_Business_Asset_Registry.md", "governance/HVT-0003_Business_Asset_Registry_v0.5_DRAFT.md"]),
    ("governance/HVT-0004_Object_Model_Specification_v0.2_DRAFT.md", "governance/HVT-0004_Object_Model_Specification_v0.3.md", "0.3", INTERIM,
     "v0.2 (proposed) text approved by the founder as interim (its header asks for CEO Agent and Chief Architect review; the Chief Architect role is vacant). Text unchanged from v0.2.",
     ["governance/HVT-0004_Object_Model_Specification.md", "governance/HVT-0004_Object_Model_Specification_v0.2_DRAFT.md"]),
]

def bump(text, new_v, status, note):
    if f"Approval record: {DR}" in text:
        return text, False
    m_v = re.search(r"^Version: *(.+?) *$", text, re.M)
    m_s = re.search(r"^Status: *(.+?) *$", text, re.M)
    assert m_v and m_s, "header not found"
    old_v, old_s = m_v.group(1), m_s.group(1)
    text = text[:m_s.start()] + f"Status: {status}  \nPrevious status (v{old_v}): {old_s}  \nApproval record: {DR}  " + text[m_s.end():]
    m_v = re.search(r"^Version: *(.+?) *$", text, re.M)
    text = text[:m_v.start()] + f"Version: {new_v}  \nPrevious version: {old_v}  " + text[m_v.end():]
    row = f"| {new_v} | 2026-10-18 | {status}. {note} Founder's words: “{WORDS}” See {DR}. |"
    if re.search(r"^## Changelog", text, re.M):
        lines = text.rstrip("\n").split("\n")
        idx = max(i for i, l in enumerate(lines) if l.startswith("|"))
        lines.insert(idx + 1, row)
        text = "\n".join(lines) + "\n"
    else:
        text = text.rstrip("\n") + "\n\n## Version history (added 2026-10-18)\n\n| Version | Date | Change |\n|---|---|---|\n" + \
               f"| {old_v} | (earlier) | Status was: {old_s} |\n{row}\n"
    return text, True

def pointer(text, newer):
    tag = f"> **Kept for the record.** The current version is `{Path(newer).name}` ({DR})."
    if tag in text:
        return text
    i = text.find("\n---")
    return text[:i] + "\n\n" + tag + text[i:] if i > 0 else tag + "\n\n" + text

if __name__ == "__main__":
    changed = []
    for rel, v, st, note in ITEMS:
        p = ROOT / rel
        t, did = bump(p.read_text(encoding="utf-8"), v, st, note)
        if did:
            p.write_text(t, encoding="utf-8"); changed.append(rel)
    for src, dst, v, st, note, olds in NEW_FILES:
        d = ROOT / dst
        if not d.exists():
            t, _ = bump((ROOT / src).read_text(encoding="utf-8"), v, st, note)
            t = t.replace("(proposed)", "").replace("Version: " + v + " ", "Version: " + v)
            d.write_text(t, encoding="utf-8"); changed.append(dst)
        for o in olds:
            p = ROOT / o
            p.write_text(pointer(p.read_text(encoding="utf-8"), dst), encoding="utf-8")
    print("\n".join(changed))
