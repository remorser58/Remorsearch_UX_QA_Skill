"""These authored observations test extraction, not product UX."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from collect_peekly_ux_evidence import RELATIONS, signals

class SignalTests(unittest.TestCase):
    def observation(self):
        text = ' '.join(RELATIONS) + ' 결과를 불러왔어요. 인스타를 한 번 연결해 두세요.'
        return {'action': 'Upload synthetic file', 'text': text, 'facts': {
            'last_action': 'upload', 'text': text,
            'controls': [{'label': label + ' 5명', 'visible': False} for label in RELATIONS]}}

    def test_import_visibility_and_connection_copy_have_separate_signals(self):
        obs = self.observation(); before = copy.deepcopy(obs)
        self.assertEqual(signals(obs), ['UX-01', 'UX-03'])
        self.assertEqual(obs, before)
        obs['facts']['controls'][0]['visible'] = True
        self.assertEqual(signals(obs), ['UX-03'])

    def test_sample_or_unconfirmed_upload_does_not_establish_import_issue(self):
        obs = self.observation(); obs['facts']['last_action'] = 'click'
        self.assertEqual(signals(obs), [])
        obs = self.observation(); obs['facts']['text'] = ' '.join(RELATIONS)
        self.assertEqual(signals(obs), [])

    def test_detour_requires_an_import_seeking_action_and_missing_entry(self):
        obs = {'action': '가져오기 경로를 찾으러 더보기로 간다', 'text': '더보기 레이더 약관과 개인정보',
            'facts': {'controls': []}}
        self.assertEqual(signals(obs), ['UX-02-detour'])
        obs['action'] = '더보기의 레이더를 본다'
        self.assertEqual(signals(obs), [])

    def test_wizard_request_is_not_the_missing_skip_link_false_positive(self):
        obs = {'action': 'Open import', 'text': '인스타그램에 내 파일을 요청해요 1 / 3단계',
            'facts': {'controls': [{'label': '받은 파일 바로 넣기'}]}}
        self.assertEqual(signals(obs), ['UX-04'])
