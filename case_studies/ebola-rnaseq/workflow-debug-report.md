# Workflow Debug Report: Ebola Virus Infection RNA-seq Analysis

## Failure Classification
- **Primary Failure Surface**: Tool / Job Runtime Failure
- **Failing Step**: `deseq2` (Job ID: `af2fb7855feedbd6`, Tool ID: `toolshed.g2.bx.psu.edu/repos/iuc/deseq2/deseq2/2.11.40.8+galaxy3`)
- **Invocation State**: Incomplete (`100% 6/6 scheduled`, `3/3 terminal jobs: 2 green, 1 red`)
- **Exit Code**: 1

## Evidence Captured
- **Command Line**:
  ```sh
  Rscript .../deseq2.R ... --sample_sheet_mode --sample_sheet ... --custom_design_formula --design_formula '~ Genotype + Timepoint + Condition' -i -y salmon -x mapping.txt
  ```
- **Tool Stderr**:
  ```text
  reading in files with read.delim (install 'readr' package for speed up)
  1 2 
  transcripts missing from tx2gene: 1
  summarizing abundance
  summarizing counts
  summarizing length
  Error in DESeqDataSet(se, design = design, ignoreRank) : 
    design contains one or more variables with all samples having the same value,
    remove these variables from the design
  Calls: get_deseq_dataset ... DESeqDataSetFromTximport -> DESeqDataSetFromMatrix -> DESeqDataSet
  ```

## Diagnosis
1. **Salmon Step**: Succeeded completely on both samples (`SRR5085167`, `SRR5085168`), generating valid transcript abundance tables (`quant.sf`) via `biocontainers`.
2. **DESeq2 Step**: Succeeded in reading Salmon `quant.sf` files via `tximport`, but failed when instantiating the `DESeqDataSet` object.
3. **Cause of Failure**:
   The workflow's `tool_state` for DESeq2 set `design_formula: "~ Genotype + Timepoint + Condition"`. However, the test dataset in `sample_metadata.tabular` only provided 2 samples (`SRR5085167` and `SRR5085168`), both of which had `Genotype=WT` and `Timepoint=24`.
   In DESeq2, every variable in the design formula must have at least two levels across the sample set; otherwise, the design matrix contains invariant columns that cannot be estimated.

## Recommended Repair
1. Set the workflow's default design formula in `galaxy-workflow.gxwf.yml` to `~ Condition` (the primary biological contrast: Mock vs Ebola infection).
2. Expand the test fixture in `ebola-test/test-data/` to include 4 samples (2 Mock replicates and 2 Ebola replicates), providing sufficient statistical degrees of freedom for DESeq2 dispersion fitting.
3. Update `galaxy-workflow.gxwf-tests.yml` to include the 4 samples in `reads_paired_collection` and `sample_metadata.tabular`.
