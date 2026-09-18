# Galaxy data-flow brief — *C. auris* Scf1 RNA-seq differential expression

Source handoffs: `freeform-summary.md` (Santana et al. 2023, *Science* 381:1461–1467; DOI 10.1126/science.adf8972) and `freeform-galaxy-interface.md` (phase 2).

This brief owns the Galaxy-shaped abstract DAG: nodes, edges, collection map/reduce choices, shape-changing placeholder transformations, and unresolved tool needs. It is **not** gxformat2, pins no Tool Shed tool ids or versions, and settles no step parameters. Built-in Galaxy collection operations are named as *candidates* (`__SAMPLE_SHEET_TO_TABULAR__`, `__FILTER_FROM_FILE__`) because the shape argument is unintelligible without them; the template and step-implementation Molds confirm or replace each one.

Consumers: `compare-against-iwc-exemplar`, `freeform-summary-to-galaxy-template`, `freeform-summary-to-galaxy-test-plan`.

---

## 1. What this phase settled

**Settled.** The per-sample `condition` metadata reaches DESeq2's factor levels by an identifier-keyed split of the counts collection, driven by a tabular projection of the sample sheet. §4 gives the path, the rejected alternatives, and the one residual verification. This closes open-requirements entry `sample-sheet-condition-to-deseq2-factor-wiring`.

**Deliberately left open.** The DESeq2 node's arity — one run over a three-level factor versus two runs over two-level factors (`deseq2-contrast-realization-unsettled`) — is not settled here, and §4.4 shows why it does not need to be: both realizations consume the *same* per-level counts collections, so the entire upstream wiring is realization-independent. What would settle it is wrapper evidence this phase has no route to: an IWC exemplar at phase 4, or a `summarize-galaxy-tool` pass on the chosen DESeq2 wrapper.

**Newly surfaced.** Three places where the interface brief's declared shapes are not achievable as written under Galaxy map-over semantics (§7), plus two parameterization gaps (§7.3, §5.4). All five are ledgered.

---

## 2. Abstract operation graph

```
[in 1] RNA-seq reads  (collection, sample_sheet:paired, column_definitions: condition, replicate)
  │
  ├─ map over each fastq ──► (A) qc_raw_reads ────────────────► [out 1] text summary   (nested — §7.1)
  │                                                            [out 2] HTML report
  │
  ├─ map over each row ───► (B) trim_reads ───────────────────► [out 3] trimming report
  │                              │                             [out 4] trimmed reads
  │                              ▼
  │                         (C) align_reads ◄── [in 2] genome FASTA
  │                              │            ◄── [in 3] annotation GTF
  │                              ├──────────────────────────────► [out 5] BAM
  │                              ├──────────────────────────────► [out 6] mapping summary
  │                              ▼
  │                         (D) count_features ◄── [in 3] annotation GTF
  │                              │               ◄── [in 5] strandedness
  │                              ├──────────────────────────────► [out 7] gene counts per sample
  │                              └──────────────────────────────► [out 8] assignment summary
  │                                        │
  └─ (E) sample_metadata_table ────────┐   │  (counts collection, keyed by element identifier)
         (__SAMPLE_SHEET_TO_TABULAR__) │   │
                                       ▼   │
                      (F₁..F₃) select_level_L  ×3  ◄── [in 4] reference condition level (+ §7.3)
                                       │   │
                                       ▼   ▼
                      (G₁..G₃) counts_for_level_L  ×3   (__FILTER_FROM_FILE__)
                                       │
                                       ▼  reduce: collection → multiple=true data input, one per level
                              (H) differential_expression  (DESeq2)
                                       ├──────────► [out 9]  normalized counts
                                       ├──────────► [out 10] results: tnSWI1 vs AR0382
                                       ├──────────► [out 11] results: AR0387 vs AR0382
                                       ├──────────► [out 14] diagnostic plots
                                       ▼
                      (I₁, I₂) filter_significant  ×2 ◄── [in 6] padj, [in 7] fold change (§7.3)
                                       ├──────────► [out 12] significant: tnSWI1 vs AR0382
                                       └──────────► [out 13] significant: AR0387 vs AR0382
```

### 2.1 Nodes

