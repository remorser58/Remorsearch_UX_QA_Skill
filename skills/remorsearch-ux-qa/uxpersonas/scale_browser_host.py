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

from uxresearch.canonical import byte_digest
from uxresearch.storage import safe_path
from . import swarm


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
            return {"operation_id":request["operation_id"],"context_id":context,
                "request_sha256":request["request_sha256"],"trace_id":"browser-close-"+context[-12:],
                "result":result}
        if kind != "tool":
            raise RuntimeError("unsupported_browser_host_operation")
        evidence = safe_path(payload["evidence_path"])
        if context not in self.processes:
            await self._exchange(context, "start", {"url":self.target_url, "chrome":self.chrome,
                "profile_dir":str(evidence / "browser-profile"), "evidence_path":str(evidence),
                "fixtures_dir":str(self.fixtures)})
        name = payload["name"]
        arguments = payload["arguments"]
        if name not in {"observe", "click", "type", "upload", "scroll", "wait"}:
            raise RuntimeError("tool_not_allowlisted")
        result = await self._exchange(context, "act", {"name":name, "arguments":arguments})
        if set(result) != {"text","facts","captures","checks"}:
            raise RuntimeError("browser_observation_contract")
        # Product sample content may contain synthetic-looking account handles.
        # Scrub identifiers before the observation crosses into the model/queue;
        # screenshots remain private, hash-bound evidence and are not uploaded.
        # Hashes are machine metadata, not free text. A hexadecimal digest can
        # contain a digit run which the privacy scrubber mistakes for a card.
        # Verify original capture bytes and never rewrite their identifiers.
        result = {**result, **swarm.clean({key: result[key]
            for key in ("text", "facts", "checks")})}
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
