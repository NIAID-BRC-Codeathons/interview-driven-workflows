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

No Docker, no database, no server process — this is a set of command-line
scripts you run directly.

## 1. Get the code

If you don't already have it:

```bash
git clone https://github.com/NIAID-BRC-Codeathons/interview-driven-workflows.git
cd interview-driven-workflows
```

(If you're reading this from an existing checkout, just `cd` into it.)

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

Verify it worked:

```bash
planemo --version
python3 -c "import yaml, anthropic; print('ok')"
```

## 3. Set credentials (only if you need those specific features)

Nothing below is required to route a description or fetch/validate an
existing workflow — that works with zero configuration. Set these only when
you use the feature that needs them:

| Env var | Needed for | How to get one |
| --- | --- | --- |
| `ANTHROPIC_API_KEY` | `scripts/build_workflow.py` (generating a new workflow when nothing in the catalog matches) | console.anthropic.com — this makes a real, billed API call per run |
| `GALAXY_URL` + `GALAXY_USER_KEY` | `scripts/run_workflow_tests.sh` against an existing Galaxy instance | Your Galaxy account's API key (Galaxy → User → Preferences → Manage API Key). usegalaxy.org works for a quick test. |
| `GITHUB_TOKEN` | `scripts/fetch_iwc_workflow.py`, only if you hit GitHub's 60-requests/hour anonymous rate limit | A GitHub personal access token, no special scopes needed |

Without `GALAXY_URL`/`GALAXY_USER_KEY`, `run_workflow_tests.sh` falls back to
downloading a disposable Galaxy instance automatically — no account needed,
but expect it to take several minutes and a few GB of disk on first run.

Set them for your current shell session:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export GALAXY_URL=https://usegalaxy.org
export GALAXY_USER_KEY=...
```

## 4. Try it

Three example interviews ship in `interviews/raw/` so you have something to
run immediately:

```bash
python3 scripts/run_pipeline.py interviews/raw/example-sarscov2-amplicon.txt
python3 scripts/run_pipeline.py interviews/raw/example-ecoli-outbreak-cgmlst.txt
python3 scripts/run_pipeline.py interviews/raw/example-unknown-pathogen-nanopore.txt
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
# Execute the workflow against real data (needs GALAXY_URL/KEY, or waits for
# a disposable Galaxy to download):
scripts/run_workflow_tests.sh workflows/use/<interview-id>/workflow.ga

# Propose and apply a change to an adapted workflow (see the script's
# docstring for the change-spec format):
scripts/adapt_workflow.py propose workflows/adapt/<id>/workflow.ga change_spec.json
scripts/adapt_workflow.py apply   workflows/adapt/<id>/workflow.ga change_spec.json out.ga
```

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
  instance, which genuinely takes several minutes the first time. This is
  expected, not a hang.

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

**5. Remove the pipeline entirely:** if you no longer want this checkout at
all, first check for anything you'd lose:

```bash
git status   # confirm nothing you want to keep is uncommitted
```

then delete the project directory itself (`rm -rf` on the whole checkout, or
just delete it in Finder/Explorer). This is a plain git checkout with no
system-level registration anywhere else, so deleting the directory is a
complete uninstall.

## What's not deployable yet

`route.py`'s use/adapt/build decision only searches a curated ~20-workflow
catalog (`knowledge_base/pathogen_genomics/galaxy_pipeline_catalog.yaml`),
not the live IWC registry, and there's no MCP/BRC-Analytics grounding or
Galaxy Workflow Foundry integration wired up — see `PROPOSAL.md` Goals 1–3
and `scripts/README.md` for what's real today versus what's still a stub.
