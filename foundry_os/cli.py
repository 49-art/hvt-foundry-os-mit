"""python -m foundry_os {status|verify|cards|decisions|ladder <intake.json>}"""
from __future__ import annotations

import argparse
import json
import sys

from . import ENGINE_ID, MATURITY, VERSION
from .governance import scan, verify
from .ladder import Ladder, load_intake


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="foundry_os", description="HVT Foundry OS (ENG-0004 Configurator, Prototype)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status"); sub.add_parser("verify"); sub.add_parser("cards"); sub.add_parser("decisions")
    lp = sub.add_parser("ladder"); lp.add_argument("intake")
    a = ap.parse_args(argv)
    if a.cmd == "verify":
        r = verify(); print(json.dumps(r, indent=2)); return 0 if r["ok"] else 1
    if a.cmd == "status":
        r = verify()
        print(f"HVT Foundry OS {VERSION} — {ENGINE_ID} Configurator ({MATURITY})")
        print(f"Constitution v{r['constitution_version']} · graph {r['graph_objects']} objects · "
              f"{r['documents']} documents · verify {'OK' if r['ok'] else 'FAILED'}")
        return 0 if r["ok"] else 1
    if a.cmd == "cards":
        L = Ladder()
        for t, o in sorted(L.types.items()):
            c = o["card"]
            print(f"{t}  v{o['version']} {o['status']:<10} complexity {c.get('complexity_score')}  {o['name']}")
        return 0
    if a.cmd == "decisions":
        for m in scan():
            if m["_file"].startswith("decisions/"):
                print(f"{m.get('Document ID'):<22} {m.get('Status','')[:60]}")
        return 0
    if a.cmd == "ladder":
        print(json.dumps(Ladder().run(load_intake(a.intake)), indent=2, ensure_ascii=False))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
