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
are "analysis request" shaped — data described, a goal stated. Here are two
of them, in full, unedited.

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

<br>

**Notice what both examples share:** a concrete data description (organism,
platform, read count/type) and a stated goal — even though neither writer
was told to phrase it that way. That's the shape 54.6% of real questions
take, and it's exactly the shape `route.py` and the rest of this pipeline
are built to consume.
