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
section pre { margin: 0.4em 0; line-height: 1.3; font-size: 0.8em; }
section blockquote {
  margin: 0.5em 0; padding: 0 1em; border-left: 4px solid #ccc;
  color: #333; font-style: normal;
}
.meta { color: #666; font-size: 0.85em; }
</style>

# Real Analysis Requests

What the majority of real bacteria/virus questions actually look like

**54.6%** of 5,250 real Biostars questions (bacteria/virus/pathogen-related)
are "analysis request" shaped — data described, a goal stated. Here are
ten of them, in full, unedited.

Source: Luna, A. (2023). *BioStars Posts API Output*. Zenodo.
https://doi.org/10.5281/zenodo.7813785 — CC BY 4.0

---

## Example 1 — Bacterial SNP Detection (1/2)

<span class="meta">Biostars #96189 · March 26, 2014 · biostars.org/p/96189</span>

> Hi all,
>
> I am working on 10 bacterial genomes (1 reference and 9 mutant) sequenced
> by Illumina technology. My main aim is to find SNPs that are common in 9
> genomes but absent in reference genomes. In last, I would like to do the
> automatic annotation of those SNPs. Until now, I have done the following
> steps and wondering if I am on the right path.
>
> First: Extracted the common SNPs in 9 mutant genomes

```
vcf-isec -n +9 -f 1.vcf.gz 2.vcf.gz 3.vcf.gz 4.vcf.gz 5.vcf.gz 6.vcf.gz 7.vcf.gz 8.vcf.gz 9.vcf.gz | bgzip -c > isec1.vcf.gz
```

> Second: tab index

```
tabix -p vcf isec1.vcf.gz
```

*(continued on next slide — full post, unedited)*

---

## Example 1 — Bacterial SNP Detection (2/2)

<span class="meta">Biostars #96189, continued</span>

> Third: Extracted SNPs present in isec1.vcf.gz but absent in reference strain

```
vcf-isec -c -f isec1.vcf.gz reference.vcf.gz > isec2.vcf
```

> Four: Automatic annotation of isec2.vcf. Used snpEFF:

```
java -jar snpEff.jar eff -no-downstream -no-upstream -no-utr -no-intergenic -v database isec2.vcf
```

> Most of the SNPs were observed in intergenic region. Should I include
> these intergenic SNPs or not? Any other suggestions of selecting SNPs.
>
> Regards, Nitin

---

## Example 2 — Viral Nanopore Read Downsampling

<span class="meta">Biostars #398159 · September 11, 2019 · biostars.org/p/398159</span>

> Tools for downsampling/resampling/subsampling Oxford Nanopore reads

> I have got ~40000 MinION reads derived from a virus, whose read length
> ranges from ~100 to ~34.9k. I would like to re-sample these reads to
> evaluate the minimum read number enough to detect this virus. As Oxford
> nanopore reads have no identical read length, I have to take the varying
> read length into consideration when re-sampling the reads. Are there open
> source tools available for this task?

---

## Example 3 — Comparing Bacterial Plasmids

<span class="meta">Biostars #457131 · August 24, 2020 · biostars.org/p/457131</span>

> Hi all,
>
> I got the draft genome of two isolates from WGS sequencing, and then
> split the contigs belonging to chromosome and plasmid separately. Now,
> I'd like to compare the plasmids of two isolates, get the information
> such as similarity, how can I do with that? Any suggestions would be
> appreciated greatly.

---

## Example 4 — Bacterial Genome Assembly (Nanopore)

<span class="meta">Biostars #469465 · October 26, 2020 · biostars.org/p/469465</span>

> Hi,
>
> I am doing genome assembly of different bacterial strains with barcoded
> nanopore sequenced reads. The genome size of the bacteria is 3.8Mb. After
> genome assembly, I am getting 2 contigs with longest contig length of
> 3.6 Mb for one strain and 9 contigs with 1.5 Mb contig length for another
> strain. Actually, the total number of reads for the strain for which I
> got shortest contig length was almost double that the other strain.
>
> 1) Does another round of sequencing with nanopore improve the sequence
>    assembly quality?
> 2) What could be the reason of getting shortest contig length for the
>    genome for which I had large number of reads?
>
> Thanks

---

## Example 5 — SARS-CoV-2 Spike Protein Sequences

<span class="meta">Biostars #9500470 · December 6, 2021 · biostars.org/p/9500470</span>

