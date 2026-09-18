# Setup & Deployment

How to install this pipeline and run it, for anyone on the team who isn't
the person who wrote it. For what each script actually does, see
`scripts/README.md`; this file is just: get it running.

## What this is

A pipeline that takes a free-text research description and either points to
an existing Galaxy workflow, prepares one for adaptation, or generates a new
one — validating the result against the real Galaxy Tool Shed at every step.
See `PROPOSAL.md` for the full project context.

## Prerequisites

- **Python 3.10 or later** (the scripts use `X | None` type hints, which need
  3.10+). Check with `python3 --version`.
- **git**, to have this repo checked out.
- **Network access** to GitHub (fetching real workflows from the IWC
  registry) and, for two optional steps below, to api.anthropic.com and a
  Galaxy instance.
- **A Galaxy account and API key — set this up before you start testing if
  you want to exercise the full pipeline**, including actually running a
  workflow against real data (`scripts/run_workflow_tests.sh`). This is the
  **preferred way to test**: sign up free at
  [usegalaxy.org](https://usegalaxy.org), then get your key from
  **User → Preferences → Manage API Key**. Without this, that one step
  falls back to downloading and configuring a disposable Galaxy instance
  from scratch, which works with zero setup but is slow and heavy (see
  step 3). Everything else in this pipeline (routing, fetching, static
  validation) needs no account at all.
  **Note this means your workflow and test data get uploaded to and
  processed by that Galaxy server** (e.g. usegalaxy.org), not run on your
  own machine — see the callout in step 3 before using this with anything
  other than the example data.

No Docker, no database, no server process — this is a set of command-line
scripts you run directly.

## 1. Get the code

If you don't already have it:

```bash
git clone https://github.com/NIAID-BRC-Codeathons/interview-driven-workflows.git
cd interview-driven-workflows/dejian_workflow
```

All commands below assume you're `cd`'d into `dejian_workflow/`.

### Updating an existing checkout

If you already installed this before and just want the latest version,
`git pull` alone isn't enough — dependencies change too (for example,
`galaxy-mcp`/`fastmcp` were added after some earlier installs), and a stale
venv won't have them:

```bash
cd interview-driven-workflows/dejian_workflow  # implementation folder
git status                             # confirm no local changes you'd lose
git pull origin main

source .venv/bin/activate
pip install -r requirements.txt        # picks up any new/changed dependencies
```

If `git status` shows local changes before pulling, `git stash -u` them
first rather than pulling over them. Then re-run the verify command in
step 2 below to confirm the venv actually picked up the update.

## 2. Install dependencies

Use a virtual environment so this doesn't pollute your system Python:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

This installs:
- `planemo` — real Galaxy workflow validation and test execution (no Galaxy
  server required for validation)
- `pyyaml` — reads the pipeline catalog
- `anthropic` — only needed for the "build a new workflow" path
- `galaxy-mcp` + `fastmcp` — a real MCP client/server pair
  (`scripts/galaxy_mcp_client.py`) that lets `route.py` search the full,
  live IWC workflow registry, not just this repo's curated ~20-workflow
  catalog. No credentials needed for this — it's a public, read-only
  search.

Verify it worked:

```bash
planemo --version
python3 -c "import yaml, anthropic, galaxy_mcp, fastmcp; print('ok')"
```

## 3. Set credentials (only if you need those specific features)

Nothing below is required to route a description or fetch/validate an
existing workflow — that works with zero configuration. Set these only when
you use the feature that needs them:

| Env var | Needed for | How to get one |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | `scripts/build_workflow.py` (generating a new workflow when nothing in the catalog matches) | console.anthropic.com — this makes a real, billed API call per run |
| `GALAXY_URL` + `GALAXY_USER_KEY` | `scripts/run_workflow_tests.sh` against an existing Galaxy instance — **preferred, set this up in advance** | Your Galaxy account's API key (Galaxy → User → Preferences → Manage API Key). usegalaxy.org is free and works well for this. |
| `GITHUB_TOKEN` | `scripts/fetch_iwc_workflow.py`, only if you hit GitHub's 60-requests/hour anonymous rate limit | A GitHub personal access token, no special scopes needed |

**Use `GALAXY_URL`/`GALAXY_USER_KEY` if you can** — it runs against a real,
already-running Galaxy in a couple of minutes. Without it,
`run_workflow_tests.sh` falls back to downloading and configuring a
disposable Galaxy instance from scratch automatically — no account needed,
but expect several minutes to tens of minutes and several GB of disk/network
use, largely because it also has to install each tool's own dependencies the
first time. Prepare the account beforehand (see Prerequisites) rather than
discovering this mid-test.

