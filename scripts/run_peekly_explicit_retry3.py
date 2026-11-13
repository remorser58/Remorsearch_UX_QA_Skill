#!/usr/bin/env python3
"""Fresh isolated retry for only the three unresolved v3 personas.

The original stage remains immutable. This is a new queue with the same pinned
build, frozen fixtures, v3 persona revisions, engine manifest and free route.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/remorsearch-ux-qa/scripts"))
from live_scale_browser import run_stage

LIBRARY = ROOT / ".ux-loop/peekly-persona-library-v3"
PRODUCT = Path("/Volumes/SanDisk2TB/m4mini/CodeProjects/insta-tracker/.omo/worktrees/peekly-import-ux-20261113")
FIXTURES = ROOT / ".ux-loop/peekly-fixtures-v4"
BUILD = PRODUCT / ".ux-loop/peekly-build-manifest.json"
OUT = ROOT / ".ux-loop/peekly-explicit-success-retry-3-v2"
PERSONAS = ["PER-PEEKLY-V2-014", "PER-PEEKLY-V2-015", "PER-PEEKLY-V2-016"]


async def main() -> None:
    if OUT.exists():
        raise RuntimeError("retry_output_exists_preserved")
    if not BUILD.is_file() or not (FIXTURES / "fixture-manifest.json").is_file():
        raise RuntimeError("pinned_build_or_fixture_missing")
    OUT.mkdir(mode=0o700, parents=True, exist_ok=False)
    args = SimpleNamespace(
        run_root=OUT, library=LIBRARY, product_id="peekly",
        url="http://127.0.0.1:4174/",
        target="Peekly isolated local preview; immutable source commit 51110f4c569673faa8d242d5b85c4b47afb54cbb",
        goal=("Retry only three unresolved v3 personas in a new isolated queue. "
              "Use the frozen 51110f4 build and hash-pinned v4 synthetic fixtures. "
              "Execute all explicit criteria; keep untested criteria not_run and native iOS checks N/A. "
              "Do not use real Instagram accounts, payments, or external destinations."),
        build_id="peekly-web-51110f4-20261113",
        build_artifact=BUILD, fixtures=FIXTURES,
        chrome=Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        node=Path("/Users/m4mini/.aside/runtime/bin/node"), turns=24,
    )
    print("RETRY_COHORT", ",".join(PERSONAS), flush=True)
    summary = await run_stage(args, PERSONAS, 4)
    print("RETRY_FINAL", summary, flush=True)


if __name__ == "__main__":
    asyncio.run(main())
