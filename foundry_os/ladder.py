"""DOC-0008 v1.0 ladder, run from the graph. ENG-0004 Configurator — Prototype (DR-2026-11-20-11)."""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import CONSTITUTION, GRAPH, ROOT

sys.path.insert(0, str(ROOT / "kernel"))
from foundry_kernel import FoundryKernel  # noqa: E402

PENDING = "Draft — pending human review (Raj stamp; not a Foundry approval)"

# DR-2026-11-20-08 §3: specific retail types win over the generic BUT-0005.
RETAIL_SPECIFIC = ("BUT-0002", "BUT-0003", "BUT-0004")
DUAL_PAIRS = {("BUT-0002", "BUT-0003"), ("BUT-0003", "BUT-0002"),
              ("BUT-0007", "BUT-0004"), ("BUT-0007", "BUT-0005")}

# Words that show an owner is asking for something a card puts out of scope.
OUT_OF_SCOPE_TRIGGERS = {
    "BUT-0006": ["clinical", "medical record", "patient notes", "treatment notes", "nhs", "insurance",
                 "diagnos", "advice on whatsapp", "prescri"],
    "BUT-0003": ["certif", "certificate", "prove it's halal", "prove it is halal"],
    "BUT-0002": ["scrape", "scraping", "supplier price list"],
    "BUT-0004": ["instagram password", "take over my instagram", "run my instagram"],
    "BUT-0007": ["cis", "erp", "multi-crew", "full costing"],
}
STOCK_WORDS = ("stock", "reorder", "run out", "runs out", "inventory")
TWO_SOURCE_WORDS = ("two lists", "two places", "wholesaler book", "cupboard", "the book and the")


def _norm(s: str) -> str:
    return (s or "").lower().replace("’", "'").replace("‘", "'")


def _hit(word: str, text: str) -> bool:
    w = _norm(word)
    return re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", text) is not None


