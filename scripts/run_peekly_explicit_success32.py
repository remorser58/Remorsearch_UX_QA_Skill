#!/usr/bin/env python3
"""Run the frozen 32-persona cohort against the immutable Peekly 51110f4 build."""
from __future__ import annotations

import asyncio
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/remorsearch-ux-qa/scripts"))
from live_scale_browser import _load_personas, run_stage

LIBRARY = ROOT / ".ux-loop/peekly-persona-library-v3"
PRODUCT = Path("/Volumes/SanDisk2TB/m4mini/CodeProjects/insta-tracker/.omo/worktrees/peekly-import-ux-20261113")
FIXTURES = ROOT / ".ux-loop/peekly-fixtures-v4"
BUILD = PRODUCT / ".ux-loop/peekly-build-manifest.json"
OUT = ROOT / ".ux-loop/peekly-explicit-success-32"


async def main() -> None:
    if OUT.exists():
        raise RuntimeError("run_output_exists_preserved")
    if not (PRODUCT / ".git").exists() or not BUILD.is_file() or not (FIXTURES / "fixture-manifest.json").is_file():
        raise RuntimeError("pinned_product_build_or_fixture_missing")
    personas = _load_personas(LIBRARY, "peekly", 32)
    if len(personas) != 32 or len(set(personas)) != 32:
        raise RuntimeError("same_32_persona_library_gate_failed")
    OUT.mkdir(mode=0o700, parents=True, exist_ok=False)
    args = SimpleNamespace(
        run_root=OUT, library=LIBRARY, product_id="peekly",
        url="http://127.0.0.1:4174/",
        target="Peekly isolated local preview; immutable source commit 51110f4c569673faa8d242d5b85c4b47afb54cbb",
        goal=("Complete every saved persona's own PRD-mapped task against the frozen 51110f4 product build. "
              "Use only fixtures named in the frozen v4 manifest. Each criterion has an explicit screen, selector, "
              "required text/value, precondition, action and timeout in the task. Perform every named upload and "
              "every lower-level flow before final judgment. Observe DOM after each action; cite observations and "
              "screenshots. Native deterministic checks override model not_run and native failures cannot be erased. "
              "Do not test real Instagram, accounts, payments or external destinations. Desktop-only native iOS "
              "share-sheet preview is N/A, never passed. Report unsupported native iOS checks separately."),
        build_id="peekly-web-51110f4-20261113",
        build_artifact=BUILD, fixtures=FIXTURES,
        chrome=Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        node=Path("/Users/m4mini/.aside/runtime/bin/node"), turns=24,
    )
    print("COHORT", ",".join(personas), flush=True)
    summary = await run_stage(args, personas, 32)
    if not summary["stage_ready_for_expansion"]:
        raise RuntimeError("32_persona_stage_incomplete_preserved")
    print("FINAL", summary, flush=True)


if __name__ == "__main__":
    asyncio.run(main())
