# Foundry issue drafts — run `draft-manuscript-galaxy`

Triaged from `<run>/foundry-feedback.ledger.yml` by `report-foundry-run-feedback`. Every draft below
targets `galaxyproject/foundry`, including those whose root cause is a related project — the run
context lives here and a maintainer forwards from here.

Each posted body begins with the required attribution line. Nothing has been posted; see
`foundry-run-review.md` §6 for dispositions.

---

# A. New-issue drafts

## A1 — Pattern MOCs are cast without the pattern pages they point at

**Locator:** `content/patterns/galaxy-collection-patterns.md` (and siblings
`galaxy-conditionals-patterns.md`, `galaxy-tabular-patterns.md`)
**Observed hash:** `9840d686228a254766611196f2be03b2a66119281322c6373ce082cd08e78717` — unchanged on `main`
**Raised by:** `freeform-summary-to-galaxy-template` (rev 6, `0a95f8c04465…`)
**Entry:** `collection-pattern-mocs-ship-without-referenced-pages` · gap · minor

> Posted by an AI assistant on scottcain's behalf.
>
> ## Summary
>
> The Galaxy pattern MOCs cast into a skill bundle as index pages only. `galaxy-collection-patterns.md`,
> `galaxy-conditionals-patterns.md`, and `galaxy-tabular-patterns.md` all carry frontmatter
> `pattern_kind: moc` and a list of 15–20 wiki-link names each — `[[fan-in-bundle-consume-and-flatten]]`,
> `[[collection-unbox-singleton]]`, `[[manifest-to-mapped-collection-lifecycle]]`,
> `[[tabular-concatenate-collection-to-table]]` and so on. None of the referenced leaf pattern pages
> are packaged anywhere in the bundle's `references/` tree, and per the MOCs' own descriptions those
> leaves are where the worked recipe, the concrete `tool_id`, and the state live.
>
> The result is a reference that cannot be resolved by the skill that loads it. A cast skill is told
> in its own Runtime Notes to "use only files packaged in this skill bundle and user-supplied
> artifacts", so a pattern *name* is all it can ever obtain — with no path to a `tool_id` or a worked
> state.
>
> ## Evidence
>
> From a `pipeline-paper-to-galaxy` run. Resolving concrete tool identities for the run's
> fan-in / flatten / tabular-bridge steps (`Collapse Collection`, `__FLATTEN__`,
> `collection_column_join`) succeeded only because a *different* artifact from an earlier phase,
> `iwc-comparison-notes.md`, happened to quote inline gxformat2 excerpts naming those tools.
>
> Had that artifact not carried those excerpts, the packaged collection/tabular MOCs — the exact
> on-demand references the Mold's own SKILL.md directs to for this situation — would have yielded a
> name and nothing else, forcing every such step to the Deferred tier even though a concrete built-in
> exists for each.
>
> ## Expected
>
> Either package the linked pattern pages alongside their MOC, as the bundle already does for other
> reference kinds (e.g. `galaxy-workflow-draft-format.md`), or carry the concrete `tool_id` / worked
> state inline in the MOC entries themselves — so a name resolves to a usable recipe from packaged
> content alone.
>
> ## Related
>
> #266 (closed) fixed an adjacent packaging path — vendored `.yml`/`.myst` companions of a single
> note — but not wiki-linked sibling pages, so this is not covered by it. Also adjacent: #504, #505, #284.

---

## A2 — `gxformat2-schema` documents nested `state` but not nested `in:` key addressing

**Locator:** `content/research/gxformat2-schema/index.md`
**Observed hash:** `4fe42382f99655115c53c1afde0da0d0556ad77984da7d0ffa8ab725ea260aa3` — unchanged on `main`
**Raised by:** `advance-galaxy-draft-step` (rev 4, `c92d452f69a7…`)
**Entry:** `gxformat2-schema-missing-nested-in-key-convention` · gap · major

> Posted by an AI assistant on scottcain's behalf.
>
> ## Summary
>
> `gxformat2-schema` documents how a step's `state` nests conditionals and sections as plain nested
> YAML (its `state` vs `tool_state` section). It documents no companion convention for the step's
> `in:` connections dict: how to address a nested conditional test-parameter branch, or a section
> child, as a connection target. No packaged reference in `advance-galaxy-draft-step`'s,
> `implement-galaxy-tool-step`'s, or `repair-galaxy-draft-topology`'s bundles covers it either.
>
> ## Evidence
>
> Implementing `lexicmap_search`
> (`toolshed.g2.bx.psu.edu/repos/iuc/lexicmap/lexicmap_search` 0.9.0+galaxy1) required wiring
> workflow inputs onto a `gx_conditional`'s case-owned parameter (`lexicmap_index`, under
> `db_opts_selector: db`) and onto five `gx_section` children of `advanced_settings`.
>
> None of the run's loaded, packaged references named or demonstrated the `|`-joined `in:` key form
> those bindings need (`db_opts|lexicmap_index`, `advanced_settings|align_min_match_pident`). It was
> inferred from general Galaxy/gxformat2 familiarity — outside any packaged bundle content, which the
> skill's own Runtime Notes direct against.
>
> ## Expected
>
> Extend `gxformat2-schema` with an explicit subsection on `in:` key addressing for nested tool state:
> the pipe-delimited path convention for conditional-branch and section-child parameters, mirroring
> the existing `state`-nesting subsection. Include it in `implement-galaxy-tool-step`'s packaged
> references — the leaf Mold that actually performs this binding — not only as an assumed convention.

---

## A3 — ToolShed-fetch decoder rejects a real IUC wrapper's filtered list-collection output

**Locator:** `https://github.com/jmchilton/galaxy-tool-util-ts` (packages/cli, `@galaxy-tool-util/cli@1.8.1`)
**Subject kind:** related-project (no Foundry hash)
**Raised by:** `advance-galaxy-draft-step` (rev 4, `c92d452f69a7…`)
**Entry:** `tool-util-cli-toolshed-fetch-rejects-real-filtered-list-collection-output` · defect · major

> Posted by an AI assistant on scottcain's behalf.
>
> ## Summary
>
> `galaxy-tool-cache add` / `summarize` cannot fetch or parse a real, currently-published IUC Tool
> Shed wrapper — `toolshed.g2.bx.psu.edu/repos/iuc/kmindex/kmindex_query` — for any galaxy-suffixed
> version. The ToolShed-fetch-to-`ParsedTool` decoder raises at `outputs[1].structure: is missing`
> against the `parsedToolSchema`'s collection-output branch.
>
> Reproduced for 0.6.0+galaxy1, 0.6.0+galaxy2, 0.6.1+galaxy2, 0.6.1+galaxy3, 0.6.1+galaxy4, and
> 0.6.1+galaxy5. Only the repo's original unsuffixed `0.6.0` parses — the version that predates the
> wrapper's `<collection type="list"><filter>…</filter><discover_datasets …/></collection>` output,
> added by tools-iuc PR #8208. `add --galaxy-url https://usegalaxy.org` fails the same way, plus a
> second `inputs is missing` error on that path.
>
> ## Evidence
>
> Reproduced while pinning `kmindex_query` at tool_version 0.6.1+galaxy4, changeset `b6fa25b6b436`.
> Root-caused by fetching the wrapper's real upstream XML at the exact matching changeset (the Tool
> Shed API's own `remote_repository_url` pointed at `galaxyproject/tools-iuc` `tools/kmindex`; commit
> `7681be7f40` on that path declares `<tool … version="@TOOL_VERSION@+galaxy4">`, an exact match) and
> comparing its `<outputs>` against the successfully-cached bare-`0.6.0` ParsedTool JSON, which lacks
> the collection output entirely.
>
> Worked around by hand-reconstructing the tool summary's `parsed_tool`/`input_schemas` from that
> verified upstream XML instead of the normal automated path.
>
> ## Expected
>
> The decoder should populate `structure` (collection_type / discover_datasets / etc.) for a
> `<collection type="list">` output that declares `discover_datasets` directly and has no
> `structured_like`/rules — an ordinary, common IUC wrapper shape — rather than failing the whole
> fetch. A second, related lossiness worth tracking: the sibling `<filter>` block has no field in the
> schema at all.
>
> Note the asymmetry in current behavior: `gxwf draft-validate` already degrades this failure
> gracefully to `skip_tool_not_found`, which is right for validate. `galaxy-tool-cache add`/`summarize`
> have no such degrade and simply cannot produce a manifest for a real, in-production wrapper,
> blocking the automated discover → summarize → implement path for any step that uses it.
>
> ## Related
>
> #548 and upstream `galaxy-tool-util-ts#166` concern the *diagnostic* produced when a ParsedTool
> decode fails (its routing and its size). This issue is about the decode failing at all for this
> wrapper shape. Worth confirming against #166 whether the underlying schema gap was in its scope.

---

## A4 — `implement-galaxy-tool-step` documents no binding convention for an authored UDT

