"""Prepare, execute once, or read back the frozen copied-Peekly UI pilot.

Preparation reuses the existing Library/workspace/swarm APIs and opens no browser.
Only the explicit run mode calls local_run.execute; readback cannot redispatch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SKILL = REPO / "skills/remorsearch-ux-qa"
sys.path.insert(0, str(SKILL))
from uxpersonas import browser_run, local_run, swarm, workspace
from uxresearch.canonical import canonical, digest as value_digest

BENCHMARK_FILES = ("protocol.json", "generate-fixtures.mjs", "run_pilot.py", "README.md")
ADAPTER_NAME = "browser-adapter-v2.json"
PLAN_NAME = "reviewed-plan-v2.json"
CRITERION_MAP_NAME = "criterion-map-v2.json"


def file_digest(path):
    hasher = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def read_json(path):
    path = Path(path)
    if path.is_symlink() or path.resolve(strict=True) != path or not path.is_file():
        raise ValueError("Only canonical regular evidence files are accepted")
    return json.loads(path.read_text())


def write_bytes(path, raw):
    path = Path(path)
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        info = path.lstat()
        if (not stat.S_ISREG(info.st_mode) or info.st_nlink != 1
                or path.resolve(strict=True) != path or path.read_bytes() != raw):
            raise ValueError("Existing file differs or is unsafe; never overwrite: " + str(path))
        return
    with path.open("xb") as handle:
        handle.write(raw)
    os.chmod(path, 0o600)


def write_json(path, value):
    write_bytes(path, canonical(value))


def library_id(identity):
    return "PER-" + identity.removeprefix("P-")


def mapped_profiles(protocol):
    """Reuse the old pilot mapping: PER- prefix and assigned requirement union."""
    result = []
    for persona in protocol["personas"]:
        requirements = list(persona["requirement_ids"])
        for task in protocol["tasks"]:
            if task["persona_id"] == persona["persona_id"]:
                for rid in task["requirement_ids"]:
                    if rid not in requirements:
                        requirements.append(rid)
        result.append({**persona, "persona_id": library_id(persona["persona_id"]),
                       "requirement_ids": requirements})
    return result


class Journey:
    def __init__(self, protocol_task):
        self.original = protocol_task
        self.steps, self.checks, self.refs, self.map = [], [], [], []
        self.criteria = {"success": [], "recovery": []}
        self.requirement_refs = {rid: [] for rid in protocol_task["requirement_ids"]}

    def click(self, target):
        self.steps.append(dict(action="click", target=target, settle_ms=500))

    def upload(self, identities, selectors):
        self.steps.append(dict(action="upload", target=selectors["file_button"],
                               input=".sheet-body input", files=identities, timeout_ms=5000, settle_ms=1000))

    def wait(self):
        self.steps.append(dict(action="wait", ms=1000))

    def check(self, kind, original_index, identity, selector, expected, description, requirements):
        index = len(self.criteria[kind])
        self.criteria[kind].append(description)
        self.checks.append(dict(id=identity, selector=selector, property="text",
                                expected=expected, normalize_whitespace=True,
                                after_step=len(self.steps), severity="P1",
                                consequence=description))
        ref = dict(kind=kind, index=index)
        self.refs.append(dict(ref, check_id=identity))
        self.map.append(dict(ref, check_id=identity,
                             protocol_criterion=dict(kind=kind, index=original_index),
                             after_step=len(self.steps)))
        for rid in requirements:
            if rid in self.requirement_refs:
                self.requirement_refs[rid].append(ref)

    def counts(self, kind, original_index, prefix, followers, following, selectors, requirements):
        self.check(kind, original_index, prefix + "-followers", selectors["followers_count"],
                   f"팔로워 {followers}명", f"{prefix}: 결과의 팔로워 수가 {followers}명으로 표시된다", requirements)
        self.check(kind, original_index, prefix + "-following", selectors["following_count"],
                   f"팔로잉 {following}명", f"{prefix}: 결과의 팔로잉 수가 {following}명으로 표시된다", requirements)

    def finish(self):
        task = self.original
        for kind in ("success", "recovery"):
            used = {item["protocol_criterion"]["index"] for item in self.map if item["kind"] == kind}
            if used != set(range(len(task[kind + "_criteria"]))):
                raise ValueError("A composite protocol criterion has no measured refinement")
        exclusions = {
            "R-SAMPLE": "Human discoverability, comprehension and individual handle identity are outside these automatic text checks.",
            "R-COMPARE": "Individual row/name identity requires separate PNG review; no inferred cause, human comprehension or full comparison-domain acceptance is claimed.",
            "R-IMPORT": "The fixed missing-following and valid synthetic cases do not cover other accounts, every malformed format or every interruption.",
            "R-ZIP-LIMIT": "One fixed archive inside the byte bound does not prove the complete size domain.",
            "R-FILE-LIMIT": "One fixed large JSON pair inside the byte bound does not prove every allowed file or boundary size.",
            "R-TOTAL-LIMIT": "One fixed bundle inside the aggregate bound does not prove every archive structure or aggregate boundary.",
        }
        coverage = []
        case = {"T-SAMPLE": "built-in-sample-tour", "T-RECOVER": "missing-following-recovery",
                "T-LARGE-ZIP": "bounded-150k-zip", "T-LARGE-JSON": "bounded-150k-json"}[task["id"]]
        descriptions = {
            "T-SAMPLE": {
                "R-SAMPLE": "Enter the built-in sample, show 7 followers, 10 following and the five-person nonreciprocal list title, then restore the welcome choices on sample exit.",
                "R-COMPARE": "In the built-in sample tour, show six departures, its list title and the explicit limitation on inferring a cause."},
            "T-RECOVER": {
                "R-IMPORT": "Import the 12/12 previous ZIP, refuse the missing-following ZIP, preserve the earlier 12/12 result and recover with the 7/10 current ZIP.",
                "R-COMPARE": "After one imported record show next-import guidance; after missing-file recovery show six departures, its list title and the comparison limitation."},
            "T-LARGE-ZIP": {
                "R-IMPORT": "Display the 150000 follower count and 150000 following count from the fixed ZIP; on rejection preserve the 12/12 baseline counts and show the small 7/10 recovery counts.",
                "R-ZIP-LIMIT": "Display the two expected 150000 counts after importing the fixed 816720-byte archive inside the documented 128 MiB archive bound.",
                "R-FILE-LIMIT": "Display the two expected 150000 counts from the fixed ZIP whose largest JSON entry is 11850029 bytes, inside the documented 32 MiB per-file bound.",
                "R-TOTAL-LIMIT": "Display the two expected 150000 counts from the fixed ZIP with 23712900 uncompressed bytes, inside the documented 64 MiB aggregate bound."},
            "T-LARGE-JSON": {
                "R-IMPORT": "Display the 150000 follower count and 150000 following count from the fixed twelve-file JSON selection; on rejection preserve the 12/12 baseline counts and show the small 7/10 recovery counts.",
                "R-FILE-LIMIT": "Display the two expected 150000 counts from the fixed loose JSON selection whose largest file is 11850029 bytes, inside the documented 32 MiB per-file bound.",
                "R-TOTAL-LIMIT": "Display the two expected 150000 counts from the fixed twelve-file JSON selection totaling 23712900 bytes, inside the documented 64 MiB aggregate bound."},
        }
        for rid, refs in self.requirement_refs.items():
            obligations = []
            if refs:
                obligations.append(dict(id=rid + "-" + case, description=descriptions[task["id"]][rid],
                                        criterion_refs=refs, exclusion_reason=None))
            obligations.append(dict(id=rid + "-" + case + "-excluded",
                                    description="Unmeasured requirement conditions outside " + case,
                                    criterion_refs=[], exclusion_reason=exclusions[rid] if refs else
                                    "Loose JSON does not exercise archive-size handling; this requirement remains untested by this task."))
            coverage.append(dict(requirement_id=rid, obligations=obligations))
        plan_task = dict(
            id=task["id"], persona_id=library_id(task["persona_id"]),
            requirement_ids=task["requirement_ids"], goal=task["goal"],
            starting_state="A fresh owned headless browser context on the reviewed Peekly build; no existing account, storage or tabs.",
            actions=list(task["milestones"]),
            decisions=["Compare each visible outcome with its frozen goal before any recovery.",
                       "Keep failed, unobserved and recovered criteria separate; never shrink the large input."],
            success_criteria=self.criteria["success"], recovery_criteria=self.criteria["recovery"],
            data_namespace="synthetic-" + task["id"].lower(), resource_id="owned-peekly-headless",
            side_effects="owned_fixture_write",
            stop_conditions=["Stop on timeout, changed bytes, unexpected page activity or uncertain owned-browser cleanup.",
                             "Do not retry, adapt fixtures, log in, visit sample handles or open an OS file picker."],
            requirement_coverage=coverage)
        scenario = dict(schema_version="ergo-scenario.v1", scenario_id="SC-" + task["id"].lower(),
                        surface=dict(kind="web", url=browser_run.ORIGIN + "index.html"),
                        task_goal_ko=task["goal"], device_ids=["desktop-1920"],
                        targets=dict(status=list(dict.fromkeys(check["selector"] for check in self.checks))),
                        steps=self.steps, success=dict(task_checks=self.checks))
        journey = dict(task_id=task["id"], scenario=scenario, device_id="desktop-1920", criteria=self.refs)
        return plan_task, journey, self.map


def build_plans(protocol):
    selectors = protocol["ui_contract"]["selectors"]
    text = protocol["ui_contract"]["exact_text"]
    tasks, journeys, mapping = [], [], {}
    for task in protocol["tasks"]:
        item = Journey(task)
        tid = task["id"]
        if tid == "T-SAMPLE":
            item.click(selectors["sample"])
            item.counts("success", 0, "sample", 7, 10, selectors, ["R-SAMPLE"])
            item.check("success", 0, "not-back-count", selectors["nonreciprocal_count"], "5",
                       "나를 맞팔 안 한 사람 수가 5명이다", ["R-SAMPLE"])
            item.check("success", 1, "departures-count", selectors["departures_count"], "6명",
                       "샘플 비교에서 빠진 계정 수가 6명이다", ["R-COMPARE"])
            item.click(selectors["nonreciprocal_open"])
            item.check("success", 0, "not-back-list-title", selectors["list_title"], "나를 맞팔 안 한 사람 5명",
                       "나를 맞팔 안 한 사람 목록 제목에 5명이 표시된다", ["R-SAMPLE"])
            item.click(selectors["dialog_close"])
            item.click(selectors["departures_open"])
            item.check("success", 1, "departures-list-title", selectors["list_title"], "팔로워에서 빠진 계정 6명",
                       "빠진 계정 목록 제목에 6명이 표시된다", ["R-COMPARE"])
            item.check("success", 1, "comparison-limit", selectors["limitation"], text["departure_limit"],
                       "비교 결과만으로 계정이 사라진 이유를 알 수 없다는 안내가 보인다", ["R-COMPARE"])
            item.click(selectors["dialog_close"])
            item.click(selectors["sample_close"])
            item.check("recovery", 0, "welcome-returned", "body:not(:has(.result-hero)) .welcome-title",
                       text["welcome_title"], "샘플 종료 후 결과 영역 없이 환영 화면으로 돌아온다", ["R-SAMPLE"])
            item.check("recovery", 0, "file-start-returned", selectors["start"], "인스타그램 파일로 시작하기",
                       "샘플 종료 후 파일로 시작할 수 있다", ["R-SAMPLE"])
            item.check("recovery", 0, "sample-start-returned", selectors["sample"], "샘플로 둘러보기",
                       "샘플 종료 후 샘플 진입 선택지가 돌아온다", ["R-SAMPLE"])
        else:
            item.click(selectors["start"])
            item.click(selectors["immediate_import"])
            item.upload(["ZIP-PREVIOUS"], selectors)
            if tid == "T-RECOVER":
                item.counts("success", 0, "previous", 12, 12, selectors, ["R-IMPORT"])
                item.check("success", 0, "single-record-guidance", selectors["single_snapshot_hint"],
                           text["single_snapshot_hint"], "한 기록에서 다음 기록을 넣어 비교하도록 안내한다", ["R-COMPARE"])
            else:
                item.counts("recovery", 0, "baseline-before-large", 12, 12, selectors, ["R-IMPORT"])
            item.click(selectors["import_again"])
            item.click(selectors["immediate_import"])
            if tid == "T-RECOVER":
                item.upload(["ZIP-MISSING-FOLLOWING"], selectors)
                item.check("success", 1, "missing-following-error", selectors["import_error"],
                           text["missing_following"], "팔로잉 목록 누락을 구체적으로 안내하고 새 결과로 바꾸지 않는다", ["R-IMPORT"])
            else:
                ids = (["ZIP-LARGE-150000"] if tid == "T-LARGE-ZIP" else
                       [row["id"] for row in protocol["fixtures"] if row["id"].startswith("JSON-LARGE-")])
                item.upload(ids, selectors)
                item.wait()
                requirements = [rid for rid in task["requirement_ids"] if tid == "T-LARGE-ZIP" or rid != "R-ZIP-LIMIT"]
                item.check("success", 0, "large-followers", selectors["large_followers_outcome"], "팔로워 150000명",
                           "고정된 큰 입력의 팔로워 150000명이 결과 화면에 표시된다", requirements)
                item.check("success", 0, "large-following", selectors["large_following_outcome"], "팔로잉 150000명",
                           "고정된 큰 입력의 팔로잉 150000명이 결과 화면에 표시된다", requirements)
            item.click(selectors["dialog_close"])
            item.counts("recovery", 0, "preserved-previous", 12, 12, selectors, ["R-IMPORT"])
            item.click(selectors["import_again"])
            item.upload(["ZIP-CURRENT"], selectors)
            item.counts("recovery", 1, "recovered-current", 7, 10, selectors, ["R-IMPORT"])
            if tid == "T-RECOVER":
                item.check("recovery", 1, "recovered-departures-count", selectors["departures_count"], "6명",
                           "회복한 두 기록에서 빠진 계정 수가 6명이다", ["R-COMPARE"])
                item.click(selectors["departures_open"])
                item.check("recovery", 1, "recovered-departures-title", selectors["list_title"], "팔로워에서 빠진 계정 6명",
                           "회복한 비교 목록 제목에 빠진 계정 6명이 표시된다", ["R-COMPARE"])
                item.check("recovery", 1, "recovered-comparison-limit", selectors["limitation"], text["departure_limit"],
                           "회복한 비교에서도 원인을 단정할 수 없다는 한계가 보인다", ["R-COMPARE"])
                item.click(selectors["dialog_close"])
        plan_task, journey, refinements = item.finish()
        expected_steps = protocol["measurement_contract"]["actions"][tid]
        if len(item.steps) != expected_steps or len(item.steps) > 16:
            raise ValueError("Frozen action count changed")
        tasks.append(plan_task)
        journeys.append(journey)
        mapping[tid] = refinements
    adapter = dict(schema_version=browser_run.ADAPTER, journeys=journeys,
                   uploads=[dict(id=row["id"], path="uploads/" + row["path"],
                                 name=row["name"], mime_type=row["mime_type"]) for row in protocol["fixtures"]],
                   workers=["assets/importWorker-hLjzVhak.js"])
    plan = dict(schema_version=browser_run.PLAN, product_id=protocol["product_id"],
                runner=ADAPTER_NAME, timeout_seconds=30, tasks=tasks)
    if swarm.clean(plan) != plan or any(swarm.clean(journey) != journey for journey in journeys):
        raise ValueError("The authored plan violates the existing privacy gate")
    return adapter, plan, mapping


class Pilot:
    def __init__(self, stage):
        os.umask(0o077)
        self.stage = Path(stage)
        if not self.stage.is_absolute() or self.stage.resolve(strict=True) != self.stage:
            raise ValueError("Use one canonical absolute owned stage path")
        if not self.stage.is_relative_to(REPO / ".ux-loop"):
            raise ValueError("Stage must stay in this checkout's owned ignored workspace")
        self.root = self.stage / "ui-pilot"
        self.source = self.root / "source"
        self.work = self.root / "work"
        self.library = self.root / "persona-library"
        self.protocol = read_json(HERE / "protocol.json")
        self.plan_path = self.root / PLAN_NAME
        self.prepared_path = self.root / "prepared.json"

    def verify_inputs(self):
        protocol = self.protocol
        if protocol["fixture_hash_state"] != "frozen":
            raise ValueError("Fixture hashes must be frozen before preparation")
        receipt_path = self.stage / "product-build-receipt.json"
        if file_digest(receipt_path) != protocol["build_binding"]["receipt_sha256"]:
            raise ValueError("Frozen build receipt changed")
        receipt = read_json(receipt_path)
        product = self.stage / "product-build"
        if receipt["product_copy"] != str(product) or receipt["outcome"] != "built" or not receipt["preservation"]["all_required_checks_passed"]:
            raise ValueError("Source-bound build and original preservation were not confirmed")
        if receipt["source_manifest_sha256"] != protocol["peekly_source_manifest_sha256"]:
            raise ValueError("Build belongs to a different source")
        dist_manifest_path = self.stage / "product-dist-manifest.json"
        if receipt["dist_manifest"]["path"] != str(dist_manifest_path) or file_digest(dist_manifest_path) != protocol["build_binding"]["dist_manifest_sha256"]:
            raise ValueError("Frozen build manifest changed")
        dist_manifest = read_json(dist_manifest_path)
        dist_files = {name: row for name, row in dist_manifest.items() if row["kind"] == "file"}
        if len(dist_files) != 6 or sum(row["size"] for row in dist_files.values()) != protocol["build_binding"]["dist_bytes"]:
            raise ValueError("Expected the exact six-file build")
        content = {name: {key: row[key] for key in ("kind", "sha256", "target") if key in row}
                   for name, row in dist_manifest.items()}
        if value_digest(content) != protocol["build_binding"]["dist_content_sha256"]:
            raise ValueError("Build content manifest differs")
        observed = []
        for base, directories, files in os.walk(product / "dist", followlinks=False):
            for name in directories + files:
                if (Path(base) / name).is_symlink():
                    raise ValueError("No links in reviewed dist")
            observed += [(Path(base) / name).relative_to(product / "dist").as_posix() for name in files]
        if set(observed) != set(dist_files):
            raise ValueError("The build contains missing or extra files")
        selected = {}
        for name, row in dist_files.items():
            raw = workspace.read_file(product / "dist", name, sensitive_check=True)
            if len(raw) != row["size"] or hashlib.sha256(raw).hexdigest() != row["sha256"]:
                raise ValueError("Built file changed: " + name)
            selected[name] = raw
        prd = workspace.read_file(product, "docs/PRD.md", sensitive_check=True)
        if hashlib.sha256(prd).hexdigest() != protocol["build_binding"]["prd_sha256"]:
            raise ValueError("Product PRD changed")
        selected["docs/PRD.md"] = prd
        fixture_root = self.stage / "synthetic-fixtures"
        manifest_path = fixture_root / "fixture-manifest.json"
        if file_digest(manifest_path) != protocol["fixture_manifest_sha256"]:
            raise ValueError("Fixture manifest changed")
        manifest = read_json(manifest_path)
        if manifest["files"] != protocol["fixtures"] or manifest["total_bytes"] != protocol["fixture_total_bytes"]:
            raise ValueError("Fixture contract differs from the frozen protocol")
        generation = read_json(fixture_root / "generation-receipt.json")
        if (not generation["source_bytes_unchanged"] or
                generation["build_receipt_sha256"] != protocol["build_binding"]["receipt_sha256"] or
                generation["fixture_manifest_sha256"] != protocol["fixture_manifest_sha256"] or
                generation["generator_sha256"] != file_digest(HERE / "generate-fixtures.mjs")):
            raise ValueError("Synthetic generation provenance differs")
        for row in protocol["fixtures"]:
            raw = workspace.read_file(fixture_root, row["path"], sensitive_check=True)
            if len(raw) != row["bytes"] or hashlib.sha256(raw).hexdigest() != row["sha256"]:
                raise ValueError("Fixture changed: " + row["id"])
            selected["uploads/" + row["path"]] = raw
        if sum(row["bytes"] for row in protocol["fixtures"]) > 32 * 1024 * 1024:
            raise ValueError("Fixture budget exceeded")
        return selected

    def call(self, command, *arguments):
        ops = self.root / "operations"
        ops.mkdir(mode=0o700, exist_ok=True)
        number = len(list(ops.glob("*.json"))) + 1
        env = {"PATH": os.defpath, "PYTHONDONTWRITEBYTECODE": "1", "TZ": "UTC",
               "LANG": "C", "LC_ALL": "C", "HOME": str(self.stage / "build-home"),
               "TMPDIR": str(self.stage / "build-tmp")}
        result = subprocess.run([sys.executable, "-B", str(SKILL / "scripts/ux_personas.py"),
                                 command, "--library", str(self.library), *map(str, arguments)],
                                env=env, cwd=REPO, capture_output=True, text=True, timeout=30)
        write_json(ops / f"{number:03d}-{command}.json",
                   dict(exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr))
        if result.returncode:
            raise RuntimeError("Persona CLI failed; preserve the operation log and stop")
        return json.loads(result.stdout)

    def prepare(self, resume=False):
        if not resume and (self.root.exists() or self.root.is_symlink()):
            raise ValueError("Never overwrite or reuse an earlier ui-pilot preparation")
        selected = self.verify_inputs()
        adapter, plan, mapping = build_plans(self.protocol)
        profiles = mapped_profiles(self.protocol)
        persona_input = dict(schema_version="ux-persona-library-input.v1",
                             product_id=self.protocol["product_id"], mode="prd_hypothesis", review_days=30,
                             context=dict(prd_path=str(self.source / "docs/PRD.md"),
                                          prd_sha256=self.protocol["build_binding"]["prd_sha256"],
                                          requirements=self.protocol["requirements"]), personas=profiles)
        if resume:
            self.verify_python_prerequisite_interruption(selected, adapter, plan, mapping, persona_input)
            write_json(self.root / "resume-prepare-requested.json",
                       dict(schema_version="peekly-headless-preparation-resume.v1",
                            reason="Only Python prerequisite rejection occurred; original authored artifacts are retained unchanged and the reviewed v2 baseline refinement is written separately before any execution",
                            preserved_rejection_sha256=file_digest(self.root / "operations/001-import.json"),
                            preserved_authoring_artifacts=self.protocol["authoring_revision"]["preserved_artifacts"],
                            python=sys.executable, python_version=sys.version,
                            existing_inputs_verified=True, library_existed=False,
                            browser_or_attempt_existed=False))
        self.root.mkdir(mode=0o700, exist_ok=resume)
        self.source.mkdir(mode=0o700, exist_ok=resume)
        for relative, raw in selected.items():
            write_bytes(self.source / relative, raw)
            if file_digest(self.source / relative) != hashlib.sha256(raw).hexdigest():
                raise ValueError("Copied UI input bytes differ")
        write_json(self.source / ADAPTER_NAME, adapter)
        write_json(self.plan_path, plan)
        write_json(self.root / CRITERION_MAP_NAME, mapping)
        source = self.root / "persona-input.json"
        write_json(source, persona_input)
        imported = self.call("import", "--input", source)
        repeated = self.call("import", "--input", source)
        if any(row["changed"] for row in repeated["imported"]):
            raise ValueError("Identical persona import did not reuse existing revisions")
        self.call("list", "--product", self.protocol["product_id"])
        for profile in profiles:
            self.call("reuse", "--product", self.protocol["product_id"],
                      "--persona", profile["persona_id"], "--revision", "1")
        write_json(self.root / "library-reuse-summary.json",
                   dict(schema_version="peekly-headless-library-reuse.v1",
                        imported=imported["imported"], identical_reimport=repeated["imported"],
                        new_process_per_command=True,
                        mapping_scope="Only PER- prefix and assigned requirement-ID union are added",
                        protocol_to_library_ids={p["persona_id"]: library_id(p["persona_id"]) for p in self.protocol["personas"]},
                        unexecuted_personas=self.protocol["unexecuted_personas"]))
        reviewed = sorted([*selected, ADAPTER_NAME])
        summary = workspace.prepare(self.source, self.work, reviewed_files=reviewed)
        prepared = workspace._state(self.work)
        accepted = local_run._plan(self.plan_path, prepared)
        library_hash, personas = local_run._selection(self.library, prepared, accepted)
        swarm._prepare_plan(local_run._SelectedLibrary(personas),
                            dict(schema_version=swarm.SCHEMA, product_id=accepted["product_id"],
                                 build=dict(id="prepared-peekly-headless", artifact_path=str(self.work / "workspace.json"),
                                            sha256=file_digest(self.work / "workspace.json")),
                                 max_parallel=1, lease_seconds=120, max_attempts=1, tasks=accepted["tasks"]))
        self.validate_native(prepared, accepted, personas)
        if (self.work / local_run.MARKER).exists() or (self.work / local_run.DIRECTORY).exists():
            raise ValueError("Preparation must not create an execution attempt")
        guarded = [PLAN_NAME, CRITERION_MAP_NAME, "source/" + ADAPTER_NAME,
                   "persona-input.json", "persona-library/library.json", "library-reuse-summary.json",
                   "work/workspace.json", "native-validation.json"]
        if resume:
            guarded.extend(["operations/001-import.json", "resume-prepare-requested.json",
                            "source/browser-adapter.json", "reviewed-plan.json", "criterion-map.json"])
        marker = dict(schema_version="peekly-headless-prepared.v1", preparation_only=True,
                      browser_executed=False, attempt_created=False,
                      benchmark_hashes={name: file_digest(HERE / name) for name in BENCHMARK_FILES},
                      artifact_hashes={name: file_digest(self.root / name) for name in guarded},
                      source_hashes={name: file_digest(self.source / name) for name in reviewed},
                      library_selection_sha256=library_hash, tasks=len(accepted["tasks"]), profiles=len(profiles),
                      task_actions={row["task_id"]: len(row["scenario"]["steps"]) for row in adapter["journeys"]},
                      task_checks={row["task_id"]: len(row["criteria"]) for row in adapter["journeys"]},
                      build_receipt_sha256=self.protocol["build_binding"]["receipt_sha256"],
                      fixture_manifest_sha256=self.protocol["fixture_manifest_sha256"],
                      note="Pure native schema/byte validation passed; runtime preflight and exact runtime freeze remain required before the first claim.")
        write_json(self.prepared_path, marker)
        return dict(prepared=True, root=str(self.root), plan=str(self.plan_path), work=str(self.work),
                    library=str(self.library), prepared_sha256=file_digest(self.prepared_path),
                    protocol_sha256=file_digest(HERE / "protocol.json"), runner_sha256=file_digest(HERE / "run_pilot.py"),
                    adapter_sha256=file_digest(self.source / ADAPTER_NAME),
                    plan_sha256=file_digest(self.plan_path), tasks=marker["task_actions"],
                    measured_checks=marker["task_checks"], preparation_report=summary)

    def verify_python_prerequisite_interruption(self, selected, adapter, plan, mapping, persona_input):
        """Narrow host-authorized recovery of preparation, never of a task attempt."""
        if (not self.root.is_dir() or self.root.resolve(strict=True) != self.root
                or self.library.exists() or self.work.exists() or self.prepared_path.exists()):
            raise ValueError("Preparation resume requires no Library, workspace, completion or execution state")
        if {entry.name for entry in self.root.iterdir()} != {"source", "operations", "criterion-map.json", "persona-input.json", "reviewed-plan.json"}:
            raise ValueError("Partial preparation contains unexpected entries or an intent marker")
        operations = self.root / "operations"
        if operations.resolve(strict=True) != operations or {entry.name for entry in operations.iterdir()} != {"001-import.json"}:
            raise ValueError("Only the retained first prerequisite rejection is eligible")
        rejected = read_json(operations / "001-import.json")
        if rejected != {"exit_code": 2, "stderr": "Python 3.10 or newer is required.\n", "stdout": ""}:
            raise ValueError("The interruption was not the known pre-import Python prerequisite rejection")
        preserved = self.protocol["authoring_revision"]["preserved_artifacts"]
        for name, expected_hash in preserved.items():
            raw = workspace.read_file(self.root, name, sensitive_check=True)
            if hashlib.sha256(raw).hexdigest() != expected_hash:
                raise ValueError("Preserved pre-execution authoring artifact changed: " + name)
        # The earlier adapter is preserved as evidence of the pre-execution draft.
        # The reviewed workspace will select only ADAPTER_NAME, the v2 refinement.
        expected = {**selected, "browser-adapter.json": workspace.read_file(self.source, "browser-adapter.json")}
        observed, directories_seen = set(), set()
        for current, directories, files in os.walk(self.source, followlinks=False):
            for name in directories + files:
                if (Path(current) / name).is_symlink():
                    raise ValueError("Partial preparation contains a link")
            directories_seen.add(Path(current).relative_to(self.source).as_posix())
            observed.update((Path(current) / name).relative_to(self.source).as_posix() for name in files)
        expected_directories = {"."}
        for name in expected:
            expected_directories.update(parent.as_posix() for parent in Path(name).parents)
        if observed != set(expected) or directories_seen != expected_directories:
            raise ValueError("Partial source does not have the exact reviewed file and directory set")
        for relative, raw in expected.items():
            if workspace.read_file(self.source, relative, sensitive_check=True) != raw:
                raise ValueError("Partial source bytes changed: " + relative)
        for name, value in (("persona-input.json", persona_input),):
            if workspace.read_file(self.root, name, sensitive_check=True) != canonical(value):
                raise ValueError("Authored preparation bytes changed: " + name)

    def validate_native(self, prepared, plan, personas):
        """Use the real normalizer and reviewed bytes, without a runtime probe or launch."""
        browser = browser_run.manifest(prepared, plan)
        build_hash = file_digest(self.work / "workspace.json")
        build = read_json(self.stage / "product-build-receipt.json")
        node = Path(build["node"]["path"])
        if node.resolve(strict=True) != node or file_digest(node) != build["node"]["sha256"]:
            raise ValueError("Frozen Node changed before native schema validation")
        env = {"PATH": str(node.parent) + os.pathsep + os.defpath,
               "HOME": str(self.stage / "build-home"), "TMPDIR": str(self.stage / "build-tmp"),
               "LANG": "C", "LC_ALL": "C", "TZ": "UTC"}
        command = ["/usr/bin/sandbox-exec", "-p", browser_run.NETWORK_PROFILE,
                   str(node), str(browser_run.BRIDGE), "--validate"]
        rows = []
        for task in plan["tasks"]:
            record = personas["state"]["entries"][plan["product_id"] + "/" + task["persona_id"]][-1]
            binding = dict(task_id=task["id"], attempt=1, operation_id="preflight", build_sha256=build_hash,
                           persona_id=task["persona_id"], revision=record["revision"],
                           profile_sha256=record["profile_sha256"], prd_sha256=record["context"]["prd_sha256"])
            request = browser_run.request_for(self.work, browser, task["id"], binding,
                                              self.work / "browser-preflight", plan["timeout_seconds"])
            result = subprocess.run(command, input=canonical(request), env=env, cwd=self.work,
                                    capture_output=True, timeout=10)
            row = dict(task_id=task["id"], request_sha256=hashlib.sha256(canonical(request)).hexdigest(),
                       exit_code=result.returncode, stdout=result.stdout.decode(), stderr=result.stderr.decode())
            rows.append(row)
            if result.returncode or json.loads(result.stdout) != {"schema_version": "ux-journey-browser-validation.v1", "valid": True}:
                write_json(self.root / "native-validation.json", dict(validation_only=True, command=command, checks=rows))
                raise ValueError("Native schema or reviewed-byte validation failed; no browser or attempt was created")
        write_json(self.root / "native-validation.json", dict(validation_only=True, command=command, checks=rows))

    def verify_prepared(self):
        marker = read_json(self.prepared_path)
        if marker["schema_version"] != "peekly-headless-prepared.v1" or not marker["preparation_only"]:
            raise ValueError("Expected a frozen preparation receipt")
        for name, expected in marker["benchmark_hashes"].items():
            if file_digest(HERE / name) != expected:
                raise ValueError("Benchmark changed after preparation: " + name)
        for name, expected in marker["artifact_hashes"].items():
            if file_digest(self.root / name) != expected:
                raise ValueError("Prepared artifact changed: " + name)
        for name, expected in marker["source_hashes"].items():
            if file_digest(self.source / name) != expected:
                raise ValueError("Reviewed input changed: " + name)
        self.verify_inputs()

    def execute_once(self):
        self.verify_prepared()
        intent = self.root / "first-run-requested.json"
        if intent.exists() or (self.work / local_run.MARKER).exists() or (self.work / local_run.DIRECTORY).exists():
            raise ValueError("A run was already requested; use readback, never redispatch")
        write_json(intent, dict(schema_version="peekly-headless-run-intent.v1",
                                prepared_sha256=file_digest(self.prepared_path), one_attempt_only=True))
        result = local_run.execute(self.work, library_path=self.library,
                                   input_path=self.plan_path, approved=True)
        write_json(self.root / "first-run-result.json", result)
        return result

    def readback(self):
        return workspace.status(self.work)


def main():
    if sys.version_info < (3, 10):
        raise SystemExit("Python 3.10 or newer is required before any preparation or run.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "resume_prepare", "run", "readback"))
    parser.add_argument("--stage", type=Path, required=True)
    args = parser.parse_args()
    pilot = Pilot(args.stage)
    result = {"prepare": pilot.prepare, "resume_prepare": lambda: pilot.prepare(resume=True),
              "run": pilot.execute_once, "readback": pilot.readback}[args.mode]()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if args.mode != "run" or result.get("task_scope_passed") is True else 1


if __name__ == "__main__":
    sys.exit(main())