| Node | Abstract operation | Input shape | Output shape | Execution | Confidence |
|---|---|---|---|---|---|
| A `qc_raw_reads` | read quality report | `sample_sheet:paired` fastq.gz | nested collection of txt + html, one element pair per sample | map-over, **one job per fastq** (2 per sample, 12 total) | high on the operation, medium on the output shape (§7.1) |
| B `trim_reads` | quality-trim reads at Phred 20, no adapter | `sample_sheet:paired` fastq.gz | paired-per-sample fastq.gz + per-sample txt report | map-over, one job per row (6 jobs) | high on the operation, medium on whether the pair survives as one inner collection (§7.2) |
| C `align_reads` | splice-aware alignment, index built at run time | paired fastq per sample + genome FASTA + GTF | `bam` per sample + `Log.final.out` per sample | map-over, one job per row (6 jobs); FASTA and GTF broadcast to every job | high |
| D `count_features` | per-gene read counting, stranded | `bam` per sample + GTF + strandedness | 2-column counts tabular per sample + summary tabular per sample | map-over, one job per row (6 jobs) | high |
| E `sample_metadata_table` | project sample-sheet column metadata to tabular | `sample_sheet:paired` (the **workflow input**, not any mapped output) | one tabular: element identifier, condition, replicate | single job, no map-over | medium — mechanism named in the packaged sample-sheet note, output columns unverified (§4.3) |
| F₁–F₃ `select_level_L` | keep rows whose condition equals level L, project the identifier column | tabular from E | one identifier-list tabular per level | 3 single jobs | high on the operation, low on how L is supplied (§7.3) |
| G₁–G₃ `counts_for_level_L` | filter the counts collection to the identifiers of level L | counts collection (from D) + identifier list (from F_L) | counts sub-collection, 2 elements each | 3 single jobs | medium-high |
| H `differential_expression` | negative-binomial DE across a one-factor, three-level design | one counts sub-collection per factor level | result table(s), normalized counts, diagnostic plots | **reduction** — collections consumed by `multiple=true` data inputs | high on the design, **open** on node arity (`deseq2-contrast-realization-unsettled`) |
| I₁, I₂ `filter_significant` | threshold the result table on adjusted p and effect size | one DESeq2 result tabular | filtered tabular | 2 single jobs | high on the operation, medium on the expression (§7.3) |

No node exists for any step the paper does not name. There is no MultiQC, no post-trim QC, no deduplication, no rRNA filter, and no merged count matrix — consistent with the interface brief's closed tool set.

### 2.2 Edges

| Edge | Shape before → after | Evidence |
|---|---|---|
| in 1 → A | `sample_sheet:paired` → per-fastq fan-out | Galaxy map-over: FastQC takes one dataset, so the inner `paired` axis also fans out |
| in 1 → B | `sample_sheet:paired` → per-row jobs | a paired-aware trimmer consumes the inner `paired` element whole |
| B → C | trimmed pair → alignment job | stated tool order in the supplement |
| in 2, in 3 → C | `data` broadcast into every mapped job | no map-over: a `data` input wired to a mapped step is broadcast |
| C → D | `bam` per sample → counting job | stated tool order |
| in 3 → D | `data` broadcast | featureCounts requires the same annotation as the aligner |
| in 1 → E | `sample_sheet:paired` → tabular | §4; the only edge in the workflow that reads `column_definitions` |
| E → F_L | tabular → tabular | row filter on the condition column |
| D, F_L → G_L | (collection, identifier list) → sub-collection | identifier-keyed membership filter |
| G_L → H | collection → reduced multi-data port | sample_sheet-family collections reduce into `multiple=true` data inputs |
| H → I_c | tabular → tabular | the paper's stated significance criteria |

---

## 3. Collection map/reduce decisions

**One map-over region, one reduction point.** Everything from FastQC through featureCounts is a single map-over region over the sample axis established by workflow input 1. DESeq2 is the workflow's only reduction. That is the whole of the collection story except for the split in §4.

**Element identifiers are the spine.** `AR0382_A`, `AR0382_B`, `AR0387_A`, `AR0387_B`, `AR0382_tnSWI1_A`, `AR0382_tnSWI1_B` enter at input 1 and must be unchanged at node D, because (a) the interface keys its checkpoint assertions by element identifier, and (b) §4's split matches identifiers between the metadata table and the counts collection. No node in the map-over region may rename, sort, or reshape the outer axis. If a step-implementation choice would relabel elements, that is a topology defect, not a cosmetic one.

**No collection cleanup node.** `collection-cleanup-after-mapover-failure` (filter empty/failed elements) is *not* warranted here: every step produces exactly one output per input, no step is conditional, no step can legitimately produce an empty element, and a failed element means a real failure that should surface rather than be filtered away. Six elements, dense, homogeneous. Recorded so a later Mold does not add the idiom reflexively.

