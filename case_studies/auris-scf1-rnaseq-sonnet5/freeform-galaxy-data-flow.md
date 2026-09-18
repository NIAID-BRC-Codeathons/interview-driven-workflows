# Galaxy Data-Flow Design Brief — Workflow A (SRA Landscape & Spike-In Sieve)

Source: `freeform-summary.md` (Stages A, B, C, D2) and `freeform-galaxy-interface.md` §1
(Workflow A). This brief is an abstract Galaxy-facing DAG for **Workflow A only** — inputs,
nodes, edges, collection map/reduce points, shape-changing placeholders, and unresolved tool
needs. It is not `gxformat2` and does not resolve exact Tool Shed changesets; that is
`freeform-summary-to-galaxy-template` / `implement-galaxy-tool-step`'s job.

## 0. Scope (user-confirmed, binding for this run)

This run builds **only Workflow A**: kmindex containment screen → LexicMap streaming search →
the custom multi-HSP tiling/QC/haplotype-collapsing step the user calls **LexicMapStreamer**
(built on `stream_lexicmap_msa.py`) → the am3 spike-in diagnostic. Workflows B, C, D from the
interface brief are **not wired here**:

- **Workflow B** (Stage E — Idaho 2024 / Dickins 2009 experimental-evolution trajectory
  validation, bowtie2/samtools/mpileup) is a **confirmed nice-to-have**, explicitly scoped as a
  **separate, later workflow** — out of scope for this run, not abandoned. No data-flow nodes
  are proposed for it here; see `open-requirements.ledger.yml` entry
  `workflow-scope-boundary-unresolved` (now resolved with this scope decision recorded).
- **Workflows C and D** (Stage C′ disassembler/logan-walker cDBG track, Stage F/G/H VEP +
  dual-coding calibration, Stage I ChronAeon) are out of scope for this run's design entirely.
  Their ledger entries are carried forward untouched below.

## 1. Workflow-level inputs (Workflow A)

| Input | Shape | Feeds |
|---|---|---|
| `Reference genome (NC_001422.1)` | `data` (fasta) | **Not wired to any node below** — see §7 open question; likely provenance/documentation only, not a computational dependency of Stages B/C as described in the source |
| `Gene query panel` | `data_collection`, `sample_sheet` (10 elements A,B,C,D,E,F,G,H,J,K), `column_definitions` carrying per-gene LexicMap sensitivity overrides (`align_min_match_pident`, `align_min_match_len`, `seed_min_prefix`, `min_qcov_per_genome`, all `optional: true`) | N1 (combine), N4 (per-gene LexicMap search) |
| `Logan kmindex DB selection` | `string` (multi-select over the 109 hardcoded shard names) | N2 |
| `LexicMap index selection` | `string` (multi-select over 25 domain indices / 5-index `TARGETED_PHAGE_INDICES` subset) | N4 |
| `kmindex parameters` | typed params (`zvalue=6`, `threshold=0.3`, `format=json`, `fast=false`) | N2 |
| `LexicMap parameters` | typed params (`top_n_genomes=0`, `advanced_settings\|all=true`) | N4 (default branch) |
| `Tiling/QC parameters` | typed params (`min_coverage=0.80`, `min_coverage_partial=0.50`, `min_pident=60.0`, `max_internal_stops=0`, `sample_cap=10`, `allow_frameshifts` boolean, default unconfirmed) | N5 |
| `Nominal-taxonomy BioProject classification table` | `data` (tabular, reference) | **Not wired to any node** — modeled as reference/provenance data only, per ledger `nominal-taxonomy-audit-not-modeled-as-step` |

## 2. Nodes and edges

**N1 — Combine per-gene panel into bulk query FASTA** (fan-in / combine)
Input: `Gene query panel` (sample_sheet, 10 elements) → Output: one combined multi-FASTA dataset.
Idiom: fan-in/combine (`fan-in-bundle-consume-and-flatten` family) — collection-of-sequences to
one dataset. Confidence: high (source states the combined panel is the literal kmindex query
input).

**N2 — kmindex containment screen** (map-over)
Input: N1 output (single FASTA) × `Logan kmindex DB selection` → Output: `kmindex containment
hits (per shard)`, `list` collection of JSON, one element per selected shard.
Tool: real Tool Shed wrapper, `toolshed.g2.bx.psu.edu/repos/iuc/kmindex/kmindex_query/0.6.1+galaxy4`
(existence high confidence). Open: exact Galaxy-side mechanism for exposing 109 DB shard names
as a map-over axis (repeat vs. multi-select vs. per-element data input) — ledger
`kmindex-lexicmap-index-selection-mechanism`.

