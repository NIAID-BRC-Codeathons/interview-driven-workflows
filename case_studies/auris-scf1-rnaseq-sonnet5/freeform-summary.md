# Free-Form Source Summary: Planetary-Scale Retrospective DMS of Bacteriophage ΦX174

## 0. Scope note (read this first)

The primary source is `/Users/scottcain/git/dms/paper/draft_manuscript.tex` ("The Petabase
Evolutionary Landscape of Bacteriophage ΦX174: Deconvoluting Laboratory Spike-In Clouds,
Dual-Coding Constraints, and Uncultivated Microviral Diversity", Nekrutenko et al., draft,
Sept 2026). **As it stands today, this .tex file contains only the Introduction and the first
Results section** (SRA landscape certification / spike-in sieve, ~6 pages). It does not yet
contain the later results sections (real-time purging kinetics, HyphAeon VEP benchmarking,
dual-coding shadow effect, Fane morphogenesis) that are drafted in `sections/02..07_*.md` and in
the sibling manuscript `phiX174_planetary_dms.tex` (explicitly out of scope per instructions).

Because the task asked for the *computational methods* underlying the whole project (this
summary feeds a Galaxy-workflow-reconstruction pipeline, not a manuscript-text pipeline), this
document covers the **full computational pipeline implied by draft_manuscript.tex plus the
supplementary project material** (HANDOVER.md, PROJECT_SUMMARY.md, README.md, the ChronAeon/
HyphAeon reanalysis report, the per-section drafts, and the actual Python/shell scripts at the
repo root). Facts that come only from the current draft_manuscript.tex are marked **[PAPER]**;
facts that come from the broader project context are marked **[CONTEXT]**. Downstream phases
should treat **[PAPER]** facts as the authoritative scope of "the paper" and **[CONTEXT]** facts
as enrichment / rationale for why each pipeline stage exists.

The manuscript's actual object of study is not a single wet-lab experiment: it is a
**retrospective computational re-analysis of public sequence archives** (the NCBI SRA / Logan
petabase index) for the historically important model virus ΦX174, cross-validated against a
2026 whole-genome saturation-mutagenesis (deep mutational scanning, DMS) dataset and several
classical experimental-evolution datasets. The reproducible "workflow" is therefore a data
mining + curation + statistics pipeline, not a wet-lab protocol.

## 1. High-level pipeline shape

```
[Stage A] Reference & query prep (genome, 10 CDS FASTAs)
        |
[Stage B] Petabase k-mer containment screen: kmindex (Galaxy tool) across 109 Logan k-mer DBs
        |
[Stage C] Track 1 — LexicMap sequence-to-graph streaming search (Galaxy tool) across Logan indices
        |         -> custom streaming client (stream_lexicmap_msa.py) does multi-HSP coordinate
        |            tiling, codon QC, haplotype collapsing -> clean/flagged FASTA + TSV + JSON
        |
[Stage C'] Track 2 — Disassembler/logan-walker cDBG traversal (Rust binary) on stratified
        |            diversity cohorts -> intra-host SNVs/haplotypes (VCF-like / codon MSA)
        |
[Stage D] Nominal-taxonomy SRA metadata audit (manual/registry-based BioProject certification)
        |
[Stage E] Reference experimental-evolution datasets ingested independently:
        |   - Idaho 2024 SRA time series (download -> bowtie2 align -> samtools mpileup -> custom
        |     Python trajectory caller) -> selection-rate vs DMS-fitness correlation
        |   - Dickins & Nekrutenko 2009 chemostat GAII reads (Galaxy library download -> bowtie2
        |     -> samtools mpileup -> custom trajectory caller)
        |
[Stage F] Wei/Li/Lehner 2026 whole-genome DMS dataset (external ground truth, NOT bundled in
        |   this repo — see Gaps) joined against every other stage by mutation ID
        |
[Stage G] HyphAeon (real installed CLI + Python package) zero-shot variant-effect prediction,
        |   benchmarked against GEMME/ProteoCast/ESCOTT/RSALOR/DDMut/ESM-2/ESM3/Tranception
        |
[Stage H] hyphaeon_overlaps (custom package) dual-coding consequence classification + shadow-
        |   effect calibration on overlapping ORFs (D/E, B/A, K/C, K/A)
        |
[Stage I] "ChronAeon" multi-scale sieve = a fixed sequence of HyphAeon CLI subcommands
        |   (autoclock -> r0 -> meme -> filter) plus closed-form stats (ACAT/Cauchy combination)
        |   run over the curated sequence cohorts, in run_chronaeon_phix174_sieve.py
        |
[Stage J] Fane-mechanics / Bull-Wichman literature cross-referencing (pandas joins against DMS
        |   table + curated bibliography JSON, no external tool)
        |
[Stage K] Figure generation (matplotlib/seaborn) + manuscript style linting (project-internal,
            not a science tool)
```

## 2. Stage-by-stage detail

### Stage A — Reference genome and per-gene CDS query panel
- **[PAPER/CONTEXT]** Reference genome: NCBI RefSeq `NC_001422.1` (ΦX174, 5,386 nt circular
  ssDNA). File on disk: `ref/NC_001422.1.fasta` (+ `.fai`).
- 10 canonical ORFs treated as the query/target set: **A, B, C, D, E, F, G, H, J, K** (an 11th,
  A*, is an internal in-frame product of A, not separately queried in most scripts although
  listed in some contexts). Per-gene lengths (bp/aa) and roles, from the paper's Table 1:
  - J 114/38 (DNA core packaging), K 168/56 (overlap regulator, K overlaps A and C), C 258/86
    (DNA synthesis switch), E 273/91 (lysis, MraY inhibitor), B 360/120 (internal scaffold), D
    456/152 (external scaffold, 240-mer cage), G 525/175 (major spike pentamer), H 984/328
    (pilot/DNA-ejection protein), F 1,281/427 (major capsid, T=1 60-mer), A 1,539/513
    (rolling-circle replicase). Total coding length 5,958 bp (exceeds genome length 5,386 nt
    because of overlapping frames).
- Individual gene FASTAs at `cds/A.fasta` … `cds/K.fasta`, `cds/Astar.fasta`, plus a combined
  query panel `cds/phix174_all_genes_panel.fasta` used as the multi-FASTA input to the Galaxy
  kmindex tool.
