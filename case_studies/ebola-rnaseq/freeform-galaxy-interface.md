# Galaxy Workflow Interface Brief: Ebola Virus Infection RNA-seq Analysis

## Workflow Purpose & Overview
Process paired-end RNA-seq reads from human A549 WT and A549 PTPN13-KO cells infected with Ebola virus or mock at 24 and 48 HPI. The workflow performs pseudoalignment and transcript abundance quantification with Salmon, aggregates abundances to gene-level counts, and conducts multi-factor differential expression analysis with DESeq2.

## Workflow Inputs

| Input Identifier | Label | Type | Format / Collection Shape | Optional / Default | Description |
|---|---|---|---|---|---|
| `reads_paired_collection` | Paired-end RNA-seq reads | `data_collection_input` | `list:paired` (`fastqsanger`, `fastqsanger.gz`) | Required | Dataset collection of paired-end Illumina FASTQ reads across experimental samples |
| `salmon_index` | Salmon reference transcriptome index | `data_input` | `tar`, `directory` (or `fasta`) | Required | Precomputed Salmon index directory/archive for human transcriptome targets |
| `sample_metadata` | Sample metadata / Experimental factors | `data_input` | `tabular` | Required | Tabular design matrix specifying sample IDs, Genotype (WT / KO), Condition (Mock / Ebola), and Timepoint (24 / 48) |
| `tx2gene_map` | Transcript-to-gene mapping table | `data_input` | `tabular` | Required | Two-column tab-delimited mapping of transcript IDs to gene IDs |

## Workflow Outputs

| Output Identifier | Label | Source Step / Producer | Datatype / Collection | Public / Checkpoint | Description |
|---|---|---|---|---|---|
| `salmon_quant_collection` | Salmon quantification tables (`quant.sf`) | Salmon step | `list` of `tabular` | Checkpoint / Public | Per-sample transcript abundance estimates and counts |
| `deseq2_norm_counts` | DESeq2 normalized counts matrix | DESeq2 step | `tabular` | Public | Size-factor normalized gene expression matrix across all samples |
| `deseq2_differential_results` | DESeq2 differential expression results | DESeq2 step | `tabular` | Public | Statistical test statistics (log2FC, p-value, padj/FDR) for tested contrasts |
| `deseq2_plots` | DESeq2 diagnostic plots (PCA & dispersions) | DESeq2 step | `pdf` | Public | Quality control PCA and dispersion diagnostic plots |

## Collection Shapes & Mapping Strategy
- **Reads Collection**: Structured as `list:paired` containing each biological sample as an element mapped to forward and reverse FASTQ datasets.
- **Salmon Execution**: Mapped over the `list:paired` collection, outputting a `list` of `quant.sf` tabular datasets.
- **Aggregation & Modeling**: DESeq2 takes the collection of count/abundance tables together with `sample_metadata` and `tx2gene_map` as collective inputs to model variance and differential expression across the 8 experimental groups (2 genotypes × 2 conditions × 2 timepoints).

## Confidence and Assumptions
- High confidence in `list:paired` collection shape for paired-end Illumina RNA-seq.
- High confidence in Salmon + DESeq2 toolchain as standard, well-supported Galaxy ecosystem tools.
- Checkpoint output `salmon_quant_collection` allows isolated verification of the quantification tier before differential modeling.

## Open Questions & Interface Obligations
1. Whether Salmon index is provided as a pre-built index directory/tarball or built dynamically from a FASTA file.
2. The specific DESeq2 design formula (additive `~ Genotype + Time + Condition` vs full interaction `~ Genotype * Time * Condition`).
