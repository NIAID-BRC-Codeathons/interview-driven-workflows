# Foundry run review — draft-manuscript-galaxy

Triage of `foundry-feedback.ledger.yml` for run `draft-manuscript-galaxy`, produced by
`report-foundry-run-feedback`. All upstream reports target `galaxyproject/foundry`, including
those whose root cause is a related project.

- Triaged: 2026-09-18
- Ledger: `<run>/foundry-feedback.ledger.yml` (25 entries, all `status: open`)
- Foundry `main` checked at the time of triage; tracker searched across open and closed issues.

## 1. Run coverage

| Field | Value |
| --- | --- |
| `run.pipeline` | `paper-to-galaxy` |
| `run.run_slug` | `draft-manuscript-galaxy` |
| `run.status` | `complete` |

All 12 top-level phases are `status: done` **and** `feedback_checked: true`:

| # | Skill | Status | Checked |
| --- | --- | --- | --- |
| 1 | `summarize-paper` | done | yes |
| 2 | `freeform-summary-to-galaxy-interface` | done | yes |
| 3 | `freeform-summary-to-galaxy-data-flow` | done | yes |
| 4 | `compare-against-iwc-exemplar` | done | yes |
| 5 | `freeform-summary-to-galaxy-template` | done | yes |
| 6 | `advance-galaxy-draft-step` (loop, 9 iterations) | done | yes |
| 7 | branch: test-data resolution | done | yes |
| 8 | `freeform-summary-to-galaxy-test-plan` | done | yes |
| 9 | `implement-galaxy-workflow-test` | done | yes |
| 10 | `validate-galaxy-workflow` | done | yes |
| 11 | `run-workflow-test` | done | yes |
| 12 | `debug-galaxy-workflow-output` | done | yes |

**Coverage verdict: complete and fully reviewed.** Every phase reported a feedback outcome, so
the ledger's contents are evidence of what the run actually found rather than of what it failed
to look for. No phase is unchecked and none went unreported.

Four entries were raised outside the 12 pipeline phases — three by `author-galaxy-tool-wrapper`
and `freeform-summary-to-galaxy-template` during the post-pipeline deploy step, and one
(`ga-download-normalizes-tool-id-producing-workflows-that-save-but-cannot-invoke`) by
`raised_by: manual-deploy`, which is not a Mold and carries `observed_in: null`. See §3.

## 2. Ledger integrity

- **All 25 entries are `status: open`** with `issue: null`. Nothing was previously filed, so no
  entry needed its prior disposition honored.
- **One entry carries no `observed_in` block.**
  `ga-download-normalizes-tool-id-producing-workflows-that-save-but-cannot-invoke` has
  `observed_in: null` and `raised_by: manual-deploy`, a non-Mold actor. Its `subject.content_hash`
  is also `null`. Per the protocol, missing fields were not inferred; the draft for it states the
  Foundry-side locator without an observed hash.
- **Two entries carry no `subject.content_hash`** (`paper-to-test-data-no-scoping-or-toolshed-fixture-guidance`,
  `run-workflow-test-no-mechanism-to-install-authored-galaxyusertool-udts`). For both, the
  `observed_in.mold.content_hash` matches current `main` for the same path, so the subject content
  was still verifiable; the drafts cite the observed-in hash and say which one it is.
- **One entry records `content_hash: unavailable-in-cast`**
  (`run-workflow-test-no-mechanism-to-install-authored-galaxyusertool-udts`, `run-workflow-test`
  revision 6). A later entry in the same run observed revision 7 of the same Mold at
  `259675e41c65…`, which matches current `main`.
- **No blocker-severity entries.** 13 `major`, 12 `minor`; 11 `defect`, 14 `gap`.

### Redaction applied