- Protein reference set: `ref/phix174_proteins.faa` / `.fasta`.
- Historical/auxiliary genomics pulls (not central to the pipeline but present):
  `data/ncbi_virus_phix174_annotated.tsv`, `ncbi_virus_phix174_raw.json`,
  `ncbi_virus_complete_genomes.fasta`, `ncbi_virus_phix174.gb` — an NCBI Virus resource pull used
  for the "185 complete GenBank records / 91.8% derive from lab experimental evolution"
  certification mentioned in HANDOVER.md **[CONTEXT]**.

### Stage B — Petabase k-mer containment screen (kmindex, real Galaxy tool)
- **[PAPER, "high-throughput k-mer containment indexing (kmindex)"]** Tool: **kmindex**, invoked
  as an actual installed Galaxy Tool Shed wrapper, not a hypothetical name:
  `toolshed.g2.bx.psu.edu/repos/iuc/kmindex/kmindex_query/0.6.1+galaxy4`, run via BioBlend
  (`submit_kmindex_all_genes.py`).
- Databases queried: **109 Logan SRA k-mer index shards**, organized into a fixed taxonomic/
  library-type grid, e.g. `GENOMIC_BCT`, `GENOMIC_HUMAN`, `GENOMIC_VRL`, `METAGENOMIC_ENV`,
  `METATRANSCRIPTOMIC_*`, `SYNTHETIC_*`, `VIRALRNA_*`, `TRANSCRIPTOMICSINGLECELL_*`, etc. (full
  list of 109 DB names hardcoded in `ALL_KMINDEX_DBS`).
- Concrete kmindex parameters used: `zvalue=6`, `threshold=0.3`, `format=json`, `fast=False`,
  `verbose=error`. Query input: the combined multi-FASTA panel `cds/phix174_all_genes_panel.fasta`
  uploaded as a Galaxy HDA.