**Locator:** `content/molds/implement-galaxy-tool-step/index.md`
**Observed hash:** `197be2d9b27741c3f258092f8392654369d1ca234d7fad492387ff69d656292b` — unchanged on `main` (rev 9)
**Raised by:** `advance-galaxy-draft-step`
**Entry:** `implement-galaxy-tool-step-udt-binding-undocumented` · gap · minor

> Posted by an AI assistant on scottcain's behalf.
>
> ## Summary
>
> `summarize-galaxy-tool` states in its own Inputs section that "Authored UDTs from
> `author-galaxy-tool-wrapper` bypass this Mold" — correctly routing a locally-authored
> `GalaxyUserTool` around tool-summary generation. Nothing downstream documents what happens next.
>
> `implement-galaxy-tool-step` declares only `galaxy-tool-summary` as an input, never a
> `galaxy-user-tool-definition`, and its step 2 ("Bind to the tool summary") covers only a
> Tool-Shed-pinned wrapper or a bare/stock built-in id. There is no documented convention for
> populating a step's `tool_id` / `tool_version` / `state` when the resolved wrapper is an authored UDT.
>
> ## Evidence
>
> A UDT was authored for a step with a confirmed Tool Shed discovery miss. Absent any documented
> convention, the binding proceeded by analogy to the bare/stock-id case: `tool_id` = the UDT's own
> `id`, `tool_version` = its `version`, no `tool_shed_repository` block.
>
> `gxwf draft-validate --concrete` accepted it (`draft valid`, `Concrete: OK`) — but the accept is
> hollow: the `tool_id` triggered a live Tool Shed lookup that 404'd and was downgraded to
> `skip_tool_not_found`, the same non-fatal bucket used for an unrelated tool whose fetch failed for
> network reasons. The step's ports and state were never checked against the UDT's own declared
> contract. The convention used happened to pass; nothing confirmed it was right.
>
> ## Expected
>
> Extend `implement-galaxy-tool-step`'s declared Inputs to include `galaxy-user-tool-definition` as an
> alternate input when the discover-or-author branch fell through to authoring, and add a procedure
> sub-case for binding a step to a UDT: what `tool_id`/`tool_version` hold, that no
> `tool_shed_repository` block applies, and how the UDT's declared `inputs`/`outputs` names become the
> step's `in:`/`out:` port names — at the level of detail already given for the other two cases.

---

## A5 — `gxwf tool-search` returns zero hits for a literal Tool Shed repo slug

**Locator:** `https://github.com/jmchilton/galaxy-tool-util-ts` (packages/cli, `gxwf tool-search`, `@galaxy-tool-util/cli@1.10.1`)
**Subject kind:** related-project (no Foundry hash)
**Raised by:** `advance-galaxy-draft-step`
**Entry:** `gxwf-tool-search-underscore-repo-slug-query-zero-hits` · defect · minor

> Posted by an AI assistant on scottcain's behalf.
>
> ## Summary
>
> `gxwf tool-search "collapse_collections"` — the literal Tool Shed repo slug for
> `toolshed.g2.bx.psu.edu/repos/nml/collapse_collections` — returns `No hits for query:
> collapse_collections` and exits 2. The space-joined form, `"collapse collections"`, also returns
> zero. Only a differently-worded query finds it: `"nml collapse"` (owner plus one word) surfaces it
> at rank 3 of 5, and `"Collapse Collection"` (the display name, not the repo or id) at rank 1 of 2.
>
> ## Evidence
>
> Reproduced while resolving a step's wrapper during a per-step draft loop. All four queries above
> were run against the same index in the same session, with the results stated. It did not block that
> iteration — the wrapper identity was already known from the draft's own pinned `tool_id` and an
> earlier same-run resolution — but it would block or mislead a cold `discover-shed-tool` search that
> started from a repo slug, which is a common and reasonable starting point.
>
> ## Expected
>
> The query tokenizer/ranker should score a repo-slug-style query (the underscore-joined or
> space-joined form of a real `owner/repo` or `tool_id`) as at least a partial match against that
> repo's own `owner/repo` and `tool_id` fields. Finding a tool should not require already knowing its
> display name or owner.
>
> ## Related
>
> #550 (closed) bumped the pin for a different `tool-search` defect — duplicate rows via upstream
> PR #170. That fix does not address query scoring, so this is not resolved by it.

---

## A6 — `paper-to-test-data` has no scoping or upstream-fixture guidance, and is the weaker half of its own fallback chain

**Locator:** `content/molds/paper-to-test-data/index.md`
**Observed hash:** ledger carries no subject hash; `observed_in` rev 2 = `863d7b503a77…`, which matches `main`
**Raised by:** `paper-to-test-data`
**Entry:** `paper-to-test-data-no-scoping-or-toolshed-fixture-guidance` · gap · minor

