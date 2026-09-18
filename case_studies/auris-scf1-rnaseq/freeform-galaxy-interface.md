# Galaxy workflow interface brief — *C. auris* Scf1 RNA-seq differential expression

Source handoff: `freeform-summary.md` (Santana et al. 2023, *Science* 381:1461–1467; DOI 10.1126/science.adf8972; PMID 37769084). All computational detail in that summary comes from the supplementary Materials and Methods, not the main text.

This brief is a design handoff. It is not a gxformat2 skeleton and pins no tool ids or versions. Consumers: `freeform-summary-to-galaxy-data-flow`, `compare-against-iwc-exemplar`, `freeform-summary-to-galaxy-template`, `freeform-summary-to-galaxy-test-plan`.

---

## 1. Scope

**In scope — Pipeline A, bulk RNA-seq differential expression.** FastQC → Cutadapt → RNA STAR → featureCounts → DESeq2 → significance filter, as named in the supplement. The authors state this ran on the Galaxy public server at usegalaxy.org, so the source tool chain is already a Galaxy tool chain.

**Out of scope — Pipeline B, AtMT T-DNA insertion-site mapping.** Excluded by harness decision before this phase. Recorded in the open-requirements ledger as `pipeline-b-tdna-mapping-not-carried` (`kind: dropped`) with its cited reasons, so the cut is legible to every later Mold rather than living only in this prose.

**Not ledgered.** The paper's other computational work — BLAST homology search, UniProt domain annotation, FungiDB/CGOB synteny, AlphaFold2/ColabFold + Foldseek structure prediction, Fiji + CellProfiler image analysis, FlowJo, R statistics — consumes no sequencing reads and was never candidate workflow content. It is not recorded as dropped workflow work.

**Tool set is closed to what the paper names.** No MultiQC, no aggregation or reporting step, no read-deduplication, no rRNA filter. The summary names six steps; adding a seventh would be inventing method.

---

## 2. Workflow inputs

Labels are the public API: Planemo and IWC tests address inputs by label, so these are chosen to read as test `job:` keys and are treated as breaking changes if renamed.

| # | Label | Galaxy shape | Format / type | Provenance | Confidence |
|---|-------|--------------|---------------|------------|-----------|
| 1 | `RNA-seq reads (sample sheet)` | collection, `sample_sheet:paired` | `fastqsanger.gz` | PRJNA904261 / SRP409192: 6 runs, 2 × 50 bp paired-end, NextSeq 2000 | high on paired-end shape; medium on the `sample_sheet` variant (see §2.1) |
| 2 | `Reference genome FASTA` | data | `fasta` | *C. auris* B8441, NCBI assembly GCA_002759435.2 (`Cand_auris_B8441_V2`), named in the supplement | high on the accession; medium on the delivery shape (see §2.2) |
| 3 | `Gene annotation GTF` | data | `gtf` | **Not named in the paper.** featureCounts and RNA STAR splice-junction input both require it | low — source unresolved |
| 4 | `Reference condition level` | parameter, `text` | default `AR0382` | The paper's two contrasts are both *versus* the parent AR0382 | high |
| 5 | `featureCounts strandedness` | parameter, `text` | default `reverse`; allowed `unstranded` / `forward` / `reverse` | Inferred from the library kit name (Illumina Stranded Total RNA Prep with Ribo-Zero Plus), **not stated** | low — inference only |
| 6 | `Adjusted p-value threshold` | parameter, `float` | default `0.05` | Stated: adjusted p-value < 0.05 | high |
| 7 | `Minimum absolute fold change` | parameter, `float` | default `2.0` | Stated: \|fold change\| > 2 | high |

### 2.1 Why `sample_sheet:paired` for the reads

The six runs are three conditions × two biological replicates. DESeq2 needs a per-sample condition assignment, and that assignment is per-sample typed metadata attached to paired fastq — which is exactly the `sample_sheet:paired` shape (`sample_sheet` outermost, inner `paired`).

```yaml
inputs:
  RNA-seq reads (sample sheet):
    type: collection
    collection_type: sample_sheet:paired
    column_definitions:
      - {type: string, name: condition, optional: false,
         restrictions: [AR0382, AR0387, tnSWI1]}
      - {type: string, name: replicate, optional: false,
         restrictions: [A, B]}
```

Element identifiers are the deposited sample names and must survive map-over and every collection reshape, because collection tests key assertions by element identifier:

`AR0382_A`, `AR0382_B`, `AR0387_A`, `AR0387_B`, `AR0382_tnSWI1_A`, `AR0382_tnSWI1_B`

Run-to-sample binding, for fixture work downstream: SRR22376032 → `AR0382_A`, SRR22376031 → `AR0382_B`, SRR22376030 → `AR0387_A`, SRR22376029 → `AR0387_B`, SRR22376028 → `AR0382_tnSWI1_A`, SRR22376027 → `AR0382_tnSWI1_B`.

Two consequences the data-flow Mold owns, both ledgered rather than assumed away:

