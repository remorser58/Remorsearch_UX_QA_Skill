#!/usr/bin/env python3
"""Ergonomic persona-swarm UX QA command line (see docs/ergonomic-swarm-spec.md)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ergoqa.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
