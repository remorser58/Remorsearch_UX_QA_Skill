"""Scratch checks that mirror the planned tests/test_korean_pack.py for my three files."""
import json
import pathlib
import re
import sys

SKILL = pathlib.Path("/home/user/ux-research-qa-skills/skills/remorsearch-ux-qa")
sys.path.insert(0, str(SKILL))
from uxresearch import scope, verdict  # noqa: E402

errors = []
data = json.loads((SKILL / "uxresearch/data/korea-platforms.json").read_text(encoding="utf-8"))
routes = json.loads((SKILL / "uxresearch/data/routes.json").read_text(encoding="utf-8"))
lists = scope.lists_for(routes)
platform_ids = {p["id"] for p in routes["platforms"]}
platform_hosts = [h for p in routes["platforms"] for h in p["hosts"]]
oos_hosts = [o["host"] for o in routes["out_of_scope"]]
terms_hosts = [h for t in routes["terms_restricted"] for h in t["hosts"]]

VOCAB_ROUTE = {"official_api_user_key", "official_feed", "team_export", "reader_public_page",
               "signed_in_authorised", "none"}
VOCAB_TERMS = {"reported", "confirmed", "checked_by_user", "unchecked"}

for row in data["platforms"]:
    rid = row["id"]
    for r in row["routes"]:
        if r not in VOCAB_ROUTE:
            errors.append(f"{rid}: route {r} not in vocab")
    if "researcher_note" in json.dumps(row, ensure_ascii=False):
        errors.append(f"{rid}: researcher_note present")
    for route_id in row["route_ids"]:
        if route_id not in platform_ids:
            errors.append(f"{rid}: route_id {route_id} not in routes.json platforms")
    if row["terms"]["status"] not in VOCAB_TERMS:
        errors.append(f"{rid}: bad terms status")
    entries = set()
    for host in row["hosts"]:
        probe = host.replace("*.", "x.")
        if not (verdict.host_matches(probe, platform_hosts) or verdict.host_matches(probe, oos_hosts)
                or verdict.host_matches(probe, terms_hosts)):
            errors.append(f"{rid}: host {host} not covered by routes.json")
        entry = scope.terms_entry(probe, lists)
        entries.add(entry["id"] if entry else None)
    if len(entries) > 1:
        errors.append(f"{rid}: hosts fall under different terms entries {entries}")
    entry_id = next(iter(entries)) if entries else None
    status = row["terms"]["status"]
    if entry_id is None:
        if status in ("reported", "confirmed"):
            errors.append(f"{rid}: status {status} but no routes.json terms entry covers its hosts")
    else:
        entry = next(t for t in routes["terms_restricted"] if t["id"] == entry_id)
        if entry["status"] != status:
            errors.append(f"{rid}: status {status} != routes.json {entry_id} {entry['status']}")
        if row["terms"].get("routes_entry") != entry_id:
            errors.append(f"{rid}: routes_entry {row['terms'].get('routes_entry')} != {entry_id}")
        if "terms_restricted" not in row["expected_stops"]:
            errors.append(f"{rid}: covered by {entry_id} but terms_restricted not expected")

# markdown mirrors
md = (SKILL / "references/research/korea/platform-map.md").read_text(encoding="utf-8")
md_ids = re.findall(r"^### `([a-z0-9-]+)` ", md, flags=re.M)
if md_ids != [r["id"] for r in data["platforms"]]:
    errors.append(f"md order differs: {md_ids}")
table_ids = re.findall(r"^\| `([a-z0-9-]+)` \|", md.split("## 3.")[0], flags=re.M)
if table_ids != [r["id"] for r in data["platforms"]]:
    errors.append("overview table order differs")


def walk(obj, out):
    if isinstance(obj, dict):
        for v in obj.values():
            walk(v, out)
    elif isinstance(obj, list):
        for v in obj:
            walk(v, out)
    elif isinstance(obj, str) and re.match(r"https?://", obj):
        out.add(obj)


json_urls = set()
walk(data, json_urls)
md_urls = set(re.findall(r"https?://[^\s)>\]]+", md))
if json_urls != md_urls:
    errors.append(f"url sets differ: {sorted(json_urls ^ md_urls)[:5]}")

# links in my two markdown files resolve
for name in ("platform-map.md", "overview.md"):
    path = SKILL / "references/research/korea" / name
    if not path.exists():
        errors.append(f"{name} missing")
        continue
    text = path.read_text(encoding="utf-8")
    for ref in set(re.findall(r"`((?:references|uxresearch|schemas|scripts|drivers)/[^`\s]+?)`", text)):
        target = ref.split("#")[0]
        if not (SKILL / target).exists():
            errors.append(f"{name}: link {ref} does not resolve")
    for ref in set(re.findall(r"\]\(([^)]+)\)", text)):
        if ref.startswith("http"):
            continue
        if not (SKILL / ref.split("#")[0]).exists():
            errors.append(f"{name}: md link {ref} does not resolve")
    for word in ("여성시대", "researcher_note", "researcher note", "연구자 메모", "유저", "이용자"):
        if word in text:
            errors.append(f"{name}: contains {word!r}")
    if re.search(r"insane|k-skill|K-skill", text):
        errors.append(f"{name}: mentions insane-* or K-skill")

jtext = json.dumps(data, ensure_ascii=False)
for word in ("여성시대", "researcher_note", "유저", "이용자", "subdued20club", "similarweb", "img.theqoo"):
    if word in jtext:
        errors.append(f"json contains {word!r}")

print("errors:", len(errors))
for e in errors:
    print(" -", e)
