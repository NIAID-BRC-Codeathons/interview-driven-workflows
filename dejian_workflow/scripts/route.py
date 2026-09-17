#!/usr/bin/env python3
"""Goal 1: decide use / adapt / build for a given interview.

Real v0 implementation: scores the interview's description against the
curated bacteria/virus catalog (search_pipeline_catalog.py) and thresholds
the top match's confidence into a use/adapt/build decision.

Thresholds were picked by eyeballing confidence scores on a handful of
example descriptions (see docs/galaxy-bacteria-virus-pipelines.marp.md) --
they are a starting point to argue with, not a calibrated cutoff. A strong,
specific match (multiple rare/distinctive keywords) scores ~0.4-0.5; a
correct-but-terse match (one or two specific terms) scores ~0.15-0.25; noise
from incidental shared words (e.g. "sample," "outbreak") sits under ~0.1.

Caveat: the LOCAL decision below only searches the curated ~20-workflow
catalog, not the live IWC registry -- scripts/search_pipeline_catalog.py's
"no match" message says this explicitly. As of this version, when the local
decision is "build", route() also checks the real, live IWC registry via
scripts/galaxy_mcp_client.py (a genuine MCP client talking to the actual
galaxyproject/galaxy-mcp server -- not a reimplementation). This has
concretely caught real gaps: "differential expression analysis of mouse
RNA-seq data" -- used elsewhere in this repo as the canonical "nothing
matches" example -- gets zero local catalog hits but three real, relevant
matches from the live registry (see eval/results/ for the demonstration).

The live check degrades gracefully: if galaxy-mcp isn't installed or the
subprocess/network call fails, `live_registry_candidates` is just omitted
(logged at low volume to stderr) -- it never breaks local routing. It also
never silently upgrades the decision: BM25 match scores aren't confidence-
calibrated the way the local catalog's IDF-ratio is, so a live hit is
surfaced as evidence for a human (or the not-yet-built interview loop) to
act on, not auto-converted into "use"/"adapt".

This function does NOT surface where its own decision might be wrong --
see generate_followup_questions.py (Goal 4) for that, which consumes this
function's output and turns unconfirmed assumptions into questions for the
researcher rather than routing silently.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from search_pipeline_catalog import match  # noqa: E402

try:
    from galaxy_mcp_client import recommend_workflows
except ImportError:
    recommend_workflows = None

USE_THRESHOLD = 0.35
ADAPT_THRESHOLD = 0.15


def _check_live_registry(description: str, top_n: int) -> list[dict] | None:
    """Best-effort live IWC registry check via the real galaxy-mcp server.

    Returns None (not an empty list) on any failure, so callers can tell
    "checked, found nothing" apart from "couldn't check at all".
    """
    if recommend_workflows is None:
        return None
    try:
        return recommend_workflows(description, limit=top_n)
    except Exception as e:
        print(f"route.py: live IWC registry check skipped ({e})", file=sys.stderr)
        return None


def route(description: str, top_n: int = 5) -> dict:
    """Return the routing decision plus the evidence behind it.

    {
      "decision": "use" | "adapt" | "build",
      "top_match": <catalog entry + _confidence + _matched, or None>,
      "candidates": [<catalog entry>, ...],  # top_n, for human review
      "live_registry_candidates": [<galaxy-mcp result>, ...] or None,
          # only populated when decision == "build"; None means either
          # "not checked" (galaxy-mcp unavailable) or the check failed --
          # not the same as "checked, found nothing" (an empty list)
    }
    """
    candidates = match(description, top_n=top_n)

    if not candidates:
        return {
            "decision": "build",
            "top_match": None,
            "candidates": [],
            "live_registry_candidates": _check_live_registry(description, top_n),
        }

    top = candidates[0]
    if top["_confidence"] >= USE_THRESHOLD:
        decision = "use"
    elif top["_confidence"] >= ADAPT_THRESHOLD:
        decision = "adapt"
    else:
        decision = "build"

    result = {"decision": decision, "top_match": top, "candidates": candidates}
    if decision == "build":
        result["live_registry_candidates"] = _check_live_registry(description, top_n)
    return result


def route_interview_file(interview_path: Path, top_n: int = 5) -> dict:
    description = interview_path.read_text()
    result = route(description, top_n=top_n)
    result["interview"] = str(interview_path)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("interview", type=Path, help="Path to an interview file (plain text description)")
    parser.add_argument("--top", type=int, default=5)
    args = parser.parse_args()

    result = route_interview_file(args.interview, top_n=args.top)
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