**Important: where the analysis actually runs.** These are not just two
speeds of the same thing — they execute in different places:

- **`GALAXY_URL`/`GALAXY_USER_KEY` (the online/preferred path):** your
  machine only orchestrates. `planemo` uploads the workflow and test data to
  that Galaxy server over its API, the tools actually execute on **that
  server's own compute** (e.g. usegalaxy.org's infrastructure, not yours),
  and planemo polls for results and downloads them back down. Your data
  leaves your machine and is processed by a third-party public service —
  fine for the example/test data this pipeline ships with, but think twice
  before pointing this at real, sensitive, or restricted research data.
- **`GALAXY_ROOT` or the `--install_galaxy` fallback:** everything — Galaxy
  itself and every tool run — executes **locally on your machine**. Nothing
  is uploaded anywhere. This is why it's slower to set up (you're
  installing a whole Galaxy) but keeps data local.

If your data can't leave your machine, don't set `GALAXY_URL` — use
`GALAXY_ROOT` or let it fall back to `--install_galaxy` instead.

Set them for your current shell session:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export GALAXY_URL=https://usegalaxy.org
export GALAXY_USER_KEY=...
```

## 4. Try it

Three synthetic example interviews ship in `interviews/raw/` so you have
something to run immediately:

```bash
python3 scripts/run_pipeline.py interviews/raw/example-sarscov2-amplicon.txt
python3 scripts/run_pipeline.py interviews/raw/example-ecoli-outbreak-cgmlst.txt
python3 scripts/run_pipeline.py interviews/raw/example-unknown-pathogen-nanopore.txt
```

There are also 50 **real** interviews (`interviews/raw/biostars-*.txt`),
sourced from an actual Q&A forum rather than written to demonstrate the
pipeline — see "How the real interview data was collected" below for where
they came from, and `interviews/BIOSTARS_SOURCES.md` for the index:

```bash
for f in interviews/raw/biostars-*.txt; do
  python3 scripts/generate_followup_questions.py "$f"
done
```

Each run prints its routing decision (use / adapt / build), fetches or
generates the workflow, and runs real static validation. Expect this: the
SARS-CoV-2 example currently **fails validation** — that's not a bug in this
pipeline, it's a real stale tool reference in that published IWC workflow,
which the validator is supposed to catch.

To run your own description:

```bash
echo "your research description here" > interviews/raw/my-request.txt
python3 scripts/run_pipeline.py interviews/raw/my-request.txt
```

To go further:

```bash
# Execute the workflow against real data -- fast with GALAXY_URL/KEY set
# (preferred), otherwise waits for a disposable Galaxy to download and
# configure (slow, first run only). This has been run for real against
# usegalaxy.org and passed -- see eval/results/2026-09-16-cgmlst-usegalaxy.md
# for the full report and a screenshot of the resulting Galaxy history.
scripts/run_workflow_tests.sh workflows/use/<interview-id>/workflow.ga

