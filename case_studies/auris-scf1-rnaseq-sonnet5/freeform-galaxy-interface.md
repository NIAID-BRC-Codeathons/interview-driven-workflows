# Galaxy Workflow Interface Design Brief

Source: `freeform-summary.md` (ΦX174 planetary-scale retrospective DMS re-analysis pipeline).
This brief maps the free-form summary's Stages A-K into a Galaxy workflow interface: inputs,
outputs, labels, collection shapes, and checkpoints. It is a design handoff, not a gxformat2
skeleton — no wiring is committed here.

## 0. Scope decision made for this brief (see open-requirements entry `workflow-scope-boundary-unresolved`)

The source summary explicitly leaves open whether the target workflow is only the SRA-landscape /
spike-in sieve (Stages A-D2, the only content in `draft_manuscript.tex` today) or the full
multi-stage project (through HyphAeon/Fane synthesis, Stages A-K, documented in
HANDOVER.md/section drafts). This brief **covers the full A-K shape** so no source work is
silently dropped, but confidence drops sharply past Stage D2:

- **High confidence, likely one workflow ("SRA landscape & spike-in sieve"):** Stages A, B, C, D2.
- **Medium confidence, likely a second workflow ("experimental-evolution validation"):** Stage E.
- **Lower confidence, likely later/separate workflows pending tool-wrapper authoring:** Stages
  C′, F, G, H, I.
- **Out of Galaxy-workflow scope (non-computational or QA-only):** Stage D's manual metadata
  audit (modeled as reference data, not a step — see `nominal-taxonomy-audit-not-modeled-as-step`),
  Stage J (pure pandas literature cross-referencing), Stage K (figures / manuscript-style QA).

Downstream phases (data-flow, IWC-exemplar comparison, template authoring) should treat this as
a candidate decomposition into 2-4 connected workflows, not a mandate for one monolith.

## 1. Workflow A — SRA Landscape & Spike-In Sieve (Stages A, B, C, D2)

### 1.1 Inputs

| Label | Type | Collection shape | Description | Confidence |
|---|---|---|---|---|
| `Reference genome (NC_001422.1)` | `data` (fasta) | — | ΦX174 RefSeq genome, 5,386 nt circular ssDNA | High |
| `Gene query panel` | `data_collection` | **`sample_sheet`** — one FASTA per row, `element_identifier` = gene symbol (A,B,C,D,E,F,G,H,J,K) | Per-gene CDS FASTAs; also usable as a combined multi-FASTA for the bulk kmindex screen | High |
| `Gene query panel column_definitions` | (attached to above) | — | `align_min_match_pident` (float), `align_min_match_len` (int), `seed_min_prefix` (int), `min_qcov_per_genome` (float) — per-gene-tuned LexicMap sensitivity, needed because genes A/C/E/K use looser thresholds than the default | Medium — see rationale in §5 |
| `Logan kmindex DB selection` | `string` (select, multi-value) | — | Selection over the 109 hardcoded Logan k-mer shard names (`GENOMIC_BCT`, `VIRALRNA_*`, etc.) | Low — mechanism open, see ledger `kmindex-lexicmap-index-selection-mechanism` |
| `LexicMap index selection` | `string` (select, multi-value) | — | 25 domain indices, or the 5-index `TARGETED_PHAGE_INDICES` subset for per-gene runs | Low — same ledger entry |
| `kmindex parameters` | typed params | — | `zvalue=6`, `threshold=0.3`, `format=json`, `fast=false` | High |
| `LexicMap parameters` | typed params | — | `top_n_genomes=0`, `advanced_settings|all=true` | High |
| `Tiling/QC parameters` | typed params | — | `min_coverage=0.80`, `min_coverage_partial=0.50`, `min_pident=60.0`, `max_internal_stops=0`, `sample_cap=10`, `allow_frameshifts` (boolean, no confirmed default) | Medium — `allow_frameshifts` default open, see ledger |
| `Nominal-taxonomy BioProject classification table` | `data` (tabular, reference) | — | Static curation table (18 BioProjects → category) enumerated in Stage D; not computed by this workflow | Medium — modeled as reference data, see ledger `nominal-taxonomy-audit-not-modeled-as-step` |

