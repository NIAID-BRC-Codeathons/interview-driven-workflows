# Galaxy history `foundry-full-11gene-panel` vs. paper Table 1

**History:** `bbd44e69cb8906b54be4b938868d5a9d` (usegalaxy.org), invocation `8d8af9e4b30d11f18054bc24110164aa`, completed 2026-09-18T03:17Z.
**Paper target:** `paper/draft_manuscript.tex` Table `tab:ingestion`, whose values are reproduced verbatim from
`results/00_ingestion/lexicmap_9genes_ingestion_manifest.csv`.
**Galaxy result compared:** hid 440 `Column join on collection 427` (11-gene joined manifest; second, complete run).

## Verdict

**The workflow ran to completion, but it does not reproduce the paper.** The headline result — the
`gpE_W7*` am3 spike-in signature in 92.59% of Gene E accessions — is absent, and the per-gene
cohorts are not gene-specific. Two independent defects are responsible, one of scope and one of
correctness.

## 1. Scale / scope mismatch (~10x)

| Quantity (10 paper genes) | Paper | Galaxy | Ratio |
|---|---:|---:|---:|
| Streamed alignment rows | 26,836,801 | 23,462,672 | 1.1x |
| Evaluated accessions | 24,378,503 | 2,491,917 | 9.8x |
| Clean full-length CDS | 17,921,411 | 2,119,377 | 8.5x |
| Multi-HSP rescued | 1,060,472 | 134,073 | 7.9x |
| Clean unique haplotypes | 316,135 | 527,680 | 0.6x |

Causes, confirmed from job parameters:

- **kmindex**: the workflow queried a single database, `GENOMIC_PHG` (`db_opts.kmindex = "GENOMIC_PHG"`,
  threshold 0.3, z=6). The paper's run (`kmindex_runs.json`) used **`num_databases: 109`**. The Galaxy
  deduplicated accession union (hid 426) holds **36,411** accessions against the paper's
  **2,114,904** (`UNION.accessions.txt`) — 58x smaller.
- **LexicMap**: the search used the usegalaxy.org cached index **`Viral`** (`db_opts.lexicmap_index = "Viral"`),
  not the full Logan petabase index the paper describes.

Gene inputs themselves are correct: all 11 query FASTAs match the paper's coordinates and lengths
(A 1539, B 360, C 258, D 456, E 273, F 1281, G 525, H 984, J 114, K 168 bp), and Gene E is the
wild-type allele (codon 7 = `TGG`/Trp, no internal stops), as the paper requires.

## 2. Correctness defect: per-gene cohorts are cross-contaminated across all 11 genes

Every gene's cohort is dominated by **Gene A** sequence, truncated to that gene's reference length.
Reconstructing the rank-1 haplotype from each per-gene summary's `nt_muts` against its own reference:

| Gene | rank-1 count | freq | true identity of rank-1 haplotype |
|---|---:|---:|---|
| A | 42,229 | 0.307 | phiX174_A @0 (100%) |
| Astar | 54,946 | 0.265 | phiX174_A @0 (100%) |
| B | 73,148 | 0.323 | phiX174_A @0 (100%) |
| C | 72,377 | 0.314 | phiX174_A @0 (100%) |
| D | 70,218 | 0.313 | phiX174_A @0 (100%) |
| E | 72,170 | 0.328 | phiX174_A @0 (100%) |
| F | 48,391 | 0.269 | phiX174_A @0 (100%) |
| G | 67,469 | 0.303 | phiX174_A @0 (100%) |
| H | 56,113 | 0.268 | phiX174_A @0 (100%) |
| J | 79,402 | 0.334 | phiX174_A @0 (100%) |
| K | 73,465 | 0.318 | phiX174_A @0 (100%) |

The tell-tale internal contradiction: Gene E reports `pident` median 100.0 / mean 99.98 and coverage
median 1.0, yet its top haplotype carries ~200 substitutions across 273 bp. Each row is a genuine
near-perfect alignment — to the *wrong gene*.