**N3 — Merge/union kmindex hit maps** (fan-in, custom aggregation)
Input: N2 output (list of per-shard JSON) → Output: `kmindex accession union` (`data`, txt).
Idiom: fan-in reduce, but the merge logic (dedup accessions across shards, keep max containment
score) is currently ad hoc Python (`harvest_collection()` walking the Galaxy history-contents API
32-threaded) — no built-in Galaxy collection operation performs this; flagged as an **unresolved
tool need** (§4). Confidence: medium — transform intent is clear, concrete Galaxy-native
implementation is not.

**N4 — LexicMap streaming search** (nested map-over: gene × index, then per-gene reduce)
Input: `Gene query panel` (sample_sheet, per-gene FASTA + optional per-gene sensitivity columns) ×
`LexicMap index selection` → per-(gene, index) tabular hit table → reduced over the index axis
→ Output: `LexicMap results (per gene)`, `sample_sheet` (mirrors the 10-gene panel).
Tool: real Tool Shed wrapper, `toolshed.g2.bx.psu.edu/repos/iuc/lexicmap/lexicmap_search/0.9.0+galaxy1`
(existence high confidence).
Conditional: for genes A/C/E/K, the sample_sheet's per-gene columns
(`align_min_match_pident=60.0`, `align_min_match_len` 35–50, `seed_min_prefix` 15–17,
`min_qcov_per_genome=30.0`) override the workflow-level `LexicMap parameters` default
(`top_n_genomes=0`, `advanced_settings|all=true`) used by the other six genes. Idiom:
`conditional-transform-or-pass-through` (pick_value between column-supplied override and
workflow default, gated on whether the optional column is populated).
Idiom for the index-axis reduce: `collection-flatten-after-fanout` (list:list → list, preserving
gene `element_identifier`). Per the sample_sheet note, this map-over does **not** propagate
`column_definitions` automatically — the per-gene tuning metadata must be read at the point of
the N4 tool call itself (from the *input* sample_sheet), not assumed to survive onto the output
collection for N5 to reuse.
Confidence: high on tool identity and the two named parameter sets; medium on the exact
index-selection surfacing mechanism (same ledger entry as N2) and on the pick_value wiring for
the conditional per-gene override.

