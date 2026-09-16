#!/usr/bin/env python3
"""Apply a reviewed, step-anchored change spec to an existing Galaxy workflow
(.ga) and mechanically verify that every untouched region is byte-stable.

This implements the safety property from PROPOSAL.md's "Approach" section:
  - changes are a reviewable, step-anchored list, not a regenerated file
  - untouched regions must be byte-stable -- verified here, not assumed
  - because untouched regions don't move, the original workflow's tests
    remain a meaningful regression baseline (run them with
    scripts/run_workflow_tests.sh against the output of `apply`)

This script deliberately does NOT interpret free-text change requests --
that needs an LLM/agent grounded in the workflow's actual tool_state (the
proposal's "adapt" path), which isn't wired up in this repo yet. What it
takes instead is a change spec: the *already-decided* list of edits, in the
format below. That's the natural handoff point for an LLM to produce and a
human to review before this script ever touches a file.

Change spec format (JSON list): each entry edits exactly one step, either
inside its parsed tool_state (Galaxy stores tool_state as a JSON *string*,
not a nested object -- this handles that) or a direct step-level field:

[
  {
    "step_id": "2",
    "tool_state_path": ["scannew_section", "min_id_new_allele"],
    "new_value": "95",
    "note": "raise minimum identity threshold for new allele calls"
  },
  {
    "step_id": "3",
    "step_field": "label",
    "new_value": "Aggregate results (renamed)",
    "note": "clarify step label per researcher request"
  }
]
"""

import argparse
import copy
import json
import sys
from pathlib import Path


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def _get_nested(d: dict, path: list[str]):
    for key in path:
        d = d[key]
    return d


def _set_nested(d: dict, path: list[str], value) -> None:
    for key in path[:-1]:
        d = d[key]
    d[path[-1]] = value


def _canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True)


def diff_report(workflow: dict, changes: list[dict]) -> str:
    """Human-readable, step-anchored diff -- what a reviewer reads before apply."""
    lines = []
    for change in changes:
        step_id = change["step_id"]
        step = workflow["steps"][step_id]
        label = step.get("label") or step.get("name") or f"step {step_id}"

        if "tool_state_path" in change:
            state = json.loads(step["tool_state"])
            old_value = _get_nested(state, change["tool_state_path"])
            where = ".".join(change["tool_state_path"])
        elif "step_field" in change:
            old_value = step.get(change["step_field"])
            where = change["step_field"]
        else:
            raise ValueError(f"change for step {step_id} has neither tool_state_path nor step_field")

        lines.append(f"step {step_id} ({label}) :: {where}")
        lines.append(f"  - {old_value!r}")
        lines.append(f"  + {change['new_value']!r}")
        if change.get("note"):
            lines.append(f"  rationale: {change['note']}")
        lines.append("")
    return "\n".join(lines)


def apply_changes(workflow: dict, changes: list[dict]) -> dict:
    """Return a deep-copied workflow with `changes` applied. Does not validate."""
    modified = copy.deepcopy(workflow)
    for change in changes:
        step = modified["steps"][change["step_id"]]
        if "tool_state_path" in change:
            state = json.loads(step["tool_state"])
            _set_nested(state, change["tool_state_path"], change["new_value"])
            step["tool_state"] = json.dumps(state)
        elif "step_field" in change:
            step[change["step_field"]] = change["new_value"]
        else:
            raise ValueError(f"change for step {change['step_id']} has neither tool_state_path nor step_field")
    return modified


def assert_byte_stable(original: dict, modified: dict, changed_step_ids: set) -> None:
    """Raise AssertionError if anything outside changed_step_ids differs.

    Checks every step not named in the change spec, plus every workflow-level
    field outside "steps" (name, tags, annotation, report, etc.).
    """
    for step_id in set(original["steps"]) | set(modified["steps"]):
        if step_id in changed_step_ids:
            continue
        if _canonical(original["steps"].get(step_id)) != _canonical(modified["steps"].get(step_id)):
            raise AssertionError(
                f"byte-stability violated: step {step_id} was not in the change spec but differs"
            )

    orig_outer = {k: v for k, v in original.items() if k != "steps"}
    mod_outer = {k: v for k, v in modified.items() if k != "steps"}
    if _canonical(orig_outer) != _canonical(mod_outer):
        raise AssertionError("byte-stability violated: workflow-level metadata outside 'steps' changed")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_propose = sub.add_parser("propose", help="Print a reviewable diff; writes nothing")
    p_propose.add_argument("workflow", type=Path)
    p_propose.add_argument("change_spec", type=Path)

    p_apply = sub.add_parser("apply", help="Apply a reviewed change spec, verifying byte-stability")
    p_apply.add_argument("workflow", type=Path)
    p_apply.add_argument("change_spec", type=Path)
    p_apply.add_argument("output", type=Path)

    args = parser.parse_args()
    workflow = _load_json(args.workflow)
    changes = json.loads(args.change_spec.read_text())

    if args.command == "propose":
        print(diff_report(workflow, changes))
        return

    modified = apply_changes(workflow, changes)
    changed_step_ids = {c["step_id"] for c in changes}
    try:
        assert_byte_stable(workflow, modified, changed_step_ids)
    except AssertionError as e:
        print(f"REFUSING to write output: {e}", file=sys.stderr)
        sys.exit(1)

    args.output.write_text(json.dumps(modified, indent=2))
    print(f"applied {len(changes)} change(s); byte-stability verified for all other steps.")
    print(f"wrote {args.output}")
    print("next: scripts/validate_workflow.sh, then scripts/run_workflow_tests.sh")
    print("against the ORIGINAL workflow's test file to check the regression baseline still holds.")


if __name__ == "__main__":
    main()