- `author-galaxy-tool-wrapper-no-check-of-wrapped-scripts-own-declared-input-ordering-assumption`
  names a **private third-party repository** as the home of the wrapped script. That name is
  removed from the upstream draft and replaced with "a private repository outside the Foundry".
  The observation survives redaction: the Foundry-side gap is in the authoring process, not in the
  script, and is fully statable without naming the repository.
- No credentials, tokens, or user-identifying filesystem paths were found in the ledger. The
  run's `galaxy.key` file is not referenced by any entry and its contents appear nowhere.
- **Retained deliberately:** usegalaxy.org workflow, invocation, history, job, and dataset-collection
  ids. These are public-server object ids that are inert without an API key, and they are the
  evidence that lets a Galaxy maintainer correlate a report against server-side state. Removing
  them would make several defect reports unverifiable. Flagging the choice here rather than making
  it silently.

## 3. Clustering

Clustered by `subject.locator`, per protocol. **25 entries → 25 clusters. Nothing merged.**

Three locator collisions were examined and deliberately **not** merged, because each pair requests a
distinct correction:

- `content/research/galaxy-workflow-invocation-failure-reference/index.md` carries two entries.
  `galaxy-workflow-invocation-check-rejects-previously-installed-tool-as-not-installed` asks for a
  stale-toolbox-read diagnostic tell; `ga-download-normalizes-tool-id-producing-workflows-that-save-but-cannot-invoke`
  reports a deterministic unversioned-`tool_id` defect and states in its own text that it is
  distinct from the first (no timing component, reproduces on demand).
- Four entries name `jmchilton/galaxy-tool-util-ts`, but at four different components
  (ToolShed-fetch decoder, `tool-search` tokenizer, `draft-validate --json` emission,
  `validate --connections` step builder) with four unrelated fixes.
- Eight entries name Galaxy core, likewise at distinct components and endpoints.

## 4. Current-main check

Every Foundry-subject locator was resolved against `galaxyproject/foundry@main` and its content
hash compared to the ledger's.

| Locator | Ledger hash | main | Result |
| --- | --- | --- | --- |
| `content/patterns/galaxy-collection-patterns.md` | `9840d686228a` | `9840d686228a` | unchanged |
| `content/research/gxformat2-schema/index.md` | `4fe42382f996` | `4fe42382f996` | unchanged |
| `content/molds/implement-galaxy-tool-step/index.md` | `197be2d9b277` | `197be2d9b277` | unchanged |
| `content/research/galaxy-user-tool-authoring/index.md` | `365fad455369` | `365fad455369` | unchanged |
| `content/molds/paper-to-test-data/index.md` | (none; observed-in `863d7b503a77`) | `863d7b503a77` | unchanged |
| `content/molds/freeform-summary-to-galaxy-test-plan/index.md` | `9c1d56e625a5` | `9c1d56e625a5` | unchanged |
| `content/research/iwc-test-data-conventions/index.md` | `1921e9397034` | `1921e9397034` | unchanged |
| `content/molds/run-workflow-test/index.md` | (none; observed-in rev 7 `259675e41c65`) | `259675e41c65` | unchanged |
| `content/research/galaxy-workflow-invocation-failure-reference/index.md` | `e8115df6ddca` | `e8115df6ddca` | unchanged |
| `content/molds/author-galaxy-tool-wrapper/index.md` | `cced8f068cd1` | `cced8f068cd1` | unchanged |
| `content/molds/advance-galaxy-draft-step/index.md` | `c92d452f69a7` (rev 4) | `ae19f7e5f5ac` (rev 7) | **changed — inspected** |

**The one changed locator was inspected rather than assumed.** `advance-galaxy-draft-step` advanced
from revision 4 to revision 7 (`revised: 2026-09-17`). Its current text contains no occurrence of
`sample_sheet`, `sample sheet`, `param_value_from_file`, or any scalar-parameter-wiring rule, so the
correction requested by `lexicmap-search-sample-sheet-column-to-scalar-port-defect` is **not**
present on main. The observation is **not** marked fixed; its draft records both the observed hash
(rev 4) and the current successor hash (rev 7), so a maintainer reviews the live text.

