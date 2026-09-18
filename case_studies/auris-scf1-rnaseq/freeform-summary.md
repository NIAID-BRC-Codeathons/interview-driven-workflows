# Free-form source summary — Santana et al. 2023, *Science*: Scf1, a *Candida auris*-specific adhesin

## Source

- **Title:** A *Candida auris*-specific adhesin, Scf1, governs surface association, colonization, and virulence
- **Authors:** Santana DJ, Anku JAE, Zhao G, Zarnowski R, Johnson CJ, Hautau H, Visser ND, Ibrahim AS, Andes D, Nett JE, Singh S, O'Meara TR
- **Journal:** *Science* 381(6665):1461–1467, 29 September 2023
- **DOI:** 10.1126/science.adf8972 · **PMID:** 37769084 · **PMCID:** PMC11235122
- **What was read:** full main text (PMC JATS full-text XML) **and** the complete supplementary Materials and Methods (NIHMS2004453-supplement-2.pdf, 60 pp, including Tables S1–S5). The main text carries no Methods section; every computational detail below comes from the supplement.

## Workflow intent

The paper is a wet-lab genetics/cell-biology study. Its computational content is two small, self-contained, **short-read Illumina** analyses, both of which the authors state were run **on the Galaxy public server at usegalaxy.org**. That makes this paper an unusually direct Galaxy-workflow reconstruction target: the tool chain named in the Methods is already a Galaxy tool chain.

The two analyses are independent and have different shapes:

- **Pipeline A — bulk RNA-seq differential expression.** Identify genes dysregulated in a low-adhesion insertional mutant (`tnSWI1`) and in a naturally low-adhesion clinical isolate (AR0387), each versus the high-adhesion parent AR0382. This is what surfaced *SCF1* (B9J08_001458) as the top dysregulated ORF (Fig. 1D, Fig. S2, Fig. S5A).
- **Pipeline B — T-DNA insertion-site mapping from WGS.** Locate *Agrobacterium tumefaciens*-mediated transformation (AtMT) transgene integration sites in insertional mutants by soft-clip extraction: align reads to the T-DNA plasmid, pull the clipped genomic flanks, re-align those to the host genome.

Pipeline A is the better primary target (standard Galaxy tools end to end, 6 public paired-end runs, two clean contrasts). Pipeline B is fully specified in the Methods but has one non-Galaxy step (see Open questions).

---

## Pipeline A — RNA-seq differential expression

### Steps, tools, parameters (all as stated in the supplement)

| # | Step | Tool named in paper | Parameters stated |
|---|------|--------------------|-------------------|
| 1 | Read QC | **FastQC** | none stated ("read quality was assessed") |
| 2 | Quality trimming | **Cutadapt** | "Phred cutoff score of 20"; no adapter sequence given |
| 3 | Splice-aware alignment | **RNA STAR** | "default parameters" |
| 4 | Feature quantification | **featureCounts** | none stated |
| 5 | Differential expression | **DESeq2** | none stated |
| 6 | Significance filter | (DESeq2 output filter) | \|fold change\| > 2 **and** adjusted p-value < 0.05 |

Platform: "Galaxy web platform public server at usegalaxy.org". No tool versions are given for any of the six steps.

### Library / sequencing facts

- Sequencing by SeqCenter (Pittsburgh, PA).
- Library prep: Illumina **Stranded Total RNA Prep with Ribo-Zero Plus**, 10 bp IDT for Illumina indices. *Stranded* — the strandedness setting matters for featureCounts and is not spelled out beyond the kit name.
- Instrument: **NextSeq 2000**, **2 × 50 bp paired-end**.
- Input material: RNA from cells grown to mid-exponential phase in YPD at 30 °C (formamide extraction, RNeasy cleanup, DNase-treated).

### Reference data

- **Genome:** *C. auris* **B8441**, NCBI assembly **GCA_002759435.2** (`Cand_auris_B8441_V2`). Same assembly is used as the reference throughout the paper (also for primer design and for Pipeline B).
- **Annotation:** not stated. featureCounts requires a GTF/GFF; the paper never names one. FungiDB and the Candida Gene Order Browser (CGOB) are cited, but only for synteny inspection of the *SCF1* locus, not as the counting annotation.

### Sample data (public, resolvable — strong test-data leads)

