# Knowledge Base

Domain guidance authored as small, individually-checkable entries and
compiled into agent instructions for the Galaxy Workflow Foundry runtime
(Goal 6). This is what turns a general workflow builder into one that's good
at pathogen genomics specifically.

- `pathogen_genomics/` — reference data conventions, BRC assembly handling,
  and the tools/analysis shapes this domain actually uses. One entry per
  concept (e.g. `assembly-selection.md`, `variant-calling-defaults.md`),
  not one giant document — entries should be small enough to cite
  individually when a failure in `eval/results/` implicates one.
  - `galaxy_pipeline_catalog.yaml` — curated catalog of ~20 bacteria/virus
    IWC workflows (organism, data type, analysis type, keywords per entry).
    This is the local decision surface `scripts/search_pipeline_catalog.py`
    matches free-text descriptions against; see `docs/galaxy-bacteria-virus-pipelines.marp.md`
    for the presented version.

Populate this reactively: when the core loop (see `scripts/`) hits a failure
that traces back to missing domain knowledge, write the entry here, then
re-run. Don't speculatively write entries for cases you haven't seen fail
yet.