**N5 — LexicMapStreamer: multi-HSP tiling, codon QC, haplotype collapsing** (map-over, multi-output per element)
Input: `LexicMap results (per gene)` (N4 output, sample_sheet) + `Tiling/QC parameters` →
mapped one tool call per gene, each producing **8 files**: `.clean.msa.fasta`,
`.clean.haplotypes.tsv`, `.clean.accessions.fasta`, `.clean_expanded.accessions.fasta`,
`.flagged.accessions.fasta`, `.flagged.tsv`, `.cohort_ledger.tsv`, `.summary.json`.
Outputs map onto the interface brief's: `Clean full-length CDS haplotypes (per gene)`, `Clean
haplotype counts (per gene)`, `Flagged accessions + audit reasons (per gene)`, `Per-accession
cohort ledger (per gene)`, `Per-gene ingestion summary` — all `sample_sheet`-shaped, gene-keyed.
Idiom: map-over with a **record-shaped per-element output**. Because each gene element produces
8 named, heterogeneously-typed artifacts (not one), `sample_sheet:record` (named typed slots) is
a better-fitting output shape than eight parallel `sample_sheet` collections that all have to be
kept in identifier lockstep by hand — flagged as a **design recommendation for the template
phase**, not a decided wiring (medium confidence; the source never states a Galaxy collection
type, this is this brief's translation).
Tool need: **LexicMapStreamer** — see §4, this is the central tool-needs item for Workflow A.
Confidence: high on operation shape and per-gene multiplicity (directly and precisely described
in the source, including the exact 8 output artifacts and the paper's headline Table 1 numbers);
medium-low on the exact CLI-flag-to-Galaxy-input mapping pending wrapper authoring.

**N6 — Ingestion manifest aggregation** (fan-in, tabular bridge)
Input: `Per-gene ingestion summary` (`.summary.json`, sample_sheet, from N5) → Output: `Ingestion
manifest (all genes)` (`data`, csv).
Idiom: tabular bridge / fan-in, akin to `tabular-concatenate-collection-to-table` but the source
rows are JSON, not TSV — each element's `.summary.json` must first be flattened into one row
before concatenation. No generic Galaxy tool flattens an arbitrary per-gene JSON summary into a
manifest row; flagged as a **placeholder transformation** (§5). Confidence: high on intent
(source names `lexicmap_9genes_ingestion_manifest.csv` explicitly as this aggregation), medium on
mechanism.

**N7 — Gene E am3 quarantine audit extraction** (collection-unbox / extract-by-identifier)
Input: `Per-gene ingestion summary` or `Flagged accessions + audit reasons (per gene)` (N5 output,
sample_sheet) → Output: `Gene E am3 quarantine audit` (`data`, JSON, single dataset).
Idiom: `collection-unbox-singleton` (`__EXTRACT_DATASET__`, `which: first` / by
`element_identifier == "E"`). The source states the am3 detection logic lives *inside*
LexicMapStreamer's QC step (not a separate computation), so this node is presented as an
**extraction of the Gene E element**, not a new statistic. Confidence: medium — the source
confirms the am3 diagnostic is computed inside N5's QC pass and is summarized in
`gene_e_am3_quarantine_audit.json`, but does not confirm whether that file is literally the Gene
E element of the `.summary.json` sample_sheet or a ninth, separate per-gene artifact N5 also
emits. Carried as an open question (§7) rather than guessed.

## 3. Collection idiom summary

| Node | Idiom | Pattern reference |
|---|---|---|
| N1 | fan-in / combine | `fan-in-bundle-consume-and-flatten` |
| N2 | map-over (list axis over DB shard selection) | `manifest-to-mapped-collection-lifecycle` |
| N3 | fan-in / custom merge (no built-in match) | — (unresolved tool need) |
| N4 | nested map-over + partial reduce; conditional per-gene override | `collection-flatten-after-fanout`, `conditional-transform-or-pass-through` |
| N5 | map-over with record-shaped multi-output per element | `sample_sheet:record` (see `galaxy-sample-sheet-collections.md`) |
| N6 | fan-in / tabular bridge from JSON | `tabular-concatenate-collection-to-table` (adapted; source is JSON not TSV) |
| N7 | extract-by-identifier | `collection-unbox-singleton` |

## 4. Unresolved Galaxy tool needs

1. **kmindex hit-map merge/union (N3).** No named existing Galaxy tool; today implemented as ad
   hoc BioBlend/Python (`harvest_collection()`, `process_kmindex_with_disassembler.py`). Needs
   either a bespoke Galaxy tool or a generic JSON-aggregation tool. Not resolved here.

2. **LexicMapStreamer (N5) — known source, wrapper authoring still pending, NOT "no existing
   implementation."** The user has confirmed the multi-HSP tiling/codon-QC/haplotype-collapsing
   logic behind `stream_lexicmap_msa.py` already exists as a real, working implementation in the
   private repository **`https://github.com/nekrut/disassembler`** — this is the actual code, not
   something to author from scratch by re-reading `stream_lexicmap_msa.py`'s prose description.
   What remains open: a Galaxy tool wrapper (XML + macros, or a Planemo-testable CLI wrapper) has
   not yet been authored against that repo's real CLI/API surface. `discover-shed-tool` should
   first check whether a Tool-Shed wrapper already exists for this repo before falling through to
   `author-galaxy-tool-wrapper`; if authoring is needed, it should target the repo's actual
   interface rather than reverse-engineering flags from the summary alone. This also affects the
   `--allow-frameshifts` default (item 3 below) and the exact shape of N5's 8 output artifacts —
   both should be confirmed by reading the real source, not left as unconfirmed prose.

3. **`--allow-frameshifts` default (N5 parameter).** Still unconfirmed, but no longer a blind
   unknown: this flag lives in the now-located `nekrut/disassembler` implementation and can be
   read directly once that repo is inspected during wrapper authoring, rather than inferred from
   `stream_lexicmap_msa.py`'s prose alone.

4. **kmindex/LexicMap DB- and index-selection surfacing (N2, N4).** The real Tool Shed tools'
   exact input schema for the 109 kmindex shards / 25 LexicMap indices has not been inspected
   (`summarize-galaxy-tool` has not run against the pinned versions). This is a property of the
   upstream IUC wrappers, not of LexicMapStreamer — the `nekrut/disassembler` discovery does not
   bear on it. Still open; see ledger.

5. **N6 JSON-to-tabular-row flattening.** No generic Galaxy tool flattens an arbitrary nested
   per-gene `.summary.json` into one manifest row; likely needs a small custom script/tool.

## 5. Placeholder (shape-changing) transformations

- N3: JSON collection (list, per-shard) → deduplicated accession list (single txt dataset) +
  implicit per-gene max-containment scores. Not a built-in Galaxy op.
