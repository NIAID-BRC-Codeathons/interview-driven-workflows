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

Caveat: this only searches the curated ~20-workflow catalog, not the live
IWC registry. A "build" decision here can mean either "no workflow exists"
or "no workflow is in this catalog yet" -- scripts/search_pipeline_catalog.py's
"no match" message says this explicitly; treat a build decision as a prompt
to check the catalog before trusting it as a registry-wide answer.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from search_pipeline_catalog import match  # noqa: E402

USE_THRESHOLD = 0.35
ADAPT_THRESHOLD = 0.15


def route(description: str, top_n: int = 5) -> dict:
    """Return the routing decision plus the evidence behind it.

    {
      "decision": "use" | "adapt" | "build",
      "top_match": <catalog entry + _confidence + _matched, or None>,
      "candidates": [<catalog entry>, ...],  # top_n, for human review
    }
    """
    candidates = match(description, top_n=top_n)

    if not candidates:
        return {"decision": "build", "top_match": None, "candidates": []}

    top = candidates[0]
    if top["_confidence"] >= USE_THRESHOLD:
        decision = "use"
    elif top["_confidence"] >= ADAPT_THRESHOLD:
        decision = "adapt"
    else:
        decision = "build"

    return {"decision": decision, "top_match": top, "candidates": candidates}


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