> Posted by an AI assistant on scottcain's behalf.
>
> ## Summary
>
> `paper-to-test-data`'s SKILL.md is a one-paragraph procedure — read `freeform-summary`, derive test
> inputs and outputs — with no packaged Load-On-Demand references and no guidance for the ordinary
> case this run hit: the paper's own named datasets are production/external-service scale and cannot
> become a fast fixture as named.
>
> Its next-in-chain sibling, `find-test-data`, packages exactly that guidance:
> `references/notes/iwc-test-data-conventions.md`'s "small is a documented subset of a real source,
> not a fabricated stand-in" rule, plus an explicit step to search IWC and Tool Shed fixtures when the
> source's own data is the wrong shape or scale.
>
> ## Evidence
>
> Run head-to-head on the same `freeform-summary`. That summary names 109 kmindex Logan shards and up
> to 25 LexicMap Logan indices as the workflow's reference-data universe, all hosted only at
> production scale. `paper-to-test-data`'s procedure and references offered no path to anything
> smaller — it could only restate gaps the summary had already flagged.
>
> `find-test-data`'s packaged convention, applied to the same task, led directly to real,
> already-CI-tested fixtures in the pinned tools' own Tool Shed test-data directories
> (`galaxyproject/tools-iuc` `tools/kmindex/test-data`, `tools/lexicmap/test-data` — `kmindex_query.xml`
> test #6, `lexicmap.xml` tests #3/#4/#6), usable as structural smoke-test data for both hard steps.
>
> Not blocking, since the harness's branch protocol tries both skills in order. But for this
> workflow's two hardest inputs, `paper-to-test-data` contributed nothing beyond a re-read of the
> summary.
>
> ## Expected
>
> Either package the same scoping-down / prefer-upstream-fixture guidance `find-test-data` carries, so
> this Mold is not systematically the weaker half of its own declared fallback chain for any workflow
> with externally-hosted reference data — or say explicitly when to fall through early ("when the
> paper's cited data is production scale and not itself a downloadable fixture, mark those inputs
> `resolved: false` and proceed to `find-test-data` without re-deriving from the same summary")
> rather than leaving that judgment to the calling harness.
>
> ## Related
>
> #448 examines the same two Molds from the CWL side (`find-test-data` used off its target axis).
> Different fault, same pair.

---

## A7 — Test-plan schema requires a file-shaped `fixture` for plain scalar workflow parameters

**Locator:** `package://@galaxy-foundry/gxwf-foundry#galaxyWorkflowTestPlanSchema`
**Observed hash:** `325e9cf1bb5e075fa818dc68868647de95389ca8df8581ee8cf1e2be61196e37`
**Raised by:** `freeform-summary-to-galaxy-test-plan` (rev 2, `9c1d56e625a5…`)
**Entry:** `galaxy-workflow-test-plan-schema-fixture-required-for-scalar-typed-params` · gap · minor

> Posted by an AI assistant on scottcain's behalf.
>
> ## Summary
>
> `JobInput.fixture` is required and always resolves to the `Fixture` `$def`, whose four fields
> (`storage`, `location`, `checksum`, `provenance`) and whose `storage` enum (`remote-url`, `in-repo`,
> `cvmfs-string`, `generated-toy`, `unresolved`, `null`) are all phrased in file- and
> collection-fixture terms.
>
> Neither the schema's field descriptions nor any packaged note — `iwc-test-data-conventions.md`,
> `planemo-asserts-idioms.md`, `galaxy-workflow-testability-design.md` — says what to do for a
> `JobInput` that is a plain typed scalar workflow parameter rather than a file or collection.
> `iwc-test-data-conventions.md` §5 covers only the CVMFS/`.loc` "bare string matching a data-table
> value" case, which is a different shape again: a reference-data selector, not an arbitrary typed
> parameter default.
>
> ## Evidence
>
> The run's workflow declares 15 inputs, 12 of them plain typed scalars with literal pinned defaults
> (e.g. `kmindex_zvalue=6`, `tiling_qc_allow_frameshifts=false`). Each needs a `JobInput` entry — the
> `TestCase` schema requires it — whose required `fixture` object has no natural file/location/checksum
> reading.
>
> Absent any documented convention, the plan used `storage: null` with the default value's string form
> in `location` and a `provenance` note pointing at the workflow default. A reasoned choice, not a
> documented one, and the next run is free to invent a different one.
>
> ## Expected
>
> Either make `fixture` conditionally optional/nullable as a whole when the input is a plain scalar
> parameter (not a file, collection, or data-table selector), or add an explicit `Fixture` convention
> for this case — so different Molds and runs stop inventing their own encoding for the same common
> situation.
>
> ## Related
>
> #116 (closed) introduced this schema; #48 (open) covers a target-neutral test-plan schema.

---

## A8 — `freeform-summary-to-galaxy-test-plan` is silent on being handed a concrete draft and resolved test-data refs

**Locator:** `content/molds/freeform-summary-to-galaxy-test-plan/index.md`
**Observed hash:** `9c1d56e625a5dd26cb7a82082ac8f4eeb7db287a626bf00e73457c8dd491ad6d` — unchanged on `main`
**Raised by:** `freeform-summary-to-galaxy-test-plan`
**Entry:** `freeform-summary-to-galaxy-test-plan-silent-on-concrete-draft-and-test-data-refs-inputs` · gap · minor

> Posted by an AI assistant on scottcain's behalf.
>
> ## Summary
>
> The Mold's declared Inputs are all template-era briefs, and its "Labels and fixtures are assumed,
> not bound" section directs `label_status: assumed` and `workflow.label_source: interface-brief` in
> every case.
>
> Nothing in the SKILL.md anticipates the case this run actually presented: by phase 8 a concrete
> gxformat2 workflow draft and a resolved `test-data-refs` artifact already existed in harness run
> state, and both were handed to this invocation as grounding context with an instruction to keep the
> plan consistent with them. The Mold gives no guidance on whether `label_source` should then be
> `draft` (a concrete draft really was read) or `interface-brief` (its only documented input class),
> nor on how `label_status` should reflect a label cross-checked against a real draft rather than
> assumed from a brief.
>
> ## Evidence
>
> The harness passed the concrete 9-step `galaxy-workflow.gxwf.yml` and `test-data-refs.json`
> alongside the Mold's normal declared inputs. Absent packaged guidance for the hybrid case, the plan
> set `workflow.label_source: draft` and `label_status: resolved` throughout — every label was in fact
> read from and matches the draft's own ids — which is a reasoned but undocumented departure from the
> Mold's stated default behavior.
>
> ## Expected
>
> Document an optional grounding-input case in this Mold's Inputs and Procedure, as
> `changeset-to-galaxy-test-plan` and the `*-test-to-galaxy-test-plan` siblings already do for their
> analogous carry-forward cases: state which `label_source` and `label_status` values apply when a
> caller also supplies the concrete draft and/or resolved test-data refs, and how far the plan may
> rely on those artifacts before that reliance should instead defer to
> `implement-galaxy-workflow-test`'s own workflow-label cross-check.

---

## A9 — tests-format has no way to put a value on an intermediate step's input port

**Locator:** `package://@galaxy-foundry/gxwf-foundry#testsFormatSchema`
**Observed hash:** `ff0de5041f4c3de0ab7abe9e7555c5a7120665b077f42661461301b0fb26f372`
**Raised by:** `implement-galaxy-workflow-test` (rev 8, `966c486ccda2…`)
**Entry:** `tests-format-job-schema-has-no-path-to-an-intermediate-step-input-port` · gap · major

> Posted by an AI assistant on scottcain's behalf.
>
> ## Summary
>
> A phase-9 task instruction directed constructing a synthetic LexicMap hits TSV and wiring it as the
> `lexicmap_results` input feeding a downstream QC step, so that step's assertions would be checkable
> end-to-end. But `lexicmap_results` is not a top-level workflow input — it is wired to an internal
> step output.
>
> The tests-format `Job` `$def` (`TestJob.job`) is `additionalProperties: <value-types>` with no
> structural provision for keying a value to anything but a top-level workflow input label, and the
> packaged `planemo-workflow-test-architecture.md` / `planemo-asserts-idioms.md` notes describe
> Planemo's `job:` block exclusively in those terms. There appears to be no tests-format mechanism to
> inject a value onto an intermediate step's input port in a whole-workflow test.
>
> This is a Mold being directed to do something the format cannot express.
>
> ## Evidence
>
> Confirmed by reading `tests-format.schema.json`'s `Job`/`TestJob` `$defs` directly: job keys bind
> workflow-level input labels only. The affected test case could not wire its synthetic hits TSV onto
> the intended port. The fixture was instead staged under `<run>/test-data/synthetic_am3/` and its
> expected effects validated by executing the vendored script directly, outside Planemo, with the
> index selection left as a documented placeholder in the test plan's `unresolved` list.
>
> ## Expected
>
> Either document explicitly — in the schema description or in
> `planemo-workflow-test-architecture.md` — that a synthetic fixture for an internal step is **not**
> expressible via `job:` and must be pursued through a real registered index / data-table entry or a
> separate component- or tool-level test; or, if Planemo/Galaxy does have an undocumented mechanism
> for this (a `--test_index`-scoped step-parameter override, say), document and cite it.
>
> ## Related
>
> #51 (closed) brought in the tests-format schema artifact.

---

## A10 — No packaged note documents the `sample_sheet` + `rows:` job-input shape

**Locator:** `content/research/iwc-test-data-conventions/index.md`
**Observed hash:** `1921e939703444604440e0768caca6e6b834a73dcfa964f450fa081143e008d3` — unchanged on `main`
**Raised by:** `implement-galaxy-workflow-test`
**Entry:** `tests-format-schema-silent-on-sample-sheet-column-definitions-shape` · gap · minor

> Posted by an AI assistant on scottcain's behalf.
>
> ## Summary
>
> The run's primary workflow input is `collection_type: sample_sheet` with four optional per-element
> `column_definitions`. `tests-format.schema.json`'s `Collection` `$def` does carry a `rows` field
> (`additionalProperties`: column-name → array) that appears meant for exactly this — but
> `iwc-test-data-conventions.md`, the authoritative packaged note on job/input YAML shapes, which
> documents List, Paired, `list:paired`, `list:list:paired`, and `composite_data` in detail, never
> mentions `sample_sheet`, `column_definitions`, or `rows`. A corpus grep across the whole skill
> bundle returns nothing beyond the bare schema field.
>
> ## Evidence
>
> The generated test file encodes per-gene overrides as
> `rows: {align_min_match_pident: [60.0, null], …}` alongside `elements:` — a best-effort construction
> against the bare schema field. It passes `gxwf validate-tests --workflow` cleanly, but there is no
> corpus precedent confirming it is what Planemo/Galaxy expects at runtime.
>
> ## Expected
>
> Add a worked `sample_sheet` + `rows:` example to `iwc-test-data-conventions.md` (or a note it
> references), alongside the existing collection-shape sections, so a Mold does not have to infer the
> shape from a generic schema field.
>
> ## Related
>
> #185 (closed) verified the gxformat2 importer preserves `column_definitions` — the import side of
> the same input kind. This is the test-fixture side.

---

## A11 — `comments: type: frame` authored without `position`/`size` is rejected by real Galaxy import

**Locator:** `galaxyproject/galaxy` — `lib/galaxy/model/__init__.py` (`WorkflowCommentModel`),
`lib/galaxy/managers/workflows.py` (`_workflow_from_raw_description`)
**Subject kind:** related-project (no Foundry hash)
**Raised by:** `implement-galaxy-workflow-test` (rev 8, `966c486ccda2…`)
**Entry:** `galaxy-workflow-frame-comments-missing-position-size-rejected-by-real-galaxy-import` · gap · major

> Posted by an AI assistant on scottcain's behalf.
>
> ## Summary
>
> A `planemo test --test_index 1 --install_galaxy` attempt failed before any test data was staged or
> any tool ran: Galaxy's real workflow-import API rejected the workflow with HTTP 400,
> `Field required in ("frame","position")` and `Field required in ("frame","size")`.
>
> The workflow's `comments:` block has four `type: frame` entries grouping steps into stages, none
> carrying `position` or `size` — fields real Galaxy's `WorkflowCommentModel` requires for any
> frame-type comment. The workflow produced by earlier phases is therefore schema-valid enough to pass
> this pipeline's own `gxwf draft-validate --concrete` gate while being **not importable into a real
> Galaxy instance**.
>
> ## Evidence
>
> `bioblend.ConnectionError: Unexpected HTTP status code: 400`, with a pydantic
> `ValidationError: WorkflowCommentModel: frame.position Field required, frame.size Field required`,
> raised from `galaxy.managers.workflows.build_workflow_from_raw_description` →
> `model.WorkflowComment.from_dict` on the first frame comment
> (`{id: 0, type: frame, data: {title: 'Stage A — input assembly'}, child_steps: [15], label: …}`).
>
> This blocked the test case before tool installation or dependency resolution was reached, so it was
> never determined whether the tool chain itself would install and run cleanly.
>
> ## Expected
>
> Whichever Mold or reference documents the gxformat2 `comments: type: frame` shape should require or
> default `position: {x, y}` and `size: {width, height}`, and `gxwf draft-validate` /
> `validate-galaxy-workflow` should be extended to catch this class of real-Galaxy-only requirement
> before a Planemo run discovers it at import time.
>
> ## Related
>
> Part of the broader gap #566 is asking about — see the deploy-guidance comment on that issue.

---

## A12 — `gxwf validate --connections` crashes on an ordinary format2 dict-shaped `step.in`

**Locator:** `https://github.com/jmchilton/galaxy-tool-util-ts` —
packages/schema `workflow/normalized/toNative.js:429` (`_extractConnections`),
packages/connection-validation `graph-builder.js`, `@galaxy-tool-util/cli@1.10.1`
**Subject kind:** related-project (no Foundry hash)
**Raised by:** `validate-galaxy-workflow` (rev 5, `74e3743fc376…`)
**Entry:** `gxwf-validate-connections-flag-crashes-uncaught-on-format2-dict-shaped-step-in` · defect · major

> Posted by an AI assistant on scottcain's behalf.
>
> ## Summary
>
> `gxwf validate <workflow>.gxwf.yml --json --connections` crashes with an uncaught
> `TypeError: step.in is not iterable` at `toNative.js:429`, exits 1, and emits no JSON report at all
> — not even a `connection_report: null` degrade of the kind tool-state fetch failures already get.
>
> Call path: `_extractConnections` ← `_buildToolStep` ← `_buildStep` ← `_buildNativeWorkflow` ←
> `toNative` ← `_coerceNormalizedNative` ← `buildWorkflowGraph` ← `validateConnectionsReport` ←
> `buildConnectionReport`.
>
> Every step's `in:` in the affected workflow is an ordinary gxformat2 mapping
> (`in: {input_list: gene_query_panel}`) — the standard and only shape gxformat2's schema documents
> for step connections. `_extractConnections`'s `for (const stepInput of step.in)` expects the native
> array shape, so any format2 workflow with a normal dict-shaped `in:` reaching this path crashes
> rather than being converted.
>
> ## Evidence
>
> `gxwf validate <wf> --json --connections` and the same plus `--strict` both exit 1 with an identical
> stack trace and no stdout JSON — the process dies before writing the report. The same workflow with
> `--json --strict` and **without** `--connections` exits 0 and produces a full report (5 ok / 0 fail /
> 4 skip).
>
> This is not an edge case for the Foundry: `validate-galaxy-workflow`'s own SKILL.md directs using
> `--connections` "when tool cache metadata is available and data-shape compatibility matters,
> especially around collections and map-over" — exactly this workflow's shape (9 steps, heavy
> collection map-over). The flag was simply unusable, and collection/map-over shape compatibility had
> to be recorded as a residual runtime risk instead.
>
> That mattered: a real wiring defect in this same workflow (see the `sample_sheet`-column-to-scalar-port
> issue from this run) is precisely the class `--connections` exists to catch, and it reached live
> Galaxy uncaught.
>
> ## Expected
>
> `_extractConnections` or its caller should normalize a format2 dict-shaped `step.in` into the array
> shape it expects — the same normalization `toNative` already performs on the plain `gxwf validate`
> path, which reads this exact workflow without error. Failing that, `--connections` should degrade
> gracefully into a reported error inside the JSON `connection_report`, matching the
> `skip_tool_not_found` precedent, rather than throwing away the entire report.

---

## A13 — No documented path for an authored `GalaxyUserTool` to reach a Planemo-managed toolbox

**Locator:** `content/molds/run-workflow-test/index.md`
**Observed hash:** ledger records `unavailable-in-cast` (rev 6); a later same-run observation of rev 7
is `259675e41c657f62…`, which matches `main`
**Raised by:** `run-workflow-test`
**Entry:** `run-workflow-test-no-mechanism-to-install-authored-galaxyusertool-udts` · gap · major

> Posted by an AI assistant on scottcain's behalf.
>
> ## Summary
>
> Neither `run-workflow-test`'s packaged references (`planemo.md`,
> `planemo-workflow-test-architecture.md`, `planemo-asserts-idioms.md`,
> `galaxy-workflow-invocation-failure-reference.md`) nor `author-galaxy-tool-wrapper`'s — which
> explicitly states its output is "a single GalaxyUserTool YAML document, not Galaxy XML" — document
> any mechanism by which a locally-authored UDT with no Tool Shed presence reaches a Planemo-managed
> Galaxy's toolbox for a workflow test run.
>
> The pipeline can author a UDT and can build a workflow that uses it, but cannot test that workflow.
>
> ## Evidence
>
> `planemo test`'s only documented tool-injection option, `--extra_tools <file|directory>`, was tried
> against a directory holding the run's 3 UDT YAML files. Planemo emits a `<tool_dir dir="…">` entry
> into the generated `tool_conf.xml` (confirmed by reading the generated file), and Galaxy's toolbox
> parses that `tool_conf.xml` — but Galaxy's classic `tool_dir` scanner only auto-discovers XML tool
> wrappers.
>
> Zero log lines in either of the run's two planemo logs reference any of the 3 UDT ids, filenames, or
> the string `GalaxyUserTool`. The subsequent real workflow-invocation attempt returned HTTP 400
> naming all three among "required tools are not installed", proving the toolbox never registered them.
>
> ## Expected
>
> Either document a real, working path for a `GalaxyUserTool` YAML to reach a Planemo-managed toolbox
> — e.g. a `gxwf`/`galaxy-tool-util` command that lowers `class: GalaxyUserTool` to a classic Galaxy
> tool XML plus script directory that `--extra_tools` can load, or an alternate Planemo/Galaxy API this
> bundle should cite — or state plainly in `run-workflow-test`'s procedure that an authored UDT with no
> lowering step is **expected** to fail toolbox resolution in a real Planemo run, and name the concrete
> blocking condition as a `not-run`/tool-install failure modality rather than leaving the caller to
> discover it empirically.
>
> ## Related
>
> #468 covers `author-galaxy-tool-wrapper`'s missing validation and schema. This is the downstream
> half: even a valid UDT has nowhere to go. See also the `/api/unprivileged_tools` issue from this run,
> which documents the path that *does* work against a real Galaxy instance.

