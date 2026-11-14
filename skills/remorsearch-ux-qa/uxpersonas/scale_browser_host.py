"""Owned loopback-only headless Chrome host for live ScaleExecution journeys.

Never attaches to a user browser. Each queue context owns a separate Chrome profile
and CDP process. Only localhost HTTP targets are accepted; cross-origin requests,
websockets, credentials and high-risk form controls are blocked.
"""
from __future__ import annotations
import asyncio
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import time
import zipfile

from uxresearch.canonical import byte_digest
from uxresearch.storage import safe_path
from . import swarm
from .peekly_criteria import evaluate as evaluate_peekly_criteria


def _preserve_driver_hashes(original, cleaned):
    """Keep typed, validated evidence digests out of free-text privacy redaction."""
    paths = (
        ("storage_snapshot", "sha256"),
        ("import_attempt", "fixture_sha256"),
        ("import_attempt", "storage_before", "sha256"),
        ("import_attempt", "storage_after", "sha256"),
    )
    for parts in paths:
        source, target = original, cleaned
        for key in parts[:-1]:
            source = source.get(key) if isinstance(source, dict) else None
            target = target.get(key) if isinstance(target, dict) else None
        if isinstance(source, dict) and isinstance(target, dict):
            value = source.get(parts[-1])
            if isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value):
                target[parts[-1]] = value


