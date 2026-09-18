# Galaxy Workflow Data-Flow Brief: Ebola Virus Infection RNA-seq Analysis

## Data-Flow Overview
The workflow transforms raw paired-end RNA-seq collections into sample-level transcript abundance estimates and downstream gene-level differential expression statistics.

```
[reads_paired_collection (list:paired)] ──┐
                                          ├─► [Step 1: salmon_quant (map-over)] ──► [salmon_quant_collection (list)]
[salmon_index] ───────────────────────────┘                                              │
                                                                                         ▼
[sample_metadata (tabular)] ───────────────────────────────────────────────────────────► [Step 2: deseq2 (reduce)] ──► [deseq2_norm_counts]
                                                                                         ▲                           ──► [deseq2_differential_results]
[tx2gene_map (tabular)] ─────────────────────────────────────────────────────────────────┘                           ──► [deseq2_plots]
```

## Step Details and Collection Operations

### Step 1: `salmon_quant` (Map-over)
- **Operation**: Pseudoalignment and transcript abundance quantification.
- **Input Wiring**:
  - `paired_reads`: Connected to `reads_paired_collection` (mapped over each paired element).
  - `index`: Connected to `salmon_index`.
- **Collection Behavior**: Maps over the input `list:paired` collection, preserving sample element identifiers.
- **Output**: `quant.sf` transcript quantification table per element, producing a `list` collection `salmon_quant_collection`.

### Step 2: `deseq2` (Reduce / Collective modeling)
- **Operation**: Multi-factor differential gene expression modeling using DESeq2.
- **Input Wiring**:
  - `counts_or_abundance`: Connected to `salmon_quant_collection` (accepting the collection of quantification tables).
  - `sample_table`: Connected to `sample_metadata`.
  - `tx2gene`: Connected to `tx2gene_map`.
- **Collection Behavior**: Reduces the collection of sample abundances into collective matrix modeling.
- **Outputs**:
  - `normalized_counts`: Tabular normalized expression values across samples.
  - `differential_expression`: Tabular results with log2 fold-changes, p-values, and adjusted FDR.
  - `qc_plots`: Diagnostic PDF containing PCA and dispersion plots.

## Galaxy Tool Equivalents & Unresolved Needs
- `salmon_quant`: Standard Galaxy tool `toolshed.g2.bx.psu.edu/repos/bgruening/salmon/salmon/1.10.0+galaxy0` (or compatible version).
- `deseq2`: Standard Galaxy tool `toolshed.g2.bx.psu.edu/repos/iuc/deseq2/deseq2/2.11.40.8+galaxy0` (or compatible version).
- No custom wrappers required; standard ToolShed tools fulfill all operations.

## Confidence and Open Questions
- High confidence in map-over on `list:paired` feeding directly into DESeq2's collection-aware input interface or standard tabular aggregation.
- Carried open requirement: Verify DESeq2 parameter interface for tximport/tx2gene integration vs feeding gene-level count tables directly.
