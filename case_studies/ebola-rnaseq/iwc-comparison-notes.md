# IWC Comparison Notes: Ebola Virus Infection RNA-seq Analysis

## Nearest Exemplar Identification
- **Primary Domain Exemplar (Differential Expression)**: `transcriptomics/rnaseq-de/rnaseq-de-filtering-plotting`
- **Secondary Domain Exemplar (Paired-end Collection Mapping & Quantification)**: `transcriptomics/rnaseq-pe/rnaseq-pe`
- **Confidence**: High (matching domain: transcriptomics/RNA-seq, matching collection topology: `list:paired` mapped to per-sample quantification tables and reduced into DESeq2).

## Relevant Subgraph Excerpt
Excerpt from `transcriptomics/rnaseq-de/rnaseq-de-filtering-plotting` (`iwc-exemplar.gxwf.yml`):

```yaml
  - id: Differential Analysis
    label: Differential Analysis
    tool_id: toolshed.g2.bx.psu.edu/repos/iuc/deseq2/deseq2/2.11.40.8+galaxy3
    tool_version: 2.11.40.8+galaxy3
    in:
      - id: select_data|rep_factorName_0|rep_factorLevel_0|countsFile
        source: Counts from changed condition
      - id: select_data|rep_factorName_0|rep_factorLevel_1|countsFile
        source: Counts from reference condition
    out:
      - id: deseq_out
      - id: plots
      - id: counts_out
    tool_state:
      output_options:
        output_selector:
          - pdf
          - normCounts
```

## Structural Comparison & Diff

| Feature | Upstream Briefs (`ebola-test`) | IWC Exemplar (`rnaseq-de` / `rnaseq-pe`) | Comparison & Guidance |
|---|---|---|---|
| **Input Collection Shape** | `list:paired` (FASTQ) | `list:paired` (`rnaseq-pe`) | Direct match. Preserves sample names across map-over operations. |
| **Quantification Tier** | Salmon pseudoalignment (`salmon quant`) | HISAT2/STAR + featureCounts | Distinct tool family (Salmon vs aligner+counter), but topologically identical: map over `list:paired` producing a list of sample tabular files. |
| **Differential Expression** | Multi-factor DESeq2 (WT vs KO, Mock vs Ebola, 24 vs 48 HPI) | Two-condition DESeq2 (`rnaseq-de`) | The exemplar uses pairwise factor levels. In the multi-factor setting, DESeq2 takes the sample matrix or factor levels across conditions. |
| **Outputs** | `quant.sf` collection, normalized counts, differential results, diagnostic plots | Normalized counts, differential results, volcano/heatmap plots | Consistent output hierarchy; promoting `salmon_quant_collection` as a checkpoint output follows IWC best practices. |

## Guidance for Downstream Template Authoring
1. **Draft Steps**:
   - `salmon_quant`: Drafty step marked with `_plan_tool_id: toolshed.g2.bx.psu.edu/repos/bgruening/salmon/salmon` mapped over `reads_paired_collection`.
   - `deseq2`: Drafty step marked with `_plan_tool_id: toolshed.g2.bx.psu.edu/repos/iuc/deseq2/deseq2` connected to the `salmon_quant` collection output and metadata tables.
2. **Collection Wiring**: Use `connect_across: true` or native Galaxy collection mapping semantics so that Salmon operates per sample pair and passes a `list` collection into DESeq2.
