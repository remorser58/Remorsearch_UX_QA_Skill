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


class ClickedWithoutRole(unittest.TestCase):
    """SM-08: controls the task clicked that keyboard and screen-reader users cannot operate."""

    def run_check(self, elements, clicked):
        c = ctx(elements)
        c.clicked_element_ids = set(clicked)
        return checks.check_semantics(c)

    def test_div_chip_clicked_by_the_task(self) -> None:
        chip = el("chip", "generic", (10, 300, 90, 36), text="매운맛", tag="div", a11y=a11y("content", focusable=False))
        obs = [o for o in self.run_check([chip], ["chip"]) if o.check_id == "SM-08"]
        self.assertEqual([(o.element_key.split("|")[0], o.severity) for o in obs], [("#chip", "P1")])

    def test_from_the_driver_step_record(self) -> None:
        steps = [{"step_index": 3, "before": "S-2", "result": "ok", "action": {"action": "tap", "target": "#qform-mc1-o3"},
                  "target_control": {"tag": "div", "role": None, "dom_id": "qform-mc1-o3", "control": False, "contains_control": False,
                                     "ancestor_ids": ["qform-mc1", "qform-mc"], "text": "① 12"}},
                 {"step_index": 4, "before": "S-3", "result": "ok", "action": {"action": "tap", "target": "#ok"},
                  "target_control": {"tag": "span", "role": None, "dom_id": None, "control": True, "contains_control": False, "ancestor_ids": []}},
                 {"step_index": 5, "before": "S-4", "result": "ok", "action": {"action": "tap", "target": "#qform-mc1-o3"},
                  "target_control": {"tag": "div", "role": None, "dom_id": "qform-mc1-o3", "control": False, "contains_control": False,
                                     "ancestor_ids": ["qform-mc1", "qform-mc"], "text": "① 12"}}]
        obs = checks.check_clicked_controls({"run_id": "R", "steps": steps}, {"profile_id": "P"}, {})
        self.assertEqual([(o.check_id, o.element_key.split("|")[0], o.severity) for o in obs], [("SM-08", "#qform-mc1-o3", "P1")])
        self.assertIn("#qform-mc", obs[0].extra["context_selectors"])
        # With driver records present, the snapshot-based fallback stays silent.
        chip = el("chip", "generic", (10, 300, 90, 36), text="매운맛", tag="div", a11y=a11y("content", focusable=False))
        c = ctx([chip], run={"run_id": "R", "steps": steps})
        c.clicked_element_ids = {"chip"}
        self.assertEqual([o for o in checks.check_semantics(c) if o.check_id == "SM-08"], [])

    def test_focusable_native_label_or_card_with_a_link_pass(self) -> None:
        focusable = el("f", "generic", (10, 300, 90, 36), text="순한맛", tag="div", a11y=a11y("content", focusable=True))
        label = el("l", "generic", (10, 350, 90, 36), text="동의", tag="label", a11y=a11y("content", focusable=False))
        card = el("card", "generic", (10, 400, 340, 120), text="상품 카드", tag="div", a11y=a11y("content", focusable=False))
        link = el("more", "link", (20, 480, 100, 30), text="자세히", tag="a", interactive=True, a11y=a11y("content"))
        unclicked = el("u", "generic", (10, 600, 90, 36), text="안내", tag="div", a11y=a11y("content", focusable=False))
        obs = self.run_check([focusable, label, card, link, unclicked], ["f", "l", "card"])
        self.assertEqual([o for o in obs if o.check_id == "SM-08"], [])


