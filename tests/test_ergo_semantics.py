"""Semantics and layout checks (SM-01..04, LY-01) on synthetic snapshots."""

from __future__ import annotations

import unittest

import _paths  # noqa: F401  (puts the skill folder on sys.path)

from ergoqa import checks  # noqa: E402
from test_ergo_fixes import ctx, el  # noqa: E402


def a11y(source="content", **kw):
    out = {"name_source": source, "invalid": False, "user_invalid": False, "described_by": [], "error_message": None,
           "required": False, "focusable": True, "tabindex": None}
    out.update(kw)
    return out


def ids(obs, check_id):
    return sorted(o.element_key.split("|")[0] for o in obs if o.check_id == check_id)


class Names(unittest.TestCase):
    def test_icon_button_without_name(self) -> None:
        icon = el("close", "button", (300, 10, 44, 44), interactive=True, tag="button", a11y=a11y("none"))
        named = el("ok", "button", (10, 600, 340, 48), text="확인", interactive=True, tag="button", a11y=a11y("content"))
        obs = checks.check_semantics(ctx([icon, named]))
        self.assertEqual(ids(obs, "SM-01"), ["#close"])
        self.assertEqual(next(o for o in obs if o.check_id == "SM-01").severity, "P2")
        self.assertEqual(next(o for o in checks.check_semantics(ctx([icon], path_ids=("close",))) if o.check_id == "SM-01").severity, "P1")

    def test_label_in_name(self) -> None:
        mismatch = el("buy", "button", (10, 600, 340, 48), text="구매하기", name="장바구니 결제 진행", interactive=True, tag="button",
                      a11y=a11y("aria-label"))
        contains = el("buy2", "button", (10, 660, 340, 48), text="구매하기", name="구매하기 - 3개 상품", interactive=True, tag="button",
                      a11y=a11y("aria-label"))
        glyph = el("x", "button", (300, 10, 44, 44), text="×", name="닫기", interactive=True, tag="button", a11y=a11y("aria-label"))
        card = el("card", "link", (10, 100, 340, 120), text="여름 세일 원피스 39,000원 무료배송 오늘 출발 리뷰 1,204개", name="여름 세일 원피스",
                  interactive=True, tag="a", a11y=a11y("aria-label"))
        self.assertEqual(ids(checks.check_semantics(ctx([mismatch, contains, glyph, card])), "SM-02"), ["#buy"])


class Fields(unittest.TestCase):
    def test_placeholder_only_and_unlabelled_fields(self) -> None:
        ph = el("phone", "textbox", (10, 200, 340, 44), interactive=True, tag="input", name="010-0000-0000", a11y=a11y("placeholder"))
        none = el("memo", "textbox", (10, 260, 340, 44), interactive=True, tag="textarea", a11y=a11y("none"))
        ok = el("card", "textbox", (10, 320, 340, 44), interactive=True, tag="input", name="카드 번호", a11y=a11y("label"))
        submit = el("go", "button", (10, 400, 340, 44), interactive=True, tag="input", text="제출", name="제출", a11y=a11y("value"))
        obs = checks.check_semantics(ctx([ph, none, ok, submit], path_ids=("phone",)))
        self.assertEqual(ids(obs, "SM-03"), ["#memo", "#phone"])
        sev = {o.element_key.split("|")[0]: o.severity for o in obs if o.check_id == "SM-03"}
        self.assertEqual(sev, {"#phone": "P2", "#memo": "P2"})
        self.assertEqual(ids(obs, "SM-01"), [])


