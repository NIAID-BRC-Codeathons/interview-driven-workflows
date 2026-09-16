#!/usr/bin/env python3
"""Goal 4: turn a routing decision's silent assumptions into follow-up
questions for the researcher, instead of silently guessing.

This is deterministic and grounded in the router's own matching data (see
search_pipeline_catalog.py's "_unconfirmed_dimensions") -- not an LLM
guessing what to ask, which would need credentials this pipeline can't
assume are available (see build_workflow.py). It only surfaces gaps that
actually exist in the matching data; it does not fabricate concerns.

Known limitation: this only SURFACES the questions. There is no interactive
interview loop here to collect your answers and re-route based on them --
that's the other half of Goal 4, and doing it right needs either a human in
the loop or an LLM/MCP-grounded conversation, neither of which is wired up
in this repo. Treat this script's output as "here is what a human reviewer
should ask before trusting this routing decision," not as a closed loop.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from route import route  # noqa: E402

DIMENSION_PROMPTS = {
    "organism": (
        "This candidate assumes organism/target: {values}. Your description "
        "didn't mention a matching term -- is that correct for your data, or "
        "is the actual organism/pathogen different?"
    ),
    "data_type": (
        "This candidate assumes data type: {values}. Your description didn't "
        "specify a matching sequencing platform or data shape -- what "
        "platform and read type do you actually have (e.g. Illumina "
        "paired-end, Nanopore, amplicon vs. whole-genome)?"
    ),
    "analysis_type": (
        "This candidate performs: {values}. Your description didn't clearly "
        "state that as the goal -- is that the analysis you want, or "
        "something else?"
    ),
}

GENERIC_BUILD_QUESTIONS = [
    "What organism or pathogen is this analysis for?",
    "What sequencing platform and data type do you have (e.g. Illumina "
    "paired-end, Nanopore, amplicon vs. whole-genome)?",
    "What is the specific analysis goal (e.g. variant calling, strain "
    "typing, annotation, resistance gene detection)?",
    "Do you have a specific reference genome or database in mind, or "
    "should one be selected for you?",
]


def generate_questions(description: str, route_result: dict | None = None) -> list[str]:
    """Return a list of follow-up questions grounded in the routing result.

    Pass a precomputed route_result (from route.route()) to avoid re-scoring
    when the caller already has it; otherwise it's computed here.
    """
    route_result = route_result if route_result is not None else route(description)
    decision = route_result["decision"]
    top_match = route_result.get("top_match")

    if not top_match:
        return list(GENERIC_BUILD_QUESTIONS)

    questions = []
    for dim in top_match.get("_unconfirmed_dimensions", []):
        values = ", ".join(top_match.get(dim, [])) or "unspecified"
        questions.append(f"[{dim}] " + DIMENSION_PROMPTS[dim].format(values=values))

    if decision == "adapt":
        questions.append(
            f"[fit] '{top_match['name']}' is the closest catalog match but only "
            f"a partial one (confidence {top_match['_confidence']:.2f}). What "
            "specifically differs between what you need and what this "
            "workflow does?"
        )

    if not questions and decision == "build":
        # top_match existed but confidence was still below the build threshold
        questions = list(GENERIC_BUILD_QUESTIONS)

    return questions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("interview", type=Path, help="Path to an interview file")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    description = args.interview.read_text()
    route_result = route(description)
    questions = generate_questions(description, route_result)

    if args.json:
        json.dump({"decision": route_result["decision"], "questions": questions}, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return

    print(f"routing decision: {route_result['decision']}")
    if not questions:
        print("No unconfirmed dimensions -- routing had no silent assumptions to surface.")
        return
    print(f"\n{len(questions)} follow-up question(s) before trusting this routing decision:\n")
    for i, q in enumerate(questions, 1):
        print(f"{i}. {q}")


if __name__ == "__main__":
    main()
