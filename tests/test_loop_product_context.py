"""Product-context intent protection: the opt-in goal binding gates writes and completion.

One focused module for the additive contract: preserved constraints must be acknowledged
before any code write with a concrete prewrite decision, unresolved material conflicts
block only the fixes they overlap, explicitly authorized changes need a recorded current
human decision (the operator grant, never a provider claim), and completion requires a
fresh, same-round replay-linked intent review covering every applicable constraint with
actual declared scenario evidence. Packets without the binding keep the exact v1 behavior.
"""
import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from loop_factory import ROOT, SKILL, append_recovery_round, make_packet
from uxloop.contracts import validate_packet
from uxloop.engine import report, run
from uxloop.io import ContractError, sha
from uxloop.storage import load

ACTOR = 'test-supervisor'
REASON = 'Approve only the isolated fixture site patch'
CONTEXT_AT = '2026-09-14T00:00:00+00:00'
REVIEW_AT = '2026-09-14T00:07:00+00:00'
REVIEW2_AT = '2026-09-14T00:17:00+00:00'

CONFLICT = {
    'id': 'conflict-label',
    'description': '프로젝트 문서는 지금의 "다음" 라벨을 유지할 것을 권고하지만, 요청은 목적지를 분명히 하라고 한다.',
    'source_id': 'ctx-doc',
    'scope': {'paths': ['index.html'], 'scenario_ids': []},
}
UNRELATED_CONFLICT = {
    'id': 'conflict-checkout',
    'description': '결제 흐름의 안내 문구를 바꿀지는 별도로 정해야 한다.',
    'source_id': 'ctx-doc',
    'scope': {'paths': ['checkout.html'], 'scenario_ids': []},
}
PRESERVED_ENTRY = {'fix_id': 'fix-1', 'constraint_id': 'constraint-action-flow', 'outcome': 'preserved',
                   'evidence': '재실행에서 버튼 위치와 진행 흐름은 그대로이고 라벨만 목적지를 분명히 나타냈다.',
                   'run_id': 'replay-1'}
CHANGED_ENTRY = {'fix_id': 'fix-1', 'constraint_id': 'constraint-action-flow', 'outcome': 'intentionally_changed',
                 'evidence': '요청한 결정대로 라벨이 바뀌었고 확인 흐름은 유지되었다.', 'run_id': 'replay-1'}
CONFLICT_ENTRY = {'fix_id': 'fix-1', 'conflict_id': 'conflict-label', 'outcome': 'resolved',
                  'evidence': '요청한 결정대로 라벨만 바뀌었고 확인 흐름은 유지되었다.', 'run_id': 'replay-1'}


def go_kwargs(kwargs):
    options = {'grants': ['code_write'], 'actor': ACTOR, 'reason': REASON}
    options.update(kwargs)
    return options


def context_payload(conflicts=(), memory_status='searched_not_available', include_memory_source=False,
                    drop_memory_search=False):
    sources = [
        {'id': 'ctx-doc', 'kind': 'project_doc', 'ref': 'docs/product-notes.md', 'version': 'git ad5b461',
         'checked_at': '2026-09-13'},
        {'id': 'ctx-decision', 'kind': 'current_user_decision', 'ref': '요청 대화 2026-10-01', 'version': 'session-1',
         'checked_at': '2026-10-01'},
    ]
    if include_memory_source:
        sources.append({'id': 'ctx-memory', 'kind': 'memory', 'ref': 'memory://sessions/ergo', 'version': 'auto',
                        'checked_at': '2026-09-12'})
    payload = {
        'kind': 'product_context', 'goal_id': 'goal-action-label',
        'product': {'name': '예제 상점', 'version': '1', 'surface': 'https://example.test/product'},
        'memory_search': {'status': memory_status,
                          'detail': 'AGENTS.md, README, PRD와 세션 기록 위치를 확인했다. 이 제품에 대해 남아 있는 메모리는 없다.'},
        'sources': sources,
        'constraints': [{
            'id': 'constraint-action-flow',
            'title': '다음 행동 버튼의 위치와 진행 흐름 유지',
            'reason': '기획 문서에 근거해 사용자가 다음 행동을 한 단계씩 확인하며 진행하도록 의도적으로 설계되었다.',
            'source_id': 'ctx-doc', 'decision_date': '2026-09-13',
            'scope': {'paths': ['index.html'], 'scenario_ids': ['scenario-1']},
        }],
        'conflicts': list(conflicts),
    }
    if drop_memory_search:
        payload.pop('memory_search')
    return payload