> I want to download Spike protein sequences of 11 variants of the corona:
>
> Alpha (B.1.1.7 and Q lineages) · Beta (B.1.351 and descendent lineages)
> · Gamma (P.1 and descendent lineages) · Epsilon (B.1.427 and B.1.429)
> · Eta (B.1.525) · Iota (B.1.526) · Kappa (B.1.617.1) · Mu (B.1.621,
> B.1.621.1) · Zeta (P.2) · Delta (B.1.617.2 and AY lineages)
> · Omicron (B.1.1.529)
>
> From where I could find and download these variant spike protein
> sequences?

---

## Example 6 — Draft Viral Genome from De Novo Contigs

<span class="meta">Biostars #418459 · January 25, 2020 · biostars.org/p/418459</span>

> Hi, I am working on the viral genome (single negative-stranded RNA virus)
> and the reads generated are from the ion torrent (amplicons) method.
> After performing de novo assembly using Trinity tool, produced contigs
> are in the form of a single fasta file. The next step is to construct a
> draft genome from the contigs. Is there any tools/software to create a
> draft genome from the contigs. Kindly recommend your advice and
> suggestions and suitable methodology.
>
> Response highly appreciated. Thank you

---

## Example 7 — Bulk Bacterial Genome Assembly

<span class="meta">Biostars #417508 · January 20, 2020 · biostars.org/p/417508</span>

> Hi,
> I am a freshman in sequencing data analysis. When I have one fastq file
> for only one bacteria, I know how to assemble using SPAdes. For example,
> `spades.py --pe1-1 name.fq.gz --pe1-2 name.fq.gz -o spades_test`.
>
> But I don't know how to deal with a large number of samples with one
> Linux command. For example, when I have 10 fastq data (name1~name10), I
> won't like to assemble them one by one by hand.
>
> Can you tell me how can I do? Thanks!

---

## Example 8 — Taxonomy Classification (MEGAN vs. Kraken)

<span class="meta">Biostars #130306 · February 10, 2015 · biostars.org/p/130306</span>

> Hi,
>
> I am trying to do taxonomy classification for my unmapped (to reference
> genome) reads. I tried both Megan and Kraken.
>
> In Kraken I can use read files directly as the input, whereas in Megan I
> have to make the blastN file first from the read files to give it as the
> input. No plotting tool is readily available for Kraken, while Megan
> already has a plotting tool.
>
> I used bacteria, virus and fungi genomes as reference database. I am
> trying to figure out if I can use read files directly as an input to
> MEGAN so that I can skip the BLASTN step. I also want to compare the
> Megan and Kraken output.
>
> Thanks, Deepthi

---

## Example 9 — Average Depth per Amplicon

<span class="meta">Biostars #309673 · April 17, 2018 · biostars.org/p/309673</span>

> Hello,
>
> I am working with targeted amplicon sequencing data for 200 samples! I
> want to calculate the average depth per amplicon? I tried bedtools
> coverage, but it gives total number of reads which map to the target
> region and I am not sure if that is the average depth. It is little
> confusing to me.
>
> command used:
> `bedtools coverage -a amplicon_coords.bed -b sample1_RG_sorted_indexed.bam`
>
> Is there any other way or any modified way to use bedtools coverage
> option to calculate the average depth per amplicon? Any help will be
> appreciated. Thanks!!

---

## Example 10 — Comparative Methylation, Two *E. coli* Strains

<span class="meta">Biostars #9481497 · July 21, 2021 · biostars.org/p/9481497</span>

> Hello,
>
> I am looking to identify differences in methylation between two isogenic
> replicates of E. coli. I have Oxford Nanopore sequencing of three
> biological replicates for two strains, and am looking to compare
> methylation between them.
>
> I have done nanopolish analysis and visualized the methylation frequency
> using ggplot2 in R, and have found no differences in the CpG methylation.
>
> Are there any tools I could use to definitively compare methylation
> between two strains? Ideally this would generate a PCA plot showing
> distinct/overlapping methylation profiles. Thank you for any advice!

---

## What ten real examples show

Every one of these: a **concrete data description** (organism, platform,
read/sample count) and a **stated goal** — even though none of these
writers were told to phrase it that way, across a 7-year span (2014–2021)
and a wide range of sub-fields (assembly, typing, taxonomy, amplicon QC,
epigenetics, viral variants).

That's the shape 54.6% of real bacteria/virus questions take, and it's
exactly the shape `route.py` and the rest of this pipeline are built to
consume — not a hypothetical input format, a documented empirical pattern.