**No fan-in / concatenate node.** The interface deliberately exposes no merged count matrix, because the Galaxy DESeq2 tool consumes per-sample count files. A `tabular-concatenate-collection-to-table` bridge would be invented method. The only fan-in in the design is DESeq2's own reduction of the per-level collections.

**The outer axis is nominally `sample_sheet`, not `list`.** A tool mapped over a `sample_sheet`-family collection produces a `sample_sheet`-shaped output *without* `column_definitions` (packaged note `galaxy-sample-sheet-collections`, "Mapping rules"). Behaviourally that is a list — it maps, reduces, and filters like one — but its declared collection type is not the string `list`, which matters to anything that type-checks, including test assertions. The interface's output table calls outputs 1–8 `list`/`list:paired`. Ledgered: `mapped-outputs-carry-sample-sheet-outer-axis`.

---

## 4. The condition factor: how it reaches DESeq2 (settled)

This is the decision phase 2 handed down and the reason this phase exists.

### 4.1 The problem, precisely

The `condition` and `replicate` values live in `column_definitions` / per-row `columns` on workflow input 1. Galaxy does not propagate either through map-over. By node D the counts collection carries element identifiers and nothing else. DESeq2 needs its samples grouped by factor level — one set of count files per level — so the grouping has to be reconstructed from a source that still has it.

The metadata survives in exactly one place: **the workflow input itself**, which is still addressable as a node input no matter how far downstream the consumer sits. Every workable route starts there.

### 4.2 The settled route

```
in 1 (sample_sheet:paired, metadata intact)
   └─► E  __SAMPLE_SHEET_TO_TABULAR__      → sample metadata table
            (element identifier | condition | replicate)
   └─► F_L filter rows: condition == L ; project the identifier column
            → identifier list for level L                     (×3: AR0382, AR0387, tnSWI1)
                     └─► G_L __FILTER_FROM_FILE__(counts from D, identifier list)
                             → counts sub-collection for level L   (2 elements)
                                     └─► H DESeq2 factor-level port L
```

Three properties make this the right route rather than merely a workable one:

1. **It joins on element identifiers**, which is the one key Galaxy guarantees across the map-over region — the identifier-keyed wiring the packaged sample-sheet note prescribes over "inventing parallel parameter inputs".
2. **It touches the map-over region not at all.** Nodes A–D are unchanged, promoted outputs 1–8 keep their identifier space, and the split is a side branch off the workflow input.
3. **It is the `sync-collections-by-identifier` idiom** from the packaged collection-pattern MOC (membership sync: derive identifiers from one source, filter a sibling collection), used for its intended purpose rather than adapted.

### 4.3 The one residual

The packaged note documents `__SAMPLE_SHEET_TO_TABULAR__` as iterating elements and tab-joining "for downstream tabular consumers", but does not state its output columns — specifically whether the **element identifier is emitted as a column**. The identifier is the join key for the entire split; if the tool emits only the `column_definitions` values, node E produces a table whose rows cannot be attributed to collection elements and F/G collapse.

This is a bounded, checkable question rather than a design unknown, and it does not change the route — only the implementation of node E. If the identifier is absent, node E is replaced by an Apply Rules projection over the same input collection (identifier column plus a metadata column), and everything from F onward is unchanged. Ledgered: `sample-sheet-to-tabular-identifier-column-unverified`.

### 4.4 Why this is independent of the DESeq2 realization

Both candidate realizations of `deseq2-contrast-realization-unsettled` consume the same three per-level counts collections:

- **One run, three-level factor** — H has three factor-level ports (G₁, G₂, G₃) and emits both contrasts against the reference level.
- **Two runs, two-level factors** — H splits into H₁ (G_AR0382, G_tnSWI1) and H₂ (G_AR0382, G_AR0387); the reference-level collection feeds both.

Nodes E, F₁–F₃, G₁–G₃ are identical either way, as is the map-over region. The choice changes only how many DESeq2 nodes exist and which level ports they carry, so it can be deferred to wrapper evidence without holding up the template's spine. The interface's output surface (two result tables, two filtered tables) is satisfied under both.

### 4.5 Why this is robust to the interface's own fallback

