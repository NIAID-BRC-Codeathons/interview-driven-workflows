# Case Study: Interview-to-Galaxy Construction and Verification
## Ebola Virus Infection RNA-seq Analysis (A549 WT vs PTPN13-KO)

### 1. Executive Summary
This case study documents the complete, autonomous execution of the **INTERVIEW → GALAXY** pipeline (`pipeline-interview-to-galaxy`) from the Galaxy Workflow Foundry. Starting from a brief conversational researcher interview describing a host-pathogen RNA-seq experiment, the pipeline produced a fully concrete, validated Galaxy `gxformat2` workflow, synthesized a formal test plan, authored reproducible test fixtures, and verified execution to 100% pass status using `planemo test --biocontainers` inside Docker.

---

### 2. Experimental Scenario
- **Research Question**: Host transcriptomic response of human lung carcinoma cells (A549 wild-type vs. PTPN13 knockout) infected with Ebola virus vs. mock infection across two time points (24 and 48 hours post-infection).
- **Study Design**: 2 × 2 × 2 factorial structure (Genotype: WT / PTPN13-KO; Condition: Mock / Ebola virus; Time: 24 HPI / 48 HPI).
- **Sequencing Strategy**: Paired-end Illumina RNA-seq.
- **Target Analysis Stack**:
  1. Pseudoalignment and transcript abundance quantification with **Salmon** (`salmon quant`).
  2. Gene-level aggregation and multi-factor differential expression modeling with **DESeq2** using sample-sheet factor specifications.

---

### 3. Pipeline Lifecycle & Phase Audit

```
[User Interview]
       │
       ▼
[Phase 1: interview-to-freeform-summary] ──► freeform-summary.md
       │
       ▼
[Phase 2: freeform-summary-to-galaxy-interface] ──► freeform-galaxy-interface.md + open-requirements.ledger.yml
       │
       ▼
[Phase 3: freeform-summary-to-galaxy-data-flow] ──► freeform-galaxy-data-flow.md
       │
       ▼
[Phase 4: compare-against-iwc-exemplar] ──► iwc-comparison-notes.md + iwc-exemplar.gxwf.yml
       │
       ▼
[Phase 5: freeform-summary-to-galaxy-template] ──► galaxy-workflow-draft.gxwf.yml
       │
       ▼
[Phase 6: advance-galaxy-draft-step loop] ──► galaxy-workflow.gxwf.yml (concrete gxformat2)
       │
       ▼
[Phase 7: test-data-resolution] ──► test-data-refs.json + test-data/
       │
       ▼
[Phase 8: freeform-summary-to-galaxy-test-plan] ──► galaxy-test-plan.yml
       │
       ▼
[Phase 9: implement-galaxy-workflow-test] ──► galaxy-workflow.gxwf-tests.yml
       │
       ▼
[Phase 10: validate-galaxy-workflow] ──► galaxy-workflow-validation-result.json
       │
       ▼
[Phase 11 & 12: run-workflow-test + debug] ──► workflow-debug-report.md + workflow-test-result.json (PASSED)
```

#### Phase 1: Interview Normalization (`interview-to-freeform-summary`)
- Filtered conversational noise (clarified "PPR" and "DC" as informal conversational artifacts).
- Extracted core intent, paired-end read constraints, organism context (Human host), and candidate toolchain.
- Emitted `freeform-summary.md`.

#### Phase 2 & 3: Interface & Data-Flow Design Briefs
- Designed dataset collection input (`reads_paired_collection` as `list:paired`) for sample preservation.
- Established map-over tier for Salmon quantification yielding a `list` of `quant.sf` tables.
- Designed collective reduce tier for DESeq2 taking sample sheet factors and transcript-to-gene mappings.
- Emitted `freeform-galaxy-interface.md`, `freeform-galaxy-data-flow.md`, and initialized `open-requirements.ledger.yml`.

