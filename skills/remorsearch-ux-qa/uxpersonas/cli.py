"""Local persona library and host-driven UX task orchestration."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from uxresearch.canonical import EngineError
from uxresearch.storage import read_json
from .library import Library


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    default = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local/state")) / "remorsearch-ux-qa/personas"
    for name in ("import", "list", "retire", "reuse", "prune", "plan", "claim", "record", "report", "retry"):
        sub = commands.add_parser(name)
        sub.add_argument("--library", type=Path, default=default, help="private persistent persona directory")
        if name in {"import", "plan", "record"}:
            sub.add_argument("--input", type=Path, required=True)
        if name in {"plan", "claim", "record", "report", "retry"}:
            sub.add_argument("--run", type=Path, required=True)
        if name in {"retire", "reuse"}:
            sub.add_argument("--product", required=True)
            sub.add_argument("--persona", required=True)
        if name == "list":
            sub.add_argument("--product")
        if name == "reuse":
            sub.add_argument("--revision", type=int)
        if name == "retire":
            sub.add_argument("--reason", required=True)
        if name == "claim":
            sub.add_argument("--worker", required=True)
            sub.add_argument("--task")
        if name == "retry":
            sub.add_argument("--task", required=True)
            sub.add_argument("--reconciliation", type=Path,
                             help="explicit host inspection attestation for an uncertain fixture-write outcome")
    return root


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        with Library(args.library) as library:
            if args.command == "import":
                result = library.import_profiles(read_json(args.input))
            elif args.command == "list":
                result = library.list(args.product)
            elif args.command == "retire":
                result = library.retire(args.product, args.persona, args.reason)
            elif args.command == "reuse":
                result = library.get(args.product, args.persona, args.revision)
            elif args.command == "prune":
                result = library.prune()
            else:
                from . import swarm
                if args.command == "plan":
                    result = swarm.create_plan(library, args.run, read_json(args.input))
                elif args.command == "claim":
                    result = swarm.claim(library, args.run, args.worker, args.task)
                elif args.command == "record":
                    result = swarm.record(library, args.run, read_json(args.input))
                elif args.command == "retry":
                    result = swarm.retry(library, args.run, args.task,
                                         reconciliation=read_json(args.reconciliation) if args.reconciliation else None)
                else:
                    result = swarm.report(library, args.run)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 1 if args.command == "prune" and result["blockers"] else 0
    except EngineError as exc:
        print(json.dumps({"result": "blocked", "issue": exc.issue}, ensure_ascii=False), file=sys.stderr)
        return exc.exit_code or 2
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        print(json.dumps({"result": "blocked", "issue": {"code": "input_or_io", "reason": "Input or local state is missing, malformed or unsafe."}}), file=sys.stderr)
        return 2
