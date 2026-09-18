# Case Study: Paper-to-Galaxy Construction and Verification
## *Candida auris* SCF1 Adhesin RNA-seq (Santana et al. 2023, *Science*)

### 1. Executive Summary

This case study documents a run of the **PAPER → GALAXY** pipeline (`pipeline-paper-to-galaxy`)
against a published paper rather than an interview. Starting from a PubMed URL, the pipeline read the
paper's supplementary methods, designed the Galaxy interface and data flow, checked both against the
IWC corpus, and drove a 26-iteration per-step loop to a concrete `gxformat2` workflow that passes
every static gate available. It then resolved real test data from the paper's own deposited
sequencing runs, synthesized a test plan, authored fixtures, and attempted execution.

**The run is partial.** Phases 1–10 completed. Phase 11 (`run-workflow-test`) failed twice for two
different, fully diagnosed reasons, and phase 12 was never reached. **No end-to-end execution has
passed**, so nothing here should be read as a verified workflow. What *is* verified is stated
precisely in §6.

The run was executed with `--use-subagents --checkpoint --feedback`. The checkpoint history (40
commits, one per phase or loop iteration) remains in the run repository at
`.foundry-runs/auris-scf1/.git`; every artifact here can be traced to the commit that produced it.

---

### 2. Experimental Scenario

- **Source**: Santana DJ et al., "A *Candida auris*-specific adhesin, Scf1, governs surface
  association, colonization, and virulence", *Science* 381(6665):1461-1467 (2023).
  PMID 37769084, PMC11235122, DOI 10.1126/science.adf8972.
- **Research question**: which genes are dysregulated in low-adhesion *C. auris* variants — an
  insertional mutant (`tnSWI1`) and a naturally low-adhesion clinical isolate (AR0387) — relative to
  the high-adhesion parent AR0382. This is the analysis that surfaced *SCF1* (`B9J08_001458`).
- **Study design**: one factor, three levels, n=2. Two contrasts against the AR0382 reference level.
- **Sequencing**: Illumina NextSeq 2000, 2 × 50 bp paired-end, stranded total RNA (Ribo-Zero Plus).
- **Target stack**: FastQC → Cutadapt → RNA STAR → featureCounts → DESeq2, against *C. auris* B8441
  (GCA_002759435.2).

**Why this paper is an unusual target.** The main text has *no* methods section — every computational
detail lives in a 60-page supplement, which the summarization phase retrieved via NCBI eutils JATS.
And the authors state they ran both analyses on usegalaxy.org, so the paper's tool chain already *is*
a Galaxy tool chain. A second analysis in the paper (AtMT T-DNA insertion-site mapping) was
deliberately scoped out: one of its steps (`extractSoftClipped`, SE-MEI) has no Tool Shed wrapper and
its pTO128 plasmid reference has no public accession.

---

### 3. Pipeline Lifecycle & Phase Audit

```
[Paper: PMID 37769084]
       │
       ▼
[Phase 1: summarize-paper] ──────────────────► freeform-summary.md
       │
       ▼
[Phase 2: freeform-summary-to-galaxy-interface] ──► freeform-galaxy-interface.md + open-requirements.ledger.yml
       │
       ▼
[Phase 3: freeform-summary-to-galaxy-data-flow] ──► freeform-galaxy-data-flow.md
       │
       ▼
[Phase 4: compare-against-iwc-exemplar] ─────► iwc-comparison-notes.md + iwc-exemplar.gxwf.yml
       │
       ▼
[Phase 5: freeform-summary-to-galaxy-template] ──► galaxy-workflow-draft.gxwf.yml
       │
       ▼
[Phase 6: advance-galaxy-draft-step ×26] ────► galaxy-workflow.gxwf.yml (concrete gxformat2)
       │
       ▼
[Phase 7: test-data-resolution] ─────────────► test-data-refs.json + test-data/
       │   (branch resolved at the first link: paper-to-test-data)
       ▼
[Phase 8: freeform-summary-to-galaxy-test-plan] ──► galaxy-test-plan.yml
       │
       ▼
[Phase 9: implement-galaxy-workflow-test] ───► galaxy-workflow.gxwf-tests.yml + test-data/
       │
       ▼
[Phase 10: validate-galaxy-workflow] ────────► galaxy-workflow-validation-result.json
       │                                        20 validated / 7 skipped / 0 fail
       ▼
[Phase 11: run-workflow-test] ───────────────► ✗ FAILED TWICE (planemo-smoke*.log)
       │
       ▼
[Phase 12: debug-galaxy-workflow-output] ────► NOT REACHED
```

#### Phases 1–5: source → design

Phase 1 read the PMC full text and the supplement, and returned ten open questions rather than
inventing what the paper omits. Phase 2 chose a **`sample_sheet:paired`** reads input carrying
`condition`/`replicate` column definitions — the decision the rest of the run hinged on — and flagged
at the time that it was making it *blind to its own testability*. Phase 3 settled how the condition
factor reaches DESeq2: the metadata survives in exactly one place, the workflow input, so the split
is taken off the input rather than off any mapped output, joined on element identifier.