class Reflow(unittest.TestCase):
    """RF-01: static re-render at 320 CSS px (WCAG 1.4.10)."""

    def run_doc(self, scroll_width, root_clips=False):
        off = {"selector": "#fee-summary", "dom_id": "fee-summary", "ancestor_ids": ["step3"], "tag": "div",
               "box": {"x": 8, "y": 400, "w": 400, "h": 60}, "text": "수수료 합계 3,000원"}
        return {"run_id": "R", "reflow": [{"snapshot_id": "S-3", "url": "http://x", "width": 320, "client_width": 320,
                                           "scroll_width": scroll_width, "root_clips": root_clips, "offenders": [off]},
                                          {"snapshot_id": "S-4", "url": "http://x", "width": 320, "error": "timeout"}]}

    def test_overflow_is_reported_once_with_its_container(self) -> None:
        obs = checks.check_reflow(self.run_doc(416), {"profile_id": "P"}, {})
        self.assertEqual([(o.check_id, o.element_key.split("|")[0], o.severity) for o in obs], [("RF-01", "#fee-summary", "P2")])
        self.assertEqual(obs[0].extra["context_selectors"], ["#step3"])
        self.assertEqual(obs[0].measurement["value"], 408)

    def test_no_overflow_no_finding_unless_the_root_clips(self) -> None:
        self.assertEqual(checks.check_reflow(self.run_doc(320), {"profile_id": "P"}, {}), [])
        clipped = checks.check_reflow(self.run_doc(320, root_clips=True), {"profile_id": "P"}, {})
        self.assertIn("잘려", clipped[0].message_ko)

    def test_text_lost_at_320_without_page_scroll(self) -> None:
        # A one-line bar with overflow:hidden: the timer fits at the device width and is
        # cut away at 320 px, with no sideways scroll to reach it (F102).
        timer = {"dom_id": "qbar-timer", "ancestor_ids": ["qbar", "view-quiz"], "tag": "p", "visible_full": 1.0,
                 "visible_320": 0.0, "box": {"x": 330, "y": 20, "w": 120, "h": 24}, "text": "남은 시간 09:41"}
        doc = {"run_id": "R", "reflow": [{"snapshot_id": "S-3", "width": 320, "client_width": 320, "scroll_width": 320,
                                          "root_clips": False, "offenders": [], "lost": [timer, dict(timer)]}]}
        snap = {"S-3": {"elements": [el("qbar-timer", "timer", (330, 20, 120, 24), text="남은 시간 09:41", dom_id="qbar-timer")]}}
        obs = checks.check_reflow(doc, {"profile_id": "P"}, snap)
        self.assertEqual([(o.check_id, o.element_key.split("|")[0], o.severity) for o in obs], [("RF-01", "#qbar-timer", "P2")])
        self.assertEqual(obs[0].measurement["name"], "visible_share_at_320")
        self.assertEqual(obs[0].extra["context_selectors"], ["#qbar", "#view-quiz"])
        self.assertEqual(obs[0].element_ids, ["qbar-timer"])


class FocusManagement(unittest.TestCase):
    """FM-02 and SM-06 at a step, from the snapshot's focus and layers."""

    def ctx_for(self, layers_before, layers_after, focus, elements=(), action="tap"):
        c = ctx(list(elements), previous={"snapshot_id": "S-0", "layers": layers_before, "elements": []},
                step={"action": {"action": action}})
        c.snapshot["focus"] = focus
        c.snapshot["layers"] = layers_after
        return c

    def test_new_layer_without_focus_is_reported(self) -> None:
        sheet = {"selector": "#addr-modal", "dom_id": "addr-modal", "kind": "sheet", "contains_focus": False}
        obs = checks.check_focus_management(self.ctx_for([], [sheet], {"on_body": False, "tag": "button", "dom_id": "btn-addr"}))
        self.assertEqual([(o.check_id, o.element_key.split("|")[0], o.severity) for o in obs], [("FM-02", "#addr-modal", "P2")])

    def test_focus_inside_old_layers_scrolls_and_old_recordings_pass(self) -> None:
        dlg = {"selector": "#dlg", "dom_id": "dlg", "kind": "modal", "contains_focus": True}
        stale = {"selector": "#menu", "dom_id": "menu", "kind": "sheet", "contains_focus": False}
        self.assertEqual(checks.check_focus_management(self.ctx_for([], [dlg], {"on_body": False, "dom_id": "code"})), [])
        self.assertEqual(checks.check_focus_management(self.ctx_for([stale], [stale], {"on_body": True})), [])
        self.assertEqual(checks.check_focus_management(self.ctx_for([], [stale], {"on_body": True}, action="scroll")), [])
        old = self.ctx_for([], [stale], {"on_body": True})
        old.snapshot.pop("focus")
        self.assertEqual(checks.check_focus_management(old), [])

    def test_focus_moved_under_a_fixed_header(self) -> None:
        name = el("applicant-name", "textbox", (16, 0, 328, 48), interactive=True, tag="input", dom_id="applicant-name",
                  occluded_fraction=1.0, occluded_by="#hdr", a11y=a11y("label"))
        obs = checks.check_focus_management(self.ctx_for([], [], {"on_body": False, "dom_id": "applicant-name"}, [name]))
        self.assertEqual([(o.check_id, o.measurement["phase"], o.severity) for o in obs], [("SM-06", "step", "P2")])