- **Column metadata does not propagate through map-over.** A tool mapped over a `sample_sheet` produces a `sample_sheet`-shaped output *without* `column_definitions`. So the `condition` column is readable at the input and is gone by the time featureCounts has produced counts. Getting condition back — to split counts per factor level for DESeq2 — has to be an explicit step (`__SAMPLE_SHEET_TO_TABULAR__` plus a filter/split, or the rules DSL). Ledger: `sample-sheet-condition-to-deseq2-factor-wiring`.
- **Fallback, if that wiring proves unbuildable.** Replace input 1 with a `list:paired` collection labeled `RNA-seq reads` plus a `data` input `Sample metadata table` (tabular: sample_id, condition, replicate), and split on that table. This is named here so the fallback is a recorded alternative, not an improvisation. The same ledger entry carries it.

Rejected alternative: three condition-scoped `list:paired` inputs (one per condition), which wires to DESeq2's factor-level repeats trivially but hard-codes the three-level design into the interface and makes the workflow unusable for any other sample set.

### 2.2 Reference data delivery

*C. auris* B8441 is not a Galaxy mainstream reference. This brief settles the genome as a **history dataset (fasta)** rather than a built-in index or data-table string, on portability grounds: a remote-URL fixture is resolvable by a test on any server, a CVMFS index is not. RNA STAR then builds its index at run time from that FASTA plus the annotation.