**BioProject PRJNA904261** (SRA study SRP409192), RNA-Seq, TRANSCRIPTOMIC, RANDOM selection, PAIRED, Illumina NextSeq 2000, submitted by University of Michigan. Six runs, 2 biological replicates × 3 conditions, ~22–30 M spots each (~2.2–3.0 Gbp per run):

| Run | Experiment | Sample | Condition |
|-----|-----------|--------|-----------|
| SRR22376032 | SRX18346538 | AR0382_A | parent AR0382 (clade I, high adhesion), rep A |
| SRR22376031 | SRX18346539 | AR0382_B | parent AR0382, rep B |
| SRR22376030 | SRX18346540 | AR0387_A | AR0387 (clade I, low adhesion), rep A |
| SRR22376029 | SRX18346541 | AR0387_B | AR0387, rep B |
| SRR22376028 | SRX18346542 | AR0382_tnSWI1_A | AR0382 tnSWI1 (B9J08_003460) insertional mutant, rep A |
| SRR22376027 | SRX18346543 | AR0382_tnSWI1_B | AR0382 tnSWI1, rep B |

Taxon 498019 (*Candidozyma auris*, formerly *Candida auris*). BioSamples SAMN31835905–SAMN31835910.

### Contrasts and expected biological result (useful as workflow assertions)

- **tnSWI1 vs AR0382:** *SCF1* (B9J08_001458) is the strongest and most significantly dysregulated gene (down). No significant dysregulation of the ALS or IFF/HYR adhesin families.
- **AR0387 vs AR0382:** *SCF1* is the most down-regulated gene; ~29-fold expression difference between the two wild-type isolates. Little transcriptome overlap with tnSWI1.
- A third comparison, tnBCY1 (B9J08_002818) vs AR0382 (Fig. S2), is described in the text — *SCF1* strongly down, *IFF4109* not — but **no tnBCY1 runs exist in PRJNA904261**. Only three conditions were deposited.
- Background fact usable as a sanity check: *SCF1* expression in AR0382 sits in the top 2.5% of all genes.

---

## Pipeline B — AtMT T-DNA insertion-site mapping (WGS)

### Steps, tools, parameters

