# Talk to Galaxy: Interview-Driven Workflow Construction and Repair

**NIAID-BRCs AI Codeathon 2.0** · September 16–18, 2026 · Argonne National Laboratory

Source: [full proposal gist](https://gist.github.com/dannon/ceb8685f9c958f5a20ad6e4b0eb630ca)

> This document is the organizing team's project proposal, reproduced here for
> the team's reference. It is a starting point, not the charter — the charter
> (due August 28, 2026) is the team's own synthesis and may diverge from this.

---

## Project Overview

Guiding researchers from a free-form conversation about their analysis to a
validated, tested, runnable Galaxy workflow — built new or adapted from an
existing one, and portable across resource centers.

**Themes:** Automated Workflow Generation and Execution; Virtual BRC Helpdesk

## Core Concept

A researcher describes an analysis in their own words. The system interviews
them to fill in what they left unsaid, determines whether the analysis they
want already exists, and then either hands back a published workflow, adapts
an existing one to their case, or builds a new one. In every branch the
result is a real, executable Galaxy workflow that passes static validation
and an actual test run — not a recommendation, not an outline, and not a
plausible-looking file that fails on import.

This builds on the **Galaxy Workflow Foundry** (galaxyproject/foundry), an
open knowledge base that decomposes workflow construction into small,
individually validated steps compiled into instructions an AI agent follows.
Two paths already exist and have been reviewed upstream — build from scratch,
and modify an existing workflow from a conversation — but both are only
exercised today against fixed example cases. Putting them in front of real
scientists describing real analyses, grounding them in a specific resource
center's data holdings, and measuring what comes out has never happened.

The interview runs inside an MCP-native agentic runtime (Loom/Orbit), which
lets it reach a resource center's catalog live and ask informed questions
instead of deferring them. That also makes portability testable: pointing the
same runtime and interview at a second resource center's MCP server tests
whether the grounding generalizes or is quietly BRC-shaped — a test only
possible with other centers' people in the room.

## Team

**Team Name:** TBD

**Lead:** Marius van den Beek

| Name                | Affiliation                        | Role / Expertise                         |
| ------------------- | ----------------------------------- | ----------------------------------------- |
| Marius van den Beek | *(fill in)*                         | Workflow generation, knowledge authoring |
| Dannon Baker        | Johns Hopkins University / BRC Analytics | BRC catalog integration, agentic runtime |
| *(open)*            | Another resource center, ideally    | Second MCP server integration            |
| Dejian Zhao         | Yale School of Medicine             | Bioinformatician — interview collection  |
| *(open)*            |                                      | Bioinformatician — failure triage        |
| *(open)*            |                                      | Developer — evaluation harness           |

*(README.md lists Dave Rogers and Marius van den Beek as leads per the
codeathon organizing team; final team assignments are pending.)*

## Goals and Objectives

1. **Route before building.** Decide early whether a published workflow
   already does what the researcher needs: **use** it as-is, **adapt** one
   that's close, or **build** new. Today the system compares against
   published workflows only after committing to build — promoting that to an
   explicit early routing decision improves UX and saves effort.

2. **Ground the interview in real data holdings.** Connect through MCP to the
   BRC Analytics catalog so the interview can ask informed questions during
   the conversation (e.g., "these are the assemblies/annotations we have for
   that organism, which do you want?") and resolve reference data to real
   accessions instead of deferring.

3. **Prove the grounding is portable.** Point the same runtime and interview
   at a second resource center's MCP server, run a comparable session, and
   report the integration friction encountered.

4. **Close the loop with the researcher.** Turn tracked-but-unresolved
   obligations (a declared output with no producing step, an unpinned
   parameter, a tool with no known example) into targeted follow-up
   questions instead of surrendering them into the final result as labelled
   gaps.

5. **Adversarially review assumptions.** The characteristic failure mode is
   not a crash but a confident fabrication — a vague answer quietly promoted
   into a specific tool or parameter. Add a review pass in a separate context
   that attacks captured intent: is this the tool the researcher meant, is
   this parameter real or invented, was uncertainty preserved or silently
   resolved?

6. **Author a pathogen-genomics knowledge base.** Reference data conventions,
   BRC assembly handling, and domain-typical tools/analysis shapes, written
   as knowledge-base entries and compiled into agent instructions.

7. **Report a real pass rate.** Of collected interviews, how many produced a
   workflow that passed static validation, and how many passed an executed
   test run? Publish the number and a failure taxonomy.

8. **Grade the interview, not just the workflow.** Score ~20 expert-authored
   cases on correct analysis selection, provenance, and the quality of
   clarification questions asked — measuring the interview itself, which
   pass rate alone can't see.

## Approach

Every step is graded by a program, not a person's impression:

- **Static validation** independently checks tool identifiers, tool version
  revisions, parameter names on every connection between steps, conditional
  branches inside tool settings, and identifier validity.
- **A workflow test runner** executes the result against real data.
- **For adaptation:** a structural diff enforces that regions the researcher
  did not ask to change are left byte-for-byte identical.

That last property is what makes conversational modification safe rather
than a leap of faith:

- The conversation produces a **reviewable, step-anchored list of changes**
  before anything is applied — a human reads a diff, not a regenerated file
  to re-audit from scratch.
- **Untouched regions must be byte-stable.** Reordering, relabeling, or
  reformatting any untouched region is a scored failure, not a cosmetic
  difference.
- Because untouched regions don't move, **the original workflow's own tests
  remain a meaningful regression baseline** — the modified workflow must keep
  passing them, except where a requested change intentionally alters an
  output.

The evaluation framework distinguishes mechanically-checked properties from
judgment-based ones and requires mechanical checks to be genuinely executed,
not just described — so the pass rate is a measurement, not an invention.

## Milestones

- **Interview collection (day 1+, ongoing):** collect real, uncleaned
  analysis requests from participants at the event.
- **Routing layer:** the use/adapt/build decision against the published
  workflow registry — gates which path each interview follows, so it comes
  early.
- **Core loop (day 2):** run collected interviews through both paths,
  execute mechanical checks, triage every failure into a taxonomy, fix
  knowledge-base entries the failures implicate, re-run. Ground the
  interview in BRC catalog data as soon as the first "I don't know what
  assemblies exist" failure appears.
- **Portability run:** same runtime and interview against a second resource
  center's MCP server, with a written report of what worked / had to adapt.
- **Human-in-the-loop and adversarial review (day 3),** then the final
  pass-rate report and two live demonstrations: a spoken description
  becoming a running workflow, and an existing published workflow adapted by
  conversation, shown with its diff and a green regression suite.

## Data and Resources Required

| Resource Type      | Source / Link                                                    | Purpose                                                        |
| ------------------- | ----------------------------------------------------------------- | --------------------------------------------------------------- |
| Tools / Services    | Galaxy Workflow Foundry (galaxyproject/foundry)                   | Reviewed build/modify paths and compiled agent instructions     |
| Tools / Services    | Static workflow validation CLI; Planemo workflow test runner      | Mechanical oracles that grade every step                        |
| Tools / Services    | MCP-native agentic runtime with a durable notebook (Loom/Orbit)   | Deployment harness; runs and records the interview              |
| Tools / Services    | BRC Analytics MCP server; a second resource center's MCP server  | Interview grounding, and the portability test                   |
| Corpus              | IWC public workflow registry                                      | Routing decisions, comparison examples, adaptation targets       |
| Data                | BRC Analytics catalog — assemblies, annotations, priority pathogens | Grounding the interview to ask informed questions              |
| Interviews          | Codeathon participants                                             | The evaluation set, and the genuinely scarce input               |
| Compute / Storage   | Galaxy instance for test execution                                 | Running generated workflows against real data                   |
| LLMs / AI Models    | Any tool-capable model with MCP support                            | Runtime for the compiled instructions                            |

## Expected Outcomes / Deliverables

- Routing layer: use / adapt / build, decided against the published workflow
  registry.
- A BRC-grounded interview resolving reference data to real accessions
  during the conversation, running inside an MCP-native agentic runtime.
- A portability report from a second resource center's MCP server, including
  integration friction encountered.
- A follow-up question loop that reopens unresolved gaps with the researcher
  instead of surrendering them silently.
- An adversarial assumption-review pass, expressed as reusable checkable
  properties rather than one-off prose.
- A pathogen-genomics knowledge base, compiled into agent instructions.
- Collected interviews and their generated workflows, contributed back as
  permanent evaluation cases.
- A pass-rate report across both paths, with a published failure taxonomy —
  the headline result.
- Scored results on ~20 expert-authored cases, including quality of
  clarification questions.
- Two live demonstrations: build from scratch, and adapt an existing
  workflow.

## Potential Impact and Next Steps

If the pass rate is good, this is the strongest available answer to whether
AI can build bioinformatics workflows, because it is measured against a
validator and an executed test rather than a reviewer's impression. If it is
poor, the failure taxonomy is still a concrete roadmap — more useful than a
collection of prompts.

The adaptation path has the shortest line to production. Every researcher
who wants a published workflow slightly changed currently either learns the
workflow editor or files an issue and waits. "Describe the change, review the
diff, run the regression tests" is a capability the community would use the
week it works, with safety properties already specified and mechanically
checkable. The portability result determines how far that reaches: if the
same interview works against a second resource center with modest
adaptation, this generalizes across the BRC ecosystem rather than being a
Galaxy-and-BRC-only convenience. Evaluation cases collected at the event
persist as a public benchmark after it ends.

## Technical Support Needed

- A Galaxy instance for executing workflow tests
- LLM API access with sufficient quota for repeated multi-step runs
- A partner participant from another resource center willing to point the
  runtime at their MCP server
- Help soliciting analysis descriptions from participants ahead of the
  event, so interview collection can begin on day 1