class ZeroSize(unittest.TestCase):
    """AUT-20: controls with no rendered box but still in the accessibility tree."""

    def test_name_rules_apply_with_capped_severity(self) -> None:
        link = el("empty", "link", (8, 8, 0, 0), interactive=True, tag="a", a11y=a11y("none", rendered=True), visible=False)
        span = el("sb", "button", (8, 8, 0, 0), interactive=True, tag="span", a11y=a11y("none", focusable=False, rendered=True), visible=False)
        field = el("tb", "textbox", (8, 26, 1904, 0), interactive=True, tag="div", a11y=a11y("none", focusable=False, rendered=True), visible=False)
        obs = checks.check_semantics(ctx([link, span, field], path_ids=("empty",)))
        got = {(o.check_id, o.element_key.split("|")[0]): o for o in obs}
        self.assertEqual(sorted(got), [("SM-01", "#empty"), ("SM-01", "#sb"), ("SM-03", "#tb")])
        self.assertEqual(got[("SM-01", "#empty")].severity, "P2")  # P1 on a path, capped: nobody sees it
        self.assertEqual(got[("SM-01", "#sb")].severity, "P3")  # not focusable either
        self.assertFalse(got[("SM-03", "#tb")].measurement["visible_to_sighted"])

    def test_hidden_or_named_zero_size_controls_pass(self) -> None:
        hidden = el("h", "link", (8, 8, 0, 0), interactive=True, tag="a", a11y=a11y("none", hidden=True, rendered=True), visible=False)
        gone = el("g", "button", (0, 0, 0, 0), interactive=True, tag="button", a11y=a11y("none", rendered=False), visible=False)  # display:none
        old = el("o", "button", (0, 0, 0, 0), interactive=True, tag="button", a11y=a11y("none"), visible=False)  # recorded before the field existed
        named = el("n", "checkbox", (8, 8, 0, 0), interactive=True, tag="input", name="동의", a11y=a11y("label", rendered=True), visible=False)
        no_href = el("a0", "link", (8, 8, 0, 0), interactive=True, tag="a", a11y=a11y("none", focusable=False, rendered=True), visible=False)
        self.assertEqual(checks.check_semantics(ctx([hidden, gone, old, named, no_href])), [])  # ACT c487ae inapplicable 6: <a />


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

    def test_text_cut_by_a_clipping_ancestor(self) -> None:
        price = el("sauce-2-price", "text", (200, 300, 60, 20), text="+500원",
                   clipped={"x": True, "y": False, "ellipsis": False, "by": "#sauce-2"})
        obs = [o for o in checks.check_semantics(ctx([price])) if o.check_id == "LY-01"]
        self.assertEqual(len(obs), 1)
        self.assertEqual(obs[0].measurement["clipped_by"], "#sauce-2")
        self.assertEqual(obs[0].extra["context_selectors"], ["#sauce-2"])
        self.assertIn("바깥 상자(#sauce-2)", obs[0].message_ko)

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

    def test_focus_probes_before_clicks_on_mid_task_screens(self) -> None:
        # The walks never saw the quiz footer; the probe before the click on it did.
        def probe(sel, px, visible=True, moved=False, covered=None):
            return {"snapshot_id": "S-7", "selector": sel, "dom_id": sel[1:], "name": "", "focus_visible": visible, "moved": moved,
                    "indicator_px": px, "indicator_any_px": px, "in_viewport": True, "box": {"x": 0, "y": 0, "w": 90, "h": 48},
                    "obscured_fraction": covered}
        steps = [{"step_index": 3, "focus_probe": probe("#submit", 0)}, {"step_index": 4, "focus_probe": probe("#save", 0, visible=False)},
                 {"step_index": 5, "focus_probe": probe("#next", 0, moved=True)}, {"step_index": 6, "focus_probe": probe("#ok", 320, covered=1.0)},
                 {"step_index": 7, "focus_probe": {"skipped": "field_focused"}}, {"step_index": 8}]
        run = {"run_id": "R", "steps": steps, "focus_walks": [{"phase": "load", "snapshot_id": "S-0", "stops": []}]}
        obs = checks.check_focus_walks(run, {"profile_id": "P"})
        self.assertEqual([(o.check_id, o.element_key.split("|")[0], o.snapshot_id) for o in obs], [("SM-05", "#submit", "S-7")])
        self.assertEqual((obs[0].measurement["phase"], obs[0].measurement["step_index"]), ("step", 3))
        self.assertIn("3단계", obs[0].message_ko)

    def test_indicator_drawn_elsewhere_in_the_viewport_passes(self) -> None:
        # ACT oj04fd: nothing changes near the element, but a distant marker does (AUT-09).
        run = {"run_id": "R", "focus_walks": [{"phase": "load", "snapshot_id": "S-0", "stops": [
            {"selector": "#far", "name": "", "indicator_px": 0, "indicator_any_px": 87, "obscured_fraction": 0, "in_viewport": True, "box": {"x": 0, "y": 0, "w": 90, "h": 40}},
            {"selector": "#none", "name": "", "indicator_px": 0, "indicator_any_px": 2, "obscured_fraction": 0, "in_viewport": True, "box": {"x": 0, "y": 50, "w": 90, "h": 40}}]}]}
        obs = checks.check_focus_walks(run, {"profile_id": "P"})
        self.assertEqual([(o.check_id, o.element_key.split("|")[0]) for o in obs], [("SM-05", "#none")])
        self.assertEqual(obs[0].measurement["viewport_px"], 2)

    def test_user_opened_layer_is_exempt_only_when_escape_reveals(self) -> None:
        def stop(sel, reveals, phase_user=True):
            return {"selector": sel, "name": "", "indicator_px": 400, "obscured_fraction": 1.0, "obscured_by": "#menu",
                    "obscured_user_opened": phase_user, "escape_reveals": reveals, "in_viewport": True, "box": {"x": 0, "y": 0, "w": 90, "h": 40}}
        run = {"run_id": "R", "focus_walks": [{"phase": "end", "snapshot_id": "S-1", "stops": [stop("#menu-under", True), stop("#chat-under", False),
                                                                                               stop("#banner-under", None, False)]}]}
        obs = {o.element_key.split("|")[0]: o for o in checks.check_focus_walks(run, {"profile_id": "P"})}
        self.assertNotIn("#menu-under", obs)
        self.assertEqual(obs["#chat-under"].severity, "P2")
        self.assertIn("사용자가 연", obs["#chat-under"].message_ko)
        self.assertEqual(obs["#banner-under"].severity, "P2")  # author content (a cookie banner): the note does not apply

    def test_escape_does_not_exempt_on_the_initial_screen(self) -> None:
        # On a fresh load nothing is user-opened, whatever the driver inferred.
        stop = {"selector": "#x", "name": "", "indicator_px": 400, "obscured_fraction": 1.0, "obscured_by": "#menu",
                "obscured_user_opened": True, "escape_reveals": True, "in_viewport": True, "box": {"x": 0, "y": 0, "w": 90, "h": 40}}
        obs = checks.check_focus_walks({"run_id": "R", "focus_walks": [{"phase": "load", "snapshot_id": "S-0", "stops": [stop]}]}, {"profile_id": "P"})
        self.assertEqual([(o.check_id, o.severity) for o in obs], [("SM-06", "P2")])

    def test_partly_obscured_is_a_hypothesis(self) -> None:
        obs = [o for o in checks.check_focus_walks(self.run_doc(), {"profile_id": "P"}) if o.check_id == "SM-06"]
        tiers = {o.element_key.split("|")[0]: checks.tier("SM-06", o.measurement) for o in obs}
        self.assertEqual(tiers, {"#half": "hypothesis", "#under": "finding"})


if __name__ == "__main__":
    unittest.main()