class ScaleBrowserHost:
    def __init__(self, *, target_url, chrome, node, driver_path, adapter_path, fixtures_path, parallel_safe=True):
        from urllib.parse import urlsplit
        parsed = urlsplit(target_url)
        if (parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
                or parsed.username or parsed.password or parsed.query or parsed.fragment):
            raise ValueError("The live Scale browser target must be an explicit loopback HTTP origin without credentials/query.")
        if not Path(chrome).is_file() or not os.access(chrome, os.X_OK):
            raise ValueError("A dedicated Chrome executable is required.")
        if not Path(node).is_file() or not os.access(node, os.X_OK):
            raise ValueError("A dedicated Node executable is required.")
        self.target_url = target_url
        self.chrome, self.node = str(Path(chrome).resolve()), str(Path(node).resolve())
        self.driver = Path(driver_path).resolve()
        self.fixtures = safe_path(fixtures_path)
        if not self.fixtures.is_dir() or not (self.fixtures / "fixture-manifest.json").is_file():
            raise ValueError("A frozen synthetic fixture directory and manifest are required.")
        adapter = Path(adapter_path).resolve()
        manifest_bytes = (self.fixtures / "fixture-manifest.json").read_bytes()
        self.adapter_sha256 = hashlib.sha256(adapter.read_bytes() + self.driver.read_bytes() + manifest_bytes).hexdigest()
        self.info = dict(name="owned-headless-chrome-cdp", mode="model_tools",
            model="OpenCodex local gateway via RoutedScaleProvider",
            adapter_sha256=self.adapter_sha256, isolated_contexts=True,
            parallel_safe=bool(parallel_safe))
        self.processes = {}
        self.locks = {}
        self.context_paths = {}
        self.serials = {}
        self.context_tasks = {}
        self.context_uploads = {}
        self.context_observations = {}
        self.context_fixture_validation = {}

    def _validate_fixture_upload(self, fixture_name):
        """Expose bounded fixture-shape metadata without leaking fixture contents."""
        if (not isinstance(fixture_name, str) or fixture_name.startswith("@group:")
                or not fixture_name.lower().endswith(".zip")):
            return None
        try:
            path = safe_path(self.fixtures / fixture_name, self.fixtures)
            with zipfile.ZipFile(path) as archive:
                html_members = [name for name in archive.namelist()
                                if name.lower().endswith(".html")]
                if not html_members:
                    return None
                documents = []
                for member in html_members[:32]:
                    raw = archive.read(member)
                    html = raw.decode("utf-8-sig", "replace")
                    complete = bool(
                        re.search(r"<html\b", html, re.I)
                        and re.search(r"<body\b", html, re.I)
                        and re.search(r"</body\s*>[\s\S]*</html\s*>", html, re.I)
                    )
                    documents.append({
                        "member": Path(member).name,
                        "complete_html_document": complete,
                    })
                return {
                    "fixture": fixture_name,
                    "archive_valid": True,
                    "html_documents": documents,
                    "complete_html_documents": bool(documents) and all(
                        row["complete_html_document"] for row in documents),
                }
        except (OSError, ValueError, KeyError, zipfile.BadZipFile):
            return {"fixture": fixture_name, "archive_valid": False,
                    "reason": "fixture_archive_unreadable"}

    def can_resume(self, context_id, observations):
        process = self.processes.get(context_id)
        return bool(process and process.returncode is None)

    async def _exchange(self, context_id, kind, payload):
        lock = self.locks.setdefault(context_id, asyncio.Lock())
        async with lock:
            process = self.processes.get(context_id)
            if kind == "start" and process is None:
                evidence = safe_path(payload["evidence_path"])
                profile = evidence / "browser-profile"
                profile.mkdir(mode=0o700, exist_ok=False)
                if profile.stat().st_mode & 0o077:
                    raise RuntimeError("browser_profile_permissions")
                process = await asyncio.create_subprocess_exec(
                    self.node, str(self.driver), cwd=str(evidence),
                    stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.DEVNULL)
                self.processes[context_id] = process
                self.context_paths[context_id] = str(profile)
            if process is None or process.returncode is not None:
                raise RuntimeError("browser_context_not_running")
            ident = self.serials.get(context_id, 0) + 1
            self.serials[context_id] = ident
            packet = json.dumps({"id": ident, "kind": kind, "payload": payload}, ensure_ascii=False, separators=(",", ":"))
            process.stdin.write(packet.encode() + b"\n")
            await process.stdin.drain()
            raw = await asyncio.wait_for(process.stdout.readline(), timeout=25)
            if not raw or len(raw) > 65536:
                raise RuntimeError("browser_transport_closed")
            reply = json.loads(raw)
            if reply.get("id") != ident or reply.get("error") or "result" not in reply:
                raise RuntimeError("browser_action_failed:" + str(reply.get("error", "unknown"))[:120])
            return reply["result"]

    async def call(self, kind, request):
        context = request["context_id"]
        payload = request["payload"]
        self.context_tasks = getattr(self, "context_tasks", {})
        self.context_uploads = getattr(self, "context_uploads", {})
        self.context_observations = getattr(self, "context_observations", {})
        self.context_fixture_validation = getattr(self, "context_fixture_validation", {})
        if kind == "close":
            process = self.processes.get(context)
            if process is None:
                return {"operation_id":request["operation_id"],"context_id":context,
                    "request_sha256":request["request_sha256"],"trace_id":"browser-close-empty",
                    "result":{"stopped":True}}
            try:
                result = await self._exchange(context, "close", {})
                await asyncio.wait_for(process.wait(), timeout=5)
            except Exception:
                if process.returncode is None:
                    process.terminate()
                result = {"stopped":False}
            self.processes.pop(context, None)
            self.context_paths.pop(context, None)
            self.context_tasks.pop(context, None)
            self.context_uploads.pop(context, None)
            self.context_observations.pop(context, None)
            self.context_fixture_validation.pop(context, None)
            return {"operation_id":request["operation_id"],"context_id":context,
                "request_sha256":request["request_sha256"],"trace_id":"browser-close-"+context[-12:],
                "result":result}
        if kind != "tool":
            raise RuntimeError("unsupported_browser_host_operation")
        evidence = safe_path(payload["evidence_path"])
        task = payload.get("task")
        if isinstance(task, dict):
            self.context_tasks.setdefault(context, copy.deepcopy(task))
        self.context_uploads.setdefault(context, set())
        self.context_observations.setdefault(context, [])
        self.context_fixture_validation.setdefault(context, [])
        if context not in self.processes:
            await self._exchange(context, "start", {"url":self.target_url, "chrome":self.chrome,
                "profile_dir":str(evidence / "browser-profile"), "evidence_path":str(evidence),
                "fixtures_dir":str(self.fixtures)})
        name = payload["name"]
        arguments = payload["arguments"]
        if name not in {"observe", "click", "type", "upload", "upload_cancel",
                        "upload_save_failure", "scroll", "wait"}:
            raise RuntimeError("tool_not_allowlisted")
        try:
            result = await self._exchange(context, "act", {"name":name, "arguments":arguments})
        except RuntimeError as exc:
            # This exact driver rejection happens before mouse-button/key dispatch.
            # Preserve the failure as an observed state; do not replay the click
            # or relax the target guard. Transport/unknown side effects still stop.
            if name != "click" or str(exc) != "browser_action_failed:click_target_not_allowed_or_visible":
                raise
            result = await self._exchange(context, "act", {"name":"observe", "arguments":{}})
            result["facts"]["rejected_action"] = {"name": name, "reason": "target_not_allowed_or_visible",
                "click_dispatched": False, "automatic_click_retry": False}
            result["text"] = ("Click NOT dispatched: target was not allowed or visible. "
                "This is a failed action, not a successful navigation. Re-observe the current "
                "controls and choose a safe recovery; no click was retried.\n" + result["text"])
        if name in {"upload", "upload_cancel", "upload_save_failure"} and isinstance(arguments, dict) and isinstance(arguments.get("file"), str):
            fixture_name = arguments["file"]
            self.context_uploads[context].add(fixture_name)
            validation = self._validate_fixture_upload(fixture_name)
            if validation and validation not in self.context_fixture_validation[context]:
                self.context_fixture_validation[context].append(validation)
        if set(result) != {"text","facts","captures","checks"}:
            raise RuntimeError("browser_observation_contract")
        result["facts"]["fixture_uploads"] = sorted(self.context_uploads[context])
        result["facts"]["fixture_validation"] = copy.deepcopy(
            self.context_fixture_validation[context])
        task = self.context_tasks.get(context)
        if task:
            result["checks"] = evaluate_peekly_criteria(task, result["facts"], result["text"],
                self.context_uploads[context], self.context_observations[context])
        # Product sample content may contain synthetic-looking account handles.
        # Scrub identifiers before the observation crosses into the model/queue;
        # screenshots remain private, hash-bound evidence and are not uploaded.
        # Hashes are machine metadata, not free text. A hexadecimal digest can
        # contain a digit run which the privacy scrubber mistakes for a card.
        # Verify original capture bytes and never rewrite their identifiers.
        original_facts = result["facts"]
        result = {**result, **swarm.clean({key: result[key]
            for key in ("text", "facts", "checks")})}
        _preserve_driver_hashes(original_facts, result["facts"])
        self.context_observations[context].append({"text": result["text"], "facts": result["facts"]})
        for capture in result["captures"]:
            if not isinstance(capture, dict) or set(capture) != {"path", "sha256"}:
                raise RuntimeError("browser_capture_integrity:metadata")
            path = safe_path(evidence / capture["path"], evidence)
            if not path.is_file():
                raise RuntimeError("browser_capture_integrity:missing")
            if path.stat().st_mode & 0o077:
                raise RuntimeError("browser_capture_integrity:permissions")
            if byte_digest(path.read_bytes()) != capture["sha256"]:
                raise RuntimeError("browser_capture_integrity:digest")
        return {"operation_id":request["operation_id"],"context_id":context,
            "request_sha256":request["request_sha256"],"trace_id":"browser-"+request["operation_id"][-16:],
            "result":result}

    async def shutdown(self):
        outcomes = await asyncio.gather(*[
            self.call("close", {"operation_id":"shutdown-"+key[-12:],"context_id":key,
                "request_sha256":"0"*64,"deadline":time.time()+10,"payload":{}})
            for key in list(self.processes)], return_exceptions=True)
        return all(isinstance(x,dict) and x.get("result",{}).get("stopped") is True for x in outcomes)