Whether usegalaxy.org actually carries a built-in `GCA_002759435.2` index was **not checked in this phase** — no phase of this run owns reference-data shape (this run's roster has no `*-to-galaxy-reference-data` Mold). Ledgered as `reference-genome-delivery-shape-unverified` so the data-flow Mold can revisit it with evidence.

Note that the annotation choice is load-bearing and unresolved: NCBI RefSeq GFF and FungiDB GFF for the same assembly differ in gene ID space and in attribute keys (`gene_id` vs `ID`), which changes both featureCounts' `-g` attribute and every downstream gene identifier — including whether `B9J08_001458` (SCF1) appears under that name at all. The interface fixes the *datatype* as `gtf`; if the chosen source is GFF3, either the input datatype or a conversion step changes. Ledger: `featurecounts-annotation-source-unnamed`.

### 2.3 Parameter surface

Exposed as typed workflow parameters: the two significance thresholds (stated by the paper, and the workflow's headline criteria), the reference condition level (needed to make a three-level factor explicit), and strandedness (inferred, so a reviewer must be able to see and change it).

Baked into steps, not exposed: Cutadapt quality cutoff `-q 20` (pinned by the paper), RNA STAR defaults ("default parameters", pinned by the paper). No adapter sequence is exposed because the paper names none — the Cutadapt step is read as quality trimming only. Ledger: `cutadapt-adapter-and-length-filter-unstated`.

---

## 3. Workflow outputs

Every output below is a top-level `outputs:` entry with the label as its public name and an explicit `outputSource`. Roles: **checkpoint** = promoted because it is the best deterministic or structural assertion target; **user-facing** = promoted for the user, weak assertion expected.

| # | Label | Shape | Format | Role | Assertion intent |
|---|-------|-------|--------|------|------------------|
| 1 | `FastQC raw reads: text summary` | collection (`list`) | `txt` | checkpoint | per-sample module PASS/WARN/FAIL lines, total-sequence counts by regex |
| 2 | `FastQC raw reads: HTML report` | collection (`list`) | `html` | user-facing | existence / size |
| 3 | `Cutadapt trimming report` | collection (`list`) | `txt` | checkpoint | reads processed / written counts; deterministic given fixed input |
| 4 | `Trimmed reads` | collection (`list:paired`) | `fastqsanger.gz` | user-facing | size only |
| 5 | `STAR alignments (BAM)` | collection (`list`) | `bam` | user-facing | size only — binary |
| 6 | `STAR mapping summary` | collection (`list`) | `txt` | checkpoint | `Log.final.out`: input read count, uniquely-mapped % — the text stats behind the binary |
| 7 | `Gene counts per sample` | collection (`list`) | `tabular` | checkpoint | strongest checkpoint in the workflow: exact per-gene integer counts, addressable by gene id |
| 8 | `featureCounts assignment summary` | collection (`list`) | `tabular` | checkpoint | Assigned / Unassigned\_NoFeatures / Unassigned\_Ambiguous totals — also the direct read-out of whether strandedness was set right |
| 9 | `DESeq2 normalized counts` | data | `tabular` | checkpoint | supports the paper's sanity check that SCF1 sits in the top 2.5% of AR0382 expression |
| 10 | `DESeq2 results: tnSWI1 vs AR0382` | data | `tabular` | checkpoint | full result table; SCF1 = `B9J08_001458` present, negative log2FC |
| 11 | `DESeq2 results: AR0387 vs AR0382` | data | `tabular` | checkpoint | full result table; SCF1 negative log2FC, ~29-fold per the paper |
| 12 | `Significant genes: tnSWI1 vs AR0382` | data | `tabular` | checkpoint | filtered at inputs 6 and 7; SCF1 is the top row by significance |
| 13 | `Significant genes: AR0387 vs AR0382` | data | `tabular` | checkpoint | filtered; SCF1 the most down-regulated gene |
| 14 | `DESeq2 diagnostic plots` | data | `pdf` | user-facing | existence / size |

Design notes:

- Outputs 5 and 6 are a deliberate pair, and so are 1 and 2: where the natural output is binary or a rendered report, the sibling text/stats artifact is promoted alongside it so the workflow has something assertable behind the thing users want to look at.
- Output 7 is the single most valuable checkpoint. It is deterministic given a fixed reference, annotation, and strandedness, it is addressable per gene id, and it fails loudly if any of those three is wrong — which is precisely where this reconstruction's largest unknowns sit.
- **Two contrasts, two result outputs.** The paper reports tnSWI1 vs AR0382 and AR0387 vs AR0382. This brief fixes the *output surface* at two labeled result tables and two labeled filtered tables. Whether those come from one DESeq2 run over a three-level factor or two runs over two-level factors is a data-flow/wrapper decision, not an interface one. Ledger: `deseq2-contrast-realization-unsettled`.
- No merged count matrix is exposed: the Galaxy DESeq2 tool consumes per-sample count files directly, so a merge step would be invented rather than translated.
- No output uses `hide` or `delete_intermediate_datasets`, and no promoted checkpoint relies on `rename` for its identity.

---

## 4. Provenance and confidence

| Decision | Evidence class | Confidence |
|---|---|---|
| Six-step tool chain (FastQC, Cutadapt, RNA STAR, featureCounts, DESeq2, filter) | stated in the supplement | high |
| Paired-end, 2 × 50 bp, six runs, three conditions, n = 2 | deposited metadata (PRJNA904261) | high |
| Element identifiers = deposited sample names | deposited metadata | high |
| Genome = GCA_002759435.2 (B8441) | stated in the supplement | high |
| Significance thresholds (\|FC\| > 2, padj < 0.05) | stated in the supplement | high |
| Cutadapt = quality trimming at Phred 20, no adapter | stated cutoff; no-adapter reading is inference | medium |
| Strandedness = reverse | inference from kit name only | low |
| One-factor / three-level / n = 2 DESeq2 design | inferred from the deposited runs; no design formula in the paper | medium |
| Annotation GTF source | absent from the paper | none — open |
| Tool versions | absent from the paper for every Galaxy step | none — open |
| `sample_sheet:paired` input variant | design inference from Galaxy collection semantics | medium |
| Reference genome as history FASTA | design inference on portability grounds | medium |

**Version fidelity is not claimable.** The paper versions only its non-Galaxy software (R 4.0.3, DescTools 0.99.49, survminer 0.4.9, Fiji 1.52, CellProfiler 3.1.9). Any workflow built from this brief pins its own tool versions and reproduces the authors' *method*, never their exact software stack. This should be stated on the workflow itself, not just here. Ledger: `galaxy-tool-versions-unpinnable-from-source`.

---

## 5. Open questions

Each of these is also an open-requirements ledger entry; the ledger is the machine-readable form and the entry id is given so the two do not drift.

1. **Which annotation?** NCBI RefSeq GFF for GCA_002759435.2, or FungiDB's B8441 GFF. The choice changes gene IDs, counts, and the featureCounts `-g` attribute. Largest single gap in reproducing this analysis. → `featurecounts-annotation-source-unnamed`
2. **Is the library really reverse-stranded?** Only the kit name supports it. Output 8 is the empirical check: a wrong setting shows up as a large `Unassigned_NoFeatures` fraction. → `rnaseq-strandedness-inferred-from-kit-name`
3. **How does per-sample `condition` reach DESeq2's factor levels**, given that sample-sheet column metadata does not propagate through map-over? Fallback named in §2.1. → `sample-sheet-condition-to-deseq2-factor-wiring`
4. **Can a `sample_sheet:paired` workflow input be expressed as a test fixture** in a Planemo/IWC `-tests.yml` job block? If not, the §2.1 fallback becomes mandatory and this interface changes. → `sample-sheet-input-test-fixture-expressibility`
5. **One three-level DESeq2 run or two two-level runs** to produce the two contrasts? → `deseq2-contrast-realization-unsettled`
6. **Does usegalaxy.org carry a built-in B8441 index?** Not checked; genome settled provisionally as a history FASTA. → `reference-genome-delivery-shape-unverified`
7. **Cutadapt adapter sequence and minimum-length filter** are both unstated. → `cutadapt-adapter-and-length-filter-unstated`
8. **No tool versions for any Galaxy step.** → `galaxy-tool-versions-unpinnable-from-source`
9. **tnBCY1 vs AR0382 (Fig. S2) cannot be built** — no tnBCY1 runs were deposited. Recorded as dropped source work, not as a gap the pipeline might yet close. → `tnbcy1-contrast-not-carried`
10. **Pipeline B is not carried.** → `pipeline-b-tdna-mapping-not-carried`
