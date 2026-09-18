# IWC Exemplar Comparison — Workflow A (SRA Landscape & Spike-In Sieve)

Scope: this comparison covers **Workflow A only** (kmindex containment screen → LexicMap
streaming search → LexicMapStreamer multi-HSP tiling/QC/haplotype-calling → per-gene
aggregation → am3 quarantine audit extraction), per `freeform-galaxy-data-flow.md`. Workflows
B/C/D from `freeform-galaxy-interface.md` are out of scope here.

Corpus: `https://github.com/galaxyproject/iwc`, cloned/pulled to `~/.foundry/iwc` on
2026-09-17 (up to date, no new commits since prior clone). Searched with `grep` across all
`.ga` files under `workflows/`, and normalized three candidates with
`gxwf convert --to format2 --compact` for structural inspection.

## Verdict: No High/Medium-confidence domain exemplar

**Confidence: Low (cross-domain structural pattern references only). No nearest domain
exemplar surfaced; `iwc-exemplar.gxwf.yml` is intentionally omitted.**

Walking the skill's feature hierarchy:

1. **Domain/analysis intent** — no match. `grep -rli "kmindex\|lexicmap"` across the entire
   corpus returns zero hits. There is no IWC workflow doing k-mer-index containment screening
   over a large bank of pre-built database shards, nor one doing multi-HSP coordinate tiling /
   codon QC / haplotype collapsing on search hits. The nearest domain neighbors by keyword
   (`kmer|sourmash|mash|containment|sketch`, `sra|accession|metagenom`) are bacterial
   genome-assembly QC, MAG binning, nanopore foodborne-pathogen detection, and generic
   SRA/BioProject fetching — all real metagenomic/microbial workflows, but none screen a fixed
   reference-database bank for containment, and none call haplotypes from multi-HSP tiled hits.
   Domain-blocking per the hierarchy's own rule ("domain comes first ... a structurally similar
   workflow in the wrong science area does not become a misleading exemplar").
2. **Input collection topology** — partial, incidental overlap only (see pattern refs below).
3. **Primary tool families** — no match (kmindex/LexicMap/LexicMapStreamer vs.
   megahit/metaspades/binette/checkm2/sra_tools/fasterq_dump elsewhere in the corpus).
4. **DAG motifs** — the only genuine overlaps are generic Galaxy idioms (map-over-collection,
   flatten, tabular-bridge), not workflow-specific recipes.
5. **Output types/report shape** — no comparable per-gene 8-artifact multi-output emitter.
6. **Test style** — no comparable fixture (see Test-issue routing below).

This is exactly the "fairly unusual IWC domain" case flagged in the run scope — not forced.

## Labeled pattern references (Low confidence, NOT domain exemplars)

Three candidates were converted and inspected. None is presented as *the* nearest exemplar;
each answers one narrow structural question for the template phase.

### 1. `data-fetching/parallel-accession-download` — cleanest map-over→multi-output→flatten skeleton

Full workflow (5 steps) converted via `gxwf convert --to format2 --compact`. Relevant excerpt
(split → per-item tool call with several named outputs → `__APPLY_RULES__` flatten):

```yaml
  - id: fasterq-dump
    tool_id: toolshed.g2.bx.psu.edu/repos/iuc/sra_tools/fasterq_dump/3.1.1+galaxy1
    in:
      - id: input|file_list
        source: Split accessions to collection/list_output_txt
    out:
      - id: list_paired
      - id: log
      - id: output_collection
      - id: output_collection_other
  - id: flatten paired output
    tool_id: __APPLY_RULES__
    in:
      - id: input
        source: fasterq-dump/list_paired
    out:
      - id: output
        add_tags: [{name: PE}]
    tool_state:
      rules:
        mapping:
          - {columns: [1], type: list_identifiers}
          - {columns: [2], type: paired_identifier}
```

Useful as the smallest legible instance of "one tool call emits several named outputs, each
routed through its own reduce" — loosely analogous to N2's map-over-shards and to N5's
multi-artifact-per-element shape, but with only 4 outputs (not 8), no per-element grouping
metadata, and no merge/dedup logic. Labeled as a **pattern reference for N2's map-over
skeleton only**, not a domain match (SRA read download vs. k-mer containment screening).

### 2. `microbiome/mags-building/MAGs-generation` — nearest structural analog for N4/N5/N6

69-step metagenomics MAG assembly/binning/QC workflow. Domain is genome assembly and binning,
not containment screening — cited purely for DAG motifs:

```yaml
  - id: _unlabeled_step_57        # Binette — per-sample bin refinement (map-over)
    tool_id: toolshed.g2.bx.psu.edu/repos/iuc/binette/binette/1.2.1+galaxy0
    out:
      - id: bins
        add_tags: [refined-sample-bins]
  - id: Pool Bins from all samples
    tool_id: __FLATTEN__               # list:list -> list, analogous to N4's index-axis reduce
    in:
      - id: input
        source: _unlabeled_step_57/bins
    out:
      - id: output
        rename: pooled_bins
    tool_state: {join_identifier: "_"}
  ...
  - id: _unlabeled_step_66
    tool_id: toolshed.g2.bx.psu.edu/repos/iuc/collection_column_join/collection_column_join/0.0.3
    in: [{id: input_tabular, source: _unlabeled_step_62}]
    tool_state: {identifier_column: "1", has_header: "1"}
```