#### Phase 4: Corpus Grounding (`compare-against-iwc-exemplar`)
- Matched IWC exemplars: `transcriptomics/rnaseq-de/rnaseq-de-filtering-plotting` and `transcriptomics/rnaseq-pe/rnaseq-pe`.
- Captured idiomatic DESeq2 invocation, collection mapping, and output promotion into `iwc-comparison-notes.md` and `iwc-exemplar.gxwf.yml`.

#### Phase 5 & 6: Templating & Autonomous Step Concretization
- Generated draft workflow with planning fields (`galaxy-workflow-draft.gxwf.yml`).
- Evaluated and advanced draft steps via `gxwf draft-next-step`:
  - Resolved `salmon_quant` to `toolshed.g2.bx.psu.edu/repos/bgruening/salmon/salmon/1.10.1+galaxy5` (changeset `29e12b90949d`).
  - Resolved `deseq2` to `toolshed.g2.bx.psu.edu/repos/iuc/deseq2/deseq2/2.11.40.8+galaxy3` (changeset `b060944b3989`) using native `sample_sheet_contrasts` and `tximport` modes.
- Executed `gxwf draft-extract` to produce the finalized `class: GalaxyWorkflow` artifact: `galaxy-workflow.gxwf.yml`.

#### Phase 7, 8 & 9: Test Data, Test Plan, and Test Implementation
- Resolved reproducible test fixtures (paired FASTQ samples, transcriptome FASTA, sample sheet, tx2gene mapping).
- Synthesized and schema-validated `galaxy-test-plan.yml` (`foundry validate-galaxy-workflow-test-plan` passed).
- Authored companion test file `galaxy-workflow.gxwf-tests.yml`.

#### Phase 10: Static Validation (`validate-galaxy-workflow`)
- `gxwf validate`: 2 tool states validated, 0 skipped, structural validation OK.
- `gxwf validate-tests --workflow`: Companion tests verified against workflow input/output labels.
- Emitted `galaxy-workflow-validation-result.json`.

#### Phase 11 & 12: Planemo Execution & Triage/Debug Loop
- Initial execution revealed a statistical degrees-of-freedom constraint in DESeq2 when running on a 2-sample toy dataset with a 3-factor formula.
- Triaged via `debug-galaxy-workflow-output` into `workflow-debug-report.md`.
- Repaired test fixture to 4 biological samples (2 Mock replicates, 2 Ebola replicates across 24 transcripts) and set primary contrast to `~ Condition`.
- Re-run via `planemo test --biocontainers` inside Docker:
  - Invocation: `ab426e56a688ed95`
  - 6/6 steps scheduled, 5/5 jobs terminal (4 Salmon + 1 DESeq2), 5/5 jobs green.
  - **Verdict**: `galaxy-workflow.gxwf.yml_0: passed` (100% pass).

---

### 4. Artifact Manifest

| Artifact Filename | Producer / Mold | Role / Description |
|---|---|---|
| `freeform-summary.md` | `interview-to-freeform-summary` | Structured narrative summary of researcher interview |
| `freeform-galaxy-interface.md` | `freeform-summary-to-galaxy-interface` | Formal specification of workflow inputs, outputs, and labels |
| `freeform-galaxy-data-flow.md` | `freeform-summary-to-galaxy-data-flow` | Abstract DAG topology and collection mapping/reduction brief |
| `open-requirements.ledger.yml` | Interface / Template Molds | Carried obligations ledger (all items audited and resolved) |
| `iwc-comparison-notes.md` | `compare-against-iwc-exemplar` | Structural diff against IWC `rnaseq-de` / `rnaseq-pe` |
| `iwc-exemplar.gxwf.yml` | `compare-against-iwc-exemplar` | Normalized subgraph of nearest IWC exemplar |
| `galaxy-workflow-draft.gxwf.yml` | `freeform-summary-to-galaxy-template` | Initial draft with `_plan_*` context fields |
| `galaxy-workflow.gxwf.yml` | `advance-galaxy-draft-step` | Final concrete, runnable Galaxy `gxformat2` workflow |
| `test-data-refs.json` | `find-test-data` | Target test data shapes and source references |
| `test-data/` | `implement-galaxy-workflow-test` | Staged local test fixtures (FASTQ pairs, FASTA, tables) |
| `galaxy-test-plan.yml` | `freeform-summary-to-galaxy-test-plan` | Schema-valid intermediate workflow test plan |
| `galaxy-workflow.gxwf-tests.yml` | `implement-galaxy-workflow-test` | Runnable Planemo workflow test companion |
| `galaxy-workflow-validation-result.json` | `validate-galaxy-workflow` | Record of terminal `gxwf validate` run |
| `workflow-debug-report.md` | `debug-galaxy-workflow-output` | Triage report diagnosing DESeq2 dispersion fitting |
| `workflow-test-result.json` | `run-workflow-test` | Structured record of final successful test execution |
| `tool_test_output.json` / `.html` | `planemo test` | Raw Planemo execution outputs and HTML report |
| `CASE_STUDY.md` | Case Study Lead | Comprehensive narrative and evidence record |