The two `package://@galaxy-foundry/gxwf-foundry#…` schema subjects are package exports, not
repository paths; their ledger hashes are carried into the drafts as observed identity without a
path-based main comparison.

Related-project subjects (11 entries) have no Foundry locator and no hash. Per protocol, the
main check was skipped for them rather than invented.

**No observation was marked fixed.** Nothing in current Foundry source contains the requested
correction.

## 5. Duplicate search

Searched `galaxyproject/foundry` across open and closed issues by canonical locator, subject label,
and correction. Three matches found; all three are **open**, so each becomes a comment draft rather
than a second issue.

| Cluster | Match | Disposition |
| --- | --- | --- |
| `galaxy-workflow-import-enforces-undocumented-per-field-length-limit-on-step-doc` | **#564** (open) — same defect: step `doc:` length crashes live Galaxy import, no static check catches it | **comment-draft** |
| `gxwf-draft-validate-json-flag-emits-non-json-diagnostics-on-stdout` | **#548** (open) — explicitly reports this same routing half of upstream `galaxy-tool-util-ts#166` as still present | **comment-draft** |
| `galaxy-user-tool-authoring-missing-element-identifier-expression` | **#468** (open) — same authoring-reference surface, same expression-form table that the issue already faults | **comment-draft** |

On #564 the run contributes a materially different measurement and a **conflicting threshold**:
#564 bisected the limit to between 3900 and 3999 characters; this run bisected it to exactly 2048
on usegalaxy.org 26.1.2.dev0. Both cannot describe one fixed constant, so the comment draft raises
that discrepancy rather than merely seconding the report.

Near misses examined and rejected as duplicates, cross-referenced in the drafts instead:

- **#266** (closed) — casting drops vendored `.yml`/`.myst` companions. Mechanically adjacent to the
  pattern-MOC cluster but a different packaging path (sidecar files vs. wiki-linked sibling pages).
  The closed fix does not cover it.
- **#550** (closed) — `tool-search` returns duplicate rows. Same command as the repo-slug cluster,
  different defect (dedup vs. tokenizer scoring). Not resolved by that fix.
- **#185** (closed) — verify the gxformat2 importer preserves `column_definitions`. Import-side; the
  test-data cluster is about the `rows:` job-input shape. Distinct.
- **#448**, **#504**, **#505**, **#284**, **#116**, **#48**, **#51**, **#191**, **#553**, **#566**,
  **#552** — adjacent scope, none requesting the same correction.

**#566** ("Needs better guidance for importing to a real galaxy instance") deserves its own note. It
is an open, unanswered *request* for exactly the guidance five of this run's deploy-time clusters
produced empirically (frame-comment `position`/`size`, `/api/unprivileged_tools` registration,
`tool_uuid` injection, `exact_tools`/`allow_missing_tools`, versioned `tool_id`). Those five remain
separate issue drafts because they are five distinct corrections against four different components —
but a sixth draft is included that answers #566 directly and links them, so the request is closed out
rather than left standing beside five issues that happen to contain its answer.

## 6. Dispositions

