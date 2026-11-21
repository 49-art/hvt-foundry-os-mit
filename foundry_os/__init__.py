"""HVT Foundry OS — ENG-0004 Configurator (Prototype), built 20 Nov 2026 under DR-2026-11-20-11 (Job D).

Runs the DOC-0008 eight-rung ladder (classify, problems, shelf, match, quote, gaps, brand, deploy)
from graph data only, and verifies the governance repository. Every output is a proposal marked
"pending human review"; nothing here approves, certifies, or registers anything.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRAPH = ROOT / "graph" / "foundry_graph.json"
CONSTITUTION = ROOT / "governance" / "HVT-0001_Constitution.md"
ENGINE_ID = "ENG-0004"
MATURITY = "Prototype"
VERSION = "1.0.0"

from .ladder import Ladder, run_ladder  # noqa: E402
from .governance import verify  # noqa: E402

__all__ = ["Ladder", "run_ladder", "verify", "ROOT", "GRAPH", "CONSTITUTION", "VERSION"]
