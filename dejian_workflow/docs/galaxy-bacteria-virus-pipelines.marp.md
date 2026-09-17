---
marp: true
theme: default
paginate: true
size: 16:9
---

<style>
section { font-size: 22px; padding: 40px 60px; }
section h2 { margin-top: 0; margin-bottom: 0.4em; }
section p, section ul, section ol { margin: 0.4em 0; }
section li { margin: 0.12em 0; }
section pre { margin: 0.4em 0; line-height: 1.3; font-size: 0.8em; }
section table { font-size: 0.85em; }
section table th, section table td { padding: 6px 10px; }
</style>

# Galaxy Pipelines for Bacteria & Virus Analysis

Catalog + a first pass at description-to-pipeline mapping

**Talk to Galaxy** · NIAID-BRCs AI Codeathon 2.0
Source: IWC registry — github.com/galaxyproject/iwc

---

## Why this matters

Goal 1 of the proposal: **route before building.**

> Determine, early in the conversation, whether a published workflow
> already does what the researcher needs — **use**, **adapt**, or **build**.

This deck is that decision surface, scoped to bacteria & virus workflows:
- What actually exists in the IWC registry today
- Machine-readable catalog: `knowledge_base/pathogen_genomics/galaxy_pipeline_catalog.yaml`
- A working v0 matcher: `scripts/search_pipeline_catalog.py`

---

## Bacterial Genomics (4 workflows)

| Workflow | Input | Does |
|---|---|---|
| **cgMLST** | Assembled contigs | Strain typing via curated MLST schemes (pubMLST, Enterobase, cgMLST.org) |
| **AMR Gene Detection** | Assembled genome | StarAMR + AMRFinderPlus + ABRicate → resistance & virulence genes |
| **Genome Annotation** | Assembled genome | Bakta CDS calling, integrons, plasmids, insertion sequences |
| **QC & Contamination Control** | Illumina PE FASTQ | Quast/Checkm2 assembly QC, Kraken2/Bracken taxonomic ID |

`workflows/bacterial_genomics/` in IWC

---

## Virology (3 workflows)

| Workflow | Input | Does |
|---|---|---|
| **Generic Non-Segmented Viral Variant Calling** | Illumina PE, ± amplicon | fastp→bwa-mem→lofreq/ivar→SnpEff for simple viruses (e.g. Morbillivirus) |
| **Influenza A Subtyping + Consensus** | Illumina PE | VAPOR segment matching, HA/NA subtyping, consensus, phylogenetics |
| **Pox Virus Amplicon (half-genome)** | Illumina PE, 2 runs/sample | Resolves ITRs by merging masked-reference mappings, iVar consensus |

`workflows/virology/` in IWC

---

## SARS-CoV-2 (7 workflows)

| Workflow | Data | Purpose |
|---|---|---|
| WGS PE / SE Variant Calling | Illumina WGS | bwa-mem/bowtie2 + lofreq + snpEff |
| Illumina Amplicon ARTIC (lofreq) | Illumina amplicon | Ampliconic variant calling, primer-site QC |
| Illumina Amplicon ARTIC (iVar) | Illumina amplicon | Rapid majority variants + pangolin/nextclade lineage |
| ONT ARTIC Variant Calling | Nanopore amplicon | minimap2 + medaka, ARTIC-style |
| Consensus Construction | VCF + BAM | Builds consensus from any of the above |
| Variation Reporting | VCF | Tabular + allele-frequency reports |

`workflows/sars-cov-2-variant-calling/` in IWC — the most mature pipeline family

---

## Metagenomics & Pathogen ID (6 workflows)

| Workflow | Organism scope | Does |
|---|---|---|
| Nanopore Preprocessing | agnostic | QC + host-read removal |
| Taxonomy Profiling (Krona) | agnostic | Kraken2 species ID + visualization |
| Gene-based Pathogen ID | agnostic | Virulence factor + AMR gene screening |
| Allele-based Pathogen ID | agnostic | SNP-based strain/variant tracking |
| PathoGFAIR Aggregation | agnostic | Cross-sample heatmaps, phylogenies |
| Raw Read AMR (metagenomic) | bacteria-leaning | Sylph taxonomy + Groot/deepARG AMR from raw short reads |

