# Scripts

The pipeline that turns an interview into a validated workflow. Each stage
is a separate script so it can be run and debugged independently, and
`run_pipeline.py` chains them for the end-to-end path.

| Script                        | Stage                                                          | Status |
| ------------------------------ | ---------------------------------------------------------------- | ------ |
| `search_pipeline_catalog.py`  | Keyword-match a description against the curated bacteria/virus catalog | **working** |
| `route.py`                    | Goal 1: use / adapt / build decision                            | **working v0** (thresholds on `search_pipeline_catalog.py` confidence) |
| `generate_followup_questions.py` | Goal 4: surface routing assumptions as questions for the researcher | **working v0** (deterministic, no LLM — see docstring for the closed-loop gap) |
| `fetch_iwc_workflow.py`       | Download a real `.ga` + test file from the IWC registry         | **working** |
| `validate_workflow.sh`        | Static validation (wraps `planemo workflow_lint`)                | **working** (real, no live Galaxy needed) |
| `run_workflow_tests.sh`       | Executed Planemo test run                                       | **working, verified** — real passing run against usegalaxy.org, see `eval/results/2026-09-16-cgmlst-usegalaxy.md` |
| `adapt_workflow.py`           | Apply a reviewed change spec + verify byte-stability            | **working v0** (no NL interpretation — see docstring) |
| `build_workflow.py`           | Build a new workflow via an LLM, then validate it                | **working v0**, needs `ANTHROPIC_API_KEY` |
| `run_pipeline.py`             | Orchestrates route → fetch/build → validate end-to-end          | **working** |

Everything above is real, tested code — not stubs — with one honest gap:
there's no Galaxy Workflow Foundry or MCP runtime wired up here, so
`build_workflow.py` uses a plain LLM call instead, and `adapt_workflow.py`
takes an already-decided change spec rather than interpreting free text
itself (see each script's docstring for why, and what a real Foundry
integration would replace). Similarly, `generate_followup_questions.py`
surfaces questions but doesn't collect answers or re-route based on them —
there's no interactive interview loop here, only the half of Goal 4 that
identifies what should be asked.

## Quickstart

```
pip install -r requirements.txt   # planemo, pyyaml, anthropic

# Route + fetch/validate an existing interview (prints follow-up questions
# for any unconfirmed assumption before proceeding):
python3 scripts/run_pipeline.py interviews/raw/example-sarscov2-amplicon.txt
python3 scripts/run_pipeline.py interviews/raw/example-ecoli-outbreak-cgmlst.txt

# See just the follow-up questions, without running the rest of the pipeline:
python3 scripts/generate_followup_questions.py interviews/raw/example-ecoli-outbreak-cgmlst.txt

# Build path (needs ANTHROPIC_API_KEY):
python3 scripts/run_pipeline.py interviews/raw/<a-description-that-matches-nothing>.txt

# Test run against real data (slow on first run -- see run_workflow_tests.sh):
scripts/run_workflow_tests.sh workflows/use/<interview-id>/workflow.ga
```

`route.py`'s use/adapt/build thresholds (`USE_THRESHOLD`/`ADAPT_THRESHOLD`)
were calibrated by eyeballing five example descriptions, not a proper
validation set — expect to retune them once real interviews come in on
day 1, and treat `eval/cases/` as where that calibration should eventually
be justified, not this file's docstring.

`run_workflow_tests.sh` needs a Galaxy instance. Fastest: set `GALAXY_URL`
+ `GALAXY_USER_KEY` to an existing instance (e.g. usegalaxy.org). Slowest
but zero-setup: leave both unset and it falls back to `--install_galaxy`,
which downloads a disposable Galaxy (many minutes, several GB, first run
only).