### 1.2 Outputs

| Label | Type | Collection shape | Producer stage | Checkpoint? | Confidence |
|---|---|---|---|---|---|
| `kmindex containment hits (per shard)` | `data_collection` (JSON) | `list`, identifier = DB shard name | Stage B | No (intermediate, high volume) | High |
| `kmindex accession union` | `data` (txt) | — | Stage B (merge) | Yes — deterministic accession list | High |
| `LexicMap results (per gene)` | `data_collection` (tabular) | `sample_sheet` (mirrors query panel) | Stage C | No (raw hit table) | High |
| `Clean full-length CDS haplotypes (per gene)` | `data_collection` (fasta) | `sample_sheet` | Stage C tiling/QC | **Yes** — deterministic, drives Table 1 numbers | High |
| `Clean haplotype counts (per gene)` | `data_collection` (tabular) | `sample_sheet` | Stage C tiling/QC | **Yes** | High |
| `Flagged accessions + audit reasons (per gene)` | `data_collection` (fasta + tabular) | `sample_sheet` | Stage C tiling/QC | Yes | High |
| `Per-accession cohort ledger (per gene)` | `data_collection` (tabular) | `sample_sheet` | Stage C tiling/QC | No (audit trail, large) | High |
| `Per-gene ingestion summary` | `data_collection` (JSON) | `sample_sheet` | Stage C tiling/QC | **Yes** — source of Table 1 | High |
| `Ingestion manifest (all genes)` | `data` (csv) | — | Stage C aggregation | **Yes** — strong table checkpoint | High |
| `Gene E am3 quarantine audit` | `data` (JSON) | — | Stage D2 | **Yes** — small, deterministic, proves the paper's core spike-in finding | High |

## 2. Workflow B — Experimental-Evolution Trajectory Validation (Stage E)

### 2.1 Inputs

| Label | Type | Collection shape | Description | Confidence |
|---|---|---|---|---|
| `Reference genome (NC_001422.1)` | `data` (fasta) | — | shared with Workflow A | High |
| `Idaho 2024 paired reads` | `data_collection` | **`sample_sheet:paired`** — columns `timepoint` (int: 0/35/70 min), `replicate` (int) | 7 MiSeq PE runs, `SRR31059334`-`SRR31059340`, competitive-growth time series tracking Gene G | High |
| `Dickins & Nekrutenko 2009 single-end reads` | `data_collection` | **`sample_sheet`** — columns `lineage` (string, restrictions `[Ancestor,B,C]`), `sample_id` (string) | 10 single-end chemostat GAII samples | High |
| `Gene G coordinate window` | `string`/`int` params | — | `NC_001422.1:2395-2919`, used to restrict Idaho mpileup | High |
| `Historically important position list` | `string` (list) | — | Fixed Dickins positions (656, 1301, 1306, 1308, 1675, 3967, 4491, 5262) always retained regardless of frequency threshold | High |
| `Wei et al. 2026 DMS table (1nt/SNV level)` | `data` (tabular, external) | — | `genome_mut_ID_nt`-keyed fitness table; hard external dependency | Low — sourcing unresolved, see ledger `wei-2026-dms-dataset-external-sourcing` |

### 2.2 Outputs

| Label | Type | Collection shape | Checkpoint? | Confidence |
|---|---|---|---|---|
| `Sorted, indexed alignments (per sample)` | `data_collection` (bam) | `sample_sheet:paired` / `sample_sheet` | No (intermediate) | High |
| `Idaho 2024 trajectories vs DMS fitness` | `data` (csv) | — | **Yes** — carries Spearman/Pearson stats, N | High |
| `Dickins 2009 empirical trajectories` | `data` (csv) | — | **Yes** | High |

Both trajectory-caller scripts (`analyze_idaho_evolution.py`, `call_dickins_trajectories.py`) are
custom hand-rolled `samtools mpileup` string parsers with no off-the-shelf equivalent identified;
the source itself suggests `bcftools mpileup`/`lofreq`/`varscan` as a native-Galaxy substitute
path (freeform-summary §5) — flagged for the tool-discovery phase, not resolved here.