`workflows/microbiome/` in IWC — useful when the organism is *unknown*

---

## Coverage snapshot: 20 workflows, honestly thin in places

- **Deep coverage:** SARS-CoV-2 (7 dedicated workflows)
- **Moderate coverage:** generic bacterial genomics (typing, AMR, annotation, QC)
- **Sparse coverage:** named viruses beyond SARS-CoV-2 — only Influenza and Pox virus have dedicated workflows
- **No dedicated workflow for:** most WHO priority pathogens by name (e.g. no "Mtb workflow," no "Salmonella workflow" — bacterial workflows here are genus-agnostic)

**Implication:** many real requests will legitimately route to **adapt** (a close generic workflow) or **build**, not **use**. That's a finding for the pass-rate report, not a catalog gap to silently paper over.

---

## Can we map a free-text description to these pipelines?

**Yes — a first version exists and works.**

`scripts/search_pipeline_catalog.py` + `knowledge_base/pathogen_genomics/galaxy_pipeline_catalog.yaml`

Approach (v0, intentionally simple and auditable):
1. Each catalog entry carries `organism`, `data_type`, `analysis_type`, and free-text `keywords`
2. Tokenize the researcher's description
3. Score each workflow by keyword-token overlap
4. Return ranked candidates **with the matched terms shown** — no black box

This is a keyword router, not semantic search — it's the honest v0 to build the MCP/embedding-based version against.

---

## Demo: it actually runs

```
$ scripts/search_pipeline_catalog.py \
  "Illumina paired-end amplicon sequencing of SARS-CoV-2, \
   want variant calls and lineage assignment with pangolin"

1. [10 matched terms] SARS-CoV-2: Illumina Amplicon PE (iVar/pangolin/nextclade)
   matched on: amplicon, assignment, cov, end, illumina,
               lineage, paired, pangolin, sars, variant

2. [8 matched terms] SARS-CoV-2: WGS PE Variant Calling
3. [7 matched terms] SARS-CoV-2: Illumina Amplicon PE (lofreq, ARTIC)
```

Correctly ranks the pangolin/nextclade workflow first — it's the only
candidate matching "assignment," "lineage," **and** "pangolin."

---

## Demo: it also knows when it doesn't know

```
$ scripts/search_pipeline_catalog.py \
  "differential expression analysis of mouse RNA-seq data"

No catalog matches. This is a candidate for the 'build' path,
or a sign the catalog needs a new entry -- not a silent failure.
```

This matters for **Goal 5 (adversarial review):** a router that always
returns *something* invites confident fabrication. Returning nothing when
nothing matches is the correct, honest behavior.

---

## Known limits of the v0 matcher

- **Synonym-blind:** "flu" only matches because it's hand-listed as a
  keyword alongside "influenza" — a paraphrase not anticipated will miss
- **No organism-name specificity:** a request naming an organism not in
  any keyword list (most named bacteria/pathogens) won't match even where
  a genus-agnostic workflow (e.g. AMR detection) would actually apply
- **Curated subset, not the live registry:** only ~20 of the full IWC
  catalog's workflows are represented here

**Next step:** swap keyword overlap for embedding similarity or an
MCP-grounded LLM call against the live IWC registry (Goal 2/3), while
keeping the same "show matched evidence, or say no match" contract.

---

## Where this plugs into the pipeline

```
interview (free-text) → search_pipeline_catalog.py → route.py
                              │
                    ranked candidates + matched terms
                              │
              use / adapt / build decision (Goal 1)
```

- **Confident top match** → propose **use** or **adapt**
- **No match, or all low-confidence** → **build**, and log it for the
  Goal 7 pass-rate/failure taxonomy

Files: `knowledge_base/pathogen_genomics/galaxy_pipeline_catalog.yaml` ·
`scripts/search_pipeline_catalog.py`