class Ladder:
    def __init__(self, graph_path: Path = GRAPH, constitution: Path = CONSTITUTION):
        self.kernel = FoundryKernel()
        self.kernel.load_constitution(constitution)
        self.kernel.load_graph(graph_path)
        self.obj = self.kernel.objects
        self.types = {i: o for i, o in self.obj.items() if o["class"] == "Business Type" and o.get("card")}

    # ---- rung 1 -----------------------------------------------------------
    def classify(self, owner_words: str, hint: Optional[str] = None) -> Dict[str, Any]:
        text = _norm(owner_words)
        scores = {}
        for tid, o in self.types.items():
            hits = [k for k in o["card"].get("classify_keywords", []) if _hit(k, text)]
            if hits:
                scores[tid] = hits
        history = []
        if any(t in scores for t in RETAIL_SPECIFIC) and "BUT-0005" in scores:
            history.append("BUT-0005 dropped: a specific retail type fits (DR-2026-11-20-08 §3)")
            scores.pop("BUT-0005")
        ranked = sorted(scores, key=lambda t: (-len(scores[t]), t))
        primary = ranked[0] if ranked else None
        if hint:
            if hint not in self.types:
                raise ValueError(f"Owner hint {hint} is not an Approved card")
            if primary and primary != hint:
                history.append(f"Proposed {primary}; owner said {hint}. Owner's stated reality wins (HVT-0001 Art. XIV.6)")
            primary = hint
        if primary is None:
            return {"type": None, "also": [], "keywords": {}, "history": history,
                    "flag": "No card fits. Do not stretch a card: log the owner's words and flag a new type "
                            "for the HVT-0006 queue (Architecture Office)."}
        also = [t for t in ranked if t != primary and (primary, t) in DUAL_PAIRS]
        return {"type": primary, "name": self.types[primary]["name"], "also": also,
                "keywords": scores, "history": history, "flag": None}

    # ---- rung 2 -----------------------------------------------------------
    def problems(self, tid: str, words: str) -> List[Dict[str, Any]]:
        text = _norm(words)
        out = []
        for pid in self.types[tid]["card"].get("problem_ids", []):
            p = self.obj.get(pid)
            if not p:
                continue
            hits = [k for k in p.get("keywords", []) if _hit(k, text)]
            if hits:
                out.append({"id": pid, "name": p["name"], "heard": hits})
        return out

    # ---- rung 3 -----------------------------------------------------------
    def shelf(self, tid: str, owned: List[str]) -> Dict[str, List[str]]:
        c = self.types[tid]["card"]
        tier2 = list(c.get("recommended_engines", []))
        for cap in c.get("required_capabilities", []) + c.get("optional_capabilities", []):
            if not cap.get("covered_by"):
                tier2.append(f"Procedure path: {cap['name']}")
        return {"tier4_owned": list(owned), "tier1": list(c.get("tier1", [])), "tier2": tier2,
                "tier3_shown_not_chosen": list(c.get("tier3_candidates", []))}

    # ---- rung 4 -----------------------------------------------------------
    def match(self, tid: str, pos: Optional[str]) -> List[Dict[str, Any]]:
        c = self.types[tid]["card"]
        on_square = _norm(pos or "") == "square"
        rows = []
        for cap in c.get("required_capabilities", []) + c.get("optional_capabilities", []):
            name = cap["name"]
            if cap.get("covered_by"):
                rows.append({"capability": name, "path": cap["covered_by"], "status": "covered by engine",
                             "note": cap.get("path")})
                continue
            if any(w in _norm(name) for w in STOCK_WORDS):
                path = ("DR-10 S1: Square inventory + low-stock alerts (owner already on Square)" if on_square
                        else "DR-10 S3: sheet + WhatsApp/email to the owner's phone (DOC-0006 v1.0); do not move the till (Art. VIII)")
                rows.append({"capability": name, "path": path, "status": "covered as procedure"})
            elif "review" in _norm(name):
                rows.append({"capability": name, "path": "DR-10: GBP reply in the owner's voice, never auto-reply (DOC-0007 v1.0)",
                             "status": "covered as procedure"})
            else:
                p = cap.get("path") or "GAP"
                rows.append({"capability": name, "path": p,
                             "status": "gap" if "GAP" in p and not cap.get("path") else "covered as procedure"})
        return rows

    # ---- rung 5 -----------------------------------------------------------
    def quote(self, tid: str) -> List[Dict[str, Any]]:
        c = self.types[tid]["card"]
        q, n = [], 1
        for t in c.get("tier1", []):
            q.append({"id": f"Q{n}", "name": t.rstrip(" *"), "tier": 1, "take": "zero", "reversible": True}); n += 1
        for e in c.get("recommended_engines", []):
            q.append({"id": f"Q{n}", "name": f"{e} {self.obj[e]['name']}", "tier": 2,
                      "take": "outright later — owner decides; not this week", "reversible": True}); n += 1
        for t in c.get("tier3_candidates", []):
            q.append({"id": f"Q{n}", "name": t, "tier": 3, "take": "— shown, not chosen", "reversible": None}); n += 1
        return q

    # ---- rung 6 -----------------------------------------------------------
    def gaps(self, tid: str, words: str, wishes: List[str], live: bool, match_rows) -> Dict[str, Any]:
        text = _norm(words + " " + " ".join(wishes))
        c = self.types[tid]["card"]
        gaps = [f"{r['capability']} — no Foundry engine; {r['path']}" for r in match_rows if r["path"] and not r["path"].startswith("ENG-")]
        trig_hit = lambda s: any(_hit(tr, s) or (len(tr) >= 6 and _norm(tr) in s)
                                 for tr in OUT_OF_SCOPE_TRIGGERS.get(tid, []))
        oos = list(c.get("out_of_scope", [])) if trig_hit(text) else []
        wish_records = [{"words_verbatim": w, "status": "Under Review",
                         "resolution": ("Out of scope by the card / law: " + "; ".join(oos))
                         if oos and trig_hit(_norm(w)) else
                         "Logged for the Architecture Office against this type; not a new type"} for w in wishes]
        trigger = bool(live and any(w in text for w in TWO_SOURCE_WORDS) and any(w in text for w in STOCK_WORDS + ("colour", "foil")))
        return {"gaps": gaps, "out_of_scope_requested": oos, "wishes": wish_records,
                "eng_0005_trigger": trigger,
                "eng_0005_note": ("Two-source stock gap heard from a LIVE owner: report to the Architecture Office "
                                  "(DR-2026-11-20-05). This tool does not register ENG-0005.") if trigger else
                                 "ENG-0005 not triggered (theatre runs never trigger it)."}

    # ---- rung 7 / 8 -------------------------------------------------------
    def brand(self, tid: str, public_surface: bool) -> Dict[str, Any]:
        c = self.types[tid]["card"]
        if not public_surface:
            return {"decision": "SKIP", "why": "No new public surface this week", "stan_lee": "not needed"}
        return {"decision": "REQUIRED", "brand_intake": c.get("brand_intake", []),
                "stan_lee": "Wake Stan Lee — Design veto deferred, not waived (DOC-0009); nothing public ships without it",
                "test": c.get("stan_lee_test")}

    def deploy(self, tid: str) -> List[str]:
        return list(self.types[tid]["card"].get("minimum_path", []))

    # ---- whole ladder -----------------------------------------------------
    def run(self, intake: Dict[str, Any]) -> Dict[str, Any]:
        words = intake.get("owner_words", "")
        prob_words = intake.get("problem_words", "")
        cls = self.classify(words, intake.get("owner_type_hint"))
        rec: Dict[str, Any] = {"engine": "ENG-0004 Configurator (Prototype, DR-2026-11-20-11)",
                               "status": PENDING, "authoritative": False,
                               "theatre": not intake.get("live", False),
                               "shop": intake.get("shop"), "date": intake.get("date") or date.today().isoformat(),
                               "rung1_classify": cls}
        tid = cls["type"]
        if tid is None:
            rec["stopped_at"] = "rung 1"
            return rec
        m = self.match(tid, intake.get("pos"))
        rec.update({
            "rung2_problems": self.problems(tid, words + " " + prob_words),
            "rung3_shelf": self.shelf(tid, intake.get("owned", [])),
            "rung4_match": m,
            "rung5_quote": self.quote(tid),
            "rung6_gaps": self.gaps(tid, words + " " + prob_words, intake.get("wishes", []), intake.get("live", False), m),
            "rung7_brand": self.brand(tid, intake.get("public_surface", False)),
            "rung8_deploy": self.deploy(tid),
        })
        if intake.get("trust_rule"):
            rec["trust_rule"] = {"owner_sentence_verbatim": intake["trust_rule"], "certified_by_foundry": False,
                                 "stored_in": "owner record + sheet 'rule / mark' column"}
        rec["complexity_score"] = self.types[tid]["card"].get("complexity_score")
        return rec


def run_ladder(intake: Dict[str, Any]) -> Dict[str, Any]:
    return Ladder().run(intake)


def load_intake(path: str) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
