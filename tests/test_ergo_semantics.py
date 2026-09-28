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
        # ACT 2ee8b8: a card link whose aria-label drops most of its visible text fails too.
        self.assertEqual(ids(checks.check_semantics(ctx([mismatch, contains, glyph, card])), "SM-02"), ["#buy", "#card"])

    def test_act_label_in_name_algorithm(self) -> None:
        self.assertTrue(checks._label_in_name("Search by date (YYYY-MM-DD)", "Search by date"))
        self.assertTrue(checks._label_in_name("Download specification", "Download gizmo specification"[:9] + " specification"))
        self.assertFalse(checks._label_in_name("Download specification", "Download the specification"))  # not contiguous
        self.assertTrue(checks._label_in_name("장바구니", "장바구니에 담기"))  # Korean particle relaxation
        self.assertTrue(checks._label_in_name("X", "닫기"))  # the close symbol is not text
        self.assertTrue(checks._label_in_name("Next →", "Next page"))


class Fields(unittest.TestCase):
    def test_placeholder_only_and_unlabelled_fields(self) -> None:
        ph = el("phone", "textbox", (10, 200, 340, 44), interactive=True, tag="input", name="010-0000-0000", a11y=a11y("placeholder"))
        none = el("memo", "textbox", (10, 260, 340, 44), interactive=True, tag="textarea", a11y=a11y("none"))
        ok = el("card", "textbox", (10, 320, 340, 44), interactive=True, tag="input", name="카드 번호", a11y=a11y("label"))
        submit = el("go", "button", (10, 400, 340, 44), interactive=True, tag="input", text="제출", name="제출", a11y=a11y("value"))
        obs = checks.check_semantics(ctx([ph, none, ok, submit], path_ids=("phone",)))
        self.assertEqual(ids(obs, "SM-03"), ["#memo"])  # no accessible name at all (WCAG 4.1.2)
        self.assertEqual(ids(obs, "SM-07"), ["#phone"])  # placeholder only: best practice, P3
        self.assertEqual({o.check_id: o.severity for o in obs if o.check_id in ("SM-03", "SM-07")}, {"SM-03": "P2", "SM-07": "P3"})
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


class ReviewFixes(unittest.TestCase):
    def test_hidden_duplicate_link_and_icon_font_text(self) -> None:
        dup = el("img-link", "link", (10, 100, 120, 80), interactive=True, tag="a", a11y=a11y("none", hidden=True, tabindex=-1))
        icon = el("nav", "button", (10, 10, 44, 44), text="menu", name="Open navigation", interactive=True, tag="button",
                  a11y=a11y("aria-label", icon_font=True))
        obs = checks.check_semantics(ctx([dup, icon]))
        self.assertEqual(ids(obs, "SM-01"), [])
        self.assertEqual(ids(obs, "SM-02"), [])

    def test_undeclared_alert_needs_an_invalid_field(self) -> None:
        qty = el("qty", "spinbutton", (10, 300, 120, 44), interactive=True, tag="input", name="수량", a11y=a11y("label"))
        toast = el("toast", "alert", (10, 700, 340, 40), text="장바구니에 담았습니다")
        self.assertEqual(ids(checks.check_semantics(ctx([qty, toast])), "SM-04"), [])
        bad = el("qty", "spinbutton", (10, 300, 120, 44), interactive=True, tag="input", name="수량", a11y=a11y("label", user_invalid=True))
        err = el("toast", "alert", (10, 700, 340, 40), text="입력을 확인해 주세요")
        self.assertEqual(ids(checks.check_semantics(ctx([bad, err])), "SM-04"), ["#toast"])

    def test_error_linked_through_a_wrapper_and_short_field_names(self) -> None:
        field = el("uid", "textbox", (10, 300, 340, 44), interactive=True, tag="input", name="ID", a11y=a11y("label", described_by=["err-box"]))
        err = el("err", "alert", (10, 60, 340, 40), text="invalid input", roles=("error_message",), ancestor_ids=["err-box"])
        self.assertEqual(ids(checks.check_semantics(ctx([field, err])), "SM-04"), [])
        unlinked = el("uid", "textbox", (10, 300, 340, 44), interactive=True, tag="input", name="ID", a11y=a11y("label"))
        self.assertEqual(ids(checks.check_semantics(ctx([unlinked, err])), "SM-04"), ["#err"])  # "id" does not name the field in "invalid"
        self.assertTrue(checks._names_field("이메일", "이메일을 입력해 주세요"))
        self.assertTrue(checks._names_field("Email address", "Please enter your email address."))
        self.assertFalse(checks._names_field("ID", "invalid input"))

    def test_tickers_are_not_clipped_text(self) -> None:
        ticker = el("tick", "paragraph", (0, 0, 360, 20), text="속보: 오늘 오후 운행 지연 안내 속보: 오늘 오후 운행 지연 안내",
                    clipped={"x": True, "y": False, "ellipsis": False, "animated": True})
        self.assertEqual([o for o in checks.check_semantics(ctx([ticker])) if o.check_id == "LY-01"], [])


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

    def test_worst_result_over_walks_and_element_mapping(self) -> None:
        stop = lambda covered, px: {"selector": "nav > button", "dom_id": None, "name": "", "indicator_px": px, "obscured_fraction": covered,  # noqa: E731
                                    "obscured_by": "#hdr" if covered else None, "in_viewport": True, "box": {"x": 10, "y": 10, "w": 44, "h": 44}}
        run = {"run_id": "R", "focus_walks": [{"phase": "end", "snapshot_id": "S-1", "stops": [stop(0.444, 300)]},
                                             {"phase": "load", "snapshot_id": "S-0", "stops": [stop(1.0, 0)]}]}
        snap = {"elements": [{"id": "el-7", "selector": 'button[aria-label="메뉴"]', "name": "메뉴", "box": {"x": 10, "y": 10, "w": 44, "h": 44}}]}
        obs = checks.check_focus_walks(run, {"profile_id": "P"}, {"S-0": snap, "S-1": snap})
        self.assertEqual([(o.check_id, o.severity, o.element_ids, o.element_key) for o in obs],
                         [("SM-06", "P2", ["el-7"], 'button[aria-label="메뉴"]|메뉴')])

    def test_runs_without_walks(self) -> None:
        self.assertEqual(checks.check_focus_walks({"run_id": "R"}, {"profile_id": "P"}), [])


if __name__ == "__main__":
    unittest.main()
