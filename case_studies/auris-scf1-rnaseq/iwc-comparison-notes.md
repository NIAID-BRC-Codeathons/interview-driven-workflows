# IWC exemplar comparison — *C. auris* Scf1 RNA-seq differential expression

Source handoffs: `freeform-galaxy-interface.md` (phase 2) and `freeform-galaxy-data-flow.md` (phase 3). Where the two conflict, the data-flow brief governs (its §7 corrects six declared shapes); this note takes that as given and diffs against the corrected reading.

Consumers: `freeform-summary-to-galaxy-template` (phase 5), `freeform-summary-to-galaxy-test-plan` (phase 8).

## Corpus provenance

| | |
|---|---|
| Corpus | `https://github.com/galaxyproject/iwc` |
| HEAD | `fe41a79` (`main`; merge of PR #1337) |
| Clone | shallow, taken 2026-09-16, read-only |
| Normalization | `gxwf convert <file>.ga --to format2 --compact` (`@galaxy-tool-util/cli`, `gxwf --version` reports `1.0.0`) |

**Environment deviation.** The Mold's procedure says to clone or pull the corpus to `~/.foundry/iwc`. That path is not creatable on this machine (`mkdir ~/.foundry` → `Operation not permitted`, with and without the Bash sandbox), so the harness supplied a fresh clone elsewhere and this phase read it in place. No `git pull` was run and nothing was written inside the clone, so the comparison is pinned to `fe41a79` rather than to corpus `main` at read time. Raised as feedback against the Mold: the path is hard-coded with no environment override.

---

## 1. Ranking

Candidates were drawn by tool family across the whole corpus, not by directory name: `deseq2` matches 2 workflows, `featurecounts` 3, `rgrnastar` 2, `cutadapt` 10.

| Rank | IWC workflow ID | Covers | Confidence |
|---|---|---|---|
| 1 | `transcriptomics/rnaseq-de/rnaseq-de-filtering-plotting` | the DE tail — data-flow nodes H, I | **High** |
| 2 | `transcriptomics/rnaseq-pe/rnaseq-pe` | the map-over head — nodes A–D | **Medium** |
| 3 | `epigenetics/cutandrun/cutandrun` | the Cutadapt step only | **Low / tool-level evidence, not a domain exemplar** |
| — | `transcriptomics/rnaseq-sr/rnaseq-sr` | single-read sibling of #2 | not ranked — wrong read topology, no independent signal |
| — | `scRNAseq/pseudobulk-worflow-decoupler-edger` | pseudobulk DE | no match — edgeR/decoupler, single-cell domain; the `deseq2` grep hit is a doc mention, not a step |

### 1.1 Why rank 1 is High

Same domain and subdomain (bulk RNA-seq differential expression). Same input topology at the boundary it covers: `list` collections of per-sample count tables, reduced into DESeq2's `multiple=true` factor-level ports — which is exactly the reduction the data-flow brief specifies at node H. Same primary tool family (`iuc/deseq2`). Same DAG motif: DESeq2 → annotate → threshold filter. Same output surface as the subject's outputs 9–13 (normalized counts, results table, filtered gene list). Matching test-fixture shape: remote Zenodo count tables with explicit per-element `identifier`, and `has_text_matching` regexes on the tabular results.

### 1.2 Why rank 2 is Medium, not High

Same domain and same input topology (`list:paired` reads). Same tool families for the two steps that matter most structurally (`iuc/rgrnastar`, `iuc/featurecounts`), including the same `output_short` / `output_summary` output pair the subject promotes as outputs 7 and 8. But: the trimmer is fastp, not Cutadapt; the reference is a built-in index, not a history FASTA; and roughly two-thirds of the workflow (Cufflinks, StringTie, bigwig coverage, MultiQC, Picard/RSeQC QC) has no counterpart in the subject's deliberately closed tool set. Partial tool-family and output match is the Medium band by definition.

### 1.3 The headline structural finding

**IWC has no single workflow spanning FastQC → DESeq2.** The corpus publishes this journey as two workflows joined at the count-table boundary: `rnaseq-pe` ends at per-sample count tables, `rnaseq-de` begins there. The subject is one workflow spanning both halves.

This is not a cosmetic packaging difference — it is *where the condition grouping lives*. Because `rnaseq-de` starts from count tables, it can demand pre-grouped collections as workflow inputs and never needs a metadata-driven split at all. The subject, being one workflow, cannot: it receives ungrouped reads and must reconstruct the grouping internally. Everything in §3 below follows from that one divergence. Recorded as open-requirements entry `iwc-splits-rnaseq-de-at-the-count-table-boundary`.

---

## 2. The log2FC question — settled by the corpus

This is the entry phase 3 flagged as the sharpest conflict, and the corpus answers it without ambiguity.

**What IWC does.** `rnaseq-de` exposes the effect-size threshold in **log2 units at the interface**:

```yaml
- id: log2 fold change threshold
  type: float
  optional: false
  default: 1
  doc: >-
    log2 fold change threshold to filter for highly regulated genes.
    A log2 FC of 3 equals to an absolute fold change of 8 (2^3).
```

and filters with the raw column, no conversion anywhere:

```yaml
component_value: abs(c3)>     # c3 == log2(FC)
```

There is no linear fold-change parameter in the workflow, no `log2()` call, and no conversion node. The user is asked for the number the tool actually reports, and the doc string teaches the conversion in prose.

**What this settles.** `fold-change-threshold-linear-vs-deseq2-log2fc` closes on the third of its three options: **restate interface input 7 as a log2 threshold with a changed label**, not a conversion node and not an inline conversion in the filter expression. Default `1.0`, which is precisely the paper's `|fold change| > 2`. The corpus default is the same number for the same reason.

**Three details the corpus supplies alongside the answer:**

1. **Column indices.** `c3` is log2FC, `c7` is adjusted p-value. These are the raw DESeq2 output columns — `deg_annotate` appends columns 8–13 (chromosome, start, end, strand, feature, gene name) and leaves 1–7 untouched, so the indices hold whether or not the subject adds an annotation step. The header the exemplar generates names them: `GeneID, Base mean, log2(FC), StdErr, Wald-Stats, P-value, P-adj, …`.
2. **`Filter1` cannot take a numeric parameter directly.** Its predicate is a text parameter. The corpus idiom is one `iuc/compose_text_param` step per threshold, concatenating a literal prefix (`c7<`, `abs(c3)>`) with the connected float. So the subject's node I is **two Galaxy steps per filter**, not one.
3. **Two chained `Filter1` steps, not one compound predicate.** `Filter with p-adj threshold` → `Filter with log2 FC threshold`, each with `header_lines: "1"`. Each intermediate is separately promotable, which is also why the exemplar can rename them distinctly.

**The consequence the ledger entry warned about is real and the corpus confirms the trap.** Had the subject kept a linear `2.0` and compared `abs(c3) > 2.0`, it would have applied a 4-fold cut — a plausible-looking table that silently omits most of the paper's gene list. Nothing in the pipeline would have caught it.

### 2.1 Inline excerpt — the parameter-to-filter bridge

From `transcriptomics/rnaseq-de/rnaseq-de-filtering-plotting`, steps `_unlabeled_step_10` and `Filter with log2 FC threshold`. Fuller subgraph in the sibling file `iwc-exemplar.gxwf.yml`, document 1.

```yaml
- id: _unlabeled_step_10
  tool_id: toolshed.g2.bx.psu.edu/repos/iuc/compose_text_param/compose_text_param/0.1.1
  in:
    - id: components_1|param_type|component_value
      source: log2 fold change threshold
  out:
    - id: out1
      hide: true
  tool_state:
    components:
      - __index__: 0
        param_type: {select_param_type: text, __current_case__: 0, component_value: "abs(c3)>"}
      - __index__: 1
        param_type: {select_param_type: float, __current_case__: 2, component_value: {__class__: ConnectedValue}}

- id: Filter with log2 FC threshold
  label: Filter with log2 FC threshold
  tool_id: Filter1
  in:
    - id: cond
      source: _unlabeled_step_10/out1
    - id: input
      source: Filter with p-adj threshold/out_file1
  out:
    - id: out_file1
      rename: Genes filtered with adj p-value and log2(FC) thresholds
  tool_state:
    header_lines: "1"
```

---

## 3. Structural divergences that matter for template authoring

Ordered by how much authoring effort they redirect.

### 3.1 The condition split has no corpus precedent at all

The data-flow brief's §4 route — `__SAMPLE_SHEET_TO_TABULAR__` → row filter → `__FILTER_FROM_FILE__` → per-level counts collections — was the run's most carefully reasoned decision. The corpus does not support it, and does not contradict it either. It simply has nothing.

Searched across all of `workflows/` at `fe41a79`:

| Token | Hits |
|---|---|
| `sample_sheet` (any collection type) | **0** |
| `__SAMPLE_SHEET_TO_TABULAR__` | **0** |
| `column_definitions` with a non-null value | **0** (the token appears only as `"column_definitions": null` on ordinary collection inputs, a serialization artifact of newer Galaxy) |
| `__FILTER_FROM_FILE__` | 6 workflows — none in transcriptomics, none for a condition split |

So: the `__FILTER_FROM_FILE__` half of the route is a real, used Galaxy idiom; the sample-sheet half is unprecedented in published IWC practice. The subject would be the first.

**What IWC does instead** is to push the grouping into the interface — two pre-grouped `list` collections, `Counts from changed condition` and `Counts from reference condition`. That is *the same shape* as the alternative phase 2 explicitly rejected ("three condition-scoped `list:paired` inputs … hard-codes the three-level design into the interface"). The rejection reasoning was sound on its own terms; it is worth knowing that the corpus made the opposite trade, and bought a simpler workflow with it.

**Guidance for the template.** Build the §4 split as designed — nothing in the corpus refutes it, and the phase-3 reasoning stands. But build it as a clearly delimited template region with the phase-2 fallback (a `data` input `Sample metadata table`) reachable by deleting one node, because it is the one region of this workflow with no worked precedent to pattern-match against, and two open entries (`sample-sheet-to-tabular-identifier-column-unverified`, `sample-sheet-input-test-fixture-expressibility`) still ride on it. Recorded as `no-iwc-precedent-for-sample-sheet-workflow-input`.

### 3.2 DESeq2 node arity — two nodes, settled

`deseq2-contrast-realization-unsettled` closes: **two DESeq2 nodes, each with a two-level factor, the reference-level collection feeding both.**

Evidence, all from the exemplar:

- The factor-level ports are `select_data|rep_factorName_0|rep_factorLevel_0|countsFile` and `…|rep_factorLevel_1|countsFile`, under `how: datasets_per_level`. Each port consumes a whole collection — confirming the data-flow brief's node-H reduction exactly.
- `deseq_out` is **a single dataset, not a collection**. Downstream of it sit `deg_annotate`, `tp_cat` and two `Filter1` steps — all single-dataset tools that would map over a collection rather than consume it whole — and the sibling `-tests.yml` asserts `has_text_matching` on the derived output as a dataset.
- The workflow's own README bounds it: *"works only with an experimental setup containing exactly 2 conditions with at least 2 replicates per condition."*

One DESeq2 job therefore yields one results table. The interface fixes two distinctly labelled results tables (outputs 10 and 11), so it needs two jobs. The `rep_factorLevel` repeat means a three-level factor is *expressible*, but a three-level run still emits one `deseq_out`, which cannot satisfy a two-output interface — so the arity question is answered by the output surface regardless of what the wrapper does with three levels.

This costs the template nothing upstream: as §4.4 of the data-flow brief predicted, both realizations consume the same per-level counts collections, so nodes E, F₁–F₃, G₁–G₃ are unchanged. Node H becomes H₁ (`G_AR0382`, `G_tnSWI1`) and H₂ (`G_AR0382`, `G_AR0387`).

One consequence worth flagging forward: with two runs, `DESeq2 normalized counts` (output 9) and `DESeq2 diagnostic plots` (output 14) are now produced twice. The interface declares one of each. Either promote from one designated run and say which, or relabel per contrast. The template should not leave this implicit.

### 3.3 FastQC fan-out — flatten, contra the data-flow brief

`fastqc-per-read-fanout-not-a-flat-list` closes **in favour of the option the data-flow brief rated "no analytical gain"**.

`rnaseq-pe` puts an explicit `__FLATTEN__` between the `list:paired` reads input and the per-fastq QC tool:

```yaml
- id: _unlabeled_step_11
  tool_id: __FLATTEN__
  in:
    - id: input
      source: Collection paired FASTQ files
  out:
    - id: output
      hide: true
  tool_state:
    join_identifier: _
```

and the consuming subworkflow declares its input as `collection_type: list` — flat. Identifiers become `<sample>_forward` / `<sample>_reverse`.

So the corpus idiom is: flatten first, run QC over a flat list. This satisfies the interface's declared `list` shape for outputs 1–2 as originally written, and it is the published convention rather than a workaround. The data-flow brief's preference for promoting the nested collection was a reasonable call made with no corpus evidence available; the evidence now exists and points the other way.

**For the test plan:** the identifier vocabulary on outputs 1 and 2 doubles to twelve — `AR0382_A_forward`, `AR0382_A_reverse`, and so on. Outputs 3–8 keep the six-element sample identifier space untouched, because the flatten is a side branch off the workflow input and does not touch the map-over region.

### 3.4 Cutadapt emits one paired collection — no re-pair node

`trimmed-reads-paired-reassembly-conditional` closes. Neither transcriptomics exemplar uses Cutadapt (both use fastp), so this comes from `epigenetics/cutandrun` — a different domain, cited for the wrapper's IO shape only and for nothing else.

`lparsons/cutadapt/cutadapt/5.2+galaxy2` driven from a `list:paired` input with `library.type: paired_collection` declares outputs `out_pairs` (type `input`, i.e. the input collection's own shape) and `report`. One paired-inner collection out, one report per element.

So placeholder transformation 5.6 (re-pair node) is **not needed** and node C takes a single collection input, as the data-flow brief's primary reading assumed. `rnaseq-pe`'s fastp behaves identically (`output_paired_coll`), so the finding is consistent across both wrappers that could fill the trimmer slot.

### 3.5 RNA STAR from a history FASTA has no corpus precedent

Every STAR step in IWC — `rnaseq-pe` and `rnaseq-sr`, the only two — uses `refGenomeSource.geneSource: indexed` with a built-in `genomeDir` selected through a `restrictOnConnections: true` string parameter, plus `sjdbGTFfile` from the history. The test jobs pass a plain genome string (`Reference genome: sacCer3`).

The subject settled input 2 as a history FASTA on portability grounds (`reference-genome-delivery-shape-unverified`), which is the right call for *C. auris* B8441 — a genome no public server indexes — but it means the template has **no worked example of the history-reference conditional branch** to pattern-match against. That branch is a different `__current_case__` in the wrapper with a different set of required sub-parameters. Recorded as `star-history-reference-wiring-has-no-corpus-precedent`; it is a step-implementation obligation, best discharged by a `summarize-galaxy-tool` pass on `iuc/rgrnastar` rather than guessed at in the template.

This does not disturb the topology. The data-flow brief's §8 note stands: six in-job index builds of a ~12.5 Mb genome, no separate index node, and the graph is insensitive to how the entry eventually resolves.

### 3.6 Strandedness is a mapped parameter, not a raw one

`rnaseq-pe` exposes a restricted human-readable string:

```yaml
- id: Strandedness
  type: string
  restrictions: ["stranded - forward", "stranded - reverse", "unstranded"]
```

and translates it per consumer with one `iuc/map_param_value` step each (`Get featureCounts strandedness parameter`, and siblings for Cufflinks and StringTie), with `unmapped.on_unmapped: fail` so an unrecognized value stops the run rather than silently defaulting.

The subject's interface input 5 is a free `text` parameter with allowed values named only in prose. The corpus idiom is strictly better here: it type-restricts at the interface, it fails loudly on a bad value, and — because the subject's featureCounts step is the only consumer — it costs exactly one extra step. Worth adopting. This does not close `rnaseq-strandedness-inferred-from-kit-name` (the *value* is still an inference from the kit name; only its expression improves), and the empirical check via output 8 remains as the data-flow brief wired it.

---

## 4. Where the corpus confirms the design

Reported so the template does not mistake silence for doubt.

- **The map-over spine A→B→C→D is conventional and matches.** `rnaseq-pe` runs trim → STAR → featureCounts over a `list:paired` collection with the GTF broadcast into every mapped job and `anno.anno_select: history`, precisely as the data-flow brief's §2.2 edge table specifies. Input 3 is consumed twice there too, by STAR's `sjdbGTFfile` and featureCounts' `reference_gene_sets` — the same double consumption §8 flagged.
- **featureCounts' output pair is the right promotion.** `output_short` and `output_summary` are exactly interface outputs 7 and 8, and the exemplar promotes the counts through to its own `Counts Table`.
- **STAR's `output_log` is the assertable text behind the BAM.** The exemplar carries it, matching the interface's deliberate binary/text pairing for outputs 5 and 6.
- **No merged count matrix.** The exemplar's DESeq2 consumes per-sample count files through collection ports; the interface's refusal to invent a concatenate node is correct.
- **No collection-cleanup node.** Neither transcriptomics exemplar filters failed or empty elements out of a dense homogeneous collection. §3 of the data-flow brief called this right.
- **Absent MultiQC is a defensible divergence, not an omission.** `rnaseq-pe` does run MultiQC, but behind a `Generate additional QC reports` boolean and over QC tools the subject does not have. Adding it would be inventing method the paper does not name, and the interface's closed tool set is the better call.

---

## 5. Test-fixture guidance (for phase 8)

Corpus-observed, from the two sibling `-tests.yml` files. This is guidance for the test-plan Mold, not work this phase owns.

- **Collections are declared inline with explicit per-element identifiers.** `rnaseq-pe-tests.yml` nests `class: Collection` / `collection_type: paired` inside `collection_type: list:paired`, with `identifier: forward` / `reverse` on the inner files. That is the fixture form for the phase-2 fallback shape.
- **No corpus fixture declares a `sample_sheet` collection or any `column_definitions`.** `sample-sheet-input-test-fixture-expressibility` therefore remains genuinely open — the corpus offers no worked example either way, and its absence is weak evidence at best.
- **Remote Zenodo URLs with SHA-1 `hashes:` on inputs.** Hashes appear on inputs only; the corpus uses no checksum assertions on outputs.
- **Assertions are tolerant by default** — `has_size` + `delta`, `has_text_matching` regexes with digit wildcards on floating-point columns. The subject's declared assertion intents fit this vocabulary. The one place to be *stricter* than the corpus default is output 7: featureCounts on a fixed reference, annotation and strandedness is deterministic, and an existence-only probe there would be the smell the packaged anti-patterns note names. Exact per-gene integer counts, as the interface intends, is the right call.
- **Labels are the API.** Both exemplars key every job entry and every output assertion by label. If §3.2's duplicated normalized-counts/plots outputs get relabelled per contrast, that is a breaking change to be made once, in the interface, before any test is written.

---

## 6. Findings routed by authoring surface

| # | Finding | Owner |
|---|---|---|
| 1 | Restate input 7 as a log2 threshold, default 1.0, relabel (§2) | interface brief, then template |
| 2 | Node I is two steps per filter: `compose_text_param` → `Filter1`, chained padj → log2FC (§2) | template |
| 3 | Node H splits into H₁ and H₂ (§3.2) | template |
| 4 | Outputs 9 and 14 are produced twice under two DESeq2 nodes — designate or relabel (§3.2) | interface brief, then template |
| 5 | Insert `__FLATTEN__` before node A; outputs 1–2 are flat `list` (§3.3) | template |
| 6 | Drop placeholder transformation 5.6; node C takes one paired collection (§3.4) | template |
| 7 | STAR history-reference branch needs wrapper evidence (§3.5) | per-step loop (`summarize-galaxy-tool` on `iuc/rgrnastar`) |
| 8 | Restrict input 5 and add a `map_param_value` bridge (§3.6) | interface brief, then template |
| 9 | Build the §4 split as a delimited region with the fallback one deletion away (§3.1) | template |
| 10 | `sample_sheet` fixture expressibility; tolerant-assertion vocabulary; label stability (§5) | test plan |
| 11 | The corpus idioms in §2 (parameter→text-filter bridge) and §3.6 (`map_param_value` fan-out) recur across IWC and are candidates for pattern pages | Foundry pattern tier |

None of these blocks downstream authoring. Findings 1–6 are applicable as written; 7 defers to the per-step loop by design; 9 is a structuring instruction, not a correction.

---

## 7. Open-requirements ledger changes

Closed by this phase (4): `fold-change-threshold-linear-vs-deseq2-log2fc`, `deseq2-contrast-realization-unsettled`, `fastqc-per-read-fanout-not-a-flat-list`, `trimmed-reads-paired-reassembly-conditional`.

Raised by this phase (3): `iwc-splits-rnaseq-de-at-the-count-table-boundary`, `no-iwc-precedent-for-sample-sheet-workflow-input`, `star-history-reference-wiring-has-no-corpus-precedent`.

Left open (12, unchanged and passed through with provenance intact). Corpus evidence bearing on entries this phase did not close, recorded here rather than by editing another Mold's entries:

- **`deseq2-factor-level-names-not-parameterized`** — the corpus offers no level-name parameterization because it has no in-workflow split to parameterize; it puts the grouping in the interface instead (§3.1). The entry's two named options both stand; the corpus adds a third, which is the phase-2 fallback shape. Still open.
- **`sample-sheet-to-tabular-identifier-column-unverified`** — zero corpus uses of `__SAMPLE_SHEET_TO_TABULAR__`. The entry's note nominated "the IWC exemplar comparison" as one of three possible closers; that route is now exhausted, and the remaining two (a `summarize-galaxy-tool` pass, or the first real run) are the live ones.
- **`sample-sheet-input-test-fixture-expressibility`** — see §5. No corpus fixture either way.
- **`reference-genome-delivery-shape-unverified`** — the corpus idiom is a built-in index, which B8441 cannot use; the history-FASTA decision stands on its portability reasoning, and §3.5 records the wiring gap it creates. The entry is about *whether usegalaxy.org carries the index*, which the corpus cannot answer. Still open.
- **`rnaseq-strandedness-inferred-from-kit-name`** — §3.6 improves how the parameter is expressed, not what its value should be. Unchanged.
- **`featurecounts-annotation-source-unnamed`** — both exemplars take the GTF as a history `data` input with `gff_feature_attribute: gene_id` and `gff_feature_type: exon`, confirming the shape but naming no source for *C. auris*. Unchanged.
- **`cutadapt-adapter-and-length-filter-unstated`** — `cutandrun` wires adapter sequences from text parameters, and `rnaseq-pe` exposes optional forward/reverse adapter strings. That is an interface convention, not evidence about this paper's library. Unchanged; adding an adapter would still be adding method.
- **`mapped-outputs-carry-sample-sheet-outer-axis`**, **`galaxy-tool-versions-unpinnable-from-source`**, **`tnbcy1-contrast-not-carried`**, **`pipeline-b-tdna-mapping-not-carried`** — no corpus bearing. Unchanged.
- **`sample-sheet-condition-to-deseq2-factor-wiring`** — already `resolved` by phase 3. The corpus does not refute its `because`, so no `supersedes` is warranted; §3.1 records that the route is unprecedented, which is a different claim from wrong.
