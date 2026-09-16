# Workflows

Output of the routing decision (Goal 1: use / adapt / build). Every workflow
here must pass static validation and an executed Planemo test run — that's
the whole premise of the project, not an aspiration.

- `use/` — an existing published IWC workflow fetched as-is (real `.ga` +
  test file, via `scripts/fetch_iwc_workflow.py`), for a routing decision
  confident enough that no modification is proposed.
- `build/` — workflows generated from scratch via `scripts/build_workflow.py`
  (LLM-driven, since the Galaxy Workflow Foundry isn't wired up in this repo
  yet -- see that script's docstring). One subdirectory per interview, e.g.
  `build/<interview-id>/workflow.ga`.
- `adapt/` — workflows produced by modifying an existing published workflow.
  Each entry should keep:
  - the original workflow (or a pinned reference to its IWC registry
    version),
  - the step-anchored diff that was reviewed before being applied,
  - the resulting workflow,
  - the regression test results (original tests re-run against the
    modified workflow).

Byte-stability of untouched regions in `adapt/` outputs is a scored
property, not a nice-to-have — see PROPOSAL.md's "Approach" section. Don't
hand-edit files in here; regenerate them through the pipeline so the diff
stays honest.