---

## A14 — `replacement_collection` indexes `rows` unconditionally, crashing Planemo staging for a `sample_sheet` input without `rows`

**Locator:** `galaxyproject/galaxy` — `lib/galaxy/tool_util/cwl/util.py`
(`galaxy-tool-util==25.1.2`, vendored into `planemo==0.75.47`)
**Subject kind:** related-project (no Foundry hash)
**Raised by:** `run-workflow-test`
**Entry:** `galaxy-tool-util-replacement-collection-requires-rows-key-unconditionally` · defect · major

> Posted by an AI assistant on scottcain's behalf.
>
> ## Summary
>
> `galaxy.tool_util.cwl.util.replacement_collection()` — the function Planemo's
> `stage_in`/`galactic_job_json` path uses to turn a tests-format `job:` Collection value into an
> HDCA-creation payload — contains:
>
> ```python
> if collection_type.startswith("sample_sheet"):
>     kwds["rows"] = value["rows"]
> ```
>
> An unconditional dict index, not `.get()`, on an **optional** key. `tests-format.schema.json`'s
> `Collection` `$def` does not require `rows`. Any `sample_sheet`-typed Collection job input that
> legitimately omits it crashes Planemo's staging step with an uncaught `KeyError: 'rows'` before any
> Galaxy invocation is created — instead of surfacing as a graceful staging report.
>
> ## Evidence
>
> `planemo test --install_galaxy --test_index 1 --extra_tools <dir> <workflow>.gxwf.yml` crashed with
> `execution_problem: "'rows'"`, `status: "error"`, `invocation_details: null`, `job: null` in the
> structured `tool_test_output.json` — staging failed before an invocation existed. Traceback:
>
> ```
> planemo/galaxy/activity.py:441 stage_in
>   -> galaxy/tool_util/client/staging.py:275 stage
>   -> galaxy/tool_util/cwl/util.py:388 galactic_job_json
>   -> :234 replacement_item
>   -> :362 replacement_collection
>   -> KeyError: 'rows'
> ```
>
> The isolating variable is confirmed by contrast: the run's other test case, whose same
> `sample_sheet` input **does** carry a `rows:` block, staged past this exact code path without error
> in the immediately following run and reached a real (differently-failing) invocation attempt.
>
> The omitting test case was deliberate — `rows` was "not meaningful for generic non-phiX174 fixture
> content" — and that file passed `gxwf validate-tests --workflow --json` cleanly with `rows` absent.
>
> ## Expected
>
> `replacement_collection` should use `kwds["rows"] = value.get("rows", {})`, or omit the key entirely
> when absent if Galaxy's collection-create API tolerates that — matching the tests-format schema's own
> treatment of `rows` as optional for a `sample_sheet` Collection value.

---

## A15 — Invocation-failure reference has no tell for a stale toolbox read vs. a real install failure

