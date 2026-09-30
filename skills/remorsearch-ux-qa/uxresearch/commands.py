"""Offline engine command surface and sanitized errors."""
from __future__ import annotations

from pathlib import Path

from .canonical import EngineError
from .storage import Store,read_bytes,read_json
from .engine import fresh,gate_command,merge_command

COMMANDS={"merge","gate","report-check","export-audience","minimize"}


def add_parser(commands):
    for name in sorted(COMMANDS):
        parser=commands.add_parser(name,help={"merge":"Merge typed reader returns with authoritative captures","gate":"Regrade every claim and check the research process","report-check":"Check report order, citations and statement mapping","export-audience":"Export an honest incomplete audience draft","minimize":"Create an allowlisted loop projection"}[name])
        parser.add_argument("--run",required=True)
        parser.add_argument("--lock-timeout",type=float,default=5)
        if name=="merge":
            parser.add_argument("--manifest",type=Path,required=True);parser.add_argument("--acknowledgements",type=Path);parser.add_argument("--search-ledger",type=Path,required=True);parser.add_argument("--imports",type=Path);parser.add_argument("--returns",type=Path,nargs="+",required=True)
        else:
            parser.add_argument("--bundle",type=Path,required=True)
            if name=="gate":parser.add_argument("--write-bundle",action="store_true")
            else:parser.add_argument("--gate",type=Path,required=True)
        if name=="report-check":parser.add_argument("--report",type=Path,required=True);parser.add_argument("--statements",type=Path,required=True)
        if name=="export-audience":parser.add_argument("--audience-id",required=True)


def execute(args,run):
    with Store(run.path,args.lock_timeout) as store:
        def validate_publish(outputs):
            from .engine import expired_sources, now_of
            from .merge import validate_policy
            validate_policy(run)
            bundle=outputs.get("bundle.json")
            if bundle and expired_sources(bundle,now_of(run)):
                raise EngineError("expired", "Retention deadline passed before manifest commit; purge and rerun.")
        store.validator=validate_publish
        try:
            if args.command=="merge":return merge_command(args,run,store)
            if args.command=="gate":return gate_command(args,run,store)
            bundle,gate=fresh(run,store,args.bundle,args.gate)
            if args.command=="report-check":
                from .reports import check
                result=check(read_bytes(args.report).decode("utf-8"),read_json(args.statements),bundle,gate,run.routes)
                store.publish("report-check",{"report_check.json":result})
                return result["exit_code"],["report_check.json"],result["violations"],result["warnings"]
            if args.command=="export-audience":
                from .audiences import make_draft,todo_markdown
                brief=read_json(run.path/"brief.json")
                draft=make_draft(bundle,gate,brief,args.audience_id)
                store.publish("export-audience",{"audience.draft.json":draft,"audience.todo.md":todo_markdown(draft)})
                return 0,["audience.draft.json","audience.todo.md"],[],[]
            from .minimize import minimize
            out,result=minimize(bundle,gate)
            if result["exit_code"]:
                store.failure("minimize.json",result)
                return result["exit_code"],["minimize.json"],result["issues"],result["warnings"]
            store.publish("minimize",{"bundle.min.json":out,"minimize.json":result})
            return 0,["bundle.min.json","minimize.json"],[],result["warnings"]
        except (OSError, UnicodeError, TypeError, KeyError, IndexError, AttributeError, RecursionError) as exc:
            error=EngineError("io_or_integrity", "Required input is missing, malformed or unsafe.")
            if args.command in {"merge", "gate"}:
                store.failure("gate_failed.json", dict(result="fail", exit_code=2, issues=[error.issue]))
            raise error from exc
        except EngineError as exc:
            if args.command=="report-check" and exc.exit_code!=3:
                store.failure("report_check.json",dict(schema_version="ux-report-check.v1",result="fail",exit_code=exc.exit_code,violations=[exc.issue],warnings=[],citations=[],mapping_checks=[],supported_coverage=None,bundle_id=None,gate_input_sha256=None,report_sha256=None,mapping_sha256=None))
            if exc.exit_code!=3 and args.command in {"merge","gate"}:
                store.failure("gate_failed.json",dict(result="fail",exit_code=exc.exit_code,issues=[exc.issue]))
            raise
