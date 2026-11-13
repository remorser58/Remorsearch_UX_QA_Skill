#!/usr/bin/env python3
"""Single frozen-engine 32-persona v3 rerun for the final comparison."""
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
OUT = ROOT / ".ux-loop/peekly-explicit-success-32-final"


async def main() -> None:
    if OUT.exists():
        raise RuntimeError("final_run_output_exists_preserved")
    if not BUILD.is_file() or not (FIXTURES / "fixture-manifest.json").is_file():
        raise RuntimeError("pinned_build_or_fixture_missing")
    personas = _load_personas(LIBRARY, "peekly", 32)
    if len(personas) != 32 or len(set(personas)) != 32:
        raise RuntimeError("same_32_v3_persona_gate_failed")
    OUT.mkdir(mode=0o700, parents=True, exist_ok=False)
    args = SimpleNamespace(
        run_root=OUT, library=LIBRARY, product_id="peekly",
        url="http://127.0.0.1:4174/",
        target="Peekly isolated local preview; immutable source commit 51110f4c569673faa8d242d5b85c4b47afb54cbb",
        goal=("Final 32-persona v3 comparison run on one frozen selector-safe engine. "
              "The engine includes structural-only DOM selectors and manifest-key-only fixture uploads. "
              "Execute every declared current-PRD criterion using only hash-pinned v4 synthetic fixtures. "
              "Never infer a pass from text alone; unexecuted applicable criteria remain not_run. "
              "Native iOS-only behavior is N/A on desktop. No real Instagram accounts, payments or external destinations."),
        build_id="peekly-web-51110f4-20261113",
        build_artifact=BUILD, fixtures=FIXTURES,
        chrome=Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        node=Path("/Users/m4mini/.aside/runtime/bin/node"), turns=24,
    )
    print("FINAL_FROZEN_ENGINE_COHORT", ",".join(personas), flush=True)
    summary = await run_stage(args, personas, 32)
    print("FINAL_FROZEN_ENGINE_RESULT", summary, flush=True)


if __name__ == "__main__":
    asyncio.run(main())
