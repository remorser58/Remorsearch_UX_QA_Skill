"""Two processes read 12 URLs on a lifted host (budget 10) through one run folder."""
import json, os, subprocess, sys, tempfile, time
from pathlib import Path
sys.path.insert(0, "/home/user/ux-research-qa-skills/tests")
import test_ux_read as T
server = T.FixtureServer()
for i in range(12):
    server.page("reported.test", f"/p/{i}", "post-normal.html")
tmp = Path(tempfile.mkdtemp(prefix="conc-", dir="/tmp/claude-0/-home-user-ux-research-qa-skills/e780fd74-671a-5856-a21d-1181ebfa73fb/scratchpad/r2code"))
brief = json.loads((T.FIXTURES / "brief.json").read_text(encoding="utf-8"))
brief["access_policy"]["terms_checked"] = [{"host": "reported.test", "terms_url": "http://reported.test/terms",
                                            "checked_on": time.strftime("%Y-%m-%d", time.gmtime()),
                                            "result": "permits_this_reading"}]
(tmp / "brief.json").write_text(json.dumps(brief), encoding="utf-8")
env = {**os.environ, "REMORSEARCH_ALLOW_PRIVATE": "1", "REMORSEARCH_TEST_RESOLVE": "reported.test=127.0.0.1",
       "PYTHONPATH": str(T.SKILL)}
shim = [sys.executable, "-m", "uxresearch.cli"]
run = tmp / "run"
out = subprocess.run(shim + ["start", "--run", str(run), "--routes", str(T.ROUTES), "--brief", str(tmp / "brief.json"),
                             "--min-interval", "5"], env=env, capture_output=True, text=True)
print("start", out.returncode, out.stdout[-300:] if out.returncode else "")
def worker(indices):
    script = "; ".join(f"python3 -m uxresearch.cli read --run {run} --max-wait 600 http://reported.test:{server.port}/p/{i} >/dev/null 2>>{tmp}/err{indices[0]}.log; echo $? >> {tmp}/codes{indices[0]}.txt" for i in indices)
    return subprocess.Popen(["bash", "-c", script], env=env)
procs = [worker(list(range(0, 12, 2))), worker(list(range(1, 12, 2)))]
for p in procs:
    p.wait()
codes = [int(x) for f in tmp.glob("codes*.txt") for x in f.read_text().split()]
print("exit codes:", sorted(codes))
hosts = json.loads((run / "hosts.json").read_text())
print("docs on reported.test:", hosts["hosts"]["reported.test"]["docs"])
print("page hits:", len([h for h in server.hits("reported.test") if h.startswith("/p/")]))
server.close()