| # | Cluster (entry id) | Sev | Disposition |
| --- | --- | --- | --- |
| 1 | `collection-pattern-mocs-ship-without-referenced-pages` | minor | issue-draft |
| 2 | `gxformat2-schema-missing-nested-in-key-convention` | major | issue-draft |
| 3 | `tool-util-cli-toolshed-fetch-rejects-real-filtered-list-collection-output` | major | issue-draft |
| 4 | `implement-galaxy-tool-step-udt-binding-undocumented` | minor | issue-draft |
| 5 | `galaxy-user-tool-authoring-missing-element-identifier-expression` | minor | **comment-draft → #468** |
| 6 | `gxwf-tool-search-underscore-repo-slug-query-zero-hits` | minor | issue-draft |
| 7 | `gxwf-draft-validate-json-flag-emits-non-json-diagnostics-on-stdout` | minor | **comment-draft → #548** |
| 8 | `paper-to-test-data-no-scoping-or-toolshed-fixture-guidance` | minor | issue-draft |
| 9 | `galaxy-workflow-test-plan-schema-fixture-required-for-scalar-typed-params` | minor | issue-draft |
| 10 | `freeform-summary-to-galaxy-test-plan-silent-on-concrete-draft-and-test-data-refs-inputs` | minor | issue-draft |
| 11 | `tests-format-job-schema-has-no-path-to-an-intermediate-step-input-port` | major | issue-draft |
| 12 | `tests-format-schema-silent-on-sample-sheet-column-definitions-shape` | minor | issue-draft |
| 13 | `galaxy-workflow-frame-comments-missing-position-size-rejected-by-real-galaxy-import` | major | issue-draft |
| 14 | `gxwf-validate-connections-flag-crashes-uncaught-on-format2-dict-shaped-step-in` | major | issue-draft |
| 15 | `run-workflow-test-no-mechanism-to-install-authored-galaxyusertool-udts` | major | issue-draft |
| 16 | `galaxy-tool-util-replacement-collection-requires-rows-key-unconditionally` | major | issue-draft |
| 17 | `galaxy-workflow-invocation-check-rejects-previously-installed-tool-as-not-installed` | major | issue-draft |
| 18 | `galaxy-udt-registration-real-endpoint-is-unprivileged-tools-not-dynamic-tools` | major | issue-draft |
| 19 | `galaxy-workflow-import-enforces-undocumented-per-field-length-limit-on-step-doc` | major | **comment-draft → #564** |
| 20 | `galaxy-unprivileged-tools-lint-crashes-on-integer-input-default-value-zero` | minor | issue-draft |
| 21 | `gxformat2-step-schema-does-not-model-tool-uuid-for-dynamic-tool-resolution` | major | issue-draft |
| 22 | `lexicmap-search-sample-sheet-column-to-scalar-port-defect` | major | issue-draft (hash moved rev 4→7) |
| 23 | `galaxy-workflow-update-exact-tools-defaults-true-and-discards-per-step-error-detail` | major | issue-draft |
| 24 | `author-galaxy-tool-wrapper-no-check-of-wrapped-scripts-own-declared-input-ordering-assumption` | major | issue-draft (redacted) |
| 25 | `ga-download-normalizes-tool-id-producing-workflows-that-save-but-cannot-invoke` | major | issue-draft |
| — | deploy-guidance synthesis answering #566 | — | **comment-draft → #566** |

**Totals: 22 new-issue drafts, 4 comment drafts, 0 fixed, 0 duplicate-closed, 0 local-only, 0 wontfix.**

## 7. Summary

A complete, fully-reviewed run whose feedback is unusually deployment-heavy: 11 of 25 observations
were only reachable by pushing the finished workflow at a real Galaxy instance, and 8 of those are
Galaxy-core or harness-CLI defects rather than Foundry content gaps. The pipeline's own static gates
(`gxwf validate`, `gxwf draft-validate --concrete`) passed clean on a workflow that could not be
imported, could not be invoked once imported, and contained a wiring defect
(`sample_sheet` column → scalar tool port) that no local check can currently catch. That gap between
"passes every Foundry gate" and "runs on real Galaxy" is the through-line, and it is the same gap
open issue #566 is asking about.

Nothing in the ledger has been fixed upstream since the run. One Mold changed on main but not in the
respect this run faulted. Three observations land on existing open issues and are drafted as
comments; the rest are new.

Per protocol, no remote mutation has been performed. `foundry-issue-drafts.md` holds the bodies;
filing awaits explicit confirmation of the exact set, after which the corresponding ledger entries
are updated to `filed` with their issue URLs.
