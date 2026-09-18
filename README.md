# Interview-Driven Workflow Construction and Repair in Galaxy

**NIAID-BRCs AI Codeathon 2.0** · September 16–18, 2026 · Argonne National Laboratory

Turning a researcher’s free-form analysis request into a validated, runnable Galaxy workflow — by reusing, adapting, or building one.

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

Convert a researcher’s free-form analysis request into a validated, runnable Galaxy workflow — either by reusing, adapting, or building one.

## Three-Day MVP (proposed)

Build an MCP-native interview agent that first searches the IWC registry to decide use / adapt / build, grounds analysis choices in BRC Analytics data and tools, and resolves missing information through follow-up questions. Use Galaxy Foundry to translate intent into validated workflow steps.

Demonstrate both creation of a new workflow and conversational adaptation of an existing published workflow.

## Evaluation (proposed)

Workflow validation and Planemo test success; correctness of tool/version/parameter selection; regression testing for adapted workflows; and expert scoring of analysis choice, provenance, and clarification quality.

## Full Proposal

A longer write-up is available at <https://gist.github.com/dannon/ceb8685f9c958f5a20ad6e4b0eb630ca>.

## Team

- Dave Rogers ([@NoopDog](https://github.com/NoopDog))
- Marius van den Beek ([@mvdbeek](https://github.com/mvdbeek))
- John Chilton ([@jmchilton](https://github.com/jmchilton))
- Dejian Zhao ([@dzhaobio](https://github.com/dzhaobio))
- Scott Cain ([@scottcain](https://github.com/scottcain))

## Working here

This repository is the team's working space for the codeathon — code, notebooks, data pointers, and notes. Replace this README with the real thing once the charter is written. Team members get access through the [NIAID-BRC-Codeathons](https://github.com/NIAID-BRC-Codeathons) organization; accept the invitation if you have not already.

## Presentation

- **[Interactive Slides (10-minute presentation)](slides/)**: Complete interactive slide deck with speaker notes, live pipeline phase explorer, router simulator, case study comparisons, research edge discoveries, and upstream commit ledger.

## Case studies

Two end-to-end runs of the [Galaxy Workflow Foundry](https://github.com/galaxyproject/foundry) pipelines, each with a run dashboard, the generated workflow, tests, validation reports, and a phase-by-phase write-up. The site version of this page is at <https://niaid-brc-codeathons.github.io/interview-driven-workflows/>.

| Case study | Pipeline | Outcome | Dashboard | Write-up |
| --- | --- | --- | --- | --- |
| Ebola virus host RNA-seq | INTERVIEW → GALAXY | 12/12 phases, Planemo tests passing | [dashboard](case_studies/ebola-rnaseq/dashboard.html) | [CASE_STUDY.md](case_studies/ebola-rnaseq/CASE_STUDY.md) · [bundle](case_studies/ebola-rnaseq/) |
| *Candida auris* SCF1 adhesin RNA-seq | PAPER → GALAXY | 10/12 phases, static gates green, execution not yet passing | [dashboard](case_studies/auris-scf1-rnaseq/dashboard.html) | [CASE_STUDY.md](case_studies/auris-scf1-rnaseq/CASE_STUDY.md) · [bundle](case_studies/auris-scf1-rnaseq/) |

Test fixtures are not committed. Each bundle's `test-data-refs.json` records the pinned source URLs, checksums, and subsetting recipe needed to regenerate them; dashboard links into `test-data/` will not resolve on the published site.

## Implementations

- [Talk to Galaxy — Dejian Zhao](dejian_workflow/): pipeline code, interviews, evaluation results, and presentation decks. See the [setup guide](dejian_workflow/SETUP.md) to get started.