Phase 4's corpus check produced the run's most important structural finding: **IWC has no single
workflow spanning FastQC → DESeq2.** It publishes the journey as two workflows joined at the
count-table boundary, which is why `rnaseq-de` can demand pre-grouped count collections and never
needs an in-workflow condition split. Ours is one workflow and cannot. The sample-sheet split
therefore has **zero corpus precedent** (0 hits for `sample_sheet`, `__SAMPLE_SHEET_TO_TABULAR__`, or
non-null `column_definitions`) and is built as a delimited region with a documented swap procedure
back to a `list:paired` fallback.

#### Phase 6: the 26-iteration loop

One subagent per iteration, one step concretized per iteration, `gxwf draft-next-step` as the oracle.
TODO sentinels went 44 → 0. Every pin was resolved from the Tool Shed and corroborated against corpus
frequency; several traps were found only by doing the work (see §5).

#### Phase 7: test data from the paper's own deposits

Resolved at the **first** link of the branch — the paper's data is fully deposited. Six ENA FASTQ
pairs (PRJNA904261, SRR22376027–32) subset to 200,000 read pairs, pinned by *uncompressed* md5.
This phase closed three long-open questions by measurement rather than argument, including confirming
`sample_sheet:paired` **is** expressible in a Planemo job block, which retired phase 3's fallback.

#### Phases 8–10: plan, fixtures, validation

Phase 8 was interrupted by a session limit mid-validation and resumed rather than restarted. Phase 9
materialized all 24 fixtures and verified each against phase 7's recorded md5s — proving that recipe
reproducible — and corrected a defect in phase 7's own job block (`type: paired` must be
`collection_type: paired`; the former fails the schema with 48 errors).

---

### 4. What Was Verified, and What Was Not

**Verified:**
- Terminal `gxwf validate`: **20 validated / 7 skipped / 0 fail**, `structure_errors: []`. The gate was
  proven to have teeth (an injected bad value flips it to 19/1/7) *and* its limits measured: an
  unknown extra key and a **dropped required parameter** both still validate green.
- `gxwf validate-tests`: `{"valid": true, "errors": []}`, 172 assertions, with negative controls
  confirming typo'd input/output labels are caught.
- Every `in:` key and `tool_state` parameter name on **all 27 steps** resolved against real tool input
  trees — 0 mismatches, 0 illegal select/boolean values.
- A source-level review of the 7 steps no gate can check found **no defects**.
- gxformat2 import: the deliverable was run through both pinned `gxformat2` versions (0.21.0, 0.27.0),
  confirming every pinned parameter survives conversion to native.

**Not verified — and this is the gap:**
- **No workflow execution has succeeded.** No tool has run, no output has been produced, and none of
  the 172 assertions has been evaluated.
- **Collection algebra has no static witness.** `gxwf --connections` crashes on every format2 tool
  step (`TypeError: step.in is not iterable`), so map-over shape composition was never checked. The
  map-over spine should run 6 jobs per step and the QC branch 12; nothing has confirmed it.
- **`in:` key names carry no automated protection at all** — a draft with a wrong unqualified
  `filter_source:` key was measured to validate byte-identically green.

---

### 5. Findings That Only a Real Run Surfaces

Selected from the 61 entries in `foundry-feedback.ledger.yml`.

**The corpus trap that would have destroyed the result.** DESeq2's `deseq_out` carries **no header**
(`deseq2.R` writes it with `col.names = FALSE`), while its *normalized counts* table does
(`col.names = NA`) — one tool, opposite answers for its two tabular outputs. The IWC exemplar binds
`header_lines: "1"` on its filters, which reads as a direct answer and is not one: that workflow
*manufactures* the header it then skips, via a `tp_text_file_with_recurring_lines` → `tp_sed_tool` →
`tp_cat` chain. Copying it would have silently discarded row 1 of every result table — and the table
is sorted by padj, so row 1 is the most significant gene. **For this paper that is *SCF1* itself.**
Corpus-first is the Foundry's core principle, and this is the case where following it naively removes
the finding the workflow exists to reproduce.

**Conditional case indices follow `<when>` order, not dropdown order.** Found three times
(`GTFconditional` in RNA STAR, `datasets_per_level` and `tximport_selector` in DESeq2). Reading the
option list gives the wrong branch, silently.

**A whole class of wrappers cannot be statically checked.** gxwf's decoder expects a collection
output's fields nested inside a `structure` object; the Tool Shed serializes them **flat**. Nothing is
missing — the shapes disagree. This is not limited to built-ins: DESeq2 trips it via `split_output`,
a collection output under a branch this workflow never selects. One never-selected conditional output
makes an entire wrapper uncacheable, and 7 of 27 steps had to be hand-bound as a result.

**Two cross-step invariants that nothing enforces.** `lfc_shrinkage_type: none` on both DESeq2 nodes
(any other value drops the `stat` column, moving padj from c7 to c6 and breaking the `"c7<"` predicate
hard-coded in a different step), and `header_lines: '0'` on all seven `Filter1` steps. Both survive as
*values* in the deliverable, but `draft-extract` strips all 850 comment lines, so **the reasons do
not.** Hence `galaxy-workflow-draft.gxwf.yml` is kept here alongside the extract.