**Locator:** `content/research/galaxy-workflow-invocation-failure-reference/index.md`
**Observed hash:** `e8115df6ddca447d47d77cb33becda847cdd19b2cbe9924782bfc180b94bb451` — unchanged on `main`
**Raised by:** `debug-galaxy-workflow-output` (rev 5, `100b3f985f8e…`)
**Entry:** `galaxy-workflow-invocation-check-rejects-previously-installed-tool-as-not-installed` · gap · major

> Posted by an AI assistant on scottcain's behalf.
>
> ## Summary
>
> The note's "Request-time validation" surface (an API error before a useful invocation state exists,
> e.g. HTTP 400 "required tools are not installed") gives no guidance for telling a genuine per-tool
> dependency/installation failure apart from a toolbox-state read that is stale relative to a
> just-completed install/reload cycle.
>
> This run found a concrete, reproducible tell the note does not mention.
>
> ## Evidence
>
> In the run's second planemo test, the install manager logged that `collapse_collections` (providing
> `collapse_dataset`) was **skipped** for reinstall because its cached status was already `Installed` —
> no fresh clone, no fresh dependency resolution for it that run:
>
> ```
> Skipping installation of revision 90981f86000f of repository 'collapse_collections'
> because it was installed with the (possibly updated) revision 90981f86000f and its
> current installation status is 'Installed'.
> ```
>
> Fifty-four seconds later the `POST /api/workflows/…/invocations` returned 400 listing
> `collapse_dataset (version 5.1.0)` among seven "not installed" tools — alongside three genuinely
> freshly-cloned Tool Shed tools and three never-installable UDTs.
>
> Timing rules out an in-flight reload: the last `reload_toolbox` control-task cycle completed at
> `11:50:13,808`; the invocation POST fired at `11:50:58,531`, 45 s later. A tool with a confirmed
> pre-existing good install status being rejected points at the invocation-validation check reading
> stale or incomplete toolbox state, not at a real dependency failure for that tool.
>
> The classification had to be reconstructed ad hoc from install-manager log lines, because no
> documented reference path covers it.
>
> ## Expected
>
> Add this diagnostic tell to the "Request-time validation" row (or a new row): when a tool listed as
> "not installed" in a request-time 400 has an install-manager log line showing its install was skipped
> because it was already `Installed` from a prior or cached run, that is evidence of a
> toolbox-state read / reload-timing defect rather than a genuine dependency-resolution failure — and
> should route debugging toward Galaxy's toolbox-reload and tool-availability-check code path rather
> than toward the wrapper's conda requirements.

---

## A16 — The real UDT registration endpoint is `/api/unprivileged_tools`, not the admin-only `/api/dynamic_tools`

**Locator:** `galaxyproject/galaxy` — `lib/galaxy/webapps/galaxy/api/dynamic_tools.py`,
`lib/galaxy/webapps/galaxy/api/tools.py`
**Subject kind:** related-project (no Foundry hash)
**Raised by:** `run-workflow-test` (rev 7, `259675e41c65…`)
**Entry:** `galaxy-udt-registration-real-endpoint-is-unprivileged-tools-not-dynamic-tools` · gap · major

> Posted by an AI assistant on scottcain's behalf.
>
> ## Summary
>
> A companion finding from this run established there is no way to load a `GalaxyUserTool` YAML into a
> Planemo-managed toolbox, and separately that `POST /api/dynamic_tools` against a real production
> Galaxy returns HTTP 403 ("You must be an administrator to access this feature").
>
> Neither `run-workflow-test`'s nor `author-galaxy-tool-wrapper`'s packaged references mention that
> Galaxy exposes a **separate, non-admin-gated endpoint for exactly this**: `POST
> /api/unprivileged_tools`, gated only by a `USER_TOOL_EXECUTE` role plus the instance's
> `enable_beta_tool_formats` config flag — both satisfied by an ordinary usegalaxy.org account.
>
> A regular user's own `GalaxyUserTool` YAML, converted to the JSON body that endpoint expects,
> registers there successfully and becomes a real, invocable, user-scoped dynamic tool with a
> `tool_uuid`.
>
> ## Evidence
>
> - `POST https://usegalaxy.org/api/dynamic_tools` with a `GalaxyUserTool`-derived body → HTTP 403,
>   admin required.
> - `POST https://usegalaxy.org/api/unprivileged_tools` with the same tool content (after fixing a
>   separate lint defect — see the `value: 0` issue from this run) → 200, returning a real `tool_uuid`
>   for each of the run's 3 UDTs.
> - All three later confirmed resolvable with zero step errors via `GET /api/workflows/{id}/download`
>   once wired into the imported workflow.
>
> ## Expected
>
> `author-galaxy-tool-wrapper` and/or `run-workflow-test` should document `POST
> /api/unprivileged_tools` as the real-Galaxy registration path for an authored `GalaxyUserTool`,
> distinct from the admin-only `/api/dynamic_tools` — including its role and config gating
> (`USER_TOOL_EXECUTE`, `enable_beta_tool_formats`), and the fact that a successful registration
> returns a `tool_uuid` that a workflow step must reference rather than a bare `tool_id` string (see
> the companion `tool_uuid` issue).
>
> ## Related
>
> Directly answers part of #566.

---

## A17 — Galaxy's unprivileged-tool lint fails opaquely on an integer input with `value: 0`

**Locator:** `galaxyproject/galaxy` — unprivileged dynamic-tool creation / tool linting path
(`POST /api/unprivileged_tools`, `input_models_for_tool_source` / `TestsCaseValidation`)
**Subject kind:** related-project (no Foundry hash)
**Raised by:** `author-galaxy-tool-wrapper` (rev 5, `cced8f068cd1…`)
**Entry:** `galaxy-unprivileged-tools-lint-crashes-on-integer-input-default-value-zero` · defect · minor

> Posted by an AI assistant on scottcain's behalf.
>
> ## Summary
>
> Galaxy's tool-creation lint on `POST /api/unprivileged_tools` throws an uncaught, unhelpfully
> reported exception — `TestsCaseValidation … exception is []`, no further detail — when a
> `GalaxyUserTool` integer input declares `value: 0` as its default.
>
> ## Evidence
>
> Bisected live against the real endpoint by varying one field:
>
> - `POST https://usegalaxy.org/api/unprivileged_tools` with an integer input at `value: 0` → HTTP 400,
>   opaque lint exception. Reproduced every time.
> - Removing that one default → 200 OK, tool registered with a real `tool_uuid`.
> - Re-adding the same field with `value: 1` on a throwaway copy → registers fine, confirming the value
>   itself and not the field's presence is the trigger.
>
> ## Expected
>
> Fix the lint to handle a zero-valued integer default. Until then, `galaxy-user-tool-authoring.md`
> (`author-galaxy-tool-wrapper`'s own packaged reference, which documents `value:` for scalar inputs
> generally but carries no such warning) should warn against `value: 0` on an integer or float UDT
> input and recommend omitting the default when zero is the semantically correct one, relying on the
> step's explicitly wired value.

---

## A18 — gxformat2 has no `tool_uuid`, so a step bound to a registered UDT imports unresolved

**Locator:** `galaxyproject/gxformat2` (step schema) and `galaxyproject/galaxy`
(native `.ga` workflow-step `tool_uuid` resolution)
**Subject kind:** related-project (no Foundry hash)
**Raised by:** `freeform-summary-to-galaxy-template` (rev 6, `0a95f8c04465…`)
**Entry:** `gxformat2-step-schema-does-not-model-tool-uuid-for-dynamic-tool-resolution` · gap · major

> Posted by an AI assistant on scottcain's behalf.
>
> ## Summary
>
> A gxformat2 step referencing a real, registered user-scoped dynamic tool by bare `tool_id` imports
> and round-trips through `gxwf convert` without ever populating or requiring a `tool_uuid`. But real
> Galaxy's step-to-tool resolution for a dynamic tool **requires** the native `.ga` step to carry that
> tool's `tool_uuid` explicitly. A bare `tool_id` never resolves to a user-scoped dynamic tool, even
> after successful registration and even though the `tool_id` string itself is correct.
>
> The result: all 3 UDT steps showed "Tool is not installed" after a clean gxformat2 import, with no
> schema-level signal of what was missing.
>
> ## Evidence
>
> gxformat2 import of the run's workflow — all 3 UDT `tool_id`s correct, all 3 tools already registered
> via `/api/unprivileged_tools` — still showed all 3 steps tool-unresolved. Fetching the imported
> workflow natively via `GET /api/workflows/{id}/download` confirmed each UDT step's JSON had no
> `tool_uuid` key at all. Manually setting `tool_uuid` to each registered tool's real UUID in that
> native JSON and re-importing via `POST /api/workflows` produced a workflow with **zero step errors**
> on the same check.
>
> Compounded by a second, separately-filed `gxwf` defect (`step.in is not iterable`), which blocked
> using `gxwf` itself for the format2 → native conversion, forcing the round trip through Galaxy's own
> download endpoint.
>
> ## Expected
>
> Either extend the gxformat2 step schema and `galaxy-workflow-draft-format` to model an optional
> `tool_uuid` — populated once a dynamic/UDT tool is registered — so a draft can carry it through the
> normal pipeline; or document explicitly in `freeform-summary-to-galaxy-template`,
> `advance-galaxy-draft-step`, and `run-workflow-test` that a step resolving to a UDT must, at
> deployment time, be converted to native `.ga` with its `tool_uuid` injected post-registration. Neither
> is documented anywhere in the pipeline's packaged references today.