- N4 reduce: `list:list` (gene × index) → `list` (gene only), collapsing the index axis while
  preserving gene `element_identifier`s and re-deriving any per-gene metadata the map-over step
  did not propagate (sample_sheet `column_definitions` are not carried onto tool outputs — see
  §1's `Gene query panel` row and the sample_sheet reference note).
- N5: LexicMap tabular hit table (per gene) → 8 heterogeneous output artifacts per gene
  (fasta ×3, tabular ×3, JSON ×1, fasta ×1) — the paper's core multi-HSP tiling/QC contribution;
  a record-shaped (`sample_sheet:record`) output is recommended over eight parallel collections.
- N6: nested JSON (per gene) → flat CSV row → concatenated manifest.
- N7: sample_sheet element (gene="E") → standalone dataset (unbox).

## 6. Confidence summary

- **High:** N1, N2, N4 (tool identity + named parameter sets), N5 (operation shape, per-gene
  multiplicity, 8-artifact output), N6 (intent).
- **Medium:** N3 (merge intent clear, mechanism ad hoc), N4 (conditional pick_value wiring,
  index-selection surfacing), N5 (`sample_sheet:record` recommendation, exact CLI-to-input
  mapping pending wrapper authoring), N6 (flattening mechanism), N7 (whether the am3 audit is an
  extracted element vs. a distinct 9th artifact).
- **Low / open:** whether `Reference genome (NC_001422.1)` is wired to any node at all (§7); the
  kmindex/LexicMap DB-and-index-selection Galaxy input surface (§4.4).

## 7. Open questions carried forward (not resolved by this brief)

1. Is the whole-genome `Reference genome (NC_001422.1)` input actually consumed by any Workflow A
   node? The source's own language ("canonical ΦX174 **gene** coordinate frame") points to the
   per-gene CDS FASTAs already inside `Gene query panel`, not the full circular genome. This brief
   does **not** invent a wiring the source doesn't support — flagged here rather than connected.
   If the template phase also finds no real consumer, consider dropping it from Workflow A's
   declared inputs (it may belong to Workflow B, where `NC_001422.1:2395-2919` is genuinely used).
2. Whether `Nominal-taxonomy BioProject classification table` should remain a declared Galaxy
   workflow input at all, given it is wired to nothing (see ledger
   `nominal-taxonomy-audit-not-modeled-as-step`) — an unconnected input is unusual for a runnable
   workflow; alternative is to drop it to documentation/README rather than a workflow input.
3. Whether N7's Gene E am3 audit JSON is literally the Gene E element of N5's `.summary.json`
   sample_sheet, or a ninth, separate artifact LexicMapStreamer also emits — resolvable once the
   `nekrut/disassembler`-backed wrapper's real output surface is known.
4. Exact Galaxy-native mechanism for kmindex/LexicMap DB- and index-selection (repeat vs.
   multi-select vs. per-element data input) — pending `summarize-galaxy-tool` against the pinned
   IUC changesets.

## 8. Open-requirements ledger cross-reference

See `open-requirements.ledger.yml` for full entries. This phase:

- **Resolved** `workflow-scope-boundary-unresolved` — user confirmed this run builds Workflow A
  only; Workflow B deferred as a nice-to-have second workflow; Workflows C/D out of scope.
- **Added** `lexicmapstreamer-implementation-provenance` (resolved) and
  `lexicmapstreamer-wrapper-authoring-pending` (open) to record the `nekrut/disassembler`
  discovery and the remaining wrapper-authoring work.
- **Updated note only (status unchanged, still open)** on `allow-frameshifts-default-unconfirmed`
  and `kmindex-lexicmap-index-selection-mechanism` to add the new provenance context.
- **Untouched:** `host-biome-platform-stratification-script-gap`,
  `nominal-taxonomy-audit-not-modeled-as-step`, `chronaeon-synthetic-metadata-phase0`,
  `chronaeon-hardcoded-statistics-phases`, `wei-2026-dms-dataset-external-sourcing`,
  `hyphaeon-toolshed-status-unverified` — all pertain to Workflows B/C/D, out of scope for this
  brief's wiring.

## 9. Foundry feedback

No feedback ledger entry was appended for this run. Rationale: the skill bundle's contract note,
ledger protocol note, sample-sheet note, and the collection/tabular/conditionals pattern MOCs
were sufficient to produce this brief — every difficulty encountered (ambiguous per-gene output
shape, ad hoc merge logic, an input that may not actually be wired) was a property of the source
project, not a defect or gap in the Foundry skill bundle itself.
