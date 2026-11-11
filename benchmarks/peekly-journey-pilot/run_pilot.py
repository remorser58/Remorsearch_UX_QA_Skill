"""Run the frozen Peekly core pilot against an explicitly prepared owned copy.

No browser, server, original repository copy, dependency install or model call is
performed here. Raw library/claim files stay in the private experiment directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from measure import measure, write_json

HERE = Path(__file__).resolve().parent
PROTOCOL_SHA256 = 'ba8e48453f7ecdedba1c9aaef3f68462b7e6013bff87873a16dce9114d8b95d9'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def library_id(persona):
    # Frozen IDs remain unchanged in the protocol. The library requires PER-.
    return 'PER-' + persona.removeprefix('P-')


def mapped_profiles(protocol):
    profiles = []
    for persona in protocol['personas']:
        required = list(persona['requirement_ids'])
        for task in protocol['tasks']:
            if task['persona_id'] == persona['persona_id']:
                for rid in task['requirement_ids']:
                    if rid not in required:
                        required.append(rid)
        profiles.append({**persona, 'persona_id': library_id(persona['persona_id']),
                         'requirement_ids': required})
    return profiles


def coverage(task):
    def observed(key, description, kind, index):
        return dict(id=key, description=description,
                    criterion_refs=[dict(kind=kind, index=index)], exclusion_reason=None)

    def excluded(key, description, reason):
        return dict(id=key, description=description, criterion_refs=[], exclusion_reason=reason)

    no_ui = 'No permitted isolated browser was available; no App, DOM or native interaction was executed.'
    tid = task['id']
    result = []
    for rid in task['requirement_ids']:
        rows = []
        if rid == 'R-SAMPLE':
            rows = [observed('sample-data', 'Built-in samples can be parsed for the sample entry path', 'success', 0),
                    excluded('entry-controls', 'First-screen import button and sample link', no_ui),
                    excluded('no-format-choice', 'The primary flow does not require format knowledge', no_ui)]
        elif rid == 'R-COMPARE':
            rows = [observed('comparison-data', 'Two records produce the expected follower changes', 'success', 1),
                    excluded('single-record-guidance', 'One-record next-import guidance', no_ui),
                    excluded('visible-count-list', 'Present the count and list in the interface', no_ui)]
        elif rid == 'R-RESUME':
            rows = [observed('stored-progress', 'Persist and reload the stage and request time', 'success', 0),
                    excluded('visible-resume', 'Show the next action when the app reopens', no_ui),
                    excluded('resume-button', 'The button restores the saved stage', no_ui)]
        elif rid == 'R-IMPORT':
            if tid == 'T-RECOVER':
                rows = [observed('both-lists', 'Reject missing relationship data', 'success', 1),
                        observed('same-owner', 'Reject a different known owned identity', 'success', 1)]
            elif tid == 'T-FOLDER':
                rows = [observed('complete-lists', 'Wait for both relationship files in the latest export', 'success', 1),
                        observed('admit-repaired', 'Parse and admit the completed owned export', 'recovery', 0),
                        excluded('different-owner', 'Reject a different known account', 'Covered by the returner task; not observed by this task.')]
            else:
                rows = [observed('both-large-lists', 'Parse both complete large relationship lists', 'success', 1),
                        excluded('owner-rejection', 'Reject a different known account', 'Covered by the returner task; not observed by this task.')]
            rows.append(excluded('visible-import-help', 'Present the required selection guidance', no_ui))
        elif rid in {'R-ZIP-LIMIT', 'R-FILE-LIMIT', 'R-TOTAL-LIMIT'}:
            rows = [observed('bounded-large-input', 'Accept the frozen valid input within the documented byte bound', 'success', 1),
                    excluded('entire-size-domain', 'Every permitted size and representation', 'This finite pilot checks one fixed larger input and a smaller control, not the entire range.')]
        elif rid == 'R-STORAGE':
            rows = [observed('write-failure', 'Report failed writes without replacing committed bytes', 'success', 0),
                    observed('read-failure', 'Report read failure without overwriting existing bytes', 'success', 1),
                    observed('retry-save', 'Explicit save and reload after the owned fault is removed', 'recovery', 0),
                    excluded('unavailable-storage', 'Distinguish storage unavailability', 'No unavailable-storage condition in this fixed task.'),
                    excluded('visible-save-retry', 'Show failure and retry controls', no_ui),
                    excluded('app-write-gate', 'Stop automatic writes and imports until successful reload', no_ui)]
        elif rid == 'R-RETENTION':
            rows = [observed('two-record-floor', 'Quota retry does not prune below two records or report success', 'success', 0),
                    excluded('ten-record-cap', 'Manual and automatic imports retain the latest ten records', 'This fixed task supplies three records.'),
                    excluded('nonquota-no-prune', 'Only quota errors trigger pruning', 'This fixed task injects a quota error, not every non-quota error.'),
                    excluded('app-apply-gate', 'The App does not apply the candidate when both writes fail', no_ui)]
        elif rid == 'R-FOLDER':
            rows = [observed('skip-older-repeat', 'Skip repeated and older exports after a fresh module load', 'success', 0),
                    observed('signature-persistence', 'Persist the imported signature with the snapshot', 'success', 0)]
        else:
            raise ValueError('Unmapped frozen requirement')
        for row in rows:
            row['id'] = rid + '-' + row['id']
        result.append(dict(requirement_id=rid, obligations=rows))
    return result


class Pilot:
    def __init__(self, work, skill):
        os.umask(0o077)
        self.work = work.resolve(strict=True)
        self.product = (self.work / 'product').resolve(strict=True)
        if self.product.parent != self.work or (self.product / '.git').exists():
            raise ValueError('A dedicated non-git owned copy is required')
        if digest(HERE / 'protocol.json') != PROTOCOL_SHA256:
            raise ValueError('Frozen protocol changed')
        self.protocol = read(HERE / 'protocol.json')
        self.binding = self.work / 'product-binding.json'
        marker = read(self.product / '.remorsearch-owned-copy.json')
        if marker.get('source_manifest_sha256') != self.protocol['peekly_source_manifest_sha256']:
            raise ValueError('Owned copy does not match the frozen source manifest')
        self.library = self.work / 'persona-library'
        self.run = self.work / 'persona-run'
        self.cli = skill.resolve(strict=True) / 'scripts/ux_personas.py'
        self.ops = self.work / 'operations'
        self.ops.mkdir(mode=0o700, exist_ok=True)
        self.env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', TZ='Asia/Seoul',
                        PEEKLY_IN_APP_INSTAGRAM_LOGIN='false',
                        NODE_OPTIONS='--require=' + str(HERE / 'network_guard.cjs') + ' --max-old-space-size=1536',
                        PEEKLY_PILOT_NETWORK_LOG=str(self.work / 'network-pilot.jsonl'))
        self.verify()

    def verify(self):
        binding = read(self.binding)
        if binding['source_manifest_sha256'] != self.protocol['peekly_source_manifest_sha256']:
            raise ValueError('Source binding does not match the protocol')
        for rel, sha in binding['files'].items():
            path = (self.product / rel).resolve(strict=True)
            if not path.is_relative_to(self.product) or digest(path) != sha:
                raise ValueError('Owned source changed: ' + rel)
        return len(binding['files'])

    def call(self, command, *args):
        # Every command is a new real CLI process, including each reuse/report.
        number = len(list(self.ops.glob('*.json'))) + 1
        proc = subprocess.run([sys.executable, str(self.cli), command, '--library', str(self.library),
                               *map(str, args)], env=self.env, capture_output=True, text=True, timeout=30)
        write_json(self.ops / f'{number:03d}-{command}.json',
                   dict(exit_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr))
        if proc.returncode:
            raise RuntimeError(f'{command} failed with exit {proc.returncode}; private operation log retained')
        return json.loads(proc.stdout)

    def prepare(self):
        if self.library.exists() or self.run.exists():
            raise ValueError('Never overwrite an existing library or run')
        target = self.product / 'pilot'
        target.mkdir(mode=0o700)
        for name in ('protocol.json', 'peeklyJourneys.test.ts'):
            shutil.copyfile(HERE / name, target / name)
        profiles = mapped_profiles(self.protocol)
        spec = dict(schema_version='ux-persona-library-input.v1', product_id=self.protocol['product_id'],
                    mode='prd_hypothesis', review_days=30,
                    context=dict(prd_path=str(self.product / 'docs/PRD.md'),
                                 prd_sha256=digest(self.product / 'docs/PRD.md'),
                                 requirements=self.protocol['requirements']), personas=profiles)
        source = self.work / 'persona-input.json'
        write_json(source, spec)
        imported = self.call('import', '--input', source)
        repeated = self.call('import', '--input', source)
        if any(p['changed'] for p in repeated['imported']):
            raise ValueError('Identical import did not reuse the existing revisions')
        self.call('list', '--product', self.protocol['product_id'])
        for p in profiles:
            self.call('reuse', '--product', self.protocol['product_id'], '--persona', p['persona_id'], '--revision', 1)
        write_json(self.work / 'library-reuse-summary.json', dict(
            schema_version='peekly-library-reuse.v1', imported=imported['imported'],
            identical_reimport=repeated['imported'], new_process_per_command=True,
            protocol_to_library_ids={p['persona_id']: library_id(p['persona_id']) for p in self.protocol['personas']}))
        self.plan()
        print(json.dumps(dict(prepared=True, personas=len(profiles), tasks=len(self.protocol['tasks']),
                              unchanged_source_files=self.verify())))

    def plan(self):
        # Schema-only authoring repair is allowed before any run or claim exists.
        # Preserve each rejected input and CLI log; never reset an existing run.
        if self.run.exists() or not self.library.exists():
            raise ValueError('Plan needs an existing library and no existing run')
        tasks = []
        for task in self.protocol['tasks']:
            tasks.append({k: task[k] for k in ('id', 'requirement_ids', 'goal', 'success_criteria', 'recovery_criteria')})
            tasks[-1].update(persona_id=library_id(task['persona_id']),
                             starting_state='A new Node process with built-in synthetic samples and an empty owned in-memory storage adapter.',
                             actions=['Load the unchanged product sample and actual core modules',
                                      'Execute the frozen normal and failure criteria',
                                      'Execute the frozen recovery criterion and retain the observations'],
                             decisions=['Compare actual observations against the frozen criteria without altering them'],
                             data_namespace='fixture-' + task['id'].lower(), resource_id='owned-peekly-core',
                             side_effects='owned_fixture_write',
                             stop_conditions=['Stop on an unexpected network or listener attempt',
                                              'Stop at timeout, lease expiry, changed product bytes or inaccessible owned evidence'],
                             requirement_coverage=coverage(task))
        plan = dict(schema_version='ux-persona-swarm-input.v1', product_id=self.protocol['product_id'],
                    build=dict(id='peekly-dirty-' + self.protocol['peekly_source_manifest_sha256'][:12],
                               artifact_path=str(self.binding), sha256=digest(self.binding)),
                    max_parallel=1, lease_seconds=600, max_attempts=2, tasks=tasks)
        serial = len(list(self.work.glob('plan-input*.json'))) + 1
        plan_file = self.work / f'plan-input-{serial:02d}.json'
        write_json(plan_file, plan)
        self.call('plan', '--run', self.run, '--input', plan_file)
        print(json.dumps(dict(plan_created=True, tasks=len(tasks))))

    def task(self, task_id, retry=False):
        task = next(t for t in self.protocol['tasks'] if t['id'] == task_id)
        self.call('reuse', '--product', self.protocol['product_id'],
                  '--persona', library_id(task['persona_id']))
        if retry:
            self.call('retry', '--run', self.run, '--task', task_id)
        claim = self.call('claim', '--run', self.run, '--task', task_id, '--worker', 'owned-core-worker')
        if not claim.get('claimed'):
            raise ValueError('No claim available; do not reset the run or its budget')
        evidence = Path(claim['evidence_path'])
        claim_file = evidence / 'claim.json'
        write_json(claim_file, claim)
        starter = self.call('receipt-starter', '--run', self.run, '--claim', claim_file)
        observation = evidence / 'observation.json'
        env = dict(self.env, PEEKLY_PILOT_TASK=task_id, PEEKLY_PILOT_OBSERVATIONS=str(observation))
        metrics_dir = self.work / 'measurements'
        used = sum(read(p)['wall_seconds'] for p in metrics_dir.glob('journey-*.json')) if metrics_dir.exists() else 0
        if used >= self.protocol['bounds']['total_case_budget_seconds']:
            raise ValueError('Fixed total case budget exhausted; preserve the claim')
        measurement = measure(['node', 'node_modules/vitest/vitest.mjs', 'run',
                               'pilot/peeklyJourneys.test.ts', '--maxWorkers=1', '--minWorkers=1'],
                              self.product, metrics_dir / f'journey-{task_id}-{claim["attempt"]}.log',
                              min(90, self.protocol['bounds']['total_case_budget_seconds'] - used), env)
        self.verify()
        if not observation.exists() or measurement['timed_out']:
            raise RuntimeError('Harness did not finish with observations; retain the claim and inspect before retry')
        obs = read(observation)
        if obs.get('harness_error') or len(obs['checks']) != 3:
            raise RuntimeError('Harness error is not a product finding; original observation and claim retained')
        if measurement['exit_code'] != (0 if obs['core_goal_passed'] else 1):
            raise RuntimeError('Unexpected process result; do not attribute it to the product')
        starter.pop('drafting_guidance')
        starter.update(schema_version='ux-persona-swarm-receipt.v1',
                       outcome='inconclusive' if obs['core_goal_passed'] else 'failed',
                       reason=('Core criteria met; UI execution and screenshot evidence are unavailable.'
                               if obs['core_goal_passed'] else 'A frozen actual-product core criterion failed; no UI result is asserted.'),
                       steps=[{**step, 'evidence_ids': ['execution']} for step in obs['steps']],
                       criteria=[dict(kind=c['kind'], index=c['index'], status='passed' if c['passed'] else 'failed',
                                      observation=c['observation'], evidence_ids=['execution']) for c in obs['checks']],
                       artifacts=[dict(id='execution', kind='execution_log',
                                       path=str(observation.relative_to(self.run)), sha256=digest(observation))])
        receipt = evidence / 'receipt-input.json'
        write_json(receipt, starter)
        self.call('record', '--run', self.run, '--input', receipt)
        if starter['outcome'] == 'inconclusive':
            # The owned process finished; memory-only fixtures are gone. No claim
            # about App effects or an external provider is made by this inspection.
            inspection = evidence / 'settlement.json'
            write_json(inspection, dict(operation_id=claim['operation_id'], attempt=claim['attempt'],
                       worker_stopped=True, outcome='effects_inspected_safe_for_other_tasks',
                       note='The owned Node command exited. The fixture used process-local memory only; observations exist and all copied product source hashes are unchanged. No browser or provider ran.'))
            self.call('settle', '--run', self.run, '--task', task_id, '--inspection', inspection)
        self.call('report', '--run', self.run)
        print(json.dumps(dict(task=task_id, attempt=claim['attempt'], core_goal_passed=obs['core_goal_passed'],
                              receipt_outcome=starter['outcome'], process_exit=measurement['exit_code'],
                              wall_seconds=measurement['wall_seconds'], max_rss_bytes=measurement['max_rss_bytes'],
                              observation_sha256=digest(observation))))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--skill', type=Path, default=HERE.parents[1] / 'skills/remorsearch-ux-qa')
    parser.add_argument('command', choices=['prepare', 'plan', 'task', 'report', 'verify-copy'])
    parser.add_argument('--task', choices=['T-SAMPLE', 'T-RECOVER', 'T-LARGE', 'T-STORAGE', 'T-FOLDER'])
    parser.add_argument('--retry', action='store_true')
    args = parser.parse_args()
    pilot = Pilot(args.work, args.skill)
    if args.command == 'prepare':
        pilot.prepare()
    elif args.command == 'plan':
        pilot.plan()
    elif args.command == 'task':
        if not args.task:
            parser.error('--task is required')
        pilot.task(args.task, args.retry)
    elif args.command == 'report':
        report = pilot.call('report', '--run', pilot.run)
        print(json.dumps(dict(counts=report.get('counts'), product_ready=report.get('product_ready'))))
    else:
        print(json.dumps(dict(unchanged_source_files=pilot.verify())))


if __name__ == '__main__':
    main()
