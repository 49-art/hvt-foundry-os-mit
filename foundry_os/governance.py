"""Governance verifier: Appendix A headers, status words, ID uniqueness, Draft DR carriage,
graph boot, and sequential DR numbering."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Dict, List

from . import CONSTITUTION, GRAPH, ROOT

sys.path.insert(0, str(ROOT / "kernel"))
from foundry_kernel import FoundryKernel, parse_metadata_header  # noqa: E402

HEADER_FIELDS = ("Document ID", "Title", "Version", "Status")
STATUS_START = ("Approved", "Draft", "Superseded")
DOC_DIRS = ("governance", "assets", "decisions")


def _vkey(v: str):
    return tuple(int(x) for x in re.findall(r"\d+", v or "0")) or (0,)


def scan(root: Path = ROOT) -> List[Dict[str, str]]:
    docs = []
    for d in DOC_DIRS:
        for p in sorted((root / d).glob("*.md")):
            meta = parse_metadata_header(p.read_text(encoding="utf-8"))
            meta["_file"] = f"{d}/{p.name}"
            docs.append(meta)
    return docs


def verify(root: Path = ROOT) -> Dict[str, object]:
    errors: List[str] = []
    docs = scan(root)
    for m in docs:
        miss = [f for f in HEADER_FIELDS if not m.get(f)]
        if miss:
            errors.append(f"{m['_file']}: header missing {miss}")
        if m.get("Status") and not m["Status"].startswith(STATUS_START):
            errors.append(f"{m['_file']}: status {m['Status']!r} not in Draft/Approved/Superseded")
    # current version per ID = highest Version; must be unique and not Draft
    by_id: Dict[str, List[Dict[str, str]]] = {}
    for m in docs:
        if m.get("Document ID"):
            by_id.setdefault(m["Document ID"], []).append(m)
    current = {}
    for i, ms in by_id.items():
        top = max(_vkey(x.get("Version")) for x in ms)
        cur = [x for x in ms if _vkey(x.get("Version")) == top]
        if len(cur) > 1:
            errors.append(f"{i}: {len(cur)} files claim current version {cur[0].get('Version')} (ID reuse)")
        current[i] = cur[0]
        if cur[0].get("Status", "").startswith("Draft") and not i.startswith("DR-"):
            errors.append(f"{i}: current version is still Draft ({cur[0]['_file']})")
    # Draft decision records are never edited (Art. V.4): a later Approved DR must carry them.
    approvals = " ".join((root / "decisions" / Path(m["_file"]).name).read_text(encoding="utf-8")
                         for m in docs if m["_file"].startswith("decisions/DR-2026-11-20")
                         and m.get("Status") == "Approved")
    drafts = [i for i, m in current.items() if i.startswith("DR-") and m.get("Status", "").startswith("Draft")]
    for i in drafts:
        if i not in approvals:
            errors.append(f"{i}: Draft decision not carried by any DR-2026-11-20 approval")
    # sequential numbering of the completion series
    nums = sorted(int(i.rsplit("-", 1)[1]) for i in by_id if re.fullmatch(r"DR-2026-11-20-\d{2}", i))
    if nums != list(range(1, len(nums) + 1)):
        errors.append(f"DR-2026-11-20 series not sequential: {nums}")
    # graph boots
    k = FoundryKernel()
    try:
        k.load_constitution(CONSTITUTION)
        k.load_graph(GRAPH)
        graph_objects = len(k.objects)
    except Exception as e:  # pragma: no cover - reported, not raised
        errors.append(f"graph boot failed: {e}")
        graph_objects = 0
    return {"ok": not errors, "errors": errors, "documents": len(docs), "document_ids": len(by_id),
            "draft_decisions_carried": len(drafts), "completion_drs": len(nums), "graph_objects": graph_objects,
            "constitution_version": (k.constitution or {}).get("Version")}
