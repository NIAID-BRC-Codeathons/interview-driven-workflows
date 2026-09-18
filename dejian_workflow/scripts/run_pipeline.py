#!/usr/bin/env python3
"""End-to-end driver: interview -> route -> (fetch | build) -> validate.

This is the walking-skeleton entrypoint: prove one interview can go from
interviews/raw/ to a workflow that passes real static validation, using the
real catalog/fetch/validate/build pieces in this directory.

Decision handling:
  - "use":   fetch the real matched IWC workflow as-is, then validate it.
  - "build": if route.py's live IWC registry check (via the real galaxy-mcp
             MCP server) found candidates the local curated catalog missed,
             STOP and report them instead of spending an LLM call to
             fabricate something from scratch when a real workflow may
             already exist. Only hands off to build_workflow.py (LLM
             generation, needs ANTHROPIC_API_KEY) when the live registry
             also came up empty or couldn't be checked.
  - "adapt": fetch the real matched IWC workflow as the base, then STOP and
             print next steps. Actually deciding *what* to change from a
             free-text request needs a human or an LLM to author a change
             spec (see adapt_workflow.py's docstring) -- this script does
             not fabricate one. It hands you a real base workflow and tells
             you the exact next command to run.

Before any of that, it prints follow-up questions (Goal 4) surfacing any
assumption the routing decision made silently -- see
generate_followup_questions.py. This is advisory, not a gate: nothing here
collects your answers and re-routes based on them; that closed loop isn't
built yet. Treat the questions as "ask before trusting this," not proof
the decision is already validated.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from route import route_interview_file  # noqa: E402
from fetch_iwc_workflow import fetch  # noqa: E402
from generate_followup_questions import generate_questions  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("interview", type=Path, help="Path to an interview file in interviews/raw/")
    parser.add_argument(
        "--force-build",
        action="store_true",
        help="Build via LLM even if the live IWC registry found candidates the local catalog missed",
    )
    args = parser.parse_args()

    result = route_interview_file(args.interview)
    decision = result["decision"]
    print(f"routing decision: {decision}")
    if result["top_match"]:
        print(
            f"top match: {result['top_match']['name']} "
            f"(confidence {result['top_match']['_confidence']:.2f}, id={result['top_match']['id']})"
        )

    questions = generate_questions(args.interview.read_text(), route_result=result)
    if questions:
        print(f"\n{len(questions)} follow-up question(s) before trusting this routing decision:")
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q}")
    print()

    output_dir = Path("workflows") / ("build" if decision == "build" else "adapt" if decision == "adapt" else "use") / args.interview.stem

    if decision == "build":
        live = result.get("live_registry_candidates")
        if live:
            print(f"Local catalog found nothing, but the live IWC registry has {len(live)} candidate(s)")
            print("(via the real galaxy-mcp MCP server, not our curated catalog) -- reviewing")
            print("these before spending an LLM call to build from scratch:\n")
            for i, c in enumerate(live, 1):
                print(f"  {i}. {c['name']}  (BM25 score {c['match_score']})")
                print(f"     {c['trsID']}")
            print("\nNot auto-building. Review these first, e.g.:")
            print(f"  scripts/galaxy_mcp_client.py details '{live[0]['trsID']}'")
            print("If none actually fit, re-run with --force-build to fall back to LLM generation.")
            if not args.force_build:
                return
            print("\n--force-build set, proceeding to LLM generation anyway.\n")
        subprocess.run([sys.executable, "scripts/build_workflow.py", str(args.interview), "--output-dir", str(output_dir)], check=True)
        return

    if not result["top_match"]:
        print("error: decision is not 'build' but no top_match is present -- this shouldn't happen", file=sys.stderr)
        sys.exit(1)

    workflow_path = fetch(result["top_match"]["id"], output_dir)
    print(f"fetched {workflow_path} (from {result['top_match']['url']})\n")

    validate_result = subprocess.run(["scripts/validate_workflow.sh", str(workflow_path)])

    if decision == "use":
        if validate_result.returncode != 0:
            print("\nValidation failed on a workflow routed as 'use' -- treat this as a routing", file=sys.stderr)
            print("or catalog problem, not a green light to use it anyway.", file=sys.stderr)
            sys.exit(validate_result.returncode)
        print(f"\nReady to test: scripts/run_workflow_tests.sh {workflow_path}")
        return

    # decision == "adapt"
    print(f"\nBase workflow fetched to {output_dir}/. This is the 'adapt' path's starting point.")
    print("Next: author a change spec (see scripts/adapt_workflow.py's docstring for the format)")
    print(f"describing what the researcher actually wants changed, then run:")
    print(f"  scripts/adapt_workflow.py propose {workflow_path} <change_spec.json>   # review the diff")
    print(f"  scripts/adapt_workflow.py apply   {workflow_path} <change_spec.json> {output_dir}/adapted.ga")


if __name__ == "__main__":
    main()