| # | Step | Tool named in paper | Parameters stated |
|---|------|--------------------|-------------------|
| 1 | Read QC | **FastQC** | none stated |
| 2 | Quality trimming | **Trimmomatic** | "Phred quality cutoff of 20"; trimming mode (SLIDINGWINDOW / TRAILING / LEADING) not stated |
| 3 | Align to T-DNA plasmid | **BWA-MEM** | reference = *linearized* pTO128 (pPZP-NAT); **minimum seed length = 50**, **band width = 2** |
| 4 | Extract soft-clipped flanks | **`extractSoftClipped` from SE-MEI** (https://github.com/dpryan79/SE-MEI) | none stated; operates on the aligned BAM |
| 5 | Align flanks to host genome | **BWA-MEM** | **default configuration**; reference = *C. auris* B8441, GCA_002759435.2 |
| 6 | Confirmation | Sanger sequencing of each locus | wet-lab, out of workflow scope |

Platform: also stated as run on usegalaxy.org (the Galaxy statement covers the sequencing-data analysis in this section).

The unusual parameters in step 3 (seed 50, band width 2) are deliberate: they force long exact matches to the T-DNA and suppress gapped extension, so the read portion that is host genomic DNA stays soft-clipped rather than being forced into the plasmid alignment. Any reimplementation must preserve them.

### Library / sequencing facts

- Sequencing by SeqCenter; library prep based on the **Illumina Nextera** kit.
- Instrument: **NextSeq 550**, **2 × 150 bp paired-end**.
- Input: genomic DNA (PCA extraction) from AtMT mutants of interest.

### Sample data

**BioProject PRJNA904262** (SRA study SRP409193), WGS, GENOMIC, RANDOM, PAIRED, Illumina NextSeq 550. Two runs — these are **pools**, not single mutants:

| Run | Experiment | Sample | Spots | Avg length |
|-----|-----------|--------|-------|-----------|
| SRR22376034 | SRX18346544 | Pool_A | 16,373,182 | 294 (2 × ~147) |
| SRR22376033 | SRX18346545 | Pool_B | 19,413,010 | 293 (2 × ~147) |

BioSamples SAMN31836173–SAMN31836174.

### Reference data

- **Host genome:** same, GCA_002759435.2 (B8441).
- **T-DNA plasmid:** pTO128 (pPZP-NAT), carried by *A. tumefaciens* EHA105 strain `At pTO131`. Cited to reference (52) (the prior AtMT method paper), **not** to a public accession. The linearized sequence is a required input with no resolvable public URL found in the paper.

---

## Other computational / analytical methods in the paper (not sequencing workflows)

Recorded for completeness; none of these are plausible Galaxy workflow steps, and none are the workflow this pipeline should build.

- **Homology search:** BLAST of full-length Scf1 and of its N-terminal domain, E-value cutoff 0.05; hits limited to low-complexity repeats discarded. Reciprocal cross-BLAST of Scf1 vs *S. cerevisiae* and Flo11 vs *C. auris* (no significant homology at E ≤ 0.05).
- **Domain annotation:** UniProt automatic annotations (Scf1 = UniProt **A0A2H1A319**, N-terminal domain length 228 aa, 7.9% Arg, 14.5% Arg+Lys — Table S2).
- **Synteny:** FungiDB and Candida Gene Order Browser (CGOB) annotations for the *SCF1* locus.
- **Structure prediction:** **AlphaFold2 via ColabFold** on the N-terminal domain; **Foldseek** structure search (returned Fibronectin-III-fold proteins across domains of life, including FLO11 homologs).
- **Allelic comparison (Table S1):** Scf1 N-terminal domain % identity and tandem-repeat counts across clade representatives B8441 (I, reference), B11220 (II), B11221 (III), B11243 (IV), IFRC2087 (V), and *C. haemulonii* B11899 (60.9% NT identity). No variant-calling method is described for this table.
- **Primer design:** NCBI Primer-BLAST against GCA_002759435.2 (*C. auris*) or GCA_002926055.1 (*C. haemulonii* B11899).
- **Image analysis:** Fiji/ImageJ **1.52** custom macro (brightfield edge-detection segmentation → binary mask) → **CellProfiler 3.1.9** cell counting; z-factor assay QC (mean 0.7167, acceptance 0.5 < z < 1.0), mutant hit calling at z-score < −3 across 2,560 arrayed insertional mutants.
- **Flow cytometry analysis:** FlowJo v10.8.2; plate-reader analysis in Gen5 3.12.
- **Statistics:** R **4.0.3**, DescTools **0.99.49** (ANOVA), survminer **0.4.9** (survival). Student's t-test; one-way ANOVA with Tukey's or Dunnett's post hoc; Pearson correlation; Mantel–Haenszel log-rank with Benjamini–Hochberg correction for survival. Source data provided as Data S1 (`NIHMS2004453-supplement-Data_1_Source_Data.xlsx`).

## Strains and other identifiers worth carrying forward

- Key genes: **SCF1 = B9J08_001458** (the paper's discovery), **IFF4109 = B9J08_004109**, **SWI1 = B9J08_003460**, **BCY1 = B9J08_002818**, **ALS4112 = B9J08_004112**, **IFF4892 = B9J08_004892**. *C. haemulonii* SCF1 homolog = **CXQ85_003100**. AR0381 SCF1 allele = **CJI96_0001187**.
- Twelve ALS/IFF-HYR adhesin deletions in AR0382: B9J08_002582, _004498, _004112 (ALS); _004100, _004109, _004098, _004110, _001531, _004892, _001155, _004451, _000675 (IFF/HYR).
- Isolates: AR0382 (= B11109, clade I, high adhesion), AR0387 (= B8441, clade I, low adhesion — the reference-assembly strain), AR0381 (= B11220, clade II, low adhesion), plus AR0383–AR0390, AR0931, AR0932, AR1097, AR1099–AR1105, Chicago-1..4 from the CDC/FDA Antibiotic Resistant Isolate Bank. 19 *C. albicans* isolates from ATCC; *C. haemulonii* AR0395 (B10441).

## Assumptions carried forward

1. **The Galaxy-relevant workflow is Pipeline A (RNA-seq DE), with Pipeline B as a second candidate.** The paper contains no other analysis that consumes sequencing reads. Everything else is wet-lab or desktop software.
2. **The DESeq2 design is a simple one-factor, three-level condition model** (AR0382 / AR0387 / tnSWI1) with n = 2, yielding two pairwise contrasts against AR0382. The paper states the contrasts and the significance thresholds but never writes out a design formula; n = 2 is inferred from the six deposited runs, not stated in the Methods.
3. **Strandedness:** the Ribo-Zero Plus *Stranded* Total RNA kit is reverse-stranded (dUTP) in Illumina's standard chemistry, so featureCounts would run reverse-stranded. The paper does not say this; it is inferred from the kit name.
4. **The B8441 reference is used for RNA-seq alignment even for AR0382/AR0387 samples**, i.e. reads from a different clade-I isolate are mapped to the B8441 assembly. This is what the Methods say; it is not a transcription error.
5. **"Cutadapt with a Phred cutoff score of 20"** is read as quality trimming (`-q 20`), not adapter trimming — no adapter sequence is given anywhere.
6. Tool versions for the Galaxy steps are unknowable from the paper; any Galaxy workflow built from this must pin its own versions and cannot claim to reproduce the authors' exact versions.

## Open questions

1. **featureCounts annotation is unspecified.** No GTF/GFF source is named for the B8441 assembly. A workflow must choose one (NCBI RefSeq GFF for GCA_002759435.2, or FungiDB's B8441 GFF) and that choice will shift gene IDs and counts. This is the single largest gap for reproducing Pipeline A.
2. **No tool versions for any Galaxy step** (FastQC, Cutadapt, RNA STAR, featureCounts, DESeq2, Trimmomatic, BWA-MEM). Only non-Galaxy software is versioned (R 4.0.3, DescTools 0.99.49, survminer 0.4.9, Fiji 1.52, CellProfiler 3.1.9, FlowJo 10.8.2, Gen5 3.12).
3. **Trimmomatic trimming mode is unstated** for Pipeline B — "Phred quality cutoff of 20" could be SLIDINGWINDOW, TRAILING, or AVGQUAL. Minimum-length filtering is likewise unstated for both pipelines.
4. **`extractSoftClipped` (SE-MEI) has no known Galaxy Tool Shed wrapper.** Pipeline B cannot be assembled from stock Galaxy tools as written. Either a wrapper must be authored, or the step must be substituted (e.g. samtools/awk soft-clip extraction, or a clip-aware structural-variant caller) — a substitution changes the method and should be flagged as such, not presented as a faithful port.
5. **The pTO128 (pPZP-NAT) plasmid sequence has no public accession in this paper.** Pipeline B's step-3 reference is unresolvable from the publication alone; it would have to come from the cited AtMT method paper (ref. 52), from Addgene, or by request. This is a hard test-data blocker for Pipeline B.
6. **PRJNA904262 contains two pooled samples, not per-mutant runs.** The Methods describe insertion-site identification "from mutants of interest", but the deposited data are `Pool_A` / `Pool_B`. How pools map to the individual mutants (tnSWI1, tnBCY1) — barcoding, demultiplexing, or post-hoc assignment — is not described. Any per-mutant claim from this data needs a step the paper does not document.
7. **No tnBCY1 RNA-seq runs are public** even though Fig. S2 reports its transcriptome. A workflow test that tries to reproduce Fig. S2 has no input data.
8. **Fig. 2D's cross-isolate SCF1 expression** (r = 0.87, p = 8.4 × 10⁻⁸, 23 isolates) cannot come from RNA-seq — only 3 conditions were sequenced. It is almost certainly the RT-qPCR assay (ACT1-normalized, primers oTO1251/oTO1252), but the supplement does not explicitly tie the figure to the method. Not a sequencing-workflow concern, but do not model it as one.
9. **No variant-calling pipeline is described** for the "206 coding SNPs between AR0382 and AR0387" claim or for Table S1's allelic comparison. If a downstream design brief wants comparative genomics, it is inventing a step this paper does not contain.
10. **Access note:** the Methods exist only in the supplementary PDF. The PMC full-text XML (retrievable via NCBI eutils `efetch db=pmc`) carries the main text but stops at "Supplementary Material"; the publisher page (science.org) returns 403 and the article is not in the Europe PMC open-access set. Anyone re-deriving this summary must fetch `NIHMS2004453-supplement-2.pdf` specifically.
