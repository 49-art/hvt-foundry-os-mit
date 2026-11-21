"""
demo_boot.py — runs the full Foundry Kernel boot sequence against the real
files in this repository, including BOTH refusal paths the README requires:

  * an Agent attempting a workflow outside its Office's authority, and
  * an attempt to register a non-Agent object.

A kernel that only shows success paths hasn't demonstrated it enforces anything.

Run:  cd kernel && python3 demo_boot.py
"""
from pathlib import Path
import sys

from foundry_kernel import (FoundryKernel, KernelRefusal, BootOrderError,
                            AgentRegistrationError, UnauthorizedActionError)

ROOT = Path(__file__).resolve().parent.parent
CONSTITUTION = ROOT / "governance" / "HVT-0001_Constitution.md"
GRAPH = ROOT / "graph" / "foundry_graph.json"


def step(n, title):
    print(f"\n[{n}] {title}")


def main() -> int:
    k = FoundryKernel()
    print("HVT Foundry Kernel (HVT-0005) — boot sequence demo")
    print("=" * 60)

    step(0, "Pre-check: try to load the graph BEFORE the Constitution (must refuse)")
    try:
        k.load_graph(GRAPH)
        print("    !! graph loaded without a Constitution — this is a defect")
        return 1
    except BootOrderError as e:
        print(f"    REFUSED (expected): {e}")

    step(1, "Gate 1 — Load the Constitution")
    meta = k.load_constitution(CONSTITUTION)
    print(f"    OK: {meta['Document ID']} '{meta['Title']}' v{meta['Version']} — status {meta['Status']}")

    step(2, "Gate 2 — Load the Object Graph")
    g = k.load_graph(GRAPH)
    print(f"    OK: {len(g['objects'])} objects. ENG-0003 reuse_count (derived) = {k.reuse_count('ENG-0003')}")
    print(f"    BUT-0001 Hair Salon recommended engines: {g and k.objects['BUT-0001']['card']['recommended_engines']}")
    print(f"    PRB-0004 Manual stock — engines that solve it: {k.solvers_of('PRB-0004') or 'none (capability gap; see HVT-0006-OVL-0001)'}")
    print(f"    WSH-0001 status: {k.objects['WSH-0001']['status']} — {k.objects['WSH-0001']['status_prose']}")

    step(3, "Gate 3 — Register Agents (only the two rows in HVT-0002 §4.2)")
    for aid in ("AGT-0001", "AGT-0002"):
        a = k.register_agent(aid)
        print(f"    OK: {aid} {a['name']} → {a['office']}")

    step("3b", "REFUSAL PATH 1 — try to register a non-Agent object (ENG-0003 Commerce Engine)")
    try:
        k.register_agent("ENG-0003")
        print("    !! non-Agent registered — this is a defect")
        return 1
    except AgentRegistrationError as e:
        print(f"    REFUSED (expected): {e}")

    step(4, "Gate 4 — Execute an authorized workflow")
    r = k.execute_workflow("AGT-0002", "run_engine_search",
                           {"capability": "Stock / inventory tracking", "business_type": "BUT-0001"})
    print(f"    OK: {r.agent} ran '{r.action}' — authorized by {r.authorized_by}")
    print(f"    Result status: {r.status}  ({r.note})")

    step("4b", "REFUSAL PATH 2 — Chief Architect tries to approve a Constitution amendment")
    try:
        k.execute_workflow("AGT-0002", "approve_constitution_amendment",
                           {"proposal": "Article XIV.6 (customer correction of classification)"})
        print("    !! unauthorized action allowed — this is a defect")
        return 1
    except UnauthorizedActionError as e:
        print(f"    REFUSED (expected): {e}")

    print("\nAudit log")
    print("-" * 60)
    for entry in k.audit_log:
        print(f"  {entry.timestamp}  {entry.gate:<20} {entry.outcome:<8} {entry.detail}")
    refusals = sum(1 for e in k.audit_log if e.outcome == "refused")
    print(f"\nBoot complete. {len(k.audit_log)} audit entries, {refusals} refusals (3 expected).")
    return 0 if refusals == 3 else 1


if __name__ == "__main__":
    sys.exit(main())