---

## A19 — A `sample_sheet` column was wired onto a plain scalar tool port, a binding that can never work

**Locator:** `content/molds/advance-galaxy-draft-step/index.md`
**Observed hash:** `c92d452f69a7b40bcab5fc8e63b03e1e2abf98f2a636abc4c93ad7f3c1d03082` (revision 4)
**Current `main`:** `ae19f7e5f5ac…` (revision 7, `revised: 2026-09-17`) — **the correction below is not
present in the current text**; verified by inspection, no occurrence of `sample_sheet` or
`param_value_from_file`
**Raised by:** `debug-galaxy-workflow-output` (rev 5, `100b3f985f8e…`)
**Entry:** `lexicmap-search-sample-sheet-column-to-scalar-port-defect` · defect · major

> Posted by an AI assistant on scottcain's behalf.
>
> ## Summary
>
> A per-step draft iteration wired four per-gene sensitivity overrides directly from a `sample_sheet`
> collection onto an ordinary IUC tool's plain scalar ports
> (`in: {advanced_settings|align_min_match_pident: gene_query_panel, …}`). That binding can never work.
>
> A `sample_sheet` collection's per-element column values are readable only by a tool that itself
> declares a `data_collection` input accepting `sample_sheet` and reads columns internally via
> `DatasetCollectionWrapper.sample_sheet_row()` in its own template. `lexicmap_search`
> (`iuc/lexicmap` 0.9.0+galaxy1) is an ordinary tool with plain float/int parameters and no
> `sample_sheet` awareness. There is no generic Galaxy workflow-wiring mechanism to bind another tool's
> scalar parameter to a sample_sheet column at runtime — rewiring the connection alone cannot fix it.
> The whole design of carrying these values as sample_sheet columns was unworkable from the start for
> feeding a non-sample_sheet-aware tool.
>
> ## What makes this worth filing
>
> **No static check in the pipeline caught it.** `gxwf draft-validate` and `gxwf validate` both passed
> clean, repeatedly (0 fail, 0 structure_errors). The deploy step's own
> `GET /api/workflows/{id}/download` check reported zero step errors. And `gxwf validate --connections`
> — the one check that could in principle catch a collection-algebra type error — cannot run against
> this file at all, due to the separately-filed `step.in is not iterable` crash.
>
> It was exposed only by a real invocation on live usegalaxy.org: both per-gene `lexicmap_search` jobs
> errored pre-execution, with no command line, stdout, stderr, or exit code, and the submitted
> `advanced_settings` tool_state literally holding a raw Python object repr —
> `"<galaxy.model.DatasetCollectionElement(…) at 0x…>"` — in place of a resolved number, for all four
> ports.
>
> ## Evidence
>
> Root-caused via `GET /api/jobs/{id}?full=true` on both failed jobs, showing the
> `DatasetCollectionElement` repr in all four `advanced_settings` fields while `db_opts.lexicmap_index`
> — an ordinary text-select port in the same job — resolved correctly to `"Viral"`. That isolates the
> fault to the sample_sheet-column ports specifically.
>
> The real fix mechanism was then confirmed and built: `GET /api/tools/param_value_from_file?io_details=true`
> shows four per-`param_type` output ports, not one generic `output`. Four parallel `list` collections
> (one dataset per gene, each holding that gene's value as plain text, element identifiers matching the
> driving collection) were created via `POST /api/dataset_collections`, plus four
> `param_value_from_file` 0.1.0 steps mapped over them, and the four broken ports rewired onto those
> steps' typed output ports. Re-validated clean (9 ok / 0 fail / 4 pre-existing skips).
>
> ## Expected
>
> `implement-galaxy-tool-step` / `advance-galaxy-draft-step`'s packaged references should document as a
> **hard rule** that a `sample_sheet` collection's per-element columns cannot be wired onto another,
> non-sample_sheet-aware tool's plain scalar parameter — only onto a tool that declares a
> `data_collection` input for that sample_sheet.
>
> For the common case of a per-element-varying scalar feeding an ordinary tool, document the verified
> pattern above: a parallel `list` collection with matching element identifiers, consumed by
> `param_value_from_file` mapped over it, wired from **the output port matching the chosen
> `param_type`** (not a generic `output`) into the target scalar port.
>
> Separately, once its crash is fixed, `gxwf validate --connections` should flag a
> sample_sheet-to-scalar-parameter connection as a real type error — it is never valid, regardless of
> collection contents.

---

## A20 — `PUT /api/workflows/{id}` defaults `exact_tools` to true and discards the per-step detail it already computed

**Locator:** `galaxyproject/galaxy` — `lib/galaxy/webapps/galaxy/api/workflows.py`,
`lib/galaxy/managers/workflows.py`, `lib/galaxy/workflow/modules.py`
**Subject kind:** related-project (no Foundry hash)
**Raised by:** `debug-galaxy-workflow-output` (rev 5, `100b3f985f8e…`)
**Entry:** `galaxy-workflow-update-exact-tools-defaults-true-and-discards-per-step-error-detail` · defect · major

> Posted by an AI assistant on scottcain's behalf.
>
> ## Summary
>
> Two related problems on the workflow-update path.
>
> **1. A second escape hatch under a different name.** `PUT /api/workflows/{id}` resolves each step's
> tool via `toolbox.get_tool(tool_id, tool_version=…, exact=exact_tools, tool_uuid=…)`, where
> `exact_tools` — a real field on `WorkflowUpdateOptions` — defaults to `True` unless the request body
> sets it. This is the same false-positive tool-resolution behavior already known at *invocation* time
> (workaroundable there with `require_exact_tool_versions: false`), recurring at *save* time under a
> **different, undocumented field name**, with no hint that a save-time escape hatch exists at all.
>
> **2. The specific error is computed and then thrown away.** When `get_tool(…, exact=True)` fails,
> `update_workflow_from_raw_description` builds a real per-step message —
> `f"Step {n+1}: Requires tool '{tool_id}'."` — into `missing_tool_tups` and raises
> `MissingToolsException`. The API handler unconditionally rewrites this to a generic
> `{"err_msg": "This workflow contains missing tools. It cannot be saved until they have been removed
> from the workflow or installed.", "err_code": 0}`, discarding the already-computed per-step list
> before it reaches the client.
>
> ## Evidence
>
> `PUT /api/workflows/{id}` with a corrected native workflow JSON (bare `{"workflow": {…}}` body)
> returned the generic message for 4 tools — `collapse_dataset` 5.1.0, `lexicmap_search` 0.9.0+galaxy1,
> `kmindex_query` 0.6.1+galaxy4, `collection_column_join` 0.0.3 — each independently re-confirmed
> installed via `/api/tools/{id}/build` moments before and after.
>
> Re-submitting the identical `workflow` content with two added top-level sibling keys,
> `{"exact_tools": false, "allow_missing_tools": true}`, succeeded immediately with no other change.
>
> ## Expected
>
> 1. The error response should surface the specific per-step missing-tool list it already computed
>    (`missing_tool_tups`) instead of discarding it for a generic message with `err_code: 0`. That alone
>    would have saved a full diagnostic round trip.
> 2. Document `exact_tools` / `allow_missing_tools` — `WorkflowUpdateOptions`' real fields — as the
>    save-time equivalent of invocation-time's `require_exact_tool_versions` /
>    `allow_tool_state_corrections`, ideally in the same place. A caller who learned one has no way to
>    guess the other exists under a different name on a different endpoint.

---

## A21 — Authoring never checks a wrapped script's own declared input-ordering assumption against the tool it will consume from

**Locator:** `content/molds/author-galaxy-tool-wrapper/index.md`
**Observed hash:** `cced8f068cd1ce81fefad23a62fdb4d52b3ce805b2231f64a7fe37f258bc1e09` — unchanged on `main`
**Raised by:** `debug-galaxy-workflow-output` (rev 5, `100b3f985f8e…`)
**Entry:** `author-galaxy-tool-wrapper-no-check-of-wrapped-scripts-own-declared-input-ordering-assumption` · gap · major
**Redaction:** the wrapped script lives in a private repository outside the Foundry; that repository
is not named here. The bug in the script itself was fixed at its own source and is out of scope.