### Root cause (two compounding bugs)

1. **Workflow wiring.** Each `lexicmap_search` job received the entire panel as 11 separate query
   inputs (`query1..query11` = hids 1-11), not one gene per mapped iteration. All 22 search jobs
   therefore produced results for all 11 genes — which is why several "different" per-gene outputs
   have byte-identical sizes (e.g. 3,432,262,189 for hids 319/320/322/324/325/326/327).
2. **`lexicmap_streamer` tool bug.** The row parser (`galaxy-user-tool.yml`, the `find_col`/row-loop
   block around lines 472-640) resolves `sgenome, pident, qcovHSP, qstart, qend, qseq, sseq` and
   **never reads LexicMap's `query` column**. It buffers every row by subject accession and merges
   all HSPs onto the single `--ref` reference, so it cannot tell which query gene a row came from.
   Gene A, being the longest and first query, wins the coordinate positions.

This is distinct from the already-fixed accession-grouping bug in `lexicmap_streamer_fix.diff`
(v1.0.1); that fix does not address query-gene filtering.

## 3. Downstream consequences in the reported numbers

| Gene | Flagged stops (paper / Galaxy) | Entropy bits | WT fraction |
|---|---|---|---|
| J | 63 / 2,972 | 0.384 / 4.517 | 0.968 / 0.332 |
| K | 314 / 3,909 | 0.553 / 6.101 | 0.957 / 0.047 |
| C | 434 / 4,425 | 0.868 / 7.933 | 0.935 / 6.5e-05 |
| **E** | **2,215,172 / 15,279** | 5.856 / 7.751 | 0.0016 / 0.0 |
| B | 248 / 11,924 | 1.047 / 8.809 | 0.928 / 0.0017 |
| D | 176 / 13,207 | 1.350 / 9.735 | 2.7e-05 / 0.0 |
| G | 192 / 13,679 | 1.645 / 10.441 | 0.885 / 5.8e-05 |
| H | 178 / 15,929 | 2.108 / 11.875 | 2.0e-06 / 0.0 |
| F | 468 / 16,437 | 2.538 / 11.860 | 1.0e-06 / 0.0 |
| A | 1,245 / 19,048 | 2.850 / 10.912 | 0.825 / 0.307 |

- **Gene E / am3 — not reproduced.** Paper: 2,215,172 of 2,392,457 evaluated accessions (92.59%)
  carry `gpE_W7*`, leaving 52,862 clean wild-type. Galaxy: 15,279 flagged stops (6.31%) and 219,905
  "clean full-length". The Gene E flagged audit (hid 439, 20,100 rows) shows stops at **codon 86**,
  not codon 7 — these are not am3. The paper's central biophysical claim has no counterpart here.
- **Entropy inflated ~4x** (0.38-2.85 → 4.5-11.9 bits) and **WT fractions collapsed**, both direct
  artifacts of pooling 11 genes into each cohort.
- **Flagged stops in non-E genes 25-70x too high** (63-1,245 → 2,972-19,048), again from
  out-of-frame foreign-gene sequence.
- **Multi-HSP rescue loses its signal.** The paper's rescue count rises monotonically with gene
  length (J 14,406 → A 280,027); the Galaxy numbers are flat and inverted (A lowest at 1,817),
  because every accession now carries HSPs from all 11 genes.

## 4. Other run notes

- The history contains **two** invocations. The first (hids 12-266) failed partway: 4 LexicMap jobs
  errored (hids 153-156) and 32 downstream datasets are `paused`, so only 7 of 11 genes produced
  manifest rows. The second (hids 267-440) completed all 11 genes; only it is compared above.
- The paper's Table 1 covers 10 genes; the Galaxy panel adds **A\*** (1,023 bp), which has no paper
  counterpart.

## What would be needed to reproduce

1. Fan the LexicMap step out so each mapped iteration searches **one** gene, or add a `query`-column
   filter to `lexicmap_streamer` so it selects only rows matching its `--ref` record id. The filter
   is the more robust fix and should be added regardless.