Phase 2 named a fallback: replace input 1 with `list:paired` reads plus a `data` input `Sample metadata table` (sample_id, condition, replicate). Under that fallback, **node E disappears and nothing else changes** — the user-supplied table lands where E's output lands, and F/G/H are untouched. So if `sample-sheet-input-test-fixture-expressibility` resolves against the sample sheet at the test-plan phase, the cost is one node and an interface edit, not a redesign. That is the main reason to route the metadata through a tabular intermediate instead of a sample-sheet-native mechanism.

### 4.6 Rejected alternatives

| Alternative | Why rejected |
|---|---|
| **Apply Rules `add_column_from_sample_sheet_index` on the counts collection** | The rule reads sample-sheet column metadata, and the counts collection has none — by node D the `column_definitions` are gone. Applied to input 1 instead, it degenerates to the settled route with a different node E. |
| **Filter the counts collection by element-identifier regex** | The identifiers encode the condition, so a regex looks free. It is a trap: `AR0382_tnSWI1_A` contains the substring `AR0382`, so an unanchored match for the reference level silently captures the mutant samples and corrupts the contrast. An anchored `^AR0382_[AB]$` works but hard-binds the workflow to this study's naming convention, which is exactly what the sample-sheet input was chosen to avoid. |
| **Split the reads collection by condition up front and run three parallel map-over regions** | Triples every step, and replaces the six promoted per-sample output collections with three per-condition ones — breaking the interface's checkpoint identifier space and its assertion design. |
| **Three condition-scoped `list:paired` workflow inputs** | Already rejected at interface time for hard-coding the three-level design into the public API; nothing in the data-flow analysis reopens it. |
| **A parameter input carrying conditions in parallel with the reads** | The failure mode the packaged sample-sheet note names explicitly: parallel parameter inputs have no guaranteed correspondence with collection elements, so the sample↔condition binding becomes positional and silently wrong on reorder. |

---

## 5. Shape-changing and placeholder transformations

| # | Transformation | Where | Necessity | Note |
|---|---|---|---|---|
| 5.1 | sample-sheet → tabular bridge | node E | required | The only read of `column_definitions` in the workflow. §4.3. |
| 5.2 | tabular row filter + column projection | F₁–F₃ | required | One per factor level. Trivially implementable; the open part is where the level string comes from (§7.3). |
| 5.3 | collection membership filter by identifier file | G₁–G₃ | required | `__FILTER_FROM_FILE__` emits *two* collections (matching and non-matching); only the matching branch is consumed. The template should not promote the discarded branch. |
| 5.4 | log₂ conversion or threshold restatement before I₁/I₂ | I₁, I₂ | conditional | DESeq2 reports log₂ fold change; workflow input 7 is a **linear** fold change (default 2.0). The filter must compare `abs(log2FoldChange) > log2(threshold)`. §7.3, ledgered. |
| 5.5 | collection flatten after FastQC | after A | conditional | Needed only if the interface's flat `list` shape for outputs 1–2 is kept rather than corrected. §7.1 recommends correcting the interface instead. |
| 5.6 | re-pair trimmed reads | after B | conditional | Needed only if the chosen trimmer emits R1 and R2 as two parallel collections rather than one paired-inner collection. §7.2, ledgered. |

None of these is an invented analysis step: 5.1–5.3 are plumbing the Galaxy collection model forces, and 5.4–5.6 are shape repairs, not method. Nothing here adds a computation the paper does not describe.

---

## 6. Unresolved tool needs

Handoff units for `discover-shed-tool` / the template Mold. Input and output shapes are given because that is what discovery needs; no tool id, owner, or version is asserted.

| Need | Abstract role | In → out | Candidate class | Confidence |
|---|---|---|---|---|
| read QC report | A | `fastqsanger.gz` → `txt` + `html` | FastQC, named by the paper | high |
| quality trimming, paired-aware, Phred 20, no adapter | B | paired `fastqsanger.gz` → paired `fastqsanger.gz` + `txt` | Cutadapt, named by the paper | high |
| splice-aware aligner with run-time index build | C | paired fastq + `fasta` + `gtf` → `bam` + `txt` | RNA STAR, named by the paper | high |
| stranded feature counting | D | `bam` + `gtf` + strandedness → `tabular` ×2 | featureCounts, named by the paper | high |
| sample-sheet → tabular | E | `sample_sheet:paired` → `tabular` | built-in `__SAMPLE_SHEET_TO_TABULAR__` | medium — §4.3 |
| tabular row filter / column cut | F | `tabular` → `tabular` | stock text-manipulation tools | high |
| collection filter by identifier file | G | collection + `tabular` → collection ×2 | built-in `__FILTER_FROM_FILE__` | medium-high |
| differential expression from per-sample counts | H | counts collections per level → `tabular` + `pdf` | DESeq2, named by the paper | high on the tool, open on arity |
| significance filter with a log₂ comparison | I | `tabular` + 2 params → `tabular` | stock filter tool, if its expression language supports the comparison in §5.4 | medium |

