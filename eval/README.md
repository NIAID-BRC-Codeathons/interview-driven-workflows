# Evaluation

The project's headline result (Goals 7 and 8): a real pass rate, a failure
taxonomy, and interview-quality scores — not a reviewer's impression.

- `cases/` — the ~20 expert-authored evaluation cases (Goal 8). Each case
  should record: the original request, the correct analysis/routing
  decision, expected provenance, and what a good clarification question
  would have looked like — so a scored session can be compared against it.
- `results/` — pass-rate reports over time. One file per run, e.g.
  `results/2026-09-17_run1.md`, recording:
  - how many interviews produced a workflow passing static validation,
  - how many passed an executed Planemo test run,
  - per-case scores from `cases/` where applicable.
- `taxonomy.md` — the living failure taxonomy. Every failure triaged during
  the core loop gets classified here; this is what turns raw failures into
  a roadmap (see PROPOSAL.md's "Potential Impact" section).

Only mechanically-executed checks belong in a pass-rate number. If a check
was skipped or approximated, say so in the report rather than folding it
into the headline rate.
