"""Bounded serial subprocess measurement; never reads or modifies other processes."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time


def write_json(path, value):
    path = Path(path)
    with path.open('x', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    path.chmod(0o600)


def measure(command, cwd, output, timeout=300, env=None):
    """macOS time -lp RSS is bytes, not a sampled sum of the process tree."""
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    if output.exists() or output.with_suffix('.json').exists():
        raise ValueError('Never overwrite an earlier measurement')
    started = time.monotonic()
    timed_out = False
    with output.open('xb') as log:
        output.chmod(0o600)
        proc = subprocess.Popen(['/usr/bin/time', '-lp', *map(str, command)],
                                cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT,
                                start_new_session=True)
        try:
            code = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            # This group was created above for this command only.
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                code = proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                code = proc.wait(timeout=5)
    raw = output.read_text(encoding='utf-8', errors='replace')
    rss = re.findall(r'^\s*(\d+)\s+maximum resident set size\s*$', raw, re.M)
    real = re.findall(r'^real\s+([0-9.]+)\s*$', raw, re.M)
    result = dict(command=list(map(str, command)), exit_code=code, timed_out=timed_out,
                  wall_seconds=round(time.monotonic() - started, 6),
                  time_real_seconds=float(real[-1]) if real else None,
                  max_rss_bytes=int(rss[-1]) if rss else None,
                  measurement='macOS /usr/bin/time -lp; RSS is not a process-tree sum',
                  process_finished=True)
    write_json(output.with_suffix('.json'), result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cwd', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--timeout', type=int, default=300)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    result = measure(command, args.cwd, args.output, args.timeout)
    print(json.dumps(result, ensure_ascii=False))
    return result['exit_code'] if not result['timed_out'] else 124


if __name__ == '__main__':
    raise SystemExit(main())