2. Point kmindex at the paper's 109 databases rather than `GENOMIC_PHG` alone.
3. Point LexicMap at the Logan index rather than the cached `Viral` index.

Items 2 and 3 are scope choices and may be constrained by what usegalaxy.org offers; item 1 is a
defect and invalidates the current per-gene outputs on its own.

---

# Fixes applied (2026-09-18)

## 1. `lexicmap_streamer` v1.0.1 -> v1.0.2 — query-column filter (`galaxy-user-tool.yml`)

Root cause was that the row parser resolved `sgenome, pident, qcovHSP, qstart, qend, qseq, sseq`
and never read `query`, so it merged every row in the table onto its single `--ref`. Fixed:

- Resolve `idx_query = find_col(["query", "qseqid", "qid", "query_id"])`, and add `query` to the
  required-column check.
- Skip rows whose `query` != `ref_name` (the first token of the reference FASTA header), counting
  them in `rows_skipped_other_query` and tallying every query seen in `queries_seen`.
- **Fail loudly** when the table has rows but none for this reference — that state means the
  reference and hit table do not correspond, and the old behaviour would have emitted empty
  cohorts indistinguishable downstream from a genuine "no hits" result. The error names the
  queries that *are* present.
- Report the kept/skipped split on stdout and add `rows_skipped_other_query` to the summary JSON.
- `total_streamed_rows` now counts rows for *this* reference. Help text and the
  `lexicmap_results` input description no longer claim contiguous per-accession ordering is
  required (v1.0.1 removed that constraint; the docs still asserted it).

### Verification

| Test | Result |
|---|---|
| Synthetic am3 fixture, ref=E | 1 clean WT + 1 flagged, stop at **codon 7** — unchanged from v1.0.1 |
| ref=J against E-only table | raises, naming `phiX174_E (2 rows)` as what is present |
| ref=E against real gene-A-only slice (56,312 rows) | raises — this is the input that previously produced the bogus Gene A haplotype |
| ref=A against the same real slice | **WT fraction 0.740, entropy 3.36 bits, flagged-stop rate 0.05%** |

That last row is the substantive check. The paper's Gene A is WT fraction 0.825, entropy 2.850,
flagged stops 1,245/2,339,733 = **0.05%**. The broken run gave 0.307, 10.91 bits and 7.8%. The
flagged-stop rate now matches the paper exactly; WT fraction and entropy are in the paper's regime
(exact agreement is not expected from a 260 MB slice of a 3.4 GB table).

### Fixture correction

`test-data/synthetic_am3/{E,J}.synthetic_lexicmap_hits.tsv` carried the bare gene letter (`E`,
`J`) in the `query` column. Real LexicMap output emits the query FASTA's full record id —
verified against usegalaxy.org dataset `f9cad7b01a472135002e818bf97f6039`, whose column 1 reads
`phiX174_A`. The fixtures now use `phiX174_E` / `phiX174_J`, matching `test-data/{E,J}.fasta`.
Corrected the fixture rather than loosening the filter to accept bare letters: a lenient match
would reopen exactly the class of bug being fixed.

## 2. Index selection (`galaxy-workflow.gxwf.yml`)

- `kmindex_db_selection` default was a **truncated placeholder** —
  `GENOMIC_BCT,...,...(109 Logan shard names, ALL_KMINDEX_DBS)` — not a usable value. Replaced
  with the literal 109 names, verified against the live option set for the pinned changeset
  (which offers exactly 109, matching `kmindex_runs.json`'s `num_databases: 109`).
- `lexicmap_index_selection` default was set to the 5-index `TARGETED_PHAGE_INDICES`.
  **This was wrong and is corrected below (section 6)** — the paper used all 25.
- Both docs now note that invocation `d0dbbcc823e2674f` overrode these defaults with single
  values. **The narrow scope came from the invocation, not the workflow.**
- `paper-scale-invocation-params.json` written with the full-scope values for a rerun.

## 3. Documentation corrections

- The `lexicmap_search` step doc claimed *"mapped over gene_query_panel — one query call per
  gene"*. It now records that `query` is `multiple: true`, so the list is **reduced** into one
  job, and that the 11 jobs come from the mapped parameter axes.
- Step docs were re-trimmed to stay under Galaxy's ~2048-char limit (2398 fails, 2048 passes per
  the feedback ledger). Longest is now 1,908.
