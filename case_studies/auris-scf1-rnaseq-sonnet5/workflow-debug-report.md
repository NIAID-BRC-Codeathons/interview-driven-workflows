# Workflow debug report — galaxy-workflow.gxwf.yml

Run: draft-manuscript-galaxy (phase 12 of PAPER → GALAXY). Inputs: `workflow-test-result.json`,
`planemo-test1-output.{json,html,log}`, `planemo-test2-output.{json,html,log}`.

## Test 1 — `kmindex_wiring_smoke_generic_fixtures` (test_index 1)

**Classification: staging failure, external defect (galaxy-tool-util / Planemo), not a
workflow-authoring defect.** No Galaxy invocation was ever created.

Evidence (`planemo-test1-output.json`, `planemo-test1.log:1782-1812`):

- `execution_problem: "'rows'"`, `status: "error"`, `invocation_details: null`, `job: null` —
  the failure happened before any invocation/job object existed.
- Exact traceback:
  `planemo/galaxy/activity.py:441 stage_in` → `galaxy/tool_util/client/staging.py:275 stage` →
  `galaxy/tool_util/cwl/util.py:388 galactic_job_json` → `:234 replacement_item` →
  `:362 replacement_collection` → `KeyError: 'rows'`, i.e.
  `kwds["rows"] = value["rows"]` unconditionally indexes an optional key.