**A procedural hole in the loop Mold.** It declares the open-requirements ledger as an input carrying
"open, resolved, and surrendered" entries, but its only procedural touchpoint reads *new open* entries
*after* implementing. A decision settled earlier and recorded in a **resolved** entry is never read
back — which is exactly where the `header_lines` answer lived.

---

### 6. Statistical Cross-Check (not a workflow run)

Because phase 11 never executed, the fixture's biological claim was checked out-of-band: a
strand-aware count matrix was built from the phase-7 alignments and DESeq2 run as two separate
2-level, n=2 analyses with no shrinkage, mirroring the workflow's two nodes.

| contrast | SCF1 log2FC | padj | rank by padj | rank by \|log2FC\| |
|---|---|---|---|---|
| tnSWI1 vs AR0382 | −6.93 | 2.1e-31 | 5 of 2393 | 2 |
| AR0387 vs AR0382 | −7.95 | 4.1e-18 | 4 of 1376 | 1 |

SCF1 is significant and strongly down in both contrasts with enormous margin, so the fixture supports
the paper's core claim at 200k-pair depth. **But no rank-1 assertion holds in both contrasts** — not
by padj (5th, 4th), not by |log2FC| (2nd, 1st) — so the paper's own phrasing, "the most significantly
dysregulated gene", is not reproducible at this depth. The test plan asserts membership plus
threshold, never rank or equality.

**These numbers are `pydeseq2` over `bwa-mem` counts, not the wrapper's R DESeq2 over featureCounts
`-s 2`.** They are order-of-magnitude expectations, not targets. Deliberately *not* asserted anywhere:
the paper's ~29-fold magnitude (measurement disagrees by an order of magnitude — ~270-fold aligned;
reference bias is ruled out because AR0387 *is* the B8441 reference strain), the negative ALS/IFF-HYR
adhesin claim (those genes lack power at this depth, so their absence would be a depth artefact), and
exact integer counts.

---

### 7. Why Phase 11 Failed, Twice

**Attempt 1 — no tools installed.** Galaxy started and rejected the invocation with HTTP 400 listing
all seven Tool Shed tools. Cause, confirmed at source: `planemo/galaxy/workflows.py:349 load_shed_repos`
collects `step.get("tool_shed_repository")` and never parses the tool id. Our steps carried no such
key, so the repo list was empty and the installer returned on its first line — **silent, no log line,
no error**. Converting to `.ga` would have failed identically; ephemeris's `.ga` branch performs the
same lookup. IWC `.ga` files only work because Galaxy's *exporter* writes those blocks.

*Fix applied:* `tool_shed_repository` is a first-class gxformat2 field
(`gxformat2_strict.py:191`). The 12 shed-tool steps were annotated in place with `name`/`owner`/
`changeset_revision`/`tool_shed`, each revision resolved against the live Tool Shed metadata API
filtered to the step's exact tool id *and* pinned version — all seven resolved to exactly one
installable revision. Verified positively: `load_shed_repos` went from `[]` to 12 entries.
**This is a genuine improvement to the deliverable**, since the changesets previously lived only in
stripped comments.

**Attempt 2 — conda environment build failure.** The fix worked: Galaxy cloned repositories at their
pinned revisions (`fastqc` at `24:2c64fded1286`, etc.). But `rgrnastar` and `deseq2` — the two heaviest
environments — failed:

```
DependencyException: Conda dependency failed to build job environment.
This is most likely a limitation in conda.
You can try to shorten the path to the job_working_directory.
```

under `/private/var/folders/df/6xqpqpcd7h73b6jpx9t6cwhw0000gn/T/tmpzx1whhuh/galaxy-dev/...`. This is
the conda prefix-length limit, not a workflow defect.

**Identified fix, untried:** `../ebola-rnaseq` reached 100% pass using `planemo test --biocontainers`,
which uses Docker images instead of building conda environments and sidesteps this failure entirely.
Docker is available on this machine. The recommended invocation is in [README.md](./README.md) §2.

---

### 8. Environment Caveats

- **`$HOME` was not writable** in this run's sandbox (an allowlist permitting the workspace root and
  temp paths). Three Molds assume writable `$HOME` and all three broke: `compare-against-iwc-exemplar`
  hard-codes `~/.foundry/iwc` with no override (a dead stop), `advance-galaxy-draft-step` wants
  `~/.galaxy/tool_info_cache` (silent — without it *every* tool reports `skip` and a green verdict is
  vacuous), and the pinned `planemo==0.75.47` could not install. Feedback entries citing this describe
  a sandbox boundary, **not** a property of the host machine; `0.75.47` may install fine elsewhere.
- `planemo` **0.75.44** was used against a pinned 0.75.47; nothing observed depends on the difference.
- `gxwf --version` self-reports a stale `1.0.0` while 1.10.1 is installed, so no Mold's pinned version
  is runtime-checkable.