Full converted file kept only in the run scratchpad (not published, per Low-confidence rule).
Findings routed below.

### 3. `microbiome/metagenomic-genes-catalogue` — confirms `pick_value` tool identity

Confirms the real Tool Shed identity behind the `conditional-transform-or-pass-through` idiom
`freeform-galaxy-data-flow.md` cites for N4's per-gene sensitivity override:
`toolshed.g2.bx.psu.edu/repos/iuc/pick_value/pick_value/0.2.0` (`first_or_default` style,
`pick_from` list with `default_value`). This was already a named pattern reference in the data
flow brief, not a ledger item, so no ledger action — recorded here as confirmation for the
template phase.

## Structural diff findings, routed by authoring surface

**Template/data-flow issues (for `freeform-summary-to-galaxy-template`):**

- N4's index-axis reduce (`list:list` gene×index → `list` gene) has a real, named built-in
  analog: `__FLATTEN__` (seen pooling MAGs-generation's per-sample bin lists). Template should
  plan to wire this as a concrete built-in step, not a placeholder.
- N3 (kmindex hit-map merge/union) and N6 (JSON-summary → manifest row) both still lack a
  full built-in match, but each is now only a **partial** gap: `Collapse Collection`
  (`nml/collapse_collections`) and `collection_column_join` (`iuc/collection_column_join`)
  are real, named Tool Shed tools that handle the *concatenation*/*tabular-join* half of each
  respectively. The remaining gap narrows to a small custom step (dedup+max-score reduction for
  N3; JSON→TSV-row flattening for N6) feeding into those built-ins, not a from-scratch merge
  tool for the whole node. See new ledger entries below.
- N5's `sample_sheet:record` output-shape recommendation has **no corpus precedent** (zero
  `collection_type: record` hits across all 115 `.ga` files). The corpus's actual idiom for
  "one tool call, many named per-element artifacts" is **N parallel list/sample_sheet
  collections sharing one `element_identifier`**, recombined post hoc via
  `collection_column_join`/`__FLATTEN__` (as MAGs-generation does for bins/contigs/QC). Template
  phase should default to that corpus-precedented shape for N5's 8 outputs unless there's a
  specific reason to prefer the record shape, since the record shape has no IWC test/lint
  precedent to validate against.

**Pattern issues:** none rising to a pattern-page update — the three references above are
recorded inline here, not promoted to a standalone pattern page, since none is a repeatable
domain match (only generic collection-idiom confirmation).

**Tool-step issues:** none new. No corpus wrapper exists for kmindex/LexicMap/LexicMapStreamer;
this is consistent with (not a contradiction of) the existing ledger entries
`kmindex-lexicmap-index-selection-mechanism` and `lexicmapstreamer-wrapper-authoring-pending` —
see note-only updates below.

**Test issues (for later `*-test-to-galaxy-test-plan` phase, not acted on here):** IWC's
accepted-shortcut vocabulary (`iwc-shortcuts-anti-patterns.md`) is directly relevant once test
authoring starts: LexicMap's raw per-gene hit tables are exactly the "stochastic/version-fragile
output" case (like HyPhy's JSON) where existence-only `has_text: "{"`-style probes are accepted;
the deterministic checkpoints this brief already flagged (haplotype counts, ingestion manifest,
am3 quarantine audit JSON) should get real content assertions, per corpus convention. Not
actioned in this phase — flagged for the test-plan Mold.

## Open-requirements ledger disposition

- **Note-updated, status unchanged (still open):** `kmindex-lexicmap-index-selection-mechanism`,
  `lexicmapstreamer-wrapper-authoring-pending` — both got a corpus-search addendum (no
  precedent found); neither is settled by this comparison, both still require inspecting the
  pinned IUC tool schemas / the private `nekrut/disassembler` repo respectively.
- **Newly appended (open, not blocking):** three entries recording structural divergences the
  corpus does not cover — `kmindex-hit-merge-no-corpus-precedent` (N3),
  `n6-json-flatten-no-corpus-precedent` (N6), `n5-output-collection-shape-no-record-precedent`
  (N5). These formalize gaps that previously existed only as prose in
  `freeform-galaxy-data-flow.md` §4/§5, per this skill's mandate to record divergences with no
  corpus precedent as ledger obligations.
- **Untouched:** all other entries (`workflow-scope-boundary-unresolved`,
  `allow-frameshifts-default-unconfirmed`, `host-biome-platform-stratification-script-gap`,
  `nominal-taxonomy-audit-not-modeled-as-step`, `chronaeon-synthetic-metadata-phase0`,
  `chronaeon-hardcoded-statistics-phases`, `wei-2026-dms-dataset-external-sourcing`,
  `hyphaeon-toolshed-status-unverified`, `lexicmapstreamer-implementation-provenance`) — out of
  Workflow A's data-flow scope or not touched by this corpus check.

## Foundry feedback

No feedback ledger entry appended. The skill bundle's procedure, `convert` CLI reference, and
packaged research notes (data-flow contract, shortcuts/anti-patterns, test-data conventions,
open-requirements-ledger protocol) were sufficient to perform the corpus clone, normalize
candidates, rank them, and route findings. Nothing encountered pointed at a defect,
contradiction, or uncovered case in the Foundry skill bundle itself — the difficulty here (no
domain exemplar exists) is a property of this project's unusual tool domain, not the Foundry
asset.