- Output: per-shard JSON hit maps (accession -> containment score), tracked in
  `kmindex_runs.json`; harvested/merged later (Stage C') into `{gene}.scores.json` and
  `UNION.accessions.txt` (2,114,904 unique accessions cited in the paper).
- Job orchestration is via the Galaxy REST API / BioBlend against `https://usegalaxy.org`, using
  an API key file at `/tmp/gxy.txt` — i.e., **this stage already runs on Galaxy today** via
  ad-hoc scripting rather than a formal workflow; a major goal of this Foundry pipeline is
  presumably to formalize exactly this into a `.ga`/gxformat2 workflow.

### Stage C — Track 1: LexicMap streaming search (real Galaxy tool) + custom tiling/QC client
- **[PAPER]** Tool: **LexicMap**, "linear sequence-to-graph streaming aligner", also a real
  installed Galaxy tool: `toolshed.g2.bx.psu.edu/repos/iuc/lexicmap/lexicmap_search/0.9.0+galaxy1`
  (`pull_logan_alignments.py`). Indices queried are Logan-derived per-domain LexicMap indices:
  `BacteriaGenomic`, `BacteriaMetagenomic`, `HumanGenomic`, `HumanMetagenomic`, `MouseGenomic`,
  `Viral`, `Synthetic`, `Singlecell`, etc. (25 total; a narrower `TARGETED_PHAGE_INDICES` subset
  of 5 — `Viral`, `BacteriaMetagenomic`, `HumanMetagenomic`, `OtherMetagenomic`, `Synthetic` — is
  used for per-gene targeted runs). Parameters used: `top_n_genomes=0`, `advanced_settings|all=True`
  (i.e. return all hits, no top-N truncation). For the smaller/harder-to-recover genes (`submit_remaining_logan.py`,
  covering genes A/C/E/K), per-gene-tuned search sensitivity parameters are used instead of
  defaults: `align_min_match_pident=60.0`, `align_min_match_len` in the 35–50 range,
  `seed_min_prefix` in the 15–17 range, `min_qcov_per_genome=30.0` — i.e. short/divergent genes
  need looser seed/match thresholds to be recovered at all.
- Per-gene submission/monitor/download cycle implemented in `pull_logan_alignments.py`,
  `submit_all_structural_logan.py`, `submit_remaining_logan.py`, `process_and_benchmark_logan.py`
  — all via BioBlend against usegalaxy.org, tracked in JSON state files
  (`logan_structural_runs.json`, `logan_remaining_runs.json`, `logan_job_{gene}.json`).
- Output of the Galaxy tool: a results TSV per gene (`logan_results/{gene}.tsv` or
  `{gene}.results.tsv`) — a BLAST/LexicMap-style tabular hit table with columns including
  `sgenome` (SRA run accession), percent identity (`pident`), and HSP coordinates.
- **[PAPER]** The custom rescue step (novel algorithmic contribution, `stream_lexicmap_msa.py`,
  resolves "GitHub Issue #1" on `nekrut/dms`) streams this TSV (from a local file, stdin, or
  directly over HTTP from a Galaxy dataset `/api/datasets/{id}/display` endpoint using an API key
  at `/tmp/gxy.txt`), groups hits by SRA accession, and:
  1. Merges multiple non-overlapping HSPs per accession onto the canonical ΦX174 gene coordinate
     frame (greedy tiling, ties broken by higher `pident`) — "multi-HSP coordinate tiling".
  2. Translates using the standard/bacterial genetic code (NCBI table 11, hardcoded codon table
     in-script) and flags premature internal stop codons (excluding the natural terminal stop).
  3. QC gate, exposed as CLI flags on `stream_lexicmap_msa.py`: `--min-coverage 0.80` (full-length
     clean cut), `--min-coverage-partial 0.50` (partial/expanded cut), `--min-pident 60.0`,
     `--max-internal-stops 0`, `--sample-cap 10` (per-cohort ledger sampling), and an
     `--allow-frameshifts` flag whose default/production setting could not be confirmed from prose
     alone — treat frameshift handling as a parameter to confirm before Galaxy-wrapping this step,
     not an assumed "always reject" behavior.
  4. Partitions each accession into **Clean** vs **Flagged** cohorts and collapses Clean
     sequences into non-redundant haplotypes (weighted by observation count).
- Declared outputs per gene (prefix `{gene}`): `.clean.msa.fasta`, `.clean.haplotypes.tsv`,
  `.clean.accessions.fasta`, `.clean_expanded.accessions.fasta` (partial ≥50% cov), 
  `.flagged.accessions.fasta`, `.flagged.tsv` (audit reasons), `.cohort_ledger.tsv` (per-accession
  status for every evaluated accession), `.summary.json` (quantile distributions, regime
  diagnostics, multi-HSP recovery counts). These per-gene summary JSONs
  (`msa/phiX174_{gene}.summary.json`) are the direct source of the paper's Table 1 numbers and
  are aggregated into `results/00_ingestion/lexicmap_9genes_ingestion_manifest.csv`.
- **[PAPER]** Quantitative outcome (Table 1 in draft_manuscript.tex): 26,836,801 streamed rows /
  24,378,503 evaluated accession queries across the 10 genes; 1,060,472 multi-HSP rescues;
  17,921,411 clean full-length CDS; 316,135 unique clean haplotypes; 2,218,490 flagged internal
  stops (2,215,172 of which are in Gene E alone — the `am3` spike-in, see Stage D2 below).

### Stage C′ — Track 2: Disassembler / `logan-walker` cDBG traversal (real external tool, Rust)
- **[CONTEXT]** A second, independent analytical track described in PROJECT_SUMMARY.md /
  HANDOVER.md and implemented in `process_kmindex_with_disassembler.py`. Not mentioned in the
  current draft_manuscript.tex text, but represents real, runnable code.
- Real external binary: `logan-walker`, a Rust program built at
  `~/git/disassembler/walker/target/release/logan-walker` (project `nekrut/disassembler`,
  upstream PRs #3 and #4 referenced in README.md). Companion Python script:
  `build_walker_codon_msa.py` (same repo, `python/` dir) and `build_ref_guided.py`
  (`nekrut/logan-hypyaeon`, referenced from `pull_logan_alignments.py`).
- Purpose: traverse compacted de Bruijn graphs (cDBGs) directly from Logan's public S3 bucket
  (`s3://logan-pub`) per SRA accession, recovering intra-host alleles/SNVs and structural bubbles
  without reference-alignment bias (contrasts with Track 1's linear/reference-guided approach).
- Concrete parameters (defaults seen in `run_disassembler_for_gene(...)`,
  `process_kmindex_with_disassembler.py`): `workers=8`, `fetch_workers=6`, `min_vaf=0.10`,
  `min_abund=5.0`, `min_abund_frac=0.0`, `prune_frac=0.01` ("two-pass depth pruning": unitigs
  below 1% of gene depth pruned before realignment), `min_cov=0.85`; elsewhere (PROJECT_SUMMARY.md)
  cited as `--hops 5`, `--max-size-mb 4096`, `--emit-vcf`, `--no-emit-alts` (biallelic bubble
  phasing without chimeric alt-haplotype emission), followed by codon-level phylogeny via
  **FastTree** (real tool, GTR nucleotide model; binary at
  `~/miniconda3/envs/logan/bin/fasttree`, invoked from `process_and_benchmark_logan.py`).
- Input: harvested per-gene candidate accession lists from Stage B's merged kmindex shard JSONs
  (`harvest_collection()` in `process_kmindex_with_disassembler.py` walks a Galaxy dataset
  collection of ~2,869 shard JSON files in parallel, 32 worker threads, via the Galaxy history
  contents API). Output: `{gene}.accessions.txt`, `{gene}.scores.json`, `UNION.accessions.txt`
  (per-gene max containment scores; feeds Stage below).
- Because full reconstruction of all 2.1M accessions would require >72 TB of S3 downloads
  (PROJECT_SUMMARY.md), a **stratified diversity cohort of 2,500 accessions/gene** is drawn
  instead (`create_targeted_diversity_cohorts.py`): 500 "canonical" (containment ≥0.99, control
  spike-in baselines), 1,000 "high-homology" (0.80–0.99), 1,000 "divergent" (0.50–0.80), evenly
  sampled across each score bracket (not just top-N) to avoid clustering. Outputs:
  `kmindex_candidates/{gene}.diversity_2500.txt/.json`, `diversity_2500_summary.json`.

### Stage D — Nominal-taxonomy SRA metadata audit
- **[PAPER]** Not a computational tool per se but a manual/registry-based certification: all SRA
  runs filed under NCBI TaxID `10847` ("Escherichia phage phiX174") and `2886930`
  ("Sinsheimervirus phiX174") were enumerated (136 runs / 18 BioProjects) and each BioProject was
  manually classified into one of: Experimental Evolution (7 runs, `PRJNA1174868`/`SRP539859`,
  the Idaho 2024 study — the *only* genuine evolution study), Platform Benchmarking (36 runs;
  `SRP042938`, `SRP008975`, `ERP002532`, `ERP000074`, `SRP001260`), Paleogenomics Control (35 runs;
  `ERP001254`, MPI-EVA ancient-DNA calibration), Metagenomics/Cross-talk (29 runs; `SRP347090`,
  `SRP653402`, `ERP001281`, `SRP066453`), Method Development (18 runs; `SRP059208`, `SRP082602`
  — Cir-Seq/Droplet-Seq/O2N-Seq benchmarks), Misfiled Spike-Ins (6 runs; `SRP009433`/`SRR009433`,
  `ERP000177` GEUVADIS, `SRP003315` Drosophila, `SRP042938`), Synthetic Standards (1 run;
  `SRP363953`, pREF), General QC (4 runs; `DRP008496`, ribonucleoside misincorporation).
- Result: only 5.1% (7/136) of nominally-tagged runs are genuine evolution experiments; this
  motivates bypassing nominal taxonomy entirely and mining the full Logan index by sequence
  content instead (Stages B/C above).
- Host/biome/platform metadata stratification of the 2,114,904-accession Logan hit set (human
  clinical 14.0%, human microbiome 8.7%, model animals/livestock 20.7%, environmental
  metagenomes 18.1%, crops 8.0%, pathogen surveillance 6.4%, bacterial isolates 3.3%; platforms:
  100% Illumina — MiSeq 28.4%, HiSeq family ~48%, NovaSeq 12%) appears to be produced by
  cross-referencing SRA run metadata (BioSample/BioProject attributes) against the accession
  union list; no single script for this was identified among the root-level `.py` files — likely
  done via NCBI Entrez/SRA metadata API calls not captured in a standalone script, or via manual
  curation. **This is a gap for downstream reproducibility (see Section 5).**

### Stage D2 — The Sanger `am3` dual-coding molecular fingerprint (core finding, not a tool stage)
- **[PAPER]** A specific diagnostic mutation is used to prove that most global ΦX174 SRA hits are
  the Illumina PhiX Control v3 library (derived from the 1977 Sanger `am3` amber mutant), not wild
  biology: genome position **nt 587, G→A**. In Gene E (+1 frame, nt 568–843) this converts codon 7
  TGG→TAG (`gpE_W7*`, premature amber stop, abolishes MraY inhibition / lysis). In Gene D (0
  frame, nt 390–848) the same nucleotide is the third position of codon 66, GTC→GTA
  (`Val66Val`, 100% synonymous, procapsid scaffold unaffected). 2,215,172 / 2,392,457 (92.59%)
  of evaluated Gene E accessions carry this exact substitution; quarantining them recovers
  52,862 bona-fide wild-type Gene E sequences. This detection logic lives inside the QC step of
  `stream_lexicmap_msa.py` / is summarized in `results/02_layer1_quasispecies/
  gene_e_am3_quarantine_audit.json`.
- Downstream statistical consequence (`P(error) = 1 - e^{-Lε}` with Illumina substitution rate
  ε≈10⁻³/nt): long genes (F 1,281 bp, A 1,539 bp) accumulate singleton haplotypes at 89.9%/84.3%
  of all unique haplotypes; stratified identity curation (>99% identity = error cloud vs
  50–98% = genuine divergent microvirus) is required before any VEP benchmarking (Stage G).

### Stage E — Reference experimental-evolution datasets (real tools: bowtie2 + samtools)
- **Idaho 2024** (`PRJNA1174868` / `SRP539859`): 7 Illumina MiSeq paired-end runs
  `SRR31059334`–`SRR31059340`, competitive-growth chemostat time series at t=0, 35, 70 min,
  tracking Gene G. Download: `download_idaho_sra.py` (parallel `urllib` fetch against a manifest
  `phix174_sra_evolution_manifest.tsv` with per-file MD5 checksums, 4 worker threads) into
  `data/sra_evolution/idaho2024/`. Alignment: `align_idaho_sra.sh` —
  **bowtie2** (`bowtie2 -x ref/NC_001422.1 -1 R1 -2 R2 -p 4`) piped to **samtools sort**
  (`samtools sort -o {run}.sorted.bam -`) then **samtools index**. Both binaries are pinned to a
  specific conda env (`~/miniconda3/envs/mrsa_align/bin/{bowtie2,samtools}`).
- Trajectory calling (`analyze_idaho_evolution.py`): **samtools mpileup** restricted to Gene G
  coordinates (`-r NC_001422.1:2395-2919 -f ref/NC_001422.1.fasta -d 500000 -A -q 0`) across all
  7 BAMs simultaneously; a hand-rolled pileup-string parser (regex-based, strips read-start/end
  markers and indel length prefixes) tallies per-sample allele counts; for every non-reference
  allele at every position it computes codon context (via Biopython `CodonTable.unambiguous_dna_by_id[1]`,
  standard genetic code) to classify Synonymous/Missense/Nonsense, computes `f0`, mean `f35`
  (avg of 3 replicates), mean `f70` (avg of 3 replicates), a linear slope
  `(f70-f0)/70` and a log-ratio selection rate `s = ln((f70+ε)/(f0+ε))/70` with `ε=1e-5`, joins
  against the Wei 2026 DMS table by `genome_mut_ID_nt`, and reports Spearman/Pearson correlation
  between `s` and DMS fitness `w` (filtering to `freq_t0 > 0.0005` and non-null DMS fitness).
  Output: `idaho2024_trajectories_vs_dms.csv`. Reported result: Spearman ρ=0.3549 (P=5.9e-44),
  Pearson r=0.3632 (P=4.3e-46), N=1,439 SNVs; lethal-allele mean s=-0.0195 min⁻¹.
- **Dickins & Nekrutenko 2009** (`GBE` 1:294-307, chemostat GAII data): 10 samples (Ancestor A1–A4,
  Lineage B: B1,B3,B4, Lineage C: C1,C3,C4). Download via **BioBlend** from a specific existing
  Galaxy data-library folder (`download_dickins_galaxy.py`, folder ID `F175d7d5ddeeb1d43` on
  `https://usegalaxy.org`, imported into a history then downloaded per-HDA and gzip-compressed).
  Alignment: `align_dickins.sh` — same bowtie2 (single-end `-U`) + samtools sort/index pattern as
  Idaho, against the same `NC_001422.1` reference.
  Trajectory calling: `call_dickins_trajectories.py` — whole-genome **samtools mpileup**
  (`-d 500000 -A -q 0`, no coordinate restriction) across all 10 BAMs, same custom pileup parser,
  keeps any position with max allele frequency ≥0.5% across samples or matching a fixed list of
  historically important positions (656, 1301, 1306, 1308, 1675, 3967, 4491, 5262), joins against
  the Wei 2026 DMS table. Output: `dickins2009_empirical_trajectories.csv`. Key validated
  mutations: `C656A` (`gpE_S30*`, rises 0%→0.76%→1.58% in Lineage B; DMS fitness w=0.5829 — the
  "17-year lysis paradox"), `A1301G` (`gpF_T101A`, sweeps to 78.5%/32.7% in Lineages B/C; w=1.039),
  `G319T`/`A323G` (`gpC_V63F`/`gpC_D64G`, reach 11.0%/8.4%).

### Stage F — Wei, Li & Lehner (2026) whole-genome DMS ground truth (external dataset, NOT in repo)
- **[PAPER via citation; CONTEXT for file format]** bioRxiv doi:10.64898/2026.07.25.740675,
  "Complete Mutagenesis of the Genome and Proteome of ΦX174." N=39,335 amino-acid variants /
  16,098 SNVs across all 11 genes, competitive-growth relative fitness `w` for every accessible
  substitution.
- Every downstream script expects this at a **fixed relative path that does not exist in this
  checked-out repo**: `phix174_WGM/data/phix_all_dms100_sub_libraries_normalized_unique_stat_1nt.tsv.zip`
  (the 1nt/SNV-level table, columns include `genome_mut_ID_nt`, `phix_aa_mut_genes`,
  `phix_aa_mut_ID`, `phix_aa_mut_class`, `phix_aa_mut_class_sum`, `fitness_final`,
  `mutation_category_FDR_lethal_1nt`, `genome_nt_pos_overlap_orf`, per-gene per-position columns
  like `gene_sub_aa_mut_gene`/`_pos`/`_class`) and
  `phix174_WGM/data/evaluate_VEPs/phix_proteins_dms_mut_modelling_merged.tsv.zip` (protein-level
  table merged with precomputed VEP scores). **This external dataset is a hard input dependency
  for Stages E/G/H/J and must be sourced (from the Wei et al. bioRxiv supplement / GitHub) for
  any reproduction — see Gaps, Section 5.**

### Stage G — HyphAeon zero-shot variant-effect prediction (real installed tool)
- **[CONTEXT, confirmed by code]** HyphAeon ("Phylogenetic Axial Transformer") is **a real,
  installed multi-purpose bioinformatics package/CLI**, not merely a name used in prose. Evidence:
  `from hyphaeon.inference import load_model, get_device` and
  `from hyphaeon.disease import predict_disease_pathogenicity` (Python API, used in
  `benchmark_hyphaeon_phix174.py` and `process_and_benchmark_logan.py`, running on `torch`/GPU —
  "12.4 s on a single NVIDIA A100"); AND a separate CLI binary
  `~/miniconda3/bin/hyphaeon` invoked via `subprocess` with real subcommands
  `autoclock`, `r0`, `meme`, `filter` (see Stage I). Upstream project: `github.com/veg/hyphaeon`
  (per section drafts) — this is the Kosakovsky Pond lab's phylogenetics toolkit, i.e. plausibly
  installable as an actual Galaxy/conda tool, not project-internal glue code.
- Python-API usage (`predict_disease_pathogenicity`): inputs an MSA file path (from
  `msas_sub/{gene}_b*` — subsampled 350-taxa EVcouplings-format MSAs) and a list of mutant codes
  (parsed via regex `gp[A-Z]_([A-Z]\d+[A-Z])` from DMS IDs), scores pathogenicity per mutation,
  correlated (Spearman) against DMS `fitness_aa_mut`.
- Benchmarked against pre-computed columns already present in the input TSV for other VEP tools
  (not run by this repo, just compared): **GEMME**, **ProteoCast**, **ESCOTT**, **RSALOR**,
  **DDMut**, **ESM_IF1**, **MIF_ST**, plus separately **ESM-2 (15B)**, **ESM3 Open (1.4B)**,
  **Tranception-L** (all real published external tools/models, values taken from the merged DMS
  table, not re-run here).
- Reported results (Table 3 in the fuller manuscript draft, not yet in draft_manuscript.tex):
  HyphAeon proteome mean ρ=+0.149 (median +0.131) vs ESM-2 15B mean ρ=+0.013; per-gene range
  ρ=+0.071 (B) to +0.274 (D); stratified-curation gain 3.2× on Gene F (ρ +0.047→+0.154) and rescue
  of Gene G from negative correlation (ρ -0.011→+0.118, P=7.7e-6).

### Stage H — Dual-coding / overlapping-frame consequence classification (custom package, real code)
- **[CONTEXT, confirmed by code]** Package `hyphaeon_overlaps` (repo `nekrut/hyphaeon-overlaps-cdx`
  / `nekrut/hyphaeon-overlaps`), imported as
  `from hyphaeon_overlaps.consequences import consequence, joint_class` in
  `calibrate_hyphaeon_shadow_effect.py`. This is genuinely a separate installable Python package
  (added to `sys.path` from a sibling checkout `~/git/hyphaeon-overlaps-cdx`), i.e. NOT part of
  core HyphAeon, but a purpose-built companion library for classifying joint consequence codes
  (SS/SN/NS/NN/Stop-gain/Stop-loss) of a single nucleotide change across two overlapping reading
  frames.
- Analysis: filters DMS table to `genome_nt_pos_overlap_orf == "Overlapping Coding"`, computes
  joint class per row, groups by gene-pair (`DE`, `BA`, `KC`, `KA`) and joint class, runs
  `scipy.stats.mannwhitneyu` / `ks_2samp` / `ranksums` between asymmetric categories (NS vs SN)
  to test directional selection asymmetry, and defines the "empirical shadow penalty"
  `Δw_shadow = 1.0 - median(w_SN)`. Outputs: `de_overlap_dms_summary.csv`,
  `ba_overlap_dms_summary.csv`, `hyphaeon_overlap_calibration_results.csv`,
  `results/07_overlapping_frames/shadow_effect_calibration.json`.
- Key reported numbers: Gene D/E Mann-Whitney P=1.15e-42 (asymmetry ratio 4.01), Gene B/A
  P=5.96e-7 (ratio 1.50); shadow penalty severe in replicase gpA (Δw=0.359), near-zero in lysis
  gpE (Δw=0.051).

### Stage I — "ChronAeon Multi-Scale SRA Sieve" (`run_chronaeon_phix174_sieve.py`)
- **[CONTEXT]** This is the most structurally important script for a Galaxy workflow translation:
  it is a literal multi-phase pipeline script, explicitly implementing spec doc
  `SPEC-CHRONAEON-HYPHAEON-SRA-03` referenced in `CHRONAEON_HYPHAEON_PHIX174_REANALYSIS_REPORT.md`.
  "ChronAeon" itself does not appear to be a separate installed tool — it is this orchestration
  script's name for a *sequence of real HyphAeon CLI subcommands* plus custom pandas/numpy glue:
  - **Phase 0 (ingestion)**: aggregate per-gene `msa/phiX174_{gene}.summary.json` files (produced
    by Stage C) into `results/00_ingestion/lexicmap_9genes_ingestion_manifest.csv`; build a
    representative cross-scale FASTA+metadata dataset from Gene G haplotypes
    (`msa/phiX174_G.haplotypes.tsv`), partitioning by `mean_pident`/`coverage_pct` into
    reference/divergent-microvirus/etc. "layers."
  - **Phase 1 (`hyphaeon autoclock`)**: CLI call with flags `-a <clean_contigs.fasta>
    -d <clean_metadata.csv> --date-col collection_date --strain-col sequence_id
    --manifold tn93 -H --max-depth 3 --min-leaf-size 20 --min-delta-aicc 15.0
    --n-landmarks auto --max-memory-mb 2048 --output-dir <dir> -o <summary.json>
    -c <classified_metadata.csv>` — a hierarchical, TN93-distance-manifold, spectral/AICc-based
    clustering of taxa into "communities" and "outliers" (no BEAST, no MCMC — closed-form). Output
    JSON schema includes `tmrca`, `rate`, `r2`, `optimal_k`, `delta_aicc`, per-node
    `classification` (e.g. "Chronic / Endemic Reservoir", "Contemporaneous Transmission Dyad").
    Downstream: outlier sequences exported as `quarantined_layer1_outliers.fasta`; each leaf
    community exported as `community_{id}.fasta`.
  - **Phase 2 (Layer 1 quasispecies)**: pure pandas/numpy — computes a "structural potential
    deviation" `delta_phi = -1.2 * |residual|` from the autoclock output, classifies
    "Transient_Deleterious_Unpurged" vs "Permissive_Drift"; re-emits the Gene-E `am3` audit JSON;
    computes per-gene singleton-haplotype fractions from the haplotype TSVs.
  - **Phase 3 (`hyphaeon r0`)**: CLI call `-a <community.fasta> -g <classified_metadata.csv>
    --date-col date --strain-col id --generation-time 0.0174 --generation-sd 0.005 --units days
    -o <r0_summary.json> -c <epoch_skyline_rt.csv>` — closed-form (profile-likelihood, "<5 ms",
    explicitly not BEAST) transmission/phylodynamic R0 and growth-rate estimation. Also
    cross-correlates the Idaho-2024 real-time selection rates (Stage E output) against DMS
    fitness (Spearman/Pearson) and re-emits `idaho2024_realtime_purging_kinetics.csv` and
    `dickins2009_chemostat_trajectories.csv`.
  - **Phase 4 (`hyphaeon meme`)**: CLI call `-a <layer3_speciation_alignment.fasta> --use-tn93
    --attribute --attribution-min-lrt 3.84 -o <meme_attributed.json> -c <meme_sites.csv>` — a
    HyPhy-MEME-like episodic diversifying-selection scan reimplemented in closed form over a
    continuous TN93 distance geometry (explicitly avoids classical codon ML models / HyPhy /
    PAML), followed by a from-scratch **Aggregated Cauchy Association Test (ACAT)** omnibus
    p-value combination (`T = (1/L) Σ tan[(0.5-p_i)π]`) over per-site p-values.
  - **Phase 5+ (`hyphaeon filter`)**: a further CLI subcommand (seen invoked but not read in
    detail) used later in the same script.
  - All phase outputs land under `results/0{0-8}_*/` (see repo layout in Section 4), which are
    exactly the files cited as `Data Dependencies` throughout `sections/*.md`.
- **Important for tool-selection**: because `hyphaeon` subcommands (`autoclock`, `r0`, `meme`,
  `filter`) are a real external CLI with a nontrivial flag surface, any Galaxy wrapper for this
  stage should wrap the **actual `hyphaeon` CLI**, not re-implement its algorithms — but note this
  tool's availability/license/Tool-Shed status is unverified from this repo alone (see Gaps).
- **Reproducibility caveat (important, confirmed by direct script inspection):** not every phase
  in `run_chronaeon_phix174_sieve.py` is a genuine re-executable computation. Phase 0's synthetic
  multi-layer Gene-G FASTA is built with **fabricated, hash-derived pseudo-`collection_date`
  values**, not real SRA/BioSample metadata — any Galaxy reimplementation must source real dates
  or explicitly mark this as a synthetic-metadata demo step, not a data-driven one. Several other
  intermediate statistics that read as "computed" (e.g., the Gene D/E and Gene B/A Mann-Whitney
  medians and p-values cited in Stage H, and a per-gene VEP correlation table) appear as
  **hardcoded constants written directly into the script**, not values recomputed from input data
  at run time. Only Phases 1, 3, and 4 (the `autoclock`, `r0`, and `meme` CLI calls) are confirmed
  genuine, re-executable tool invocations; Phases 2, 6, 7, 8 are largely reporting/munging of
  numbers computed elsewhere (or baked in). A Galaxy translation should treat this whole script as
  an orchestration sketch to be decomposed into real steps, not ported verbatim.

### Stage J — Fane-mechanics and Bull/Wichman literature cross-referencing (pure pandas, no external tool)
- `synthesize_fane_mechanics.py`: joins a curated JSON bibliography (`fane_phage_abstracts.json`,
  61 papers; `fane_ba_papers.json`, 69 papers) against specific DMS table slices by gene/position
  (e.g., Gene D position 61 for the "Gly61 conformational hinge", Gene A domains 1–172 vs
  173–393 vs 394–512 for "A/A* packaging fidelity domain", using `mannwhitneyu` for domain
  contrasts).
- `generate_overlap_trajectory_analysis.py`: the most integrative custom analysis script — combines
  DMS overlap categories (D/E, B/A), Dickins 2009 trajectory positions
  (`G319T,A323G,C324T,A345G,G562T,G570T,G624T,G645T,C656A,...`), and Fane genetics into one
  synthesis, producing `de_overlap_dms_summary.csv` / `ba_overlap_dms_summary.csv` and (per its
  imports) matplotlib/seaborn figures.
- These stages are pure statistics/reporting over already-computed DMS+alignment tables; no
  bioinformatics CLI is shelled out to here.

### Stage K — Figure generation and manuscript QA (project tooling, not science tools)
- `scripts/generate_paper_figures.py`, `generate_comprehensive_figures.py`: matplotlib/seaborn,
  Okabe-Ito colorblind-safe palettes, publication PDF+PNG figure export
  (`paper/figures/fig1_sra_landscape.pdf`, `fig2_sra_spikein_curation.pdf`, etc.), using
  `scipy.stats.{spearmanr,pearsonr,mannwhitneyu}` for in-figure annotations.
- `scripts/generate_dashboard_data.py`: compiles all `results/` + `ref/phix174_proteins.faa` into
  JSON for an offline HTML dashboard (`dashboard/index.html`), not part of the scientific
  pipeline proper.
- `scripts/lint_manuscript_style.py`, `scripts/validate_references.py`,
  `manuscript-authoring-protocol/` (rules/scripts/templates + `PROTOCOL_SUMMARY.md`): a
  **deterministic prose-style linter and citation/DOI validator** enforcing an "anti-LLM
  cliché", specific-cadence writing style (see `scientific_writing.md`) and cross-checking
  citations against CrossRef/PubMed. This is purely an authoring-QA tool, **not relevant to the
  computational/scientific methods** and should be excluded from Galaxy-workflow scope.

## 3. Sample / reference data catalog (for test-data resolution phases)

| Dataset | Identifier(s) | Role | Location in repo |
|---|---|---|---|
| ΦX174 reference genome | RefSeq `NC_001422.1` (5,386 nt) | Universal alignment reference | `ref/NC_001422.1.fasta[.fai]` |
| ΦX174 proteome | 10 genes, `ref/phix174_proteins.faa` | Query panel for LexicMap/kmindex | `ref/`, `cds/*.fasta` |
| Logan SRA petabase index | kmindex: 109 DB shards; LexicMap: 25 domain indices | Universe being mined | external (usegalaxy.org-hosted Galaxy tools) |
| Idaho 2024 chemostat time series | BioProject `PRJNA1174868`, `SRP539859`; runs `SRR31059334`–`SRR31059340` | Real-time selection-rate validation | `data/sra_evolution/idaho2024/` (post-download) |
| Dickins & Nekrutenko 2009 | 10 samples A1-4/B1,3,4/C1,3,4; Galaxy library folder `F175d7d5ddeeb1d43` on usegalaxy.org | Classical chemostat sweep validation | `data/dickins2009/` (post-download); full text `dickins2009_pmc2817424.xml` |
| Wei, Li & Lehner 2026 DMS | bioRxiv 10.64898/2026.07.25.740675; N=39,335 variants / 16,098 SNVs | Ground-truth fitness surface for everything | **NOT present in repo** — expected at `phix174_WGM/data/...zip` |
| NCBI Virus complete genomes | 185 complete GenBank records | "91.8% derive from lab evolution" certification | `data/ncbi_virus_*` |
| Nominal-taxonomy SRA audit | TaxID `10847` / `2886930`; 18 BioProjects incl. `SRP042938`,`SRP008975`,`ERP002532`,`ERP000074`,`SRP001260`,`ERP001254`,`SRP347090`,`SRP653402`,`ERP001281`,`SRP066453`,`SRP059208`,`SRP082602`,`SRP009433`,`ERP000177`,`SRP003315`,`SRP363953`,`DRP008496` | Provenance certification / negative-control catalog | `paper/results_section1_sra_landscape.md`, Table 2 in the .tex |
| Fane genetics bibliography | 61–69 curated papers | Mechanistic cross-referencing | `fane_phage_abstracts.json`, `fane_ba_papers.json` |
| EVcouplings MSAs | author-supplied, from Figshare | HyphAeon input alignments | `msas/`, `msas_sub/` (350-taxa subsampled) |
| Structural references | PDB 1CD3 / 2BPA (cryo-EM coordinates) | Structural context for Fane mechanics, cited not computed on | none locally (citation only) |

## 4. `results/` directory shape (already-computed intermediate/output tables — useful as
   expected-output fixtures for a Galaxy test plan)

```
results/00_ingestion/            lexicmap_9genes_ingestion_manifest.csv, qc_clean_contigs.fasta, qc_clean_metadata.csv
results/01_autoclock_deconvolution/  autoclock_summary.json, hierarchical_summary.json, hierarchical_tree.json,
                                      classified_taxa_metadata.csv, contemporaneous_dyads.csv
results/02_layer1_quasispecies/   gene_e_am3_quarantine_audit.json, quasispecies_cloud.csv, purifying_selection_gradient.csv
results/03_layer2_transmission/   dickins2009_chemostat_trajectories.csv, idaho2024_realtime_purging_kinetics.csv, r0_phylodynamics_summary.json
results/04_layer3_speciation/     bull_wichman_adaptive_sites_benchmark.csv, hyphaeon_meme_attributed.json,
                                   hyphaeon_meme_sites.csv, layer3_speciation_alignment.fasta, neural_lineage_selection_drivers.csv
results/05_layer4_superfamily/    deep_structural_invariants.csv, structural_skeleton.fasta
results/06_dms_benchmarking/      proteome_vep_benchmark.csv
results/07_overlapping_frames/    ba_overlap_dms_summary.csv, de_overlap_dms_summary.csv, shadow_effect_calibration.json
results/08_fane_mechanics/        fane_mechanistic_landmarks.csv, gene_a_domain_dms_summary.csv, interface_kde_curves.csv
```
This numbered-layer structure (00 ingestion → 01 autoclock → 02 layer1 → 03 layer2 → 04 layer3 →
05 layer4 → 06 benchmarking → 07 overlaps → 08 Fane) is a strong hint for how to decompose the
eventual Galaxy workflow into stages/subworkflows.

## 5. Tool inventory — real/installable vs. custom/internal

**Real, externally installable tools/CLIs actually invoked in code:**
- `kmindex` (Galaxy Tool Shed: `iuc/kmindex/kmindex_query/0.6.1+galaxy4`) — k-mer containment search
- `LexicMap` (Galaxy Tool Shed: `iuc/lexicmap/lexicmap_search/0.9.0+galaxy1`) — sequence-to-graph streaming aligner
- `bowtie2` — short-read alignment (Idaho 2024, Dickins 2009)
- `samtools` (`sort`, `index`, `mpileup`) — BAM handling and pileup generation
- `FastTree` — maximum-likelihood nucleotide phylogeny (GTR model) on codon MSAs
- `logan-walker` (Rust binary, `nekrut/disassembler` project) — cDBG graph traversal / intra-host variant calling; conceptually plays the role of a reference-free variant caller / graph aligner
- `hyphaeon` — real CLI (`autoclock`, `r0`, `meme`, `filter` subcommands) + real Python package (`hyphaeon.inference`, `hyphaeon.disease`) — phylogenetic transformer VEP + closed-form phylodynamics/selection-scan toolkit (`github.com/veg/hyphaeon`)
- `hyphaeon_overlaps` — companion Python package for overlapping-ORF consequence classification (`nekrut/hyphaeon-overlaps[-cdx]`)
- `BioBlend` / Galaxy REST API — orchestration glue for all usegalaxy.org-hosted steps
- Standard Python scientific stack: `pandas`, `numpy`, `scipy.stats` (spearmanr, pearsonr, mannwhitneyu, ks_2samp, ranksums), `Biopython` (`SeqIO`, `Seq`, `CodonTable`), `torch`, `matplotlib`/`seaborn`
- Comparison-only VEP tools (scores consumed from pre-merged tables, not re-run here): GEMME, ProteoCast, ESCOTT, RSALOR, DDMut, ESM-2 (15B), ESM3 Open, Tranception-L, ESM_IF1, MIF_ST

**Custom/internal orchestration code (no separate installable tool exists — would need to be
Galaxy-wrapped as bespoke scripts, or reimplemented as native Galaxy steps):**
- `stream_lexicmap_msa.py` — multi-HSP coordinate tiling, codon QC, haplotype collapsing (the
  paper's key methodological contribution; likely the single most important custom "tool" to
  wrap for Galaxy, since it has no off-the-shelf equivalent)
- `run_chronaeon_phix174_sieve.py` — orchestration only ("ChronAeon" = a name for this script's
  phase sequence + the ACAT combination test, not a separate binary)
- Custom pileup parser embedded in `analyze_idaho_evolution.py` / `call_dickins_trajectories.py`
  (hand-rolled samtools-mpileup string parser — could likely be replaced by a standard VCF
  caller such as `bcftools mpileup`/`lofreq`/`varscan` in a Galaxy-native reimplementation)
- `create_targeted_diversity_cohorts.py`, `synthesize_fane_mechanics.py`,
  `generate_overlap_trajectory_analysis.py`, `calibrate_hyphaeon_shadow_effect.py` — bespoke
  pandas/scipy statistics scripts with no external tool dependency beyond the DMS table

**Names that are NOT separate tools** (flagging per task instructions): "ChronAeon" is a
project/spec-document name for an orchestration pattern (a fixed sequence of `hyphaeon` CLI
calls + a custom ACAT step), not an importable package or binary distinct from `hyphaeon`
itself. "Fane mechanics" / "Fane morphogenesis" refers to the body of work by virologist
Bentley A. Fane (cited literature), not a tool. "AM3 sieve" / "am3 quarantine" refers to the
biological `am3` mutant + the QC filtering logic inside `stream_lexicmap_msa.py`, not a separate
program.

## 6. Key literature / reference data anchors (for citation/README generation downstream)
- Sanger et al. 1977, *Nature* 265:687-695 (doi:10.1038/265687a0) — first DNA genome, `am3` strain origin
- Bull et al. 1997, *Genetics* 147:1497-1507 — thermal adaptation, parallel convergence
- Wichman et al. 1999, *Science* 285:422-424 — parallel evolutionary trajectories
- Dickins & Nekrutenko 2009, *Genome Biol. Evol.* 1:294-307 (doi:10.1093/gbe/evp029) — chemostat trajectories
- Wei, Li & Lehner 2026, bioRxiv doi:10.64898/2026.07.25.740675 — whole-genome/proteome DMS ground truth
- Fane & Hayashi 1991; Chen/Uchiyama/Fane 2007; Cherwa/Uchiyama/Fane 2008 (PMID 18400861); Cherwa et al. 2011; Hafenstein & Fane 2002; Roznowski et al. 2020 (PMID 31666371) — morphogenetic/structural genetics
- Lin et al. 2023, *Science* 379:1123-1130 — ESM-2 protein language model
- Mitra et al. 2015; Kozich et al. 2013 — Illumina PhiX spike-in practice, cited for the 0.5–5% spike-in-concentration claim
- Full BibTeX: `paper/references_canonical.bib`

## 7. Assumptions and open gaps (carried forward per skill protocol)

1. **draft_manuscript.tex is materially narrower than the full project.** Treated the .tex file
   as authoritative for "what the paper claims" and everything else as context/rationale, per
   explicit task instruction. A later phase should confirm whether the Galaxy workflow target is
   scoped to *only* the SRA-landscape/spike-in pipeline (Stages A–D, D2) actually in the current
   .tex, or the full multi-stage project (through HyphAeon/Fane synthesis) implied by
   HANDOVER.md/sections. This summary documents both but does not resolve the scoping question.
2. **The Wei et al. 2026 DMS dataset is a hard external dependency not present in this repo**
   (`phix174_WGM/...zip`, expected at a path that doesn't exist locally). Any reproducible
   workflow needs this sourced from the paper's data-availability statement / bioRxiv supplement.
3. **HyphAeon's installability/licensing/Tool-Shed status is unverified.** Confirmed it's a real
   CLI+library (`github.com/veg/hyphaeon` per citations) invoked via subprocess/import, but this
   summary could not check whether it's conda/pip-installable or Tool-Shed-wrapped already —
   important for the Galaxy tool-discovery phase.
4. **The host/biome/platform metadata stratification of the 2.1M-accession union set** (Figure 1B/C
   numbers in the paper) has no corresponding script among the root-level `.py` files found;
   likely produced via ad hoc NCBI Entrez/SRA-metadata queries or manual curation not captured in
   this repo snapshot. Flagged as a reproducibility gap rather than invented.
5. Several absolute paths are hardcoded to the original author's machine (`/home/anton/...`,
   `/Users/anton/...`, `/Users/sergei/...`, `/tmp/gxy.txt` API key) — treat all such paths as
   illustrative/non-portable; a Galaxy workflow would need these parameterized as inputs/config.
6. `manuscript-authoring-protocol/` was checked and confirmed to be purely about prose style/
   citation-hygiene tooling (per instructions), not science methods — excluded from the pipeline
   description above.
7. `run_chronaeon_phix174_sieve.py` (Stage I) mixes genuine tool calls (Phases 1/3/4, real
   `hyphaeon` CLI invocations) with a synthetic-metadata demo step (Phase 0's fabricated
   pseudo-dates) and several hardcoded/pre-baked statistics in the later phases. Treat this script
   as evidence of *intended* pipeline shape, not as a script to port verbatim into Galaxy steps —
   flagged so a later phase does not mistake baked-in constants for a computation to reproduce.
8. Only two stages are confirmed to already run as installed Galaxy Tool Shed tools today
   (`kmindex_query` 0.6.1+galaxy4, `lexicmap_search` 0.9.0+galaxy1, both via BioBlend against
   usegalaxy.org). Everything else in the pipeline (multi-HSP tiling/QC, disassembler/logan-walker,
   mpileup trajectory calling, HyphAeon, hyphaeon_overlaps, FastTree, ChronAeon orchestration) is
   currently ad hoc local/BioBlend scripting and will need new Galaxy tool wrappers or reimplementation
   as native Galaxy steps.

## 8. Foundry feedback

No feedback ledger entry was appended for this run. Rationale: nothing encountered during this
extraction pointed at a defect, gap, or self-contradiction in the `summarize-paper` skill bundle
itself (its SKILL.md and `_feedback.md` protocol were both clear and sufficient to complete this
task). The difficulties encountered — a narrower-than-expected primary paper, an external dataset
missing from the repo, an unscripted metadata-stratification step — are properties of this
specific project's source material, not of the Foundry skill asset, so per the ledger's own
scope rule ("does not record unmet requirements in the workflow being built") they do not
qualify as ledger entries; they are instead recorded above in Section 7 as assumptions/gaps for
the next pipeline phase to consume.
