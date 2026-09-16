# Interviews

The scarce input (Goal: milestone "Interview collection"). Real, uncleaned
analysis requests collected from codeathon participants, in their own words.

- `raw/` — one file per collected interview, uncleaned. Suggested naming:
  `YYYY-MM-DD_<participant-or-org>_<short-slug>.md` or `.json` depending on
  how the interview was captured (transcript vs. structured session log).
- Each interview should retain enough detail to re-run: the researcher's
  original request, any clarifying Q&A that happened, and the organism/data
  context mentioned.

These feed the routing layer (`scripts/route.py`) and, once scored, become
part of `eval/cases/` (the ~20 expert-authored evaluation set is a curated
subset, not all raw interviews).
