"""
Demo content for card previews and the demo shops. Everything here is invented and labelled "(demo)".
Pictures are generated shapes (no people, no real photos): a hairdryer, scissors, comb, bottle or chair
outline on the preset's pattern, each marked "demo image".
"""
from __future__ import annotations

import base64
from typing import Any, Dict

ICONS = {
    "scissors": '<g fill="none" stroke="{a}" stroke-width="14" stroke-linecap="round"><circle cx="-70" cy="90" r="42"/><circle cx="70" cy="90" r="42"/><path d="M-40 60L90-120M40 60L-90-120"/></g>',
    "comb": '<g fill="{a}"><rect x="-150" y="-60" width="300" height="46" rx="14"/>' + "".join(f'<rect x="{-140 + i * 24}" y="-20" width="12" height="90" rx="5"/>' for i in range(12)) + '</g>',
    "dryer": '<g fill="none" stroke="{a}" stroke-width="14" stroke-linejoin="round"><path d="M-130-40a70 70 0 0 1 70-70h120l70 30v80l-70 30H-60a70 70 0 0 1-70-70z"/><path d="M-40 40l-20 120h60l10-120"/><circle cx="-60" cy="-40" r="26"/></g>',
    "bottle": '<g fill="none" stroke="{a}" stroke-width="14" stroke-linejoin="round"><path d="M-30-150h60v40l30 40v200a20 20 0 0 1-20 20h-80a20 20 0 0 1-20-20V-70l30-40z"/><path d="M-60 0h120"/></g>',
    "chair": '<g fill="none" stroke="{a}" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"><path d="M-70-150h140v120h-140zM-100-10h200M-60-10v60h120v-60M0 50v70M-70 150h140"/></g>',
    "razor": '<g fill="none" stroke="{a}" stroke-width="14" stroke-linecap="round"><path d="M-140 60L60-100l60 30-170 150zM60-100l80-40"/></g>',
    "brush": '<g fill="none" stroke="{a}" stroke-width="14" stroke-linecap="round"><path d="M-30 140V10M30 140V10"/><path d="M-70 10h140l-20-150h-100z" fill="{a}" fill-opacity=".3"/></g>',
}


def picture(icon: str, colours: Dict[str, str], label: str = "demo image", w: int = 900, h: int = 700, variant: int = 0) -> str:
    """A data: URL of a generated SVG placeholder picture."""
    p, a, bg = colours["primary"], colours["accent"], colours.get("surface", colours["bg"])
    shade = ["0.0", "0.15", "0.3", "0.45"][variant % 4]
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">'
           f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p}"/>'
           f'<stop offset="1" stop-color="{a}" stop-opacity="{0.35 + float(shade)}"/></linearGradient></defs>'
           f'<rect width="{w}" height="{h}" fill="url(#g)"/>'
           f'<circle cx="{w * (0.25 + 0.15 * (variant % 3))}" cy="{h * 0.3}" r="{h * 0.42}" fill="{bg}" opacity="0.08"/>'
           f'<g transform="translate({w / 2} {h / 2 - 10}) scale(1.25)">{ICONS[icon].replace("{a}", a if variant % 2 == 0 else bg)}</g>'
           f'<rect x="20" y="{h - 64}" width="{len(label) * 13 + 30}" height="44" rx="10" fill="#000" opacity=".45"/>'
           f'<text x="35" y="{h - 34}" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#fff">{label}</text></svg>')
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


WEEK = [{"day": d, "open": o, "close": c, "closed": o == ""} for d, o, c in (
    ("mon", "", ""), ("tue", "09:30", "18:00"), ("wed", "09:30", "18:00"), ("thu", "09:30", "20:00"),
    ("fri", "09:30", "20:00"), ("sat", "09:00", "17:00"), ("sun", "", ""))]


def sample_shop(card: Dict[str, Any], pre: Dict[str, Any], choices: Dict[str, bool]) -> Dict[str, Any]:
    """Generic preview content for any preset of the hair card. Invented, labelled (demo)."""
    barber = pre.get("variant") == "barber"
    col = pre["colours"]
    services = ([
        {"name": "Skin fade (demo)", "category": "Cuts", "duration_min": 40, "price_from": "22", "audience": "men", "hair_types": ["any"]},
        {"name": "Scissor cut (demo)", "category": "Cuts", "duration_min": 30, "price_from": "18", "audience": "men"},
        {"name": "Beard shape-up (demo)", "category": "Beard & shave", "duration_min": 20, "price_from": "12", "audience": "men"},
        {"name": "Hot towel shave (demo)", "category": "Beard & shave", "duration_min": 30, "price_from": "20", "audience": "men"},
        {"name": "Kids cut (demo)", "category": "Kids", "duration_min": 25, "price_from": "14", "audience": "children"},
    ] if barber else [
        {"name": "Cut & blow-dry (demo)", "category": "Cuts", "duration_min": 60, "price_from": "45", "audience": "women", "hair_types": ["straight", "wavy", "curly"]},
        {"name": "Silk press (demo)", "category": "Styling", "duration_min": 90, "price_from": "60", "audience": "anyone", "hair_types": ["curly", "coily"]},
        {"name": "Full colour (demo)", "category": "Colour", "duration_min": 120, "price_from": "75", "audience": "anyone", "hair_types": ["any"]},
        {"name": "Knotless braids (demo)", "category": "Braids & locs", "duration_min": 240, "price_from": "120", "audience": "anyone", "hair_types": ["coily", "curly"]},
        {"name": "Men's cut (demo)", "category": "Cuts", "duration_min": 30, "price_from": "25", "audience": "men"},
    ])
    staff_names = ["Demo Barber A", "Demo Barber B"] if barber else ["Demo Stylist A", "Demo Stylist B"]
    return {
        "name": f"{pre['label']} (demo)", "preset": pre["id"], "variant": pre.get("variant"),
        "tagline": "Preview with invented content", "languages": ["en"], "hours": WEEK,
        "address": "Example Street (demo)", "postcode": "", "phone": "", "whatsapp": "",
        "offer": "Sample offer text (demo)", "offer_on": True,
        "services": services,
        "staff": [{"id": f"s{i + 1}", "name": n, "role": "Senior" if i == 0 else "Stylist", "bio": "Invented profile for the preview (demo)."}
                  for i, n in enumerate(staff_names)],
        "gallery": [{"image": picture(ic, col, variant=i), "caption": "demo image"} for i, ic in enumerate(["scissors", "comb", "dryer", "chair"])],
        "reviews": [{"author": "Sample review (demo)", "stars": 5, "text": "Invented text to show how reviews look.", "source": "demo — not a real review"}],
        "modules": choices, "demo": True,
    }