- The test case's `gene_query_panel` input in `planemo-test1-output.json` is a
  `collection_type: sample_sheet` Collection with `elements` but **no `rows` key at all** —
  and this exact test file previously passed `gxwf validate-tests --workflow ... --json`
  cleanly (per `workflow-test-result.json`'s `static_validation.valid: true`), so the schema
  legitimately treats `rows` as optional.
- Contrast: test 2's `gene_query_panel` *does* carry a `rows:` block and staged past this exact
  code path without error, isolating the variable to the missing key, not a general staging bug.

This is galaxy-tool-util 25.1.2 (vendored in planemo 0.75.47), a related project, not this
workflow. It is already tracked in the feedback ledger as
`galaxy-tool-util-replacement-collection-requires-rows-key-unconditionally` (status: open).

**Recommended next step:** upstream bug report against `galaxy.tool_util.cwl.util.replacement_collection`
(use `.get("rows", {})` instead of `value["rows"]`). As a practical local workaround (not a
schema violation, just filling in an optional field defensively) the test's `sample_sheet` job
input could add an empty `rows: {}`/`rows: []` block to unblock staging without waiting on the
upstream fix — but this is an environment workaround, not something to silently "fix" in the
workflow's own logic. Route to: user/future run (apply workaround) + upstream `galaxyproject/galaxy` issue.

## Test 2 — `gene_e_j_am3_diagnostic_synthetic_lexicmap_index` (test_index 2)

**Classification: workflow-invocation refusal at request time (HTTP 400, "required tools are
not installed") — evidence points to a toolbox-state/timing artifact as the primary cause,
compounded by one genuine, platform-specific dependency-resolution failure that is a real but
separate blocker.**

### Evidence

`planemo-test2-output.json`: `execution_problem` is a `bioblend.ConnectionError: Unexpected
HTTP status code: 400` on `POST /api/workflows/961e7c4742a92de4/invocations`
(`planemo-test2.log:1775`), body:

```
err_msg: "Workflow was not invoked; the following required tools are not installed:
toolshed.g2.bx.psu.edu/repos/nml/collapse_collections/collapse_dataset (version 5.1.0),
toolshed.g2.bx.psu.edu/repos/iuc/lexicmap/lexicmap_search (version 0.9.0+galaxy1),
toolshed.g2.bx.psu.edu/repos/iuc/kmindex/kmindex_query (version 0.6.1+galaxy4),
lexicmap_streamer (version 1.0.0), flatten_gene_summary_json_to_row (version 1.0.0),
kmindex_hit_dedup_max_score (version 1.0.0),
toolshed.g2.bx.psu.edu/repos/iuc/collection_column_join/collection_column_join (version 0.0.3)"
```

`invocation_details: null`, `job: null` — this is a request-time (pre-invocation) rejection per
galaxy-workflow-invocation-failure-reference's "Request-time validation" surface; no invocation
object was ever created, so invocation-state/message fields don't apply here.

**The key finding** (`planemo-test2.log:292`):

```
galaxy.tool_shed.galaxy_install.repository_dependencies.repository_dependency_manager INFO
11:50:04,798 Skipping installation of revision 90981f86000f of repository 'collapse_collections'
because it was installed with the (possibly updated) revision 90981f86000f and its current
installation status is 'Installed'.
```

`collapse_dataset` was **already fully installed from a cached prior run and its install was
skipped entirely** — no fresh clone, no fresh dependency resolution — yet it is *still* listed
in the 400 as "not installed" 54 seconds later. A tool with a confirmed-good, pre-existing
"Installed" status being rejected rules out "genuine dependency failure" as the explanation for
*that* tool, and is the strongest evidence available that the invocation-time tool-availability
check is reading stale/incomplete toolbox state rather than reality — i.e., a toolbox-reload
race, consistent with all 7 required tools (4 real + 3 UDT) being rejected as one uniform block
regardless of each one's actual install state.

Timing: the last `reload_toolbox` control-task cycle logged completes at `11:50:13,808` (for
`collection_column_join`, cloned `11:50:10,458`); the invocation POST fires 45s later at
`11:50:58,531`. Toolbox reload dispatch is not obviously still in flight by then — so the race,
if real, is more likely in how the invocation-validation code path reads toolbox state (e.g. a
cached toolbox snapshot on the request-handling worker) than in reload latency itself.

**Separately, a real dependency-resolution failure was also observed** — 8 repeated occurrences
of (`planemo-test2.log:313-520`, no timestamps on the subprocess output but bounded between
`11:50:13,808` and `11:50:43,834`):

```
Platform: osx-arm64
Solving environment: ...working... failed
PackagesNotFoundError: The following packages are not available from current channels:
  - coreutils=8.25
```

Web search confirms this is a real, structural platform limitation, not transient: the
`coreutils=8.25` pin is an old build that conda-forge never shipped for `osx-arm64` (current/
newer `coreutils` builds do support `osx-arm64`; older exact-pinned versions like 8.25 are
`linux-64`/`osx-64`-only). This is an Apple Silicon macOS host limitation on whichever Tool Shed
wrapper(s) pin that old `coreutils` requirement — it cannot be "coded around" in the workflow;
it needs either a different install host/architecture (e.g. Rosetta/`osx-64` conda subdir), or
the wrapper's own `coreutils` requirement pin needs to be loosened upstream.

Because `collapse_dataset`'s dependencies were never touched this run (skip-install path) while
the coreutils failures occurred elsewhere in the timeline, the two problems are best read as
distinct: (1) a toolbox-availability/timing defect affecting the invocation-validation check for
all 7 tools uniformly, and (2) a real, platform-specific conda resolution failure for at least
one of the freshly-installed shed wrappers, which would block that job even if (1) were fixed.
The 3 UDTs remain independently blocked regardless of either issue — they were never in any
toolbox (`tool_dir` scanner limitation, unchanged from phase 11's finding).

**Recommended next steps:**
- UDT-loading gap (structural, unresolved): route to a future Foundry run/maintainer decision —
  `author-galaxy-tool-wrapper` or the harness needs a lowering path from `GalaxyUserTool` YAML to
  classic Galaxy tool XML (or another Planemo-supported loading mechanism) before this workflow's
  3 authored tools can ever be tested locally. Tracked: `run-workflow-test-no-mechanism-to-install-authored-galaxyusertool-udts`.
- Toolbox-reload/timing race: investigate Galaxy's `/api/tool_shed_repositories` install-status
  and the invocation-validation code path's toolbox source (cached vs. live) — a future
  `run-workflow-test`/Planemo run, not something this workflow's authors can fix. New evidence
  captured this phase (see ledger entry added below).
- `coreutils=8.25`/osx-arm64: flag to the user as an environment/platform constraint, not a code
  fix — either re-run on `osx-64`/Rosetta emulation or an x86_64 CI host, or wait for/request an
  upstream wrapper update that loosens the `coreutils` pin.
- `lexicmap_index_selection` placeholder (`"PhiX174E_J_Am3ToyIndex"`): pre-existing, documented
  deferral from `galaxy-test-plan.yml`; unreached this run because tool-install failed first —
  still the next real blocker once 1-3 above are resolved.

## Feedback ledger

Reviewed `foundry-feedback.ledger.yml` (16 prior entries). The two entries phase 11 already
filed for this run's UDT-loading gap and the `rows` KeyError already carry strong, specific
evidence and did not need re-filing or amendment.

One new entry appended (new evidence this phase, not previously captured): the collapse_dataset
"skip-install, already Installed, still rejected" finding, which is a concrete diagnostic signal
that `galaxy-workflow-invocation-failure-reference.md` doesn't currently document — id
`galaxy-workflow-invocation-check-rejects-previously-installed-tool-as-not-installed` (kind:
gap, subject: research, `galaxy-workflow-invocation-failure-reference.md`, severity: major).

## Overall assessment of the deliverable

`galaxy-workflow.gxwf.yml` + `galaxy-workflow.gxwf-tests.yml` passed static/structural
validation cleanly (`gxwf validate-tests ... --json` → `valid: true`, no errors) and phase 10's
`galaxy-workflow-validation-result.json` was clean going into testing. Neither test failure this
phase points at a wiring, collection-shape, or authoring defect in the workflow itself:

- Test 1 died in Planemo's own staging code on a legitimately-optional field — an upstream bug.
- Test 2 never got a job to run; it was refused at the API gate by what most of the evidence
  points to as toolbox/tooling infrastructure state, not the workflow's tool references (all of
  which are correctly pinned, real Tool Shed ids/versions per `galaxy-tool-pin.json`).

The workflow is structurally sound and blocked on tooling/environment gaps, not authoring
defects: no mechanism exists yet to load the 3 hand-authored UDTs into a Planemo Galaxy
toolbox, the toolbox-availability check at invocation time appears unreliable/stale in this
harness's environment, and one real Tool Shed wrapper hits a hard osx-arm64 conda-dependency
wall. None of these are fixable by further editing `galaxy-workflow.gxwf.yml` itself. The one
remaining known, already-documented workflow-level gap (`lexicmap_index_selection` placeholder)
is a legitimate, previously-deferred TODO, not a defect exposed by this run.