- `planemo workflow_lint` reports **18 errors before and after** these edits — all pre-existing
  (test-job input coverage, ToolShed lookups, planemo's tool_id version parsing). No new issues.

## 4. Index-selection mechanism — verified live, and it changed the fix

The delimited-string modeling was **wrong**, and this was only discoverable by running it.

Both `db_opts|kmindex` and `db_opts|lexicmap_index` are `type: select, multiple: true`. Tested
against usegalaxy.org (history `bbd44e69cb8906b57012ea23efccb56e`):

| Value form | Result |
|---|---|
| `"GENOMIC_PHG,GENOMIC_VRL"` (comma-delimited string) | **REJECTED** — `Parameter 'kmindex': an invalid option ('GENOMIC_PHG,GENOMIC_VRL') was selected` |
| `["GENOMIC_PHG","GENOMIC_VRL"]` (JSON array) | **ACCEPTED** — job `bbd44e69cb8906b5eadd64618b449770` completed with 32 `GENOMIC_PHG` + 33 `GENOMIC_VRL` datasets |

A multi-select reads the whole delimited string as one option value. Since a gxformat2 `text`
workflow input cannot carry an array, the original design could never have worked — passing the
109-name string would have failed at parameter validation exactly as the two-name string did.

Consequently:

- `kmindex_db_selection` and `lexicmap_index_selection` were **removed** as workflow inputs.
- The 109 kmindex shard names and the LexicMap index list are now **literal lists in the
  step state** of `kmindex_containment_screen` and `lexicmap_search`.
- Ledger entry `kmindex-lexicmap-index-selection-mechanism` is marked **resolved** with this
  evidence.
- `galaxy-workflow.gxwf-tests.yml` no longer passes those job inputs; both were placeholders
  (`"register"`, `"db,db2"`, `"PhiX174E_J_Am3ToyIndex"`) that would have failed validation.

**Trade-off, stated plainly:** index sets are no longer settable at invocation time. Changing them
now means editing the workflow. That is the cost of the ports requiring arrays; the alternative
(a text input) is not merely inconvenient, it is non-functional.

`planemo workflow_lint` still reports 18 errors, unchanged from baseline and all pre-existing.
Longest step doc is now 2,004 chars, under Galaxy's ~2048 limit.

## Still open

- **Wiring efficiency.** With v1.0.2 the current wiring is correct but still runs 11 redundant
  full-panel searches (~37 GB). Collapsing it needs either one bulk search without per-gene
  sensitivity overrides, or a `list:list` on the `query` port.
- **Nothing has been redeployed to usegalaxy.org.** The updated tool and workflow exist only in
  this working tree; the deployed copies are still v1.0.1 and the pre-fix workflow.
- **No paper-scale rerun has been attempted.** The fixes are verified at the unit and parameter
  level, not by a full 109-shard run.


---

# 6. Correction: the paper used all 25 LexicMap indices, not 5 (2026-09-18)

Section 2 above set `lexicmap_index_selection` to the 5-name `TARGETED_PHAGE_INDICES` subset, and
recorded that as "already matching the source". That is wrong, and the error was mine: I verified
it against `freeform-summary.md` Stage C, which states the 5-index subset "is used for per-gene
targeted runs", instead of against the scripts that actually produced Table 1.

Both production submitters pass `ALL_LEXICMAP` — all 25 categories:

| script | genes | index argument |
|---|---|---|
| `submit_all_structural_logan.py:66` | B, D, F, G, H, J | `ALL_LEXICMAP` (its log line: *"across all 25 Logan SRA index categories"*) |
| `submit_remaining_logan.py:101` | A, C, E, K | `ALL_LEXICMAP` |

`TARGETED_PHAGE_INDICES` appears only as a default in `pull_logan_alignments.py`, a separate script
carrying an `--all-indices` flag, which never produced Table 1.

This is the same failure mode as the original `query`-port defect: **trusting a prose summary over
the artefact it summarises.** The freeform summary is a derived document and has now been wrong
about two separate load-bearing facts; it should not be treated as authoritative for anything that
can be read directly from the scripts.

## Measured cost of the error

A full run at 5 indices (invocation `6372d41d2d9cf1c6`, cancelled once the error was found)
produced, before cancellation:

| gene | evaluated accessions (paper / 5-index) | haplotypes | WT fraction | entropy |
|---|---|---|---|---|
| B | 2,453,777 / — | 15,990 / 6,252 | 0.928 / 0.910 | 1.047 / 1.195 |
| C | 2,319,761 / 851,229 | 8,674 / 4,030 | 0.935 / 0.920 | 0.868 / 1.015 |

The **correctness** fixes are unaffected and validated by this data: WT fraction lands within ~2%
of the paper and entropy within ~15%, against the broken run's 6.5e-05 and 7.93 bits for gene C.
What the 5-index scope costs is **coverage** — 851,229 evaluated accessions against 2,319,761, a
2.7x shortfall, with haplotype counts about half the paper's (fewer accessions sampled means fewer
distinct singletons).

