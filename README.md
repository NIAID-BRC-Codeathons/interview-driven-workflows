# Interview-Driven Workflow Construction and Repair in Galaxy

**NIAID-BRCs AI Codeathon 2.0** · September 16–18, 2026 · Argonne National Laboratory

Turning a researcher's free-form analysis request into a validated, runnable Galaxy workflow — by reusing, adapting, or building one.

Project page: https://niaid-brc-codeathons.github.io/projects/interview-driven-workflows/

---

> **This is a draft pitch, not a plan.**
>
> What follows is a one-slide proposal from the organizing team. It exists
> to seed a team, not to constrain one. Scope, methods, target organism,
> and success criteria are all still open — expect them to change
> substantially. Turning this into a real plan is the team's first job, and
> it lands in the project charter due August 28, 2026.

---

## Goal (proposed)

Convert a researcher's free-form analysis request into a validated, runnable Galaxy workflow — either by reusing, adapting, or building one.

## Three-Day MVP (proposed)

Build an MCP-native interview agent that first searches the IWC registry to decide use / adapt / build, grounds analysis choices in BRC Analytics data and tools, and resolves missing information through follow-up questions. Use Galaxy Foundry to translate intent into validated workflow steps.

Demonstrate both creation of a new workflow and conversational adaptation of an existing published workflow.

## Evaluation (proposed)

Workflow validation and Planemo test success; correctness of tool/version/parameter selection; regression testing for adapted workflows; and expert scoring of analysis choice, provenance, and clarification quality.

## Full Proposal

A longer write-up is available at <https://gist.github.com/dannon/ceb8685f9c958f5a20ad6e4b0eb630ca>.

## Leads

- Dave Rogers
- Marius van den Beek

Team assignments are still being finalized. Participants can review their project, and request a reassignment, in the participant spreadsheet circulated by the organizing team.

---

## This implementation — "Talk to Galaxy"

The code in this repository is one team's implementation of the pitch
above: turns a free-text research description into a real,
mechanically-validated Galaxy workflow — reused from the IWC registry,
adapted from one, or built from scratch — never just a plausible-looking
guess. Full context and goals this implementation is measured against:
`PROPOSAL.md`.

### Get started

Install, credentials, running it, and cleanup are all in **`SETUP.md`** —
start there. The short version:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/run_pipeline.py interviews/raw/example-sarscov2-amplicon.txt
```

### Layout

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

### What's real vs. what's a stand-in

Routing, fetching, static validation, byte-stable adaptation, and the live
IWC registry check (via a real `galaxy-mcp` MCP integration) are all real,
tested code — not stubs. The build (LLM-generation) path and the follow-up
question loop are real but incomplete (no Galaxy Workflow Foundry grounding,
no answer-collection loop yet). See `scripts/README.md`'s status table and
`SETUP.md`'s "What's not deployable yet" section for the honest, current
list of gaps.
