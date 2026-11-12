"""Synthetic native-run parser regressions, not actual browser or user evidence.

The fake invoker writes deliberately authored native documents and a two-pixel
PNG solely to exercise admission/audit. No browser, package, account or network
is launched. Real browser validation belongs to the separate CLI diagnostic.
"""
import copy
import importlib.util
import json
from contextlib import contextmanager
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/remorsearch-ux-qa"))
from ergoqa.png import encode, new_image
from uxpersonas import browser_run, local_run, workspace
from uxresearch.canonical import EngineError, byte_digest, canonical
from uxresearch.storage import atomic

_spec = importlib.util.spec_from_file_location(
    "browser_admission_fixture", ROOT / "skills/remorsearch-ux-qa/examples/journey/browser_fixture.py")
fixture = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fixture)


class BrowserJourneyAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.case_number = 0
        self.new_case()

    def new_case(self):
        self.case_number += 1
        self.__dict__.update(fixture.build(self.root / ("case-" + str(self.case_number))))
        self.calls = []
        self.mutate = lambda native, snapshots: None
        self.response_mutate = lambda response: None
        self.omit = set()
        self.problem = None
        self.cleanup = True
        self.partial = False

    def prepare_workspace(self):
        if not (self.work / "workspace.json").exists():
            workspace.prepare(self.source, self.work, reviewed_files=fixture.FILES)

    def save_adapter(self):
        atomic(self.source / "browser-adapter.json", canonical(self.adapter))

    @staticmethod
    def fake_prepare(work, prepared, plan, personas, build_hash):
        browser = browser_run.manifest(prepared, plan)
        browser["runtime"] = {"fixture_only": True}
        return browser

    @contextmanager
    def mocked(self):
        self.prepare_workspace()
        with patch.object(browser_run, "prepare", side_effect=self.fake_prepare), \
                patch.object(browser_run, "verify_runtime") as verify, \
                patch.object(browser_run, "invoke", side_effect=self.fake_invoke) as invoke:
            yield verify, invoke

    def execute(self, **kw):
        return local_run.execute(self.work, library_path=self.library,
                                 input_path=self.plan_path, approved=True, **kw)

    def fake_invoke(self, browser, cwd, request, seconds, on_spawn):
        """Produce bound, explicitly synthetic parser inputs; never a screenshot claim."""
        on_spawn()
        self.calls.append(copy.deepcopy(request))
        base = Path(request["output"])
        base.mkdir(mode=0o700)
        binding, scenario = request["binding"], request["scenario"]
        run_id = "R-" + binding["operation_id"]
        png = encode(new_image(2, 2))
        snapshots, docs, steps = [], {}, []
        observed_actions = 2 if self.partial else len(scenario["steps"])
        for i in range(observed_actions + 1):
            sid, json_name, png_name = "S-" + str(i), "snapshot-" + str(i) + ".json", "capture-" + str(i) + ".png"
            snapshots.append(dict(snapshot_id=sid, step_index=i, path=json_name, png=png_name))
            docs[json_name] = dict(schema_version="ergo-snapshot.v1", snapshot_id=sid,
                run_id=run_id, step_index=i, surface=copy.deepcopy(scenario["surface"]),
                screenshot=dict(path=png_name, sha256=byte_digest(png)),
                elements=[dict(id="E-note", visible=True, in_viewport=True,
                               occluded_fraction=0, visible_geometry="measured",
                               visible_box=dict(x=0, y=0, w=1, h=1)),
                          dict(id="E-saved", visible=True, in_viewport=True,
                               occluded_fraction=0, visible_geometry="measured",
                               visible_box=dict(x=1, y=1, w=1, h=1))])
            if i:
                action = copy.deepcopy(scenario["steps"][i - 1])
                redacted_source = any(c.get("redact") and c.get("from_step") == i
                                      for c in scenario["success"]["task_checks"])
                if action.get("redact") or redacted_source:
                    private = action.get("text", "")
                    action["text"] = "[redacted]"
                    for field in ("note", "intent", "description", "expected"):
                        if private and field in action:
                            action[field] = action[field].replace(private, "[redacted]")
                steps.append(dict(step_index=i, action=action, result="ok",
                                  before="S-" + str(i - 1), after=sid))
        if self.partial:
            steps.append(dict(step_index=3, action=copy.deepcopy(scenario["steps"][2]),
                              result="error", before="S-2", after=None))
        measured = []
        for check in scenario["success"]["task_checks"]:
            checkpoint = check["after_step"]
            result = ("unevaluable" if checkpoint > observed_actions else
                      "fail" if binding["task_id"] == "T-RETURN" and checkpoint == 2 else "pass")
            consequence = check["consequence"]
            if check.get("redact") and "from_step" in check:
                consequence = consequence.replace(scenario["steps"][check["from_step"] - 1]["text"], "[redacted]")
            measured.append(dict(kind="task_check", id=check["id"], selector=check["selector"],
                property=check["property"], checkpoint=checkpoint, severity=check["severity"],
                consequence=consequence, result=result, passed={"pass": True, "fail": False, "unevaluable": None}[result],
                step_index=checkpoint if result != "unevaluable" else None,
                snapshot_id="S-" + str(checkpoint) if result != "unevaluable" else None,
                element_id="E-note" if checkpoint == 2 else "E-saved"))
        native = dict(schema_version="ergo-run.v1", run_id=run_id, scenario_id=scenario["scenario_id"],
            profile_id=binding["persona_id"], surface=copy.deepcopy(scenario["surface"]),
            mode="scripted", driver=dict(name="playwright-web", version="1.56.1", browser_connected=False),
            success_basis="measured", status="failed" if self.partial else "completed",
            success=all(item["passed"] is True for item in measured),
            steps=steps, snapshots=snapshots, success_detail=dict(criteria=measured))
        self.mutate(native, docs)
        for name, doc in docs.items():
            if name not in self.omit:
                atomic(base / name, canonical(doc))
            png_name = doc["screenshot"]["path"]
            if png_name not in self.omit:
                atomic(base / png_name, png)
        native_raw = canonical(native)
        if "run.json" not in self.omit:
            atomic(base / "run.json", native_raw)
        response = dict(schema_version="ux-journey-browser-result.v1", binding=binding,
                        problem=self.problem, cleanup_confirmed=self.cleanup,
                        run=dict(path="run.json", sha256=byte_digest(native_raw)))
        self.response_mutate(response)
        raw = canonical(response)
        diagnostic = dict(problem=self.problem, cleanup_confirmed=self.cleanup, returncode=0,
                          elapsed_seconds=0.01, stdout_bytes=len(raw), stderr_bytes=0,
                          stdout_sha256=byte_digest(raw), stderr_sha256=byte_digest(b""))
        return response, diagnostic

    def test_synthetic_native_documents_enter_existing_receipt_and_audit(self):
        baseline = {p.name: p.read_bytes() for p in self.library.iterdir()}
        with self.mocked():
            result = self.execute()
        self.assertEqual(result["counts"]["failed"], 1)
        self.assertEqual(result["counts"]["passed"], 1)
        self.assertEqual(result["evidence_audit"]["integrity"], "consistent")
        self.assertTrue(result["ui_observed"])  # Parser field only; see module evidence disclaimer.
        self.assertFalse(result["real_user_evidence"])
        self.assertFalse(result["product_ready"])
        self.assertEqual(len(self.calls), 2)
        self.assertTrue(all(row["attempts"] == 1 for row in result["tasks"]))
        self.assertEqual(baseline, {p.name: p.read_bytes() for p in self.library.iterdir()})
        for row in result["tasks"]:
            self.assertEqual({a["kind"] for a in row["result"]["artifacts"]}, {"execution_log", "screenshot"})

    def test_completed_readback_neither_invokes_nor_rechecks_runtime(self):
        with self.mocked():
            first = self.execute()
        before = {str(p.relative_to(self.work)): (p.read_bytes(), p.stat().st_mtime_ns)
                  for p in self.work.rglob("*") if p.is_file()}
        with patch.object(browser_run, "prepare", side_effect=AssertionError("reprepare")), \
                patch.object(browser_run, "verify_runtime", side_effect=AssertionError("runtime reread")), \
                patch.object(browser_run, "invoke", side_effect=AssertionError("redispatch")):
            self.assertEqual(first, local_run.execute(self.work))
            self.assertEqual(first, workspace.status(self.work))
        self.assertEqual(before, {str(p.relative_to(self.work)): (p.read_bytes(), p.stat().st_mtime_ns)
                                  for p in self.work.rglob("*") if p.is_file()})

    def test_timeout_tail_preserves_earlier_failure_and_unvisited_recovery(self):
        self.partial, self.problem = True, "timeout"
        with self.mocked():
            result = self.execute()
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(result["counts"]["failed"], 1)
        self.assertEqual(result["counts"]["pending"], 1)
        row = result["tasks"][0]
        criteria = {(c["kind"], c["index"]): c for c in row["result"]["criteria"]}
        self.assertEqual(criteria[("success", 0)]["status"], "failed")
        self.assertEqual(criteria[("recovery", 0)]["status"], "not_run")
        self.assertEqual(criteria[("recovery", 0)]["evidence_ids"], [])
        self.assertIn("uncertain", row["result"]["steps"][-1]["observation"])
        self.assertEqual(result["evidence_audit"]["integrity"], "consistent")

    def test_uncertain_browser_cleanup_fences_all_later_dispatch_and_retry(self):
        self.cleanup, self.problem = False, "timeout"
        with self.mocked():
            with self.assertRaises(EngineError) as caught:
                self.execute()
        self.assertEqual(caught.exception.issue["code"], "execution_cleanup")
        self.assertEqual(len(self.calls), 1)
        with patch.object(browser_run, "invoke", side_effect=AssertionError("unknown attempt repeated")), \
                patch.object(browser_run, "verify_runtime", side_effect=AssertionError("later task dispatched")):
            result = local_run.execute(self.work)
        self.assertEqual(result["uncertain_dispatches"], ["T-RETURN"])
        self.assertEqual(result["tasks"][0]["attempts"], 1)
        self.assertEqual(result["tasks"][1]["attempts"], 0)
        self.assertIsNone(result["tasks"][0]["result"])
        self.assertEqual(result["counts"]["passed"], 0)

    def test_missing_native_run_snapshot_or_png_is_not_admitted(self):
        for name in ("run.json", "snapshot-2.json", "capture-2.png"):
            with self.subTest(name=name):
                self.new_case()
                self.omit = {name}
                with self.mocked():
                    result = self.execute()
                self.assertEqual(result["counts"]["passed"], 0)
                self.assertEqual(result["counts"]["inconclusive"], 1)
                self.assertEqual(result["tasks"][0]["result"]["steps"], [])
                self.assertIn("invalid_browser_evidence", result["tasks"][0]["reason"])

    def test_foreign_native_identifiers_rejected_even_with_matching_wrapper_hash(self):
        changes = [
            ("run", lambda n, d: n.update(run_id="R-foreign")),
            ("persona", lambda n, d: n.update(profile_id="PER-foreign")),
            ("build", lambda n, d: n["surface"].update(build_id="b" * 64)),
            ("scenario", lambda n, d: n.update(scenario_id="SC-foreign")),
            ("capture-run", lambda n, d: d["snapshot-2.json"].update(run_id="R-foreign")),
            ("capture-build", lambda n, d: d["snapshot-2.json"]["surface"].update(build_id="b" * 64)),
            ("capture-url", lambda n, d: d["snapshot-2.json"]["surface"].update(url="https://foreign.invalid/other.html")),
            ("capture-step", lambda n, d: d["snapshot-2.json"].update(step_index=4)),
            ("action-before", lambda n, d: n["steps"][2].update(before="S-foreign")),
        ]
        for name, mutation in changes:
            with self.subTest(name=name):
                self.new_case()
                self.mutate = mutation
                with self.mocked():
                    result = self.execute()
                self.assertEqual(result["counts"]["passed"], 0)
                self.assertEqual(result["counts"]["inconclusive"], 1)
                self.assertIn("invalid_browser_evidence", result["tasks"][0]["reason"])

    @staticmethod
    def insert_native_pre_action_capture(native, docs, reason, action_index):
        # WebSession.act snapshots at the SAME step index before acting when
        # scrolling or a newly appeared target changes the visible page. The
        # reason is stored in snapshot JSON, not the run.snapshots index.
        sid = "S-pre-" + str(action_index)
        json_name, png_name = sid + ".json", sid + ".png"
        doc = copy.deepcopy(docs["snapshot-" + str(action_index - 1) + ".json"])
        doc.update(snapshot_id=sid, step_index=action_index, notes=[reason])
        doc["screenshot"]["path"] = png_name
        docs[json_name] = doc
        native["snapshots"].insert(action_index, dict(
            snapshot_id=sid, step_index=action_index, path=json_name, png=png_name))
        step = native["steps"][action_index - 1]
        step["before"] = sid
        if reason == "pre_action_auto_scroll":
            step["auto_scrolled"] = True

    def test_driver_pre_action_capture_supports_scroll_and_late_target(self):
        for reason in ("pre_action_auto_scroll", "pre_action_target_appeared"):
            for action_index in (1, 3):
                with self.subTest(reason=reason, action_index=action_index):
                    self.new_case()
                    self.mutate = lambda native, docs: self.insert_native_pre_action_capture(
                        native, docs, reason, action_index)
                    with self.mocked():
                        result = self.execute()
                    self.assertEqual(result["counts"]["failed"], 1)
                    self.assertEqual(result["counts"]["passed"], 1)
                    self.assertEqual(result["evidence_audit"]["integrity"], "consistent")

    def test_unmarked_same_step_capture_cannot_replace_pre_action_evidence(self):
        self.mutate = lambda native, docs: self.insert_native_pre_action_capture(
            native, docs, "after_action", 3)
        with self.mocked():
            result = self.execute()
        self.assertEqual(result["counts"]["passed"], 0)
        self.assertEqual(result["counts"]["inconclusive"], 1)
        self.assertIn("invalid_browser_evidence", result["tasks"][0]["reason"])

    def test_response_persona_binding_cannot_borrow_a_valid_run(self):
        self.response_mutate = lambda r: r.update(binding={**r["binding"], "persona_id": "PER-foreign"})
        with self.mocked():
            result = self.execute()
        self.assertEqual(result["counts"]["passed"], 0)
        self.assertIn("invalid_browser_evidence", result["tasks"][0]["reason"])

    def test_check_induced_redaction_and_matching_metadata_are_admitted(self):
        for journey in self.adapter["journeys"]:
            check = journey["scenario"]["success"]["task_checks"][0]
            check["redact"] = True
            check["consequence"] = "Retain Owned draft after rejection."
            journey["scenario"]["steps"][0]["note"] = "Use Owned draft for this owned check."
        self.save_adapter()
        with self.mocked():
            result = self.execute()
        self.assertEqual(result["counts"]["failed"], 1)
        self.assertEqual(result["counts"]["passed"], 1)
        self.assertEqual(result["evidence_audit"]["integrity"], "consistent")

    def test_unseen_or_unsupported_geometry_never_turns_dom_match_into_pass(self):
        changes = [
            ("offscreen", {"in_viewport": False}),
            ("occluded", {"occluded_fraction": 0.5}),
            ("unsupported", {"visible_geometry": "unsupported"}),
            ("clipped-empty", {"visible_box": {"x": 0, "y": 0, "w": 0, "h": 1}}),
        ]
        for name, change in changes:
            with self.subTest(name=name):
                self.new_case()
                def mutation(native, docs):
                    for doc in docs.values():
                        for element in doc["elements"]:
                            element.update(change)
                self.mutate = mutation
                with self.mocked():
                    result = self.execute()
                self.assertEqual(result["counts"]["passed"], 0)
                self.assertEqual(result["counts"]["failed"], 0)
                self.assertEqual(result["counts"]["inconclusive"], 2)
                self.assertTrue(all(c["status"] == "not_run" and not c["evidence_ids"]
                                    for row in result["tasks"] for c in row["result"]["criteria"]))

    def test_missing_or_duplicate_criterion_mapping_fails_before_claim(self):
        mutations = [
            lambda a: a["journeys"][0]["criteria"].pop(),
            lambda a: a["journeys"][0]["criteria"][1].update(check_id="draft-after-error"),
            lambda a: a["journeys"][0]["criteria"][1].update(kind="success", index=0),
        ]
        for i, mutation in enumerate(mutations):
            with self.subTest(case=i):
                self.new_case()
                mutation(self.adapter)
                self.save_adapter()
                with self.mocked() as (_, invoke):
                    with self.assertRaises(EngineError) as caught:
                        self.execute()
                    invoke.assert_not_called()
                self.assertEqual(caught.exception.issue["code"], "browser_mapping")
                self.assertFalse((self.work / local_run.MARKER).exists())

    def test_runtime_change_stops_before_any_attempt_is_spent(self):
        with self.mocked() as (verify, invoke):
            verify.side_effect = EngineError("browser_runtime_changed", "Changed synthetic runtime.")
            with self.assertRaises(EngineError):
                self.execute()
            invoke.assert_not_called()
        report = workspace.status(self.work)
        self.assertTrue(all(row["attempts"] == 0 for row in report["tasks"]))
        self.assertFalse(report["execution_performed"])

    def test_runtime_change_before_next_task_preserves_first_result_and_pending_budget(self):
        with self.mocked() as (verify, invoke):
            verify.side_effect = [None, None, EngineError("browser_runtime_changed", "Changed synthetic runtime.")]
            with self.assertRaises(EngineError):
                self.execute()
            self.assertEqual(invoke.call_count, 1)
        result = workspace.status(self.work)
        self.assertEqual(result["tasks"][0]["status"], "failed")
        self.assertEqual(result["tasks"][0]["attempts"], 1)
        self.assertEqual(result["tasks"][1]["status"], "pending")
        self.assertEqual(result["tasks"][1]["attempts"], 0)

    def configure_owned_upload_documents(self, mutation=None, *, redact=False):
        """Extend the fake parser documents only, never execute or claim an upload."""
        payload = b"PK synthetic admission fixture"
        atomic(self.source / "owned-input.zip", payload)
        atomic(self.source / "owned-worker.js", b"onmessage = () => postMessage('synthetic');")
        name = "sensitive-synthetic.zip" if redact else "owned-input.zip"
        self.adapter["uploads"] = [dict(id="owned-previous", path="owned-input.zip",
                                       name=name, mime_type="application/zip")]
        self.adapter["workers"] = ["owned-worker.js"]
        for journey in self.adapter["journeys"]:
            journey["scenario"]["steps"][1] = dict(action="upload", target="#choose", input="#archive",
                                                  files=["owned-previous"], timeout_ms=100)
            if redact:
                journey["scenario"]["steps"][0]["text"] = name
                journey["scenario"]["success"]["task_checks"][0]["redact"] = True
        self.save_adapter()
        workspace.prepare(self.source, self.work,
                          reviewed_files=fixture.FILES + ["owned-input.zip", "owned-worker.js"])

        def authored_metadata(native, docs):
            request = self.calls[-1]
            entry = request["uploads"][0]
            native["owned_execution"] = dict(
                uploads=[{key: entry[key] for key in ("id", "mime_type", "size_bytes", "sha256")}],
                workers=copy.deepcopy(request["workers"]),
                network_isolation=dict(policy=browser_run.WORKER_POLICY,
                    profile_sha256=byte_digest(browser_run.NETWORK_PROFILE.encode()), bind_denied=True))
            native["steps"][1]["file_selection"] = dict(method="playwright_filechooser", input="#archive", files=[
                dict(id=entry["id"], name="[redacted]" if redact else entry["name"],
                     mime_type=entry["mime_type"], size_bytes=entry["size_bytes"], sha256=entry["sha256"])])
            if mutation:
                mutation(native, docs)
        self.mutate = authored_metadata

    def assert_upload_evidence_rejected(self):
        with self.mocked():
            result = self.execute()
        self.assertEqual(result["counts"]["passed"], 0)
        self.assertEqual(result["counts"]["inconclusive"], 1)
        self.assertEqual(result["tasks"][0]["result"]["steps"], [])
        self.assertIn("invalid_browser_evidence", result["tasks"][0]["reason"])
        self.assertEqual(len(self.calls), 1)

    def test_owned_upload_metadata_enters_receipt_and_completed_readback_without_dispatch(self):
        self.configure_owned_upload_documents()
        with self.mocked():
            first = self.execute()
        self.assertEqual(first["counts"]["failed"], 1)
        self.assertEqual(first["counts"]["passed"], 1)
        self.assertEqual(first["evidence_audit"]["integrity"], "consistent")
        self.assertTrue(all(row["attempts"] == 1 for row in first["tasks"]))
        self.assertFalse(first["real_user_evidence"])
        with patch.object(browser_run, "invoke", side_effect=AssertionError("redispatch")), \
                patch.object(browser_run, "verify_runtime", side_effect=AssertionError("runtime reread")):
            self.assertEqual(first, local_run.execute(self.work))
            self.assertEqual(first, workspace.status(self.work))

    def test_owned_upload_selection_requires_exact_id_name_mime_size_hash_and_input(self):
        changes = [
            ("missing-selection", lambda n, d: n["steps"][1].pop("file_selection")),
            ("method", lambda n, d: n["steps"][1]["file_selection"].update(method="direct-state-write")),
            ("input", lambda n, d: n["steps"][1]["file_selection"].update(input="#foreign")),
            ("missing-hash", lambda n, d: n["steps"][1]["file_selection"]["files"][0].pop("sha256")),
            ("hash", lambda n, d: n["steps"][1]["file_selection"]["files"][0].update(sha256="f" * 64)),
            ("size", lambda n, d: n["steps"][1]["file_selection"]["files"][0].update(size_bytes=1)),
            ("id", lambda n, d: n["steps"][1]["file_selection"]["files"][0].update(id="foreign")),
            ("name", lambda n, d: n["steps"][1]["file_selection"]["files"][0].update(name="foreign.zip")),
            ("mime", lambda n, d: n["steps"][1]["file_selection"]["files"][0].update(mime_type="text/plain")),
            ("extra-file", lambda n, d: n["steps"][1]["file_selection"]["files"].append(
                copy.deepcopy(n["steps"][1]["file_selection"]["files"][0]))),
            ("raw-buffer", lambda n, d: n["steps"][1]["file_selection"]["files"][0].update(buffer="not-evidence")),
        ]
        for label, mutation in changes:
            with self.subTest(change=label):
                self.new_case()
                self.configure_owned_upload_documents(mutation)
                # fake_invoke rehashes the altered native run: a matching wrapper
                # digest must not replace semantic binding to the authored input.
                self.assert_upload_evidence_rejected()

    def test_owned_execution_scope_requires_minimal_uploads_exact_workers_and_policy(self):
        changes = [
            ("missing", lambda n, d: n.pop("owned_execution")),
            ("upload-id", lambda n, d: n["owned_execution"]["uploads"][0].update(id="foreign")),
            ("upload-hash", lambda n, d: n["owned_execution"]["uploads"][0].update(sha256="f" * 64)),
            ("upload-size", lambda n, d: n["owned_execution"]["uploads"][0].update(size_bytes=1)),
            ("filename-leak", lambda n, d: n["owned_execution"]["uploads"][0].update(name="sensitive-synthetic.zip")),
            ("path-leak", lambda n, d: n["owned_execution"]["uploads"][0].update(path="owned-input.zip")),
            ("worker-hash", lambda n, d: n["owned_execution"]["workers"].update({"owned-worker.js": "f" * 64})),
            ("foreign-worker", lambda n, d: n["owned_execution"]["workers"].update({"foreign.js": "f" * 64})),
            ("policy", lambda n, d: n["owned_execution"]["network_isolation"].update(policy="allow-network")),
            ("profile", lambda n, d: n["owned_execution"]["network_isolation"].update(profile_sha256="f" * 64)),
            ("probe", lambda n, d: n["owned_execution"]["network_isolation"].update(bind_denied=False)),
        ]
        for label, mutation in changes:
            with self.subTest(change=label):
                self.new_case()
                self.configure_owned_upload_documents(mutation)
                self.assert_upload_evidence_rejected()

    def test_undeclared_owned_execution_and_upload_on_a_different_action_are_refused(self):
        self.mutate = lambda n, d: n.update(owned_execution=dict(
            uploads=[dict(id="foreign", mime_type="application/zip", size_bytes=1, sha256="f" * 64)],
            workers={}, network_isolation=None))
        self.assert_upload_evidence_rejected()
        self.new_case()
        self.configure_owned_upload_documents(lambda n, d: n["steps"][0].update(
            file_selection=copy.deepcopy(n["steps"][1]["file_selection"])))
        self.assert_upload_evidence_rejected()

    def test_redacted_upload_filename_never_reappears_in_native_owned_execution(self):
        self.configure_owned_upload_documents(redact=True)
        with self.mocked():
            result = self.execute()
        self.assertEqual(result["counts"]["failed"], 1)
        self.assertEqual(result["counts"]["passed"], 1)
        self.assertEqual(result["evidence_audit"]["integrity"], "consistent")
        for request in self.calls:
            raw = (Path(request["output"]) / "run.json").read_bytes()
            native = json.loads(raw)
            self.assertNotIn(b"sensitive-synthetic.zip", raw)
            self.assertEqual(native["steps"][1]["file_selection"]["files"][0]["name"], "[redacted]")
            self.assertEqual(set(native["owned_execution"]["uploads"][0]),
                             {"id", "mime_type", "size_bytes", "sha256"})

    def test_readback_rejects_upload_mutation_even_after_wrapper_and_artifact_rehash(self):
        self.configure_owned_upload_documents()
        with self.mocked():
            result = self.execute()
        state = local_run._read(self.work)
        row = next(row for row in result["tasks"] if row["status"] == "passed")
        claim = state["dispatches"][row["task_id"]]["claim"]
        receipt = copy.deepcopy(dict(row["result"], outcome=row["status"], reason=row["reason"]))
        root = self.work / local_run.DIRECTORY / "run"
        run_artifact = next(a for a in receipt["artifacts"] if a["id"] == "browser-run")
        native = json.loads((root / run_artifact["path"]).read_bytes())
        native["steps"][1]["file_selection"]["files"][0]["sha256"] = "f" * 64
        raw = canonical(native)
        atomic(root / run_artifact["path"], raw)
        run_artifact["sha256"] = byte_digest(raw)
        log_artifact = next(a for a in receipt["artifacts"] if a["id"] == "execution")
        log = json.loads((root / log_artifact["path"]).read_bytes())
        log["browser_response"]["run"]["sha256"] = run_artifact["sha256"]
        response = canonical(log["browser_response"])
        log["diagnostic"].update(stdout_sha256=byte_digest(response), stdout_bytes=len(response))
        raw = canonical(log)
        atomic(root / log_artifact["path"], raw)
        log_artifact["sha256"] = byte_digest(raw)
        with patch.object(browser_run, "invoke", side_effect=AssertionError("redispatch")):
            with self.assertRaisesRegex(ValueError, "browser_upload_binding"):
                browser_run.audit(self.work, state, claim, receipt)

    def test_owned_activity_rejects_foreign_worker_and_changed_served_bytes(self):
        forged = [
            dict(served_files=[], started_workers=[dict(path="foreign.js", sha256=None, count=1)]),
            dict(served_files=[dict(path="index.html", sha256="f" * 64, count=1)], started_workers=[]),
        ]
        for activity in forged:
            with self.subTest(activity=activity):
                self.new_case()
                self.configure_owned_upload_documents(lambda native, docs: native.update(
                    owned_browser_activity=copy.deepcopy(activity)))
                self.assert_upload_evidence_rejected()


if __name__ == "__main__":
    unittest.main()
