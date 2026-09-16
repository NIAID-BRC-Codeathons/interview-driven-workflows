#!/usr/bin/env python3
"""Build a new Galaxy workflow from scratch via an LLM, then mechanically
grade it -- never accept generated output that hasn't been validated.

This is the one part of the pipeline that cannot be made fully "real" without
infrastructure this repo doesn't have: the Galaxy Workflow Foundry (an agent
grounded live against the Galaxy Tool Shed) isn't wired up here. What this
script does instead, honestly: call an LLM (Claude) to generate a workflow,
then immediately run it through scripts/validate_workflow.sh -- which DOES
check tool ids/versions against the real, live Galaxy Tool Shed. A workflow
that fails validation is reported as a failure, not silently written as
"done". This is deliberately the smallest thing that respects PROPOSAL.md's
core principle ("every output is graded by a program") rather than trusting
the LLM's output on its own, which is exactly the "confident fabrication"
failure mode Goal 5 warns about.

Requires:
  - `pip install -r requirements.txt` (for the `anthropic` package)
  - Anthropic credentials: ANTHROPIC_API_KEY env var, or `ant auth login`
    (see the Claude API skill/docs for the full credential resolution order)
  - Network access to api.anthropic.com -- and this makes a real, billed API
    call each time it runs.

Known limitation: even a validation pass here only means the generated
workflow's tool ids/versions/connections are structurally sound -- it does
NOT mean the workflow does the right analysis. That requires an executed
test run (scripts/run_workflow_tests.sh) against real data with expected
outputs, which this script does not attempt automatically.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    import anthropic
except ImportError:
    anthropic = None

MODEL = "claude-opus-5"

SYSTEM_PROMPT = """You are generating a Galaxy native workflow file (.ga format --
Galaxy's native JSON workflow format, `format-version` 0.1 or later) from a
researcher's free-text analysis request.

Output ONLY a single JSON object in one fenced ```json code block, no other text
before or after it. The JSON must be a valid Galaxy .ga workflow:

- top-level keys: "a_galaxy_workflow" (true), "format-version" (e.g. "0.1"),
  "name", "annotation", "tags" (list), "steps" (object keyed by stringified
  step index starting at "0")
- an input step: {"type": "data_input", "id": <int>, "label": ..., "inputs": [...],
  "outputs": [...], "position": {"left": <int>, "top": <int>}}
- a tool step: {"type": "tool", "id": <int>, "tool_id": <a REAL, specific Galaxy
  Tool Shed id you are confident exists, of the form
  "toolshed.g2.bx.psu.edu/repos/<owner>/<repo>/<tool>/<version>">,
  "tool_version": <string>, "tool_state": <a JSON-encoded STRING, not a nested
  object -- this is a real Galaxy format quirk, tool_state is always a string>,
  "input_connections": {...}, "outputs": [...], "position": {...}}

Only use tools you are genuinely confident exist with that exact id and version.
Prefer a small number of well-known, widely-used tools over inventing anything
specific-sounding you are not sure about -- this workflow is checked against the
real, live Galaxy Tool Shed immediately after you generate it, and a plausible
but nonexistent tool id is reported as a failure, not accepted."""


def generate(description: str) -> dict:
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL,
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": description}],
    )
    text = next((b.text for b in response.content if b.type == "text"), "")
    match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    raw = match.group(1) if match else text
    return json.loads(raw)


def build(interview_path: Path, output_dir: Path) -> Path:
    description = interview_path.read_text()
    workflow = generate(description)
    output_dir.mkdir(parents=True, exist_ok=True)
    workflow_path = output_dir / "workflow.ga"
    workflow_path.write_text(json.dumps(workflow, indent=2))
    return workflow_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("interview", type=Path, help="Path to an interview file (plain text description)")
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    if anthropic is None:
        print("error: the 'anthropic' package is not installed. Run: pip install -r requirements.txt", file=sys.stderr)
        sys.exit(2)

    output_dir = args.output_dir or Path("workflows/build") / args.interview.stem

    try:
        workflow_path = build(args.interview, output_dir)
    except anthropic.AuthenticationError:
        print(
            "error: no valid Anthropic credentials found. Set ANTHROPIC_API_KEY, "
            "or run `ant auth login`.",
            file=sys.stderr,
        )
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(
            f"error: model output was not valid JSON ({e}). This is exactly the "
            "'confident fabrication' failure mode PROPOSAL.md's Goal 5 warns about "
            "-- do not retry blindly; inspect what the model actually said.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"wrote {workflow_path}")
    print("Generated by an LLM with no live tool-registry grounding during generation --")
    print("this is a v0 stand-in for Foundry's real build path. Validating now:\n")

    result = subprocess.run(["scripts/validate_workflow.sh", str(workflow_path)])
    if result.returncode != 0:
        print(
            "\nVALIDATION FAILED. Per PROPOSAL.md's core principle, a workflow that "
            "does not pass static validation is not a usable output no matter how "
            "plausible it looks -- do not treat this file as ready to use.",
            file=sys.stderr,
        )
        sys.exit(result.returncode)

    print("\nStatic validation passed. Still needs an executed test run")
    print("(scripts/run_workflow_tests.sh) before this counts as a validated workflow --")
    print("static validation alone does not confirm the workflow does the right analysis.")


if __name__ == "__main__":
    main()
