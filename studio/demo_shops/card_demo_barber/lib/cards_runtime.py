"""
Card app templates.

A *card* is a complete app template for one kind of business (first:
Hair Salon / Barber, card CARD-HAIR-01 on BUT-0001). It holds:

  * presets      – ready-made looks (colours, fonts, pattern); the owner can change colours
  * modules      – every feature the trade could want. tier "base" = the 4-star default
                   (switched on out of the box); tier "optional" = off until switched on per shop
  * content_schema – the lists the owner edits in the admin page (services, staff, …)
  * supplier_search – what the supplier finder looks for in this trade

Each module states honestly how it works today:
  working    – works with no key, tested here
  needs-key  – code written against the vendor's official docs; needs the owner's own key
  link-only  – just a link to the shop's page on another service
  unverified – we could not verify the vendor's docs; treat as a starting point

Cost notes come from the connectors' checked vendor prices (with source and
date). Where no price was checked, the note says "Price not checked".

Adding a card for another trade: see HOW_TO_ADD_A_CARD.md.
"""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional

HERE = Path(__file__).resolve().parent
DEFS = HERE / "defs"
MODULE_STATUSES = ("working", "needs-key", "code-ready-needs-key", "link-only", "unverified")
TIERS = ("base", "optional")
REQUIRED_KEYS = ("card_id", "title", "business_type_id", "version", "status", "variants", "presets", "modules", "content_schema")
FIELD_TYPES = {"text", "breaks", "text_long", "ml_text", "int", "money", "choice", "choice_or_text", "multichoice", "bool", "image",
               "url", "tags", "staff_refs", "barcode", "commission"}


class CardError(ValueError):
    pass


def _connector_catalogue() -> Dict[str, Dict[str, Any]]:
    try:
        import connectors as hvtc                 # studio/connectors (Studio) or lib/connectors (shop app)
        return {c["id"]: c for c in hvtc.catalogue()}
    except Exception:                             # pragma: no cover - template still works without connectors
        return {}


def validate_card(card: Dict[str, Any], connectors: Optional[Dict[str, Any]] = None) -> List[str]:
    """Returns a list of problems (empty = fine). Used by tests and when a new card is added."""
    probs = [f"missing key {k}" for k in REQUIRED_KEYS if k not in card]
    if probs:
        return probs
    if "Approved" in card["status"]:
        probs.append("a card template cannot be marked Approved by the Studio")
    connectors = connectors if connectors is not None else _connector_catalogue()
    ids = set()
    for m in card["modules"]:
        mid = m.get("id", "")
        if not mid or mid in ids:
            probs.append(f"module id missing or repeated: {mid!r}")
        ids.add(mid)
        if m.get("tier") not in TIERS:
            probs.append(f"{mid}: tier must be base or optional")
        if m.get("status") not in MODULE_STATUSES:
            probs.append(f"{mid}: status must be one of {MODULE_STATUSES}")
        if not m.get("description"):
            probs.append(f"{mid}: needs a plain-English description")
        for c in m.get("connectors", []):
            if connectors and c not in connectors:
                probs.append(f"{mid}: unknown connector {c}")
        for part in m.get("parts", []):
            if len(part) != 2 or part[1] not in MODULE_STATUSES:
                probs.append(f"{mid}: bad part {part}")
    for m in card["modules"]:
        if m.get("replaces") and m["replaces"] not in ids:
            probs.append(f"{m['id']}: replaces unknown module {m['replaces']}")
    if not any(m["tier"] == "base" for m in card["modules"]):
        probs.append("a card needs at least one base (4-star) module")
    pids = set()
    for p in card["presets"]:
        if p.get("id") in pids:
            probs.append(f"preset repeated: {p.get('id')}")
        pids.add(p.get("id"))
        for k in ("primary", "accent", "bg", "text"):
            v = (p.get("colours") or {}).get(k, "")
            if not (isinstance(v, str) and len(v) == 7 and v.startswith("#")):
                probs.append(f"preset {p.get('id')}: colour {k} missing")
    for lst, fields in card["content_schema"].items():
        for f in fields:
            if f.get("type") not in FIELD_TYPES:
                probs.append(f"content_schema.{lst}.{f.get('key')}: unknown type {f.get('type')}")
    return probs