> Posted by an AI assistant on scottcain's behalf.
>
> ## Summary
>
> This is not a report of a bug in a wrapped script. The Foundry-relevant gap is in the authoring
> process.
>
> `author-galaxy-tool-wrapper` wrapped a streaming script as a `GalaxyUserTool` without ever checking
> whether the script's own explicit, self-declared input-ordering assumption actually holds for the
> real upstream Galaxy tool the step would consume from in the concrete workflow.
>
> The script's own committed comment stated the assumption outright — that the stream is grouped by
> accession one block at a time, so all of an accession's HSPs are contiguous, and a reappearance can
> be treated as end-of-input. That is a directly inspectable, mechanically greppable static signal that
> correctness depends on an ordering property of the input.
>
> Nothing in `author-galaxy-tool-wrapper`'s authoring or review process prompts for cross-checking such
> an assumption against the actual output ordering of the specific Tool Shed tool the step is wired to
> consume from later in the same workflow.
>
> ## Evidence
>
> The assumption was false for that upstream tool from the start: real `iuc/lexicmap/lexicmap_search`
> 0.9.0+galaxy1 output is ranked by match quality across all matched genomes, **not** grouped by target
> accession — confirmed by direct byte-range inspection of real output. The mismatch caused two live job
> failures on real production data.
>
> The failure mode was undetectable by the test fixture that existed: a 3-decoy synthetic fixture built
> at test-authoring time cannot exhibit a "reappearing accession" pattern by construction, regardless of
> whether the assumption holds. Only a real, production-scale invocation exercised it.
>
> ## Expected
>
> Add an explicit check step to `author-galaxy-tool-wrapper`'s review/authoring procedure: when a
> wrapped script's own source, docstring, or comments assert an assumption about the shape, ordering, or
> grouping of its input (a `sort` / `group` / `contiguous` / "assumes" style comment is a strong,
> greppable signal), the authoring pass should either
>
> - (a) verify that assumption against the real, documented output-ordering behavior of the specific
>   upstream tool the step will actually be wired to — not against a hand-built fixture that cannot
>   exercise the failure mode; or
> - (b) explicitly flag it as an open, unverified risk in the step's `doc:` and in the run's ledger, for
>   a later phase to confirm before the workflow is treated as production-ready.
>
> A synthetic fixture, however carefully built, cannot substitute for this check when the fixture is by
> construction too small to violate the assumption being tested.

---

## A22 — `download?style=ga` emits unversioned `tool_id`s, producing workflows that save but cannot be invoked

**Locator:** `content/research/galaxy-workflow-invocation-failure-reference/index.md`
(observation concerns `galaxyproject/galaxy`'s download and invocation paths)
**Observed hash:** none recorded in the ledger; `observed_in: null`, `raised_by: manual-deploy`
(a non-Mold actor — see run review §2)
**Entry:** `ga-download-normalizes-tool-id-producing-workflows-that-save-but-cannot-invoke` · defect · major

> Posted by an AI assistant on scottcain's behalf.
>
> ## Summary
>
> `GET /api/workflows/{id}/download?style=ga` emits each Tool Shed step's `tool_id` as the
> **unversioned** repository path (`toolshed.g2.bx.psu.edu/repos/iuc/kmindex/kmindex_query`), with the
> version carried separately in `tool_version`.
>
> Re-importing that exact document — the download/edit/upload round trip any external deploy script
> performs — produces a workflow that **saves successfully**, shows `errors: null` on every step via
> `GET /api/workflows/{id}?legacy=false`, and lints clean, but **cannot be invoked**:
> `POST /api/workflows/{id}/invocations` returns HTTP 400 "the following required tools are not
> installed", naming tools that are installed at exactly that id and version.
>
> Setting `tool_id` to the full versioned path, with no other change, makes the same workflow invoke
> immediately. The round trip is lossy in a way that is invisible until invocation: the format the
> server hands you back is not a format the server will accept for execution.
>
> ## Evidence
>
> **Isolated** on a purpose-built one-step probe workflow (a single `tp_cat` step, plain
> `POST /api/workflows` body `{"workflow": …}` with no `exact_tools`/`allow_missing_tools` keys, so those
> flags are excluded as a cause):
>
> - `tool_id: …/text_processing/tp_cat` + `tool_version: 9.11+galaxy0` → invocation 400, "required tools
>   are not installed: …/tp_cat (version 9.11+galaxy0)".
> - Changing **only** `tool_id` to `…/text_processing/tp_cat/9.11+galaxy0` → invocation scheduled, jobs
>   ran to `ok`.
>
> **Corroborated** on the run's real workflow: the version built from a `download?style=ga` round trip
> saved fine with 0 steps in error, every tool independently confirmed present via
> `GET /api/tools/{versioned-id}` — yet invocation returned 400 listing `collapse_dataset` 5.1.0,
> `kmindex_query` 0.6.1+galaxy4, `lexicmap_search` 0.9.0+galaxy1 and `collection_column_join` 0.0.3 as
> not installed. The next version, identical apart from versioned `tool_id`s, invoked successfully.
>
> ## Expected
>
> 1. `POST /api/workflows/{id}/invocations` should resolve an unversioned `tool_id` together with the
>    step's own `tool_version`, exactly as the save path and the editor already do. Failing that, the
>    error should say the id is unversioned rather than claiming an installed tool is not installed —
>    which routes debugging toward tool installation instead of toward id formatting.
> 2. `download?style=ga` should round-trip losslessly: either emit the versioned id, or have the
>    invocation check accept what the download emits. As it stands, the documented way to fetch a
>    workflow produces a document that silently loses executability.
>
> ## Distinct from
>
> The stale-toolbox-read issue also filed from this run. That one has a reload-timing signature under
> planemo; this is deterministic, has no timing component, and reproduces on demand against a long-warm
> production toolbox.

---

# B. Existing-issue comment drafts

## B1 — comment on #564 (step `doc:` length crashes live Galaxy import)

**Target:** open issue #564 — *"advance-galaxy-draft-step/repair-galaxy-draft-topology can produce step
doc: text long enough to crash workflow import on live Galaxy instances; no lint/validate check catches it"*
**Locator:** `galaxyproject/galaxy` — `POST /api/workflows` gxformat2 import, step doc/annotation field
**Raised by:** `freeform-summary-to-galaxy-template` (rev 6, `0a95f8c04465…`)
**Entry:** `galaxy-workflow-import-enforces-undocumented-per-field-length-limit-on-step-doc` · defect · major

> Posted by an AI assistant on scottcain's behalf.
>
> An independent reproduction of this from a different `pipeline-paper-to-galaxy` run, with a
> **different measured threshold** and a **third producing Mold** — both of which seem worth resolving
> before a length check is written against a fixed constant.
>
> ## Different threshold
>
> This issue bisected the limit to between 3900 (imports) and 3999 (crashes) characters. Bisecting the
> same way against `https://usegalaxy.org/api/workflows` (26.1.2.dev0) gave a different answer:
>
> | doc length | result |
> | --- | --- |
> | 2000 | 200 OK |
> | 2048 | 200 OK |
> | 2398 | 500 "Uncaught exception in exposed API method", no traceback |
>
> That puts the ceiling at 2048 characters here, not ~3950. Both runs hit the same opaque, tracebackless
> 500, so the failure mode matches — but the two thresholds cannot both be one fixed constant. Worth
> confirming the actual DB column width upstream rather than either number, and worth considering
> whether the limit is per-field bytes vs. characters (multi-byte content differed between the two runs:
> this run's step docs contained em-dashes and other non-ASCII).
>
> ## A third producer
>
> This issue names `advance-galaxy-draft-step` and `repair-galaxy-draft-topology`. In this run, 5 steps
> exceeded the limit and the initial oversized `doc:` text came from
> **`freeform-summary-to-galaxy-template`** as well — then grew further through
> `advance-galaxy-draft-step` iterations folding `_plan_context` rationale into `doc:`, per that skill's
> own "a resolved step carries no `_plan_*` fields" rule.
>
> So the convention of parking authoring provenance in `doc:` is not confined to the two Molds named
> here; it starts at template time. Fixing it only in the draft-loop Molds would leave the template
> path producing the same overrun.
>
> ## Same blind spot confirmed
>
> Every static check in the toolchain passed clean on the oversized file, repeatedly — `gxwf
> draft-validate` and `gxwf validate` both. The 500 at real-Galaxy import was the first signal, which
> matches this issue's finding exactly.
>
> ## Suggested addition to the fix
>
> Alongside the lint/validate length check this issue already proposes: revise the template-time
> convention so `doc:` stays short and full authoring/discovery provenance goes to the
> `open-requirements` and feedback ledgers instead. The trimming this run performed — 5 step docs cut
> from full provenance prose to concise summaries — made the same workflow import successfully with no
> other change, so the provenance was never load-bearing in `doc:` to begin with.

---

## B2 — comment on #548 (`draft-validate --concrete` diagnostics)

**Target:** open issue #548 — *"`gxwf draft-validate --concrete`: the other half of #166 — a ParsedTool
decode failure's `Error.message` is still a full type declaration"*
**Locator:** `https://github.com/jmchilton/galaxy-tool-util-ts` (packages/cli, `gxwf draft-validate`,
`@galaxy-tool-util/cli@1.8.1`)
**Raised by:** `advance-galaxy-draft-step` (rev 4, `c92d452f69a7…`)
**Entry:** `gxwf-draft-validate-json-flag-emits-non-json-diagnostics-on-stdout` · defect · minor

> Posted by an AI assistant on scottcain's behalf.
>
> An independent confirmation of the routing half described here, from a separate
> `pipeline-paper-to-galaxy` run — at an **earlier CLI version**, which brackets the behavior.
>
> This issue measured `@galaxy-tool-util/cli@1.10.1`. This run hit the identical shape at **1.8.1**, so
> the routing defect spans at least 1.8.1 → 1.10.1 and is not a regression introduced between them.
>
> ## Reproduction and the one detail worth adding
>
> ```
> gxwf draft-validate <draft>.gxwf.yml --concrete --json 1>/tmp/dv.out 2>/tmp/dv.err
> ```
>
> - `/tmp/dv.err` was **empty**.
> - `/tmp/dv.out` began with the literal text `toolshed fetch failed (…` — confirmed via
>   `head -c 1 | xxd` returning `t`, not `{` — followed by the huge inline type dump and an ASCII tree
>   of the failing schema path, and only then the JSON report object.
>
> The empty-stderr detail is the part worth recording: stderr is a separate stream the process used for
> nothing at all in this redirection test, so routing the diagnostics there is unblocked by any
> competing use. This also confirms `--help`'s description of `--json` as "(Output structured JSON
> report)" is unmet in the released build.
>
> Recovery required locating the first line beginning with `{` and slicing from there before
> `json.loads` would parse. It was non-blocking only because the text happened to precede rather than
> interleave with the JSON; a caller doing a naive `stdout | jq` hard-fails.
>
> ## On the underlying decode failure
>
> The trigger here was a ParsedTool decode failure for `iuc/kmindex/kmindex_query`, which failed at
> `outputs[1].structure: is missing` on the collection-output branch. I have filed that decode failure
> separately as #572, since it looks like a schema gap distinct from this issue's diagnostic-size half — a
> `<collection type="list">` output declaring `discover_datasets` directly, with a sibling `<filter>`
> the schema has no field for. If it turns out to be in `#166`'s scope after all, that issue can absorb
> it.

---

## B3 — comment on #468 (`author-galaxy-tool-wrapper` authoring references)

**Target:** open issue #468 — *"author-galaxy-tool-wrapper: no validation step, no GalaxyUserTool schema,
and the bundled prompt contradicts it"*
**Locator:** `content/research/galaxy-user-tool-authoring/index.md`
**Observed hash:** `365fad455369945a34bda537c8dbf409a0966f0f88da9fe78b61cff32d5b0d0d` — unchanged on `main`
**Raised by:** `advance-galaxy-draft-step` (rev 4, `c92d452f69a7…`)
**Entry:** `galaxy-user-tool-authoring-missing-element-identifier-expression` · gap · minor

> Posted by an AI assistant on scottcain's behalf.
>
> One more row for this issue's "reference forms" table, found the same way — by reading the schema off
> disk because the packaged reference did not cover the case.
>
> ## The gap
>
> `galaxy-user-tool-authoring.md` §3 ("Expression syntax in `shell_command`") documents exactly one way
> to read a `data` input — the scalar/file path via `$(inputs.NAME.path)` — and says nothing about a
> `data` input's other File-object fields. In particular it never mentions `element_identifier`.
>
> But the installed `@galaxy-tool-util/schema` package's own `gx-data.js` declares, for the
> `job_runtime` state representation (the one governing values available inside a running job's command
> and configfile expressions), a File object shape of:
>
> ```js
> { class: 'File', basename, location, path, nameroot, nameext, format, size,
>   element_identifier: S.optional(S.String) }
> ```
>
> So `$(inputs.NAME.element_identifier)` is a real, schema-backed expression, not merely `.path`.
>
> ## Why it mattered in a real run
>
> Authoring a UDT mapped once per gene over a collection needed the mapped element's identifier embedded
> as a literal output column, to preserve it for a downstream join. §3, read upfront per the skill's own
> procedure, gave no indication the field exists.
>
> Its existence and validity were confirmed only by grepping the installed
> `@galaxy-tool-util/cli` package's `gx-data.js` directly — exactly the external verification this
> issue already faults the Mold for requiring, and exactly what its Runtime Notes direct against.
>
> The cost of not knowing is a silent design error, not just friction: a plausible-but-wrong alternative
> (inserting a `collection_element_identifiers` producer step purely to recover the identifier as a
> wireable parameter) would have been an avoidable topology change driven by a documentation gap rather
> than a real tool-shape constraint.
>
> ## Suggested
>
> Add `$(inputs.NAME.element_identifier)` to §3 alongside `.path`, noting it is available when the input
> is a mapped collection element. This matches the classic Galaxy tool-XML idiom already documented in
> this same skill family's `convert-nfcore-module-to-galaxy-tool` notes (`$input.element_identifier` in
> `<command>`), so the two references would finally agree.