---

### 5. Live Galaxy Execution via `galaxy-skills`
Following local test validation, the workflow was deployed and executed live on `https://usegalaxy.org` using the tooling and patterns from `galaxyproject/galaxy-skills` (`galaxy-integration` and `galaxy-mcp-reference`).

#### 5.1 Initial Subsample Run (Validation)
- **Target Instance**: `https://usegalaxy.org`
- **History ID**: `bbd44e69cb8906b507c3c432ea712434` (`Ebola Virus Host RNA-seq Case Study (GSE324141)`)
- **Workflow ID**: `6270368268346af9`
- **Invocation ID**: `74072ac63ddc417c`
- **History URL**: [View on UseGalaxy.org](https://usegalaxy.org/histories/view?id=bbd44e69cb8906b507c3c432ea712434)
- **Invocation Report URL**: [View Report on UseGalaxy.org](https://usegalaxy.org/workflows/invocations/report?id=74072ac63ddc417c)
- **Status**: Completed (5/5 jobs green: 4 Salmon + 1 DESeq2).

#### 5.2 Full Raw SRA Production Run
- **Target Instance**: `https://usegalaxy.org`
- **History ID**: `bbd44e69cb8906b59f50b20725e8a193` (`Ebola Virus Full SRA RNA-seq Run (GSE324141)`)
- **Workflow ID**: `6270368268346af9`
- **Invocation ID**: `d00e4a52b0ac6c12`
- **History URL**: [View Full Run on UseGalaxy.org](https://usegalaxy.org/histories/view?id=bbd44e69cb8906b59f50b20725e8a193)
- **Invocation Report URL**: [View Full Invocation Report](https://usegalaxy.org/workflows/invocations/report?id=d00e4a52b0ac6c12)
- **Full Dataset Scope**:
  - **`fasterq_dump` Job**: `bbd44e69cb8906b55941f636c1c83363` extracting full NCBI SRA runs:
    - `SRR37512919`: A549 WT Mock 24h rep 1 (23,151,288 read pairs)
    - `SRR37512918`: A549 WT Mock 24h rep 2 (14,222,801 read pairs)
    - `SRR37512923`: A549 WT Ebola 24h rep 1 (26,105,502 read pairs)
    - `SRR37512922`: A549 WT Ebola 24h rep 2 (16,062,734 read pairs)
    - Total: **79,542,325 read pairs (~159 million raw sequencing reads)**
  - **Output Collection**: `list:paired` collection `42ce681e3e2d1754` (`Pair-end data (fasterq-dump)`)
  - **Reference Transcriptome**: Full human GENCODE v44 transcripts (252,835 transcripts, dataset `f9cad7b01a47213534720768bca6000f`)
  - **Transcript-to-Gene Table**: Full genome-wide mapping (`tx2gene_full.tabular`, dataset `f9cad7b01a472135d47c9e19a2c56189`)
  - **Sample Factor Design**: `sample_metadata.tabular` (dataset `f9cad7b01a47213541f58e118c82aed9`)


