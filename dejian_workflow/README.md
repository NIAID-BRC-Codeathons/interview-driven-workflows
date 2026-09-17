# Talk to Galaxy

**Interview-Driven Workflow Construction and Repair in Galaxy** — NIAID-BRCs
AI Codeathon 2.0. Turns a free-text research description into a real,
mechanically-validated Galaxy workflow: reused from the IWC registry,
adapted from one, or built from scratch — never just a plausible-looking
guess. Full project context and goals: `PROPOSAL.md`.

## Get started

Install, credentials, running it, and cleanup are all in **`SETUP.md`** —
start there. The short version:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/run_pipeline.py interviews/raw/example-sarscov2-amplicon.txt
```

## Layout

| Path | What's there |
| --- | --- |
| `scripts/` | The pipeline itself — route → fetch/build/adapt → validate. See `scripts/README.md` for what each script does and its current status. |
| `interviews/` | Example input: 3 synthetic + 50 real (Biostars) curated interviews in `raw/`, plus 100 more real ones in `analysis_request_examples_100/`. See `interviews/README.md`. |
| `knowledge_base/` | The curated ~20-workflow bacteria/virus catalog the local router matches against. See `knowledge_base/README.md`. |
| `workflows/` | Output of the routing decision (`use`/`adapt`/`build`), one subdirectory per interview. See `workflows/README.md`. |
| `eval/` | Pass-rate reports, the failure taxonomy, and expert-authored evaluation cases. See `eval/README.md`. |
| `docs/` | Presentation decks: how the pipeline works, what running it against real data found, and the bacteria/virus pipeline survey. |
| `mcp/` | Config scaffold for grounding against the BRC Analytics MCP server (Goals 2–3) — **not yet wired into any script**, distinct from `scripts/galaxy_mcp_client.py`'s real, working integration with `galaxy-mcp`'s live IWC registry search. |
| `PROPOSAL.md` | The full project proposal this implementation is measured against. |
| `SETUP.md` | Install, credentials, testing, updating, and cleanup instructions. |

## What's real vs. what's a stand-in

Routing, fetching, static validation, byte-stable adaptation, and the live
IWC registry check (via a real `galaxy-mcp` MCP integration) are all real,
tested code — not stubs. The build (LLM-generation) path and the follow-up
question loop are real but incomplete (no Galaxy Workflow Foundry grounding,
no answer-collection loop yet). See `scripts/README.md`'s status table and
`SETUP.md`'s "What's not deployable yet" section for the honest, current
list of gaps.