def _add_artifact(packet, root, artifact_id, kind, payload, at):
    path = 'artifacts/' + artifact_id + '.json'
    raw = (json.dumps(payload, ensure_ascii=False, indent=2) + '\n').encode()
    (root / path).write_bytes(raw)
    packet['artifacts'].append({'id': artifact_id, 'path': path, 'sha256': sha(raw), 'kind': kind,
                                'provenance': 'fixture', 'created_at': at})
    return artifact_id


def bind_context(packet, root, payload=None, at=CONTEXT_AT):
    packet['goal']['product_context_artifact_id'] = _add_artifact(
        packet, root, 'artifact-context', 'product_context', payload or context_payload(), at)


def review_payload(packet, results=None, conflict_results=(), fix_ids=('fix-1',), revision=None, run_ids=None):
    replay = packet['replays'][0]
    return {'kind': 'intent_review', 'replay_id': replay['id'],
            'code_revision': revision or replay['regression']['code_revision'],
            'run_ids': list(run_ids if run_ids is not None else replay['run_ids']), 'fix_ids': list(fix_ids),
            'constraint_results': [dict(PRESERVED_ENTRY)] if results is None else list(results),
            'conflict_results': list(conflict_results)}


def attach_review(packet, root, payload=None, at=REVIEW_AT):
    replay = packet['replays'][0]
    if payload is None:
        payload = review_payload(packet)
        payload['constraint_results'] = [dict(PRESERVED_ENTRY)]
    replay['intent_review_artifact_id'] = _add_artifact(packet, root, 'artifact-intent-review', 'intent_review',
                                                         payload, at)


def attach_changed_review(packet, root):
    payload = review_payload(packet)
    payload['constraint_results'] = [dict(CHANGED_ENTRY)]
    attach_review(packet, root, payload)


def acknowledge(packet, decision='preserved', evidence='버튼의 위치와 진행 흐름은 그대로 두고 라벨만 목적지를 분명히 바꾼다.',
                actor=None):
    ack = {'constraint_id': 'constraint-action-flow', 'decision': decision, 'evidence': evidence}
    if actor is not None:
        ack['actor'] = actor
    packet['fixes'][0]['constraint_acknowledgements'] = [ack]


def resolve_conflicts(packet, actor=ACTOR):
    packet['fixes'][0]['conflict_resolutions'] = [
        {'conflict_id': 'conflict-label', 'actor': actor,
         'note': '요청자가 2026-10-01 대화에서 이 화면의 라벨을 먼저 다듬기로 결정했다.'}]