# Propose and apply a change to an adapted workflow (see the script's
# docstring for the change-spec format):
scripts/adapt_workflow.py propose workflows/adapt/<id>/workflow.ga change_spec.json
scripts/adapt_workflow.py apply   workflows/adapt/<id>/workflow.ga change_spec.json out.ga
```

## How the real interview data was collected

This pipeline needs real researcher language to test against, not text
written to make it look good. Here's exactly how the 50 `biostars-*.txt`
interviews were obtained, including the approaches that didn't work.

**The goal:** real, unscripted bioinformatics questions about bacteria/virus
analyses — the messiest input the pipeline is supposed to handle.

**What was tried and failed:**

1. **Scraping biostars.org search results directly** (`curl`, plain HTTP).
   Blocked — the site returns a Cloudflare bot-challenge page (`Just a
   moment...`), not content, to any non-browser request.
2. **The official, documented Biostars API** (`biostars.org/info/api/`).
   Also blocked — same Cloudflare challenge, even on the documented API
   path.
3. **Claude's own web-fetch tooling.** Also blocked — HTTP 403.
4. **Deliberately defeating that bot protection.** Considered and
   **declined** — Cloudflare's challenge is a deliberate technical access
   control the site operator put up, and circumventing it isn't something
   this project does, regardless of how few records were needed (50, in
   this case). This is a firm line, not a scope negotiation.

**What actually worked: a published, openly-licensed dataset, not a scrape.**
Someone had already extracted Biostars content through the official API and
published it as a research dataset:

> Luna, Augustin. (2023). *BioStars Posts API Output* [Data set]. Zenodo.
> https://doi.org/10.5281/zenodo.7813785
> Licensed CC BY 4.0 — the same license Biostars uses for its own content.

That's a legitimate download, not a workaround: a single 976 MB JSON file,
532,421 entries covering every post type (Question, Answer, Comment, Blog,
Tutorial, Forum, Tool, Job, News) through Biostars post ID 9557161. (The
first download attempt was silently truncated by a connection drop — worth
knowing if you re-fetch it yourself: verify the file is exactly 976,422,282
bytes and `json.load()`s cleanly before trusting it.)

**Filtering funnel down to 50:**

| Stage | Count |
|---|---|
| Total entries (all post types) | 532,421 |
| `type == "Question"` | 106,395 |
| Title/body matches a bacteria/virus/pathogen keyword list | 5,250 |
| Scores as workflow-shaped (see below), top-ranked | 200 |
| Hand-selected for the final set | **50** |

The keyword filter alone was nowhere near enough — Biostars is a general
Q&A forum, not a workflow-request board. Most hits were troubleshooting
("Argument isn't numeric... at prokka line 259"), tool installation, or
conceptual questions ("What does N50 mean?"), none of which describe an
analysis to run. A heuristic scorer downranked posts containing error
tracebacks or "what is X" phrasing and upranked posts containing
data-description language ("I have...", "fastq", "assembly") and
intent phrasing ("I want to...", "how do I...", "recommend a pipeline
for..."). The top 200 by that score were then read and hand-selected down
to 50 diverse, genuinely workflow-shaped requests spanning bacterial AMR/
typing/assembly/annotation and viral assembly/variant-calling/SARS-CoV-2/
metagenomics — manual judgment, not further automation, made the final cut.

**What the full 5,250 actually look like.** Before picking the 50, we
classified the entire bacteria/virus/pathogen-matched set — not to filter
further, but to see the real distribution of how people ask:

| Category | Count | % |
|---|---|---|
| Analysis request (data + a goal) | 2,869 | 54.6% |
| Other / unclear | 1,714 | 32.6% |
| Tool recommendation (no own data described) | 272 | 5.2% |
| Troubleshooting / error | 206 | 3.9% |
| Conceptual / definitional | 107 | 2.0% |
| Data retrieval | 54 | 1.0% |
| Installation / setup | 28 | 0.5% |

Better than expected: over half are analysis-request-shaped. But a third
land in "other/unclear" — real questions blend categories more than any
clean taxonomy admits. Three examples spanning the spectrum:

- **Clean analysis request** (majority shape, what the pipeline is built
  for): *"I am working on 10 bacterial genomes (1 reference and 9 mutant)
  sequenced by Illumina technology. My main aim is to find SNPs that are
  common in 9 genomes but absent in reference genomes..."*
  ([Biostars #96189](https://www.biostars.org/p/96189/))
- **Vague, needs clarification** (tool recommendation, 5.2% — exactly what
  `generate_followup_questions.py` should catch, not guess): *"I would
  like to classify my viral contigs, could anyone recommend me the best
  way to that? Also if someone has created viral database for blast?"*
  ([Biostars #179095](https://www.biostars.org/p/179095/))
- **Troubleshooting — out of pipeline scope entirely** (3.9%): *"I am
  getting the following error message when trying to execute AMR
  prediction... `Traceback (most recent call last):` ...
  `OSError: [Errno 2] No such file or directory`"* — ironically an
  AMR/TB request, but debugging a broken run, not describing a new
  analysis; no routing decision should apply here.
  ([Biostars #214374](https://www.biostars.org/p/214374/))

**Provenance kept, not discarded:** each `biostars-*.txt` file carries a
header (`# source`, `# title`, `# date`, `# license`) linking back to its
original post, and `interviews/BIOSTARS_SOURCES.md` indexes all 50.

**What running the real router against these 50 revealed** (not just how
the data was collected, but what it was for): a 34 adapt / 13 build / 3 use
decision split, and one confirmed false positive — an explicitly viral
genome request routed to a bacterial workflow at "use" confidence — that
`scripts/generate_followup_questions.py` correctly caught via the
unconfirmed "organism" dimension. See the commit history and
`interviews/README.md` for details.

## Troubleshooting

- **`planemo: command not found`** — your virtualenv isn't activated, or
  step 2 didn't complete. Re-run `source .venv/bin/activate`.