def list_cards() -> List[Dict[str, Any]]:
    out = []
    for f in sorted(DEFS.glob("*.json")):
        c = json.loads(f.read_text(encoding="utf-8"))
        out.append({"card_id": c["card_id"], "title": c["title"], "business_type_id": c["business_type_id"],
                    "version": c["version"], "status": c["status"], "file": f.name,
                    "base_count": sum(1 for m in c["modules"] if m["tier"] == "base"),
                    "optional_count": sum(1 for m in c["modules"] if m["tier"] == "optional"),
                    "presets": [{"id": p["id"], "label": p["label"]} for p in c["presets"]]})
    return out


def load_card(card_id: str) -> Dict[str, Any]:
    for f in sorted(DEFS.glob("*.json")):
        c = json.loads(f.read_text(encoding="utf-8"))
        if c["card_id"] == card_id:
            probs = validate_card(c)
            if probs:
                raise CardError(f"Card {card_id} has problems: " + "; ".join(probs))
            return c
    raise CardError(f"No card {card_id!r}.")


def cost_notes(module: Dict[str, Any], connectors: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Only verified vendor prices (with source and date); otherwise 'Price not checked'."""
    if module.get("cost_notes"):
        return module["cost_notes"]
    connectors = connectors if connectors is not None else _connector_catalogue()
    notes = []
    for cid in module.get("connectors", []):
        c = connectors.get(cid) or {}
        pr = c.get("pricing") or {}
        if pr.get("checked"):
            notes.append({"connector": c.get("name", cid), "text": pr.get("text"), "url": pr.get("url"), "checked": pr["checked"]})
        else:
            notes.append({"connector": c.get("name", cid), "text": "Price not checked.", "url": pr.get("url", ""), "checked": None})
    if not notes:
        notes.append({"connector": None, "text": "No outside cost: runs inside the shop's own app.", "url": "", "checked": None})
    return notes


def catalogue(card: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Modules with their cost notes and connector statuses filled in (for the Studio screen)."""
    cons = _connector_catalogue()
    out = []
    for m in card["modules"]:
        d = deepcopy(m)
        d["default_on"] = m["tier"] == "base"
        d["cost_notes"] = cost_notes(m, cons)
        d["connector_details"] = [{"id": c, "name": (cons.get(c) or {}).get("name", c),
                                   "status": (cons.get(c) or {}).get("status", "unknown")} for c in m.get("connectors", [])]
        out.append(d)
    return out


def resolve(card: Dict[str, Any], choices: Optional[Dict[str, bool]] = None) -> Dict[str, bool]:
    """Which modules are on for a shop: base on unless switched off, optional off unless switched on.
    Locked modules (the admin page) are always on. A module that 'replaces' another turns that one off."""
    choices = choices or {}
    ids = {m["id"] for m in card["modules"]}
    unknown = [k for k in choices if k not in ids]
    if unknown:
        raise CardError("Unknown module(s): " + ", ".join(unknown))
    on = {}
    for m in card["modules"]:
        v = choices.get(m["id"], m["tier"] == "base")
        on[m["id"]] = True if m.get("locked") else bool(v)
    for m in card["modules"]:
        if on[m["id"]] and m.get("replaces"):
            on[m["replaces"]] = False
    return on


def preset(card: Dict[str, Any], preset_id: str) -> Dict[str, Any]:
    for p in card["presets"]:
        if p["id"] == preset_id:
            return p
    raise CardError(f"No preset {preset_id!r} on {card['card_id']}.")
