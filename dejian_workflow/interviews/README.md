# Interviews

The scarce input (Goal: milestone "Interview collection"). Real, uncleaned
analysis requests collected from codeathon participants, in their own words.

- `raw/` — one file per collected interview, uncleaned. Suggested naming:
  `YYYY-MM-DD_<participant-or-org>_<short-slug>.md` or `.json` depending on
  how the interview was captured (transcript vs. structured session log).
- Each interview should retain enough detail to re-run: the researcher's
  original request, any clarifying Q&A that happened, and the organism/data
  context mentioned.

Two kinds of interviews live in `raw/`, distinguished by filename:

- `example-*.txt` — three synthetic interviews written to demonstrate the
  pipeline (not from a real researcher). Good for a quick smoke test, not
  for evaluating routing quality.
- `biostars-*.txt` — 50 real bioinformatics questions from Biostars, a
  public Q&A forum, obtained via a CC-BY-4.0-licensed dataset published on
  Zenodo (not scraped) and hand-selected for being genuinely workflow-shaped
  requests. See `BIOSTARS_SOURCES.md` for the full index with links back to
  each original post. Each file carries its own source header. This is the
  first real (if not codeathon-native) test of routing against actual
  researcher language, not text written to make the pipeline look good.

These feed the routing layer (`scripts/route.py`) and, once scored, become
part of `eval/cases/` (the ~20 expert-authored evaluation set is a curated
subset, not all raw interviews).

## `analysis_request_examples_100/`

A separate, larger reference collection — 100 more real Biostars questions
in the same "analysis request" category as the 50 above (data described,
a goal stated), but **not hand-curated one-by-one** the way the 50 were.
These were filtered (bacteria/virus/pathogen keyword match → classified as
`analysis_request` → length/quality filter → randomly sampled) and then
spot-checked at the sample level, not individually vetted. Zero overlap
with the 50 in `raw/` or the 10 shown in
`docs/interview-data.marp.md`.

Purpose: illustrative bulk material — "what do 100 real analysis requests
actually look like" — for research and presentation, not a second curated
interview set. If you want to run one through the pipeline, it works fine
as input (same plain-text format, same source-header convention), but
these weren't selected with pipeline-testing rigor the way `raw/biostars-*`
were. `INDEX.md` in that directory lists all 100 with links to the
original posts.
