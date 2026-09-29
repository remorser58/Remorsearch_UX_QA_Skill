#!/usr/bin/env python3
"""Run the repository-local public-page reader CLI without installing a package."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from uxresearch.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