- **Validation reports `ERROR: ... not an installable revision`** — this is
  the validator working correctly: a real problem with the fetched
  workflow's pinned tool version on the Galaxy Tool Shed, not a pipeline
  bug. Log it; don't suppress it.
- **`fetch_iwc_workflow.py` fails with a GitHub API error** — you likely hit
  the unauthenticated rate limit (60 requests/hour). Set `GITHUB_TOKEN`.
- **`build_workflow.py` errors with "no valid Anthropic credentials"** — set
  `ANTHROPIC_API_KEY`, or run `ant auth login` if you use the Claude CLI.
- **`run_workflow_tests.sh` seems stuck** — if neither `GALAXY_URL` nor
  `GALAXY_ROOT` is set, it's downloading and configuring a disposable Galaxy
  instance plus per-tool dependencies, which genuinely takes several minutes
  to tens of minutes the first time. This is expected, not a hang — but it's
  also avoidable: set `GALAXY_URL`/`GALAXY_USER_KEY` to a real Galaxy account
  (see Prerequisites) and this step takes a couple of minutes instead.

## Removing / cleaning up after testing

This pipeline installs nothing outside its own project directory except the
Python virtualenv and, if you ran `run_workflow_tests.sh` without
`GALAXY_URL`/`GALAXY_ROOT`, a Galaxy install cached by planemo. Nothing
touches system Python, no background services are started, and no daemons
are left running — cleanup is just deleting files.

**1. Deactivate and remove the virtualenv:**

```bash
deactivate            # if it's currently active
rm -rf .venv
```

This also fully removes `galaxy-mcp`/`fastmcp` (`scripts/galaxy_mcp_client.py`'s
real MCP client/server pair) — confirmed they leave no cache or state
anywhere outside the virtualenv (checked `~/.cache`, `~/.config`,
`~/.local/share`: nothing), unlike planemo's disposable-Galaxy cache in
step 3 below. There's nothing extra to clean up for them.

**2. Remove pipeline-generated output** (fetched/built/adapted workflows —
safe to delete; they're reproducible by re-running the scripts):

```bash
git clean -n workflows/ interviews/raw/   # preview what would be removed
git clean -fd workflows/ interviews/raw/  # actually remove it
```

This leaves the tracked `.gitkeep` files and example interviews in place and
only removes untracked output — check the preview output before running
the `-fd` command if you've added your own interview files you want to keep.

**3. Remove planemo's cached Galaxy install** (only if you used the
`--install_galaxy` fallback in `run_workflow_tests.sh` — this is what
actually used the "several GB" of disk mentioned above):

```bash
rm -rf ~/.planemo
```

This is planemo's own workspace/cache directory (not part of this repo) —
removing it just means the next `--install_galaxy` run re-downloads Galaxy.

**4. Unset any credentials you exported for this session:**

```bash
unset ANTHROPIC_API_KEY GALAXY_URL GALAXY_USER_KEY GITHUB_TOKEN
```

If you created a Galaxy API key or an Anthropic API key specifically for
testing this pipeline and don't need it going forward, revoke it from that
service's account settings (Galaxy: User → Preferences → Manage API Key;
Anthropic: console.anthropic.com → API Keys) — this pipeline has no way to
do that for you.

**5. Remove your local checkout entirely:** if you no longer want this on
your machine at all, first check for anything you'd lose:

```bash
git status   # confirm nothing you want to keep is uncommitted
```

then delete the top-level `interview-driven-workflows/` directory (`rm -rf`
on the whole checkout, or just delete it in Finder/Explorer). This is a
purely local deletion with no effect on the shared repo — it only removes
files from the shared repo for the whole team if you `git rm` and push a
deletion, which is a very different, much bigger action; don't do that
without team agreement. A plain local deletion has no system-level
registration anywhere else, so it's a complete local uninstall.

## What's not deployable yet

`route.py`'s use/adapt/build decision searches a curated ~20-workflow catalog
(`knowledge_base/pathogen_genomics/galaxy_pipeline_catalog.yaml`) first, and
now also checks the real, live IWC registry via a genuine MCP client/server
pair (`scripts/galaxy_mcp_client.py`, talking to
[galaxyproject/galaxy-mcp](https://github.com/galaxyproject/galaxy-mcp)) when
the local catalog finds nothing — see `scripts/README.md` for what that
integration actually catches and where it's known to misfire. What's still
missing: BRC Analytics grounding, and a Galaxy Workflow Foundry integration
for intent-to-workflow-steps generation (`build_workflow.py` still uses a
plain LLM call instead) — see `PROPOSAL.md` Goals 1–3 for the full picture.