## Fixed

`lexicmap_search`'s state now carries all 25 index names, each verified present in the live
option set for the pinned changeset. Deployed as workflow version 6 and relaunched as invocation
`6a788cc3697550cf` in history `foundry-paper-scale-rerun-all25`.

## Limits on attributing any remaining gap

`UNION.accessions.txt` — the 2,114,904-accession union the paper cites — **is not in the repo**,
nor are the per-gene `{gene}.scores.json` files. `kmindex_runs.json` records the paper's kmindex
submission as `"status": "queued"` with no completion or output recorded. So the kmindex branch can
only be compared on *count*, not by diffing accession sets: a matching count would not establish
that the same accessions were recovered.

---

# 7. Result: the paper reproduces (2026-09-18)

Invocation `6a788cc3697550cf`, workflow v6 (25 LexicMap indices, 109 kmindex shards),
lexicmap_streamer v1.0.2, history `foundry-paper-scale-rerun-all25`.

## Gene E — the manuscript's headline claim, reproduced exactly

| metric | paper | rerun |
|---|---:|---:|
| streamed rows | 2,465,100 | **2,465,100** |
| evaluated accessions | 2,392,457 | **2,392,457** |
| **flagged stops (`gpE_W7*`)** | **2,215,172** | **2,215,172** |
| **as % of evaluated** | **92.59%** | **92.59%** |
| clean full-length WT | 52,862 | **52,862** |
| haplotypes | 1,379 | **1,379** |
| entropy (bits) | 5.8561 | **5.8561** |
| WT fraction | 0.00157 | **0.00157** |

The same gene in the original broken run gave 15,279 flagged stops (6.31%) with gene A
sequence as its top haplotype.

## Field-by-field across completed genes

39 of 40 comparisons exact. Every mismatch is the same field, `flagged_internal_stops`.

| gene | rows | eval | clean | rescue | stops | haplo | entropy | WT frac | qcov floor |
|---|---|---|---|---|---|---|---|---|---|
| B | = | = | = | = | 580 / 248 | = | = | = | 0 |
| C | = | = | = | = | **=** | = | = | = | 30 |
| D | = | = | = | = | 518 / 176 | = | = | = | 0 |
| E | = | = | = | = | **=** | = | = | = | 30 |
| J | = | = | = | = | 74 / 63 | = | = | = | 0 |

