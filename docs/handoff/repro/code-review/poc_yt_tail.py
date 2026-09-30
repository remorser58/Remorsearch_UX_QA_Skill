"""PoC: YouTube lead/tail positions are measured over description + comments."""
import os, sys, unittest
from unittest import mock
sys.path.insert(0, "/home/user/ux-research-qa-skills/tests")
import test_ux_youtube as Y
from test_ux_youtube import YoutubeCase, video_item, thread, KEY

setUpModule = Y.setUpModule
tearDownModule = Y.tearDownModule

class P(YoutubeCase):
    def test_tail(self):
        vid = "Vid0000009Z"
        desc = "충전 앱을 한 달 동안 써 본 후기입니다. " * 10 + "이 영상은 협찬입니다"   # a disclosure at the END of the description
        comments = [thread("UgwA00000001", "버튼이 늦게 반응해서 불편했어요. " * 6, name="@viewer-a"),
                    thread("UgwB00000002", "이거 그냥 광고입니다", name="@viewer-b")]   # a viewer's complaint, last comment
        self.api.add(vid, item=video_item(vid, description=desc), pages=[comments])
        self.start()
        code, summary, out = self.read(f"https://www.youtube.com/watch?v={vid}")
        print("\nexit", code, summary["bucket"])
        print("promotion_hits:", summary["promotion_hits"])

if __name__ == "__main__":
    unittest.main(verbosity=1)