## 3. Workflow C (candidate, lower confidence) — Diversity Reconstruction, VEP Benchmarking, Dual-Coding Calibration (Stages C′, F, G, H)

Modeled at lower resolution because every non-kmindex/LexicMap tool here still needs a Galaxy
wrapper (per phase-1 context). Interface-level shape only:

| Label | Type | Collection shape | Description | Confidence |
|---|---|---|---|---|
| `Stratified diversity cohort accessions (per gene)` | `data_collection` (txt/json) | `sample_sheet` | 2,500 accessions/gene, 500/1000/1000 canonical/high-homology/divergent strata | Medium |
| `logan-walker cDBG traversal parameters` | typed params | — | `workers`, `fetch_workers`, `min_vaf=0.10`, `min_abund=5.0`, `prune_frac=0.01`, `min_cov=0.85`, `hops=5`, `max-size-mb=4096` | Medium |
| `Codon MSA / intra-host variant calls (per gene)` | `data_collection` (vcf-like + fasta) | `sample_sheet` | Stage C′ output | Medium — checkpoint candidate |
| `FastTree phylogenies (per gene)` | `data_collection` (newick) | `sample_sheet` | Stage C′ | Medium — checkpoint candidate |
| `EVcouplings MSAs (per gene, 350-taxa subsample)` | `data_collection` (fasta/aln) | `sample_sheet` | HyphAeon VEP input | Medium |
| `HyphAeon pathogenicity scores (per gene)` | `data_collection` (tabular) | `sample_sheet` | Stage G | **Yes** — checkpoint | Low-Medium (tool availability unverified, see ledger `hyphaeon-toolshed-status-unverified`) |
| `HyphAeon vs DMS correlation summary` | `data` (tabular) | — | Stage G | Yes | Low-Medium |
| `Overlap consequence classification (per gene-pair: DE, BA, KC, KA)` | `data_collection` (csv) | `list`, identifier = gene-pair code | Stage H | Yes | Low-Medium |
| `Shadow-effect calibration summary` | `data` (JSON) | — | Stage H | **Yes** — small, deterministic | Low-Medium |

## 4. Workflow D (candidate, lowest confidence) — "ChronAeon" Multi-Scale Sieve (Stage I)

`run_chronaeon_phix174_sieve.py` is an orchestration sketch, not a tool to port verbatim
(freeform-summary §7.7). Only Phases 1/3/4 are confirmed genuine re-executable CLI calls; Phases
0, 2, 6, 7, 8 are excluded from this brief as steps (see ledger entries
`chronaeon-synthetic-metadata-phase0`, `chronaeon-hardcoded-statistics-phases`).

| Label | Type | Collection shape | Description | Confidence |
|---|---|---|---|---|
| `Clean contigs + real collection-date metadata` | `data` (fasta) + `data` (csv) | — | Input to `hyphaeon autoclock`; **collection_date must be sourced from real SRA/BioSample metadata**, not the fabricated hash-derived placeholder in the source script | Low |
| `autoclock parameters` | typed params | — | `--manifold tn93`, `--max-depth 3`, `--min-leaf-size 20`, `--min-delta-aicc 15.0`, `--n-landmarks auto`, `--max-memory-mb 2048` | Medium |
| `autoclock summary` | `data` (JSON) | — | tmrca, rate, r2, optimal_k, delta_aicc, per-node classification | **Yes** — checkpoint | Low-Medium |
| `r0 parameters` | typed params | — | `--generation-time 0.0174`, `--generation-sd 0.005`, `--units days` | Medium |
| `r0 / phylodynamics summary` | `data` (JSON + csv) | — | epoch skyline Rt | **Yes** | Low-Medium |
| `meme parameters` | typed params | — | `--use-tn93`, `--attribute`, `--attribution-min-lrt 3.84` | Medium |
| `meme attributed sites` | `data` (JSON + csv) | — | episodic selection scan | **Yes** | Low-Medium |
| `ACAT combined p-values` | `data` (csv) | — | Cauchy combination over per-site p-values | **Yes** | Low-Medium |