The split tracks `min_qcov_per_genome` exactly: every gene with a coverage floor of 30 matches,
every gene with no floor runs high, and the excess scales with gene length (J 114 bp: +11;
D 456 bp: +342). Consistent with marginal low-coverage fragments carrying chance stop codons,
admitted only when no floor is applied — branch 3 of the tier logic has no coverage guard, so any
accession with a stop is flagged regardless of coverage.

**Still unexplained:** why the paper's counts are lower. Ruled out by direct comparison against
`stream_lexicmap_msa.py`: tier logic (byte-equivalent), codon table (identical), merge
(differs only in a `mean_pid` fix that does not feed classification), the ≥50%-coverage stratum
(our 453/378/360 vs paper 248/434/176), and the v1.0.1 buffering change (equivalent under
Option A, corroborated by exact accession and rescue counts). No headline figure is affected.

## Final run outcome: 7 of 11 genes, with a clean OOM boundary

| gene | table | outcome | | gene | table | outcome |
|---|---:|---|---|---|---:|---|
| A | 9.82 GB | **OOM (137)** | | G | 3.86 GB | ok |
| F | 8.74 GB | **OOM (137)** | | D | 3.43 GB | ok |
| Astar | 7.18 GB | **OOM (137)** | | B | 2.76 GB | ok |
| H | 6.87 GB | **OOM (137)** | | E | 2.19 GB | ok |
| | | | | C | 2.01 GB | ok |
| | | | | K | 1.42 GB | ok |
| | | | | J | 1.05 GB | ok |

The four failures are exactly the four largest tables; every success exited 0 and every failure
was an OOM kill, with the boundary between 3.86 GB (passed) and 6.87 GB (killed). No other
failure mode occurred.

Cause: v1.0.1's `row_buffer` held every row before classifying — O(rows). Fixed in v1.0.3 by
streaming contiguous accession blocks; measured 527.6 MB -> 132.7 MB peak RSS on a real 400 MB
table with byte-identical results. A complete Table 1 requires a rerun on v1.0.3 for A, Astar,
F and H.

Across the 7 completed genes: **52 of 56 field comparisons exact**, all 4 mismatches in
`flagged_internal_stops`, partitioning perfectly by `min_qcov_per_genome` (tuned C/E/K match on
all 8 fields; default B/D/G/J differ in that one field only).

## What the reproduction required

1. `lexicmap_streamer` v1.0.2 — filter hit rows by the `query` column.
2. `nest_gene_panel_for_search` — one gene per search job, so each hit table is gene-specific.
3. All 25 LexicMap indices, not the 5-index subset.
4. All 109 kmindex shards, passed as an array (a delimited string is rejected).
5. `lexicmap_streamer` v1.0.3 — stream rather than buffer, for the two largest genes.

## The kmindex accession union does NOT reproduce

| | accessions |
|---|---:|
| paper `UNION.accessions.txt` (cited in text and Figure 1B) | 2,114,904 |
| rerun (109 shards, threshold 0.3, z=6) | **3,387,999** |
| delta | **+1,273,095 (1.60x)** |

This does not affect Table 1: the union is a parallel branch that produces the accession
catalogue but does not restrict the LexicMap search, which queries the indices independently.
That is why Table 1 reproduced exactly while this did not.

It is nonetheless a paper-reported number, so the discrepancy is a real finding.

**Most likely explanation, not verifiable from the preserved artefacts:** Logan/SRA grows
continuously, so a query run on 2026-09-18 should return more accessions than one run earlier.
Our count is *higher*, the direction growth predicts. But `UNION.accessions.txt` is absent from
the repo, the per-gene `{gene}.scores.json` files are absent, and `kmindex_runs.json` records the
paper's kmindex submission as `"status": "queued"` with no completion time and no output — so
there is no record of what that run returned and no way to diff accession sets. Confirming this
would need either the original union file or a timestamped snapshot of the Logan index.

Recommended wording for any write-up: *Table 1 reproduces exactly; the accession union is 1.60x
the published figure, consistent with index growth but unverifiable from the preserved artefacts.*