class ProductContextIntentTests(unittest.TestCase):
    def setUp(self):
        (ROOT / '.ux-loop').mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / '.ux-loop')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.evidence_root = self.root / 'evidence'
        self.workspace = self.root / 'site'
        self.workspace.mkdir()
        shutil.copy2(SKILL / 'examples/loop/site/index.html', self.workspace / 'index.html')
        self.checkpoint = self.root / 'checkpoint.json'
        self.packet = make_packet(self.evidence_root)
        self.original = (self.workspace / 'index.html').read_text()

    def fresh(self, case='happy'):
        """An isolated disposable run directory for cases that must not share a checkpoint."""
        directory = tempfile.TemporaryDirectory(dir=ROOT / '.ux-loop')
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        evidence_root = root / 'evidence'
        workspace = root / 'site'
        workspace.mkdir()
        shutil.copy2(SKILL / 'examples/loop/site/index.html', workspace / 'index.html')
        packet = make_packet(evidence_root, case)
        options = go_kwargs({'workspace': workspace, 'evidence_root': evidence_root,
                             'checkpoint': root / 'checkpoint.json'})
        return packet, options

    def go(self, packet=None, **kwargs):
        return run(self.packet if packet is None else packet, self.checkpoint, self.workspace,
                   self.evidence_root, **go_kwargs(kwargs))

    def assert_not_complete(self, state, status=None):
        if status:
            self.assertEqual(state['status'], status, state['reason'])
        self.assertNotEqual(state['status'], 'complete')
        self.assertEqual(state['accepted_fix_ids'], [])
        self.assertFalse(report(state)['product_complete'])

    def assert_untouched(self, options):
        self.assertEqual((options['workspace'] / 'index.html').read_text(),
                         (SKILL / 'examples/loop/site/index.html').read_text())

    def test_binding_accepts_patch_only_after_fresh_covering_intent_replay(self):
        bind_context(self.packet, self.evidence_root)
        acknowledge(self.packet)
        attach_review(self.packet, self.evidence_root)
        self.assertEqual(validate_packet(self.packet), [])
        state = self.go()
        self.assertEqual(state['status'], 'complete', state['reason'])
        self.assertEqual(state['accepted_fix_ids'], ['fix-1'])
        self.assertIn('상품 상세 보기', (self.workspace / 'index.html').read_text())
        summary = report(state)['product_context']
        self.assertEqual(summary['artifact_id'], 'artifact-context')
        self.assertEqual(summary['memory_search'], 'searched_not_available')
        self.assertEqual(summary['constraints'][0]['id'], 'constraint-action-flow')
        self.assertEqual(summary['applied_fix_decisions']['fix-1']['acknowledgements'],
                         {'constraint-action-flow': 'preserved'})
        self.assertIn('imported authored records', ' '.join(report(state)['limitations']))
        # Completion is revalidated against the artifact hash: a tampered review cannot keep success.
        (self.evidence_root / 'artifacts/artifact-intent-review.json').write_text('{}')
        self.assert_not_complete(run(None, self.checkpoint), 'unknown')

    def test_conflict_blocks_write_until_a_current_request_settles_exactly_that_conflict(self):
        bind_context(self.packet, self.evidence_root, context_payload(conflicts=[CONFLICT]))
        acknowledge(self.packet)
        state = self.go()
        self.assert_not_complete(state, 'blocked')
        self.assertEqual(state['phase'], 'fix')
        self.assertIn('Unresolved material intent conflict conflict-label', state['reason'])
        self.assertEqual((self.workspace / 'index.html').read_text(), self.original)

        packet, options = self.fresh()
        bind_context(packet, options['evidence_root'], context_payload(conflicts=[CONFLICT]))
        acknowledge(packet)
        resolve_conflicts(packet)
        payload = review_payload(packet, conflict_results=[dict(CONFLICT_ENTRY)])
        attach_review(packet, options['evidence_root'], payload)
        self.assertEqual(validate_packet(packet), [])
        done = run(packet, **options)
        self.assertEqual(done['status'], 'complete', done['reason'])
        self.assertIn('상품 상세 보기', (options['workspace'] / 'index.html').read_text())

    def test_unrelated_conflict_or_gap_does_not_stop_safe_fixes(self):
        bind_context(self.packet, self.evidence_root, context_payload(conflicts=[UNRELATED_CONFLICT]))
        acknowledge(self.packet)
        attach_review(self.packet, self.evidence_root)
        state = self.go()
        self.assertEqual(state['status'], 'complete', state['reason'])
        self.assertEqual(report(state)['product_context']['unresolved_conflicts'][0]['id'], 'conflict-checkout')
        self.assertIn('상품 상세 보기', (self.workspace / 'index.html').read_text())

    def test_missing_or_fabricated_context_blocks_code_write_not_earlier_phases(self):
        cases = (
            ('missing artifact file',
             lambda p, r: (bind_context(p, r), (r / 'artifacts/artifact-context.json').unlink())),
            ('fabricated memory source',
             lambda p, r: bind_context(p, r, context_payload(include_memory_source=True))),
            ('unrecorded memory search',
             lambda p, r: bind_context(p, r, context_payload(drop_memory_search=True))),
        )
        for label, mutate in cases:
            with self.subTest(label=label):
                packet, options = self.fresh()
                acknowledge(packet)
                attach_review(packet, options['evidence_root'])
                mutate(packet, options['evidence_root'])
                self.assertEqual(validate_packet(packet), [])
                state = run(packet, **options)
                self.assert_not_complete(state, 'blocked')
                self.assertEqual(state['phase'], 'fix', label)  # research, planning and QA were never stopped
                self.assertIn('product context', state['reason'])
                self.assert_untouched(options)

    def test_prewrite_acknowledgement_needs_concrete_evidence_and_current_decision(self):
        cases = (
            ('no acknowledgement', lambda p, r: None, 'blocked', 'does not acknowledge'),
            ('blank evidence', lambda p, r: acknowledge(p, evidence='   '), 'blocked', 'concrete'),
            ('actor-less authorized change', lambda p, r: acknowledge(p, decision='authorized_change'),
             'invalid', None),
            ('foreign actor',
             lambda p, r: acknowledge(p, decision='authorized_change', actor='provider-agent'),
             'blocked', 'not a human decision'),
            ('decision older than the context',
             lambda p, r: (acknowledge(p, decision='authorized_change', actor=ACTOR),
                           bind_context(p, r, at='2030-01-01T00:00:00+00:00')),
             'blocked', 'current human decision'),
        )
        for label, setup, expected, reason in cases:
            with self.subTest(label=label):
                packet, options = self.fresh()
                bind_context(packet, options['evidence_root'])
                setup(packet, options['evidence_root'])
                attach_changed_review(packet, options['evidence_root'])
                if expected == 'invalid':
                    self.assertTrue(any('authorized_change requires the actor' in x
                                        for x in validate_packet(packet)), label)
                    continue
                state = run(packet, **options)
                self.assert_not_complete(state, expected)
                self.assertIn(reason, state['reason'])
                self.assert_untouched(options)
        packet, options = self.fresh()
        bind_context(packet, options['evidence_root'])
        acknowledge(packet, decision='authorized_change', actor=ACTOR)
        attach_changed_review(packet, options['evidence_root'])
        state = run(packet, **options)
        self.assertEqual(state['status'], 'complete', state['reason'])
        self.assertEqual(report(state)['product_context']['applied_fix_decisions']['fix-1']['acknowledgements'],
                         {'constraint-action-flow': 'authorized_change'})

    def test_completion_refuses_missing_stale_failing_duplicate_or_uncovered_review(self):
        duplicate = [dict(PRESERVED_ENTRY),
                     {**PRESERVED_ENTRY, 'evidence': '동일한 근거를 반복해도 증거가 되지 않는다.'}]
        cases = (
            ('no review', lambda p, r: None, 'blocked', 'no linked intent review'),
            ('wrong revision', lambda p, r: attach_review(p, r, review_payload(p, revision='f' * 64)),
             'unknown', 'stale, cross-round'),
            ('reordered run evidence', lambda p, r: attach_review(p, r, review_payload(p, run_ids=[])),
             'unknown', 'stale, cross-round'),
            ('predates replay', lambda p, r: attach_review(p, r, at='2026-09-14T00:04:30+00:00'),
             'unknown', 'predates its replay runs'),
            ('uncovered constraint', lambda p, r: attach_review(p, r, review_payload(p, results=[])),
             'unknown', 'does not cover applicable'),
            ('duplicate coverage', lambda p, r: attach_review(p, r, review_payload(p, results=duplicate)),
             'unknown', 'duplicates'),
            ('contradicting outcome',
             lambda p, r: attach_review(p, r, review_payload(p, results=[dict(CHANGED_ENTRY)])),
             'unknown', 'contradicts'),
            ('empty evidence',
             lambda p, r: attach_review(p, r, review_payload(p, results=[{**PRESERVED_ENTRY, 'evidence': '  '}])),
             'unknown', 'lacks concrete replay evidence'),
            ('run outside this replay',
             lambda p, r: attach_review(p, r, review_payload(
                 p, results=[{**PRESERVED_ENTRY, 'run_id': 'baseline-1',
                              'evidence': '수정 전 실행으로는 보존을 확인할 수 없다.'}])),
             'unknown', 'outside this round'),
        )
        for label, attach, status, reason in cases:
            with self.subTest(label=label):
                packet, options = self.fresh()
                bind_context(packet, options['evidence_root'])
                acknowledge(packet)
                attach(packet, options['evidence_root'])
                state = run(packet, **options)
                self.assert_not_complete(state, status)
                self.assertEqual(state['phase'], 'replay')
                self.assertIn(reason, state['reason'])
                self.assertEqual(state['accepted_fix_ids'], [])  # patch may exist, acceptance never happens

    def test_goal_binding_cannot_be_downgraded_or_replaced_on_resume(self):
        bind_context(self.packet, self.evidence_root)
        acknowledge(self.packet)
        attach_review(self.packet, self.evidence_root)
        self.assert_not_complete(self.go(pause_after='browser'), 'interrupted')
        for mutate in (lambda p: p['goal'].pop('product_context_artifact_id'),
                       lambda p: p['goal'].update(product_context_artifact_id='artifact-context-2')):
            downgrade = copy.deepcopy(self.packet)
            mutate(downgrade)
            with self.assertRaises(ContractError):
                run(downgrade, self.checkpoint)
        self.assertEqual(load(self.checkpoint)['packet']['goal']['product_context_artifact_id'],
                         'artifact-context')
        resumed = run(None, self.checkpoint)
        self.assertEqual(resumed['status'], 'complete', resumed['reason'])
        self.assertEqual(resumed['accepted_fix_ids'], ['fix-1'])

    def test_no_change_round_and_retry_still_require_intent_evidence(self):
        for label, review, expected in (('review attests empty coverage', True, 'complete'),
                                        ('no review', False, 'blocked')):
            with self.subTest(label=label):
                packet, options = self.fresh()
                records = packet['bundle']['records']
                records['findings'] = []
                records['proposals'] = []
                packet['fixes'] = []
                packet['rounds'][0]['fix_ids'] = []
                bind_context(packet, options['evidence_root'])
                if review:
                    payload = review_payload(packet, results=[], fix_ids=())
                    attach_review(packet, options['evidence_root'], payload)
                state = run(packet, **options)
                if expected == 'complete':
                    self.assertEqual(state['status'], 'complete', state['reason'])
                    self.assertEqual(state['accepted_fix_ids'], [])
                    self.assertEqual(state['applied_fixes'], [])
                else:
                    self.assert_not_complete(state, 'blocked')
                    self.assertIn('no linked intent review', state['reason'])

        for label, with_review, expected in (('fresh round-2 review', True, 'complete'),
                                             ('no round-2 review', False, 'blocked')):
            with self.subTest(label=label):
                packet, options = self.fresh('failed_visual')
                bind_context(packet, options['evidence_root'])
                acknowledge(packet)
                attach_review(packet, options['evidence_root'])
                self.assert_not_complete(run(packet, **options), 'failed')  # round 1 keeps its own review
                newer = append_recovery_round(packet, options['evidence_root'])
                if with_review:
                    newer['replays'][1]['intent_review_artifact_id'] = _add_artifact(
                        newer, options['evidence_root'], 'artifact-intent-review-2', 'intent_review',
                        {'kind': 'intent_review', 'replay_id': 'replay-set-2',
                         'code_revision': newer['replays'][1]['regression']['code_revision'],
                         'run_ids': ['replay-2'], 'fix_ids': ['fix-1'],
                         'constraint_results': [{**PRESERVED_ENTRY, 'run_id': 'replay-2'}],
                         'conflict_results': []}, REVIEW2_AT)
                state = run(newer, **dict(options, retry=True))
                if expected == 'complete':
                    self.assertEqual(state['status'], 'complete', state['reason'])
                    self.assertEqual(state['iteration'], 2)
                    self.assertEqual(state['accepted_fix_ids'], ['fix-1'])
                else:
                    self.assert_not_complete(state, 'blocked')
                    self.assertIn('no linked intent review', state['reason'])

    def test_packets_without_binding_keep_v1_behavior(self):
        self.assertEqual(validate_packet(self.packet), [])
        state = self.go()
        self.assertEqual(state['status'], 'complete', state['reason'])
        self.assertIsNone(report(state)['product_context'])
        self.assertEqual(len(report(state)['limitations']), 4)
        self.assertIn('상품 상세 보기', (self.workspace / 'index.html').read_text())

        acks_only = copy.deepcopy(self.packet)
        acknowledge(acks_only)
        self.assertTrue(any('requires the goal product_context_artifact_id binding' in x
                            for x in validate_packet(acks_only)))
        review_only = copy.deepcopy(self.packet)
        attach_review(review_only, self.evidence_root)
        self.assertTrue(any('requires the goal product_context_artifact_id binding' in x
                            for x in validate_packet(review_only)))
        wrong_kind = copy.deepcopy(self.packet)
        wrong_kind['goal']['product_context_artifact_id'] = 'artifact-figma'
        self.assertTrue(any('wrong artifact kind' in x for x in validate_packet(wrong_kind)))
        unknown = copy.deepcopy(self.packet)
        unknown['goal']['product_context_artifact_id'] = 'artifact-missing'
        self.assertTrue(any('unknown record' in x for x in validate_packet(unknown)))


if __name__ == '__main__':
    unittest.main()