No need on this list is expected to require `author-galaxy-tool-wrapper`. Every named tool is a long-standing IUC wrapper and every plumbing node is a Galaxy built-in — which is the expected shape for a workflow the authors state they ran on usegalaxy.org.

---

## 7. Where the interface brief's declared shapes do not hold

These are corrections this phase owes upstream, not preferences. Each is ledgered so the template does not quietly implement one reading while the test plan asserts the other.

### 7.1 FastQC outputs are nested, not flat lists

FastQC consumes one dataset. Mapped over a `sample_sheet:paired` collection it therefore fans out over the **inner** axis too: 12 jobs, and outputs shaped one pair of reports per sample, not six flat elements. The interface declares outputs 1 and 2 as `list`.

Two ways out. **Promote the nested collection** (recommended): honest about what the workflow computes, keeps per-read-direction reports — which is what a reader wants from raw-read QC — and preserves identifiers. Or **flatten** with an explicit node, which satisfies the declared `list` but rewrites the identifier space to something like `AR0382_A_forward`, doubling the identifier vocabulary the tests key on for no analytical gain. Ledger: `fastqc-per-read-fanout-not-a-flat-list`.

### 7.2 Trimmed reads may arrive as two parallel collections

The interface declares `Trimmed reads` as `list:paired`. Whether the trimmer emits one paired-inner collection per sample or two parallel single-ended collections (R1, R2) is wrapper-dependent and not knowable in this phase. If it is the latter, the design needs a re-pair node (§5.6) before node C, or node C must take two parallel collection inputs in dot-product. Ledger: `trimmed-reads-paired-reassembly-conditional`.

### 7.3 Two parameter gaps the wiring exposes

- **Factor level names.** Nodes F₁–F₃ each need a literal condition value. The interface exposes only `Reference condition level` (default `AR0382`). The two contrast levels — `AR0387`, `tnSWI1` — have no parameter and would otherwise be baked into two filter steps, which re-hard-codes into the *steps* the design the sample-sheet input kept out of the *interface*. Ledger: `deseq2-factor-level-names-not-parameterized`.
- **Fold-change units.** Input 7 is `Minimum absolute fold change`, default `2.0`, linear. DESeq2 emits log₂. Either the filter expression converts, or input 7 is restated as a log₂ threshold (default `1.0`) with its label changed. Silently comparing `|log2FoldChange| > 2.0` would apply a 4-fold cut and quietly fail to reproduce the paper's gene list. Ledger: `fold-change-threshold-linear-vs-deseq2-log2fc`.

---

## 8. Data-flow evidence bearing on entries this phase did not close

Recorded here rather than by editing another Mold's ledger entries.

- **`reference-genome-delivery-shape-unverified`.** The history-FASTA choice means RNA STAR builds its index **inside each of the six mapped jobs** — the design has no separate index-build node, because the standard RNA STAR wrapper with a history reference has no separate index step to wire. Six redundant index builds of a ~12.5 Mb fungal genome is cheap in absolute terms, so this does not argue against the portability decision; it does mean a built-in index, if one exists, would change job count but not workflow topology. Whoever revisits the entry should know the topology is insensitive to it.
- **`featurecounts-annotation-source-unnamed`.** Input 3 is consumed **twice** (nodes C and D), so the annotation choice is load-bearing for splice junctions as well as counting. If the chosen source is GFF3, a conversion node appears between input 3 and both consumers — a shape change, not just a datatype edit.
- **`rnaseq-strandedness-inferred-from-kit-name`.** The empirical check is already wired: node D's summary output (interface output 8) is promoted, so the check needs no new node and no new data.
- **`galaxy-tool-versions-unpinnable-from-source`** and **`cutadapt-adapter-and-length-filter-unstated`** have no data-flow consequence; the graph is identical under any resolution.

---

## 9. Confidence