---

## B4 — comment on #566 (guidance for importing to a real Galaxy instance)

**Target:** open issue #566 — *"Needs better guidance for importing to a real galaxy instance"*
**Locator:** n/a — synthesis answering an open request
**Contributing entries:** `galaxy-workflow-frame-comments-missing-position-size-rejected-by-real-galaxy-import`,
`galaxy-udt-registration-real-endpoint-is-unprivileged-tools-not-dynamic-tools`,
`gxformat2-step-schema-does-not-model-tool-uuid-for-dynamic-tool-resolution`,
`galaxy-workflow-update-exact-tools-defaults-true-and-discards-per-step-error-detail`,
`ga-download-normalizes-tool-id-producing-workflows-that-save-but-cannot-invoke`,
`galaxy-workflow-import-enforces-undocumented-per-field-length-limit-on-step-doc`

> Posted by an AI assistant on scottcain's behalf.
>
> This is the same situation from the other side: a `pipeline-paper-to-galaxy` run finished, and the
> workflow was then deployed to a real usegalaxy.org account by empirical trial, exactly as described
> here. It took six distinct discoveries, none of them documented anywhere in the pipeline's packaged
> references, and every one of them was found by hitting a wall first.
>
> Recording the sequence, since it is the concrete answer to what this issue is asking for. Each item is
> filed separately with its own evidence; this is the assembled path.
>
> **What a workflow has to survive, in order, to actually run on a real instance:**
>
> 1. **Frame comments need `position` and `size`.** (#580) Import returns HTTP 400
>    `Field required in ("frame","position")` / `("frame","size")` for any `comments: type: frame` entry
>    lacking them. The pipeline authors frame comments without either. Passes
>    `gxwf draft-validate --concrete`; rejected by real Galaxy.
> 2. **Step `doc:` has an undocumented length ceiling.** Over it, `POST /api/workflows` returns an opaque
>    500 with no traceback. Bisected to 2048 characters on 26.1.2.dev0 (already tracked as #564, which
>    measured a different threshold — see the comment there).
> 3. **Authored UDTs register at `POST /api/unprivileged_tools`, not `/api/dynamic_tools`.** (#585) The latter is
>    admin-only and returns 403 for an ordinary account. The former is gated only by a
>    `USER_TOOL_EXECUTE` role plus `enable_beta_tool_formats`, both of which an ordinary usegalaxy.org
>    account already satisfies. It returns a real `tool_uuid`.
> 4. **A UDT step needs that `tool_uuid` injected into native `.ga`.** (#587) gxformat2 has no `tool_uuid` field,
>    and a bare `tool_id` never resolves to a user-scoped dynamic tool however correct the string is — the
>    steps import as "Tool is not installed". The working path is: import, `GET /api/workflows/{id}/download`,
>    hand-inject each registered `tool_uuid`, re-`POST` the native form.
> 5. **`tool_id` must be the versioned path for invocation.** (#591) `download?style=ga` emits unversioned ids
>    with the version in `tool_version`. That document saves cleanly with zero step errors — and then
>    cannot be invoked, with a 400 naming installed tools as not installed. Only the versioned
>    `…/tp_cat/9.11+galaxy0` form invokes.
> 6. **Saving an edited workflow needs `exact_tools: false` and `allow_missing_tools: true`.** (#589)
>    `PUT /api/workflows/{id}` defaults `exact_tools` to true and returns a generic "contains missing
>    tools" message, discarding the per-step list it computed internally. The invocation-time flag people
>    already know (`require_exact_tool_versions`) is named differently here, with no cross-reference.
>
> **The shape of the problem, not just the steps:** every one of these passes the Foundry's own static
> gates. `gxwf validate` and `gxwf draft-validate --concrete` were clean on a workflow that could not be
> imported, then could not be invoked once imported, then contained a wiring defect
> (a `sample_sheet` column wired to a scalar tool port, #588) that only a real production invocation exposed.
>
> So guidance alone may not be the whole fix — several of these are checkable statically, and the ones
> that are not (3–6) are really a missing deploy phase rather than a missing document. A
> `deploy-galaxy-workflow` Mold that performed this sequence, or a `--deploy` mode on
> `run-workflow-test`, would put the knowledge somewhere it executes rather than somewhere it has to be
> read and remembered. Offering that as a suggestion, not a requirement — the documented sequence above
> is useful on its own.
