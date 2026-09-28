#!/usr/bin/env python3
"""Offline acceptance smoke; all mutations stay in disposable checkout-local dirs."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # skill folder: scripts, uxloop, examples
REPO = ROOT.parents[1]  # repository checkout: tests and fixtures (not shipped with the skill)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(REPO / 'tests'))

from loop_factory import make_packet  # Authored fixtures, never live provider output.
from uxloop.io import load_json


def main() -> int:
    outcomes = []
    runtime = REPO / '.ux-loop'
    runtime.mkdir(exist_ok=True)

    def command(arguments: list[str], expected: int) -> dict:
        result = subprocess.run([sys.executable, *arguments], cwd=ROOT, capture_output=True,
                                text=True, timeout=30)
        if result.returncode != expected:
            raise AssertionError(f'{arguments}: wanted {expected}, got {result.returncode}\n{result.stdout}\n{result.stderr}')
        outcomes.append({'command': 'python3 ' + ' '.join(arguments), 'exit': result.returncode, 'expected_exit': expected})
        return json.loads(result.stdout) if result.stdout.lstrip().startswith('{') else {}

    try:
        command(['scripts/validate_bundle.py', str(REPO / 'tests/fixtures/valid-bundle.json')], 0)
        for path in sorted((REPO / 'tests/fixtures').glob('invalid-*.json')):
            command(['scripts/validate_bundle.py', str(path)], 1)
        value = command(['scripts/ux_loop.py', 'validate', 'examples/loop/packet.json', '--evidence-root', 'examples/loop'], 0)
        assert value['valid'] and value['completion_assessed'] is False
        with tempfile.TemporaryDirectory(dir=runtime, prefix='smoke-') as temporary:
            root = Path(temporary)
            denied = command(['scripts/ux_loop.py', 'demo', '--output', str(root / 'denied')], 3)
            assert denied['status'] == 'blocked' and denied['accepted_fix_ids'] == []
            site = root / 'resumable'
            interrupted = command(['scripts/ux_loop.py', 'demo', '--output', str(site), '--grant', 'code_write',
                '--actor', 'smoke-supervisor', '--reason', 'Approve only the isolated fixture patch', '--pause-after', 'browser'], 6)
            checkpoint = site / 'checkpoint.json'
            before = load_json(checkpoint)
            assert interrupted['status'] == 'interrupted' and interrupted['accepted_fix_ids'] == []
            completed = command(['scripts/ux_loop.py', 'resume', '--checkpoint', str(checkpoint)], 0)
            after = load_json(checkpoint)
            assert before['run_id'] == after['run_id'] and before['permissions'] == after['permissions']
            assert before['packet']['bundle']['records']['evidence'] == after['packet']['bundle']['records']['evidence']
            assert completed['accepted_fix_ids'] == ['fix-1'] and completed['product_complete'] is False
            assert '상품 상세 보기' in (site / 'site/index.html').read_text()
            command(['scripts/ux_loop.py', 'resume', '--checkpoint', str(checkpoint)], 0)
            for case, code, status in [('failed_visual', 5, 'failed'), ('unknown_evidence', 4, 'unknown'),
                                       ('regression_failure', 5, 'failed'), ('missing_browser', 3, 'blocked')]:
                directory = root / case
                make_packet(directory, case)
                workspace = directory / 'site'
                workspace.mkdir()
                (workspace / 'index.html').write_bytes((ROOT / 'examples/loop/site/index.html').read_bytes())
                result = command(['scripts/ux_loop.py', 'run', str(directory / 'packet.json'), '--workspace', str(workspace),
                    '--evidence-root', str(directory), '--checkpoint', str(directory / 'checkpoint.json'),
                    '--grant', 'code_write', '--actor', 'smoke-supervisor', '--reason', 'Approve isolated fixture code'], code)
                assert result['status'] == status and not result['product_complete'] and result['accepted_fix_ids'] == []
            malformed = root / 'malformed.json'
            malformed.write_text('{"schema_version":"ux-loop.v1","schema_version":"unsafe"}')
            command(['scripts/ux_loop.py', 'validate', str(malformed)], 2)
        print(json.dumps({'passed': True, 'command_count': len(outcomes), 'checks': outcomes,
                          'live_integrations_executed': False}, indent=2))
        return 0
    except (AssertionError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({'passed': False, 'reason': str(exc), 'completed_checks': outcomes}, indent=2))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