## 5. Collection-shape rationale

- **`sample_sheet` over plain `list`/`list:paired`:** Several inputs pair one dataset per element
  with per-element scalar metadata that downstream steps consume as parameters, not just as
  grouping — per-gene LexicMap sensitivity thresholds (§1.1), Idaho timepoint/replicate, and
  Dickins lineage/sample_id. A `sample_sheet` (or `sample_sheet:paired`) carries that metadata as
  typed `column_definitions` instead of forcing parallel parameter inputs or baking values into
  filenames. This is a **medium-confidence design choice**: the source never describes Galaxy
  collection types explicitly (it is ad hoc BioBlend/local scripting today), so this is this
  brief's translation, not a source-stated requirement.
- Per the vendored sample_sheet reference, `sample_sheet` must be outermost and does not
  propagate `column_definitions` through a mapped tool automatically — the data-flow phase will
  need explicit re-attachment (e.g. via `__SAMPLE_SHEET_TO_TABULAR__` or rules-DSL) wherever
  per-gene tuning parameters must survive into Stage C's tiling/QC step.
- Gene-pair overlap outputs (`DE`, `BA`, `KC`, `KA`) are modeled as a plain `list` (not
  `sample_sheet`) since they carry no per-element scalar metadata beyond the identifier itself.

## 6. Labels and testability notes

- Labels above are chosen as stable domain names (e.g. `Gene E am3 quarantine audit`, `Idaho 2024
  trajectories vs DMS fitness`) rather than tool-step defaults, per the testability-design
  guidance — these are the identifiers a later `-tests.yml` would address.
- Checkpoints favor small deterministic JSON/CSV summaries (the per-gene `.summary.json` files,
  the am3 audit JSON, the trajectory CSVs, the shadow-effect calibration JSON) over the large
  audit-trail collections (cohort ledgers, raw hit tables) — those remain workflow outputs but are
  not proposed as primary test-assertion targets given their size/volume.
- `sample_sheet`-shaped collection outputs should carry gene symbol / sample_id as
  `element_identifier` throughout, so element-level test assertions (`element_tests:`) can target
  them directly.

## 7. Open questions carried to the open-requirements ledger

See `open-requirements.ledger.yml` for the full entries (9 total, all `status: open`, none
`blocking` — these are design-tier gaps/drops, not computability gaps in a draft topology):

1. `workflow-scope-boundary-unresolved` — Stages A-D2 only, vs full A-K.
2. `kmindex-lexicmap-index-selection-mechanism` — how 109/25 Logan index names surface as tool inputs.
3. `allow-frameshifts-default-unconfirmed` — QC flag default.
4. `host-biome-platform-stratification-script-gap` — no script found; dropped, not invented.
5. `nominal-taxonomy-audit-not-modeled-as-step` — modeled as reference data, not a step.
6. `chronaeon-synthetic-metadata-phase0` — fabricated dates excluded, real dates needed.
7. `chronaeon-hardcoded-statistics-phases` — Phases 2/6/7/8 excluded as non-reproducible.
8. `wei-2026-dms-dataset-external-sourcing` — external DMS ground-truth table not in repo.
9. `hyphaeon-toolshed-status-unverified` — HyphAeon/hyphaeon_overlaps Tool Shed status unknown.

## 8. Foundry feedback

No feedback ledger entry was appended for this run. Rationale: the skill's `_feedback.md`
protocol and the packaged reference notes (`open-requirements-ledger.md`,
`galaxy-sample-sheet-collections.md`, `galaxy-workflow-testability-design.md`) were sufficient to
make every interface decision above; nothing encountered pointed at a defect, contradiction, or
uncovered case in the Foundry skill bundle itself. The difficulties in this run (unresolved
project scope, an unwrapped multi-stage orchestration script, an unverified external tool's
Tool-Shed status, a missing external dataset) are properties of this project's source material,
not of the Foundry asset, so per the ledger's own scope rule they were recorded in
`open-requirements.ledger.yml` instead.