| Claim | Evidence class | Confidence |
|---|---|---|
| Node order A→B→C→D→H→I | stated tool chain in the supplement | high |
| Single map-over region over the sample axis, single reduction at DESeq2 | Galaxy collection semantics + the interface's input shape | high |
| Condition reaches DESeq2 by identifier-keyed split (§4.2) | packaged sample-sheet note (map-over does not propagate metadata) + collection-pattern MOC (`sync-collections-by-identifier`) | high on the shape, medium on node E's implementation |
| `__SAMPLE_SHEET_TO_TABULAR__` emits the element identifier | not stated in any packaged reference | low — §4.3 |
| `__FILTER_FROM_FILE__` is the right collection filter | named by the collection-pattern MOC's identifier section, one-line description only | medium-high |
| FastQC fans out per fastq (§7.1) | Galaxy map-over semantics on a single-dataset input | high |
| Trimmer output pairing (§7.2) | wrapper-dependent, no evidence available in this phase | low |
| DESeq2 node arity | wrapper-dependent, no evidence available in this phase | open, not estimated |
| No cleanup node needed | dense homogeneous collection, no conditional steps | high |
| Fold-change unit mismatch (§7.3) | DESeq2 reports log₂ by definition; interface parameter is linear | high |

Evidence-class caveat: the packaged pattern references in this bundle are **MOC index pages**, not the recipe pages they name. Every idiom selection in §3–§5 was made from a one-line MOC description, with no corpus recipe available to check tool ids or worked wiring against. Confidence above is stated accordingly, and phase 4's exemplar comparison is the natural place to correct it.

---

## 10. Open questions

Rendered as an index of the open-requirements ledger, one line per entry, so the ledger stays the single source of truth. Entry ids are the join key.

Inherited and still open:

1. `featurecounts-annotation-source-unnamed` — annotation unnamed; consumed twice (§8).
2. `rnaseq-strandedness-inferred-from-kit-name` — inference; check already wired (§8).
3. `sample-sheet-input-test-fixture-expressibility` — test-plan phase; this design absorbs either answer at the cost of one node (§4.5).
4. `deseq2-contrast-realization-unsettled` — node arity only; upstream wiring is realization-independent (§4.4).
5. `reference-genome-delivery-shape-unverified` — topology-insensitive (§8).
6. `cutadapt-adapter-and-length-filter-unstated` — no data-flow consequence.
7. `galaxy-tool-versions-unpinnable-from-source` — no data-flow consequence; expected to be surrendered at the terminal.
8. `tnbcy1-contrast-not-carried` (dropped) — unchanged.
9. `pipeline-b-tdna-mapping-not-carried` (dropped) — unchanged.

Closed by this phase:

10. `sample-sheet-condition-to-deseq2-factor-wiring` — resolved; §4.

Raised by this phase:

11. `sample-sheet-to-tabular-identifier-column-unverified` — §4.3.
12. `deseq2-factor-level-names-not-parameterized` — §7.3.
13. `fold-change-threshold-linear-vs-deseq2-log2fc` — §7.3.
14. `fastqc-per-read-fanout-not-a-flat-list` — §7.1.
15. `trimmed-reads-paired-reassembly-conditional` — §7.2.
16. `mapped-outputs-carry-sample-sheet-outer-axis` — §3.

---

## 11. Handoff notes

**To `compare-against-iwc-exemplar` (phase 4).** The two things worth diffing against the corpus are (a) how published RNA-seq workflows get a per-sample factor into DESeq2 — if IWC has a worked sample-sheet or metadata-table split, it likely settles §4.3 and possibly §7.3 at once — and (b) the DESeq2 node arity behind multiple contrasts, which settles `deseq2-contrast-realization-unsettled`. Both are shape questions an exemplar answers directly. The rest of the spine (FastQC → trim → align → count) is conventional enough that structural divergence there would be surprising.

**To `freeform-summary-to-galaxy-template` (phase 5).** Build the map-over region A–D and the split E→F→G as separate template regions; they connect only at node G's collection input. Nodes F and G are three near-identical steps each — do not collapse them into a single templated step, because DESeq2's factor-level ports are structurally distinct. Leave node H's arity as a deferred step until phase 4 reports. Do not promote the discarded branch of any `__FILTER_FROM_FILE__` (§5.3).

**To `freeform-summary-to-galaxy-test-plan` (phase 8).** Three things here change what tests can assert: the collection type of outputs 1–8 is `sample_sheet`-family, not `list` (§3); FastQC's output identifier space depends on how §7.1 resolves; and the strongest deterministic checkpoint remains output 7, keyed by gene id, which is also the input to the whole §4 split — an assertion there covers the map-over region and the identifier spine in one.