class Errors(unittest.TestCase):
    def field(self, **kw):
        return el("card", "textbox", (10, 300, 340, 44), interactive=True, tag="input", name="카드 번호", a11y=a11y("label", **kw))

    def test_far_unlinked_error_fails(self) -> None:
        err = el("err", "alert", (10, 60, 340, 40), text="입력 내용을 확인하세요", roles=("error_message",))
        self.assertEqual(ids(checks.check_semantics(ctx([self.field(), err])), "SM-04"), ["#err"])

    def test_near_or_linked_error_passes(self) -> None:
        near = el("err", "alert", (10, 350, 340, 20), text="카드 번호를 확인하세요", roles=("error_message",))
        self.assertEqual(ids(checks.check_semantics(ctx([self.field(), near])), "SM-04"), [])
        far = el("err", "alert", (10, 60, 340, 40), text="입력 내용을 확인하세요", roles=("error_message",))
        linked = self.field(described_by=["err"], invalid=True)
        self.assertEqual(ids(checks.check_semantics(ctx([linked, far])), "SM-04"), [])

    def test_error_naming_its_field_passes_and_system_notices_are_skipped(self) -> None:
        names = el("err", "alert", (10, 60, 340, 40), text="⚠ 카드 번호를 확인해 주세요.", roles=("error_message",))
        self.assertEqual(ids(checks.check_semantics(ctx([self.field(), names])), "SM-04"), [])
        notice = el("notice", "alert", (10, 60, 340, 40), text="결제 모듈 동기화 실패", roles=("critical_message",))
        self.assertEqual(ids(checks.check_semantics(ctx([self.field(), notice])), "SM-04"), [])
        vague = el("err", "alert", (10, 60, 340, 40), text="일부 항목이 올바르지 않아요", roles=("error_message",))
        self.assertEqual(ids(checks.check_semantics(ctx([self.field(), vague])), "SM-04"), ["#err"])

    def test_no_fields_no_finding(self) -> None:
        err = el("err", "alert", (10, 60, 340, 40), text="네트워크 오류", roles=("error_message",))
        self.assertEqual(ids(checks.check_semantics(ctx([err])), "SM-04"), [])


class Clipping(unittest.TestCase):
    def test_clipped_text(self) -> None:
        cut = el("title", "paragraph", (10, 100, 120, 20), text="아주 긴 상품 이름이 여기서 잘립니다", clipped={"x": True, "y": False, "ellipsis": False})
        dots = el("sub", "paragraph", (10, 130, 120, 20), text="말줄임표로 줄인 설명 문구입니다", clipped={"x": True, "y": False, "ellipsis": True})
        sr_only = el("sr", "paragraph", (0, 0, 1, 1), text="스크린리더 전용", clipped={"x": True, "y": True, "ellipsis": False})
        obs = [o for o in checks.check_semantics(ctx([cut, dots, sr_only])) if o.check_id == "LY-01"]
        self.assertEqual({o.element_key.split("|")[0]: o.severity for o in obs}, {"#title": "P2", "#sub": "P3"})

    def test_profile_invariant_and_categories(self) -> None:
        for cid, cat in (("SM-01", "semantics"), ("SM-04", "semantics"), ("LY-01", "layout")):
            self.assertIn(cid, checks.PROFILE_INVARIANT_CHECKS)
            self.assertEqual(checks.CATALOG[cid].category, cat)
            self.assertEqual(checks.tier(cid), "finding")


class FocusWalk(unittest.TestCase):
    def run_doc(self):
        def stop(sel, px, covered=0.0, name=""):
            return {"selector": sel, "name": name, "indicator_px": px, "obscured_fraction": covered, "obscured_by": "#bar" if covered else None,
                    "in_viewport": True, "box": {"x": 0, "y": 0, "w": 100, "h": 40}}
        stops = [stop("#plain", 530), stop("#nofocus", 0), stop("#faint", 3), stop("#under", 0, 1.0), stop("#half", 200, 0.444)]
        return {"run_id": "R-f", "focus_walks": [{"phase": "load", "snapshot_id": "S-0", "stops": stops},
                                                 {"phase": "end", "snapshot_id": "S-1", "stops": stops}]}

    def test_focus_not_visible_and_obscured(self) -> None:
        obs = checks.check_focus_walks(self.run_doc(), {"profile_id": "P"})
        got = sorted((o.check_id, o.element_key.split("|")[0], o.severity) for o in obs)
        self.assertEqual(got, [("SM-05", "#faint", "P2"), ("SM-05", "#nofocus", "P2"), ("SM-06", "#half", "P3"), ("SM-06", "#under", "P2")])

    def test_runs_without_walks(self) -> None:
        self.assertEqual(checks.check_focus_walks({"run_id": "R"}, {"profile_id": "P"}), [])


if __name__ == "__main__":
    unittest.main()
