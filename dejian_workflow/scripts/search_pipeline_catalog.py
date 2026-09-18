#!/usr/bin/env python3
"""Match a free-text analysis description against the local bacteria/virus
Galaxy pipeline catalog (knowledge_base/pathogen_genomics/galaxy_pipeline_catalog.yaml).

This is a v0, keyword-overlap router: a concrete, inspectable first pass at
Goal 1's "route before building" decision, scoped to the ~20 bacteria/virus
IWC workflows catalogued so far. It is a starting point, not a replacement
for scripts/route.py's TODO of querying the live, full IWC registry -- see
that file. Keyword matching is intentionally simple and auditable; it will
under-match paraphrased requests (e.g. "flu" vs "influenza" are both listed
explicitly because a naive matcher won't infer the synonym on its own).
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path

import yaml

CATALOG_PATH = (
    Path(__file__).resolve().parent.parent
    / "knowledge_base"
    / "pathogen_genomics"
    / "galaxy_pipeline_catalog.yaml"
)


def load_catalog(path: Path = CATALOG_PATH) -> list[dict]:
    with open(path) as f:
        return yaml.safe_load(f)["pipelines"]


def tokenize(text: str) -> set[str]:
    # len >= 2 drops bare single-digit/letter noise (e.g. the "2" in "SARS-CoV-2")
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) >= 2}


DIMENSION_FIELDS = ("organism", "data_type", "analysis_type")


def _entry_tokens(entry: dict) -> set[str]:
    tokens: set[str] = set()
    for field in ("keywords",) + DIMENSION_FIELDS:
        for value in entry.get(field, []):
            tokens |= tokenize(value)
    return tokens


def _field_tokens(entry: dict, field: str) -> set[str]:
    tokens: set[str] = set()
    for value in entry.get(field, []):
        tokens |= tokenize(value)
    return tokens


def _term_weights(catalog: list[dict]) -> dict[str, float]:
    """Inverse-document-frequency-style weight per term across the catalog.

    A term shared by many workflows ("illumina", "paired") barely moves the
    needle; a term unique to one or two workflows ("cgmlst", "pangolin")
    carries most of the signal. Without this, generic terms dominate raw
    overlap counts and specific requests don't outrank vague ones.
    """
    doc_freq: dict[str, int] = {}
    for entry in catalog:
        for term in _entry_tokens(entry):
            doc_freq[term] = doc_freq.get(term, 0) + 1
    n = len(catalog)
    return {term: math.log((n + 1) / df) + 1 for term, df in doc_freq.items()}


def match(description: str, catalog: list[dict] | None = None, top_n: int = 5) -> list[dict]:
    """Return up to top_n catalog entries ranked by IDF-weighted keyword overlap.

    Each result is the original entry plus:
      "_matched"    the overlapping terms, for explainability/review
      "_confidence" matched IDF-weight / this entry's total IDF-weight (0-1) --
                     roughly "what fraction of this workflow's identity did
                     the description account for"
      "_unconfirmed_dimensions" which of organism/data_type/analysis_type had
                     ZERO overlap with the description -- i.e. an assumption
                     the router made silently rather than a stated fact. Used
                     by generate_followup_questions.py to close that gap by
                     asking, not guessing.

    "_confidence" is comparable across entries of different keyword-list
    lengths and is what scripts/route.py thresholds on; the raw matched-term
    count alone is not a reliable ranking signal (see _term_weights).
    """
    catalog = catalog if catalog is not None else load_catalog()
    query_tokens = tokenize(description)
    weights = _term_weights(catalog)

    scored = []
    for entry in catalog:
        entry_tokens = _entry_tokens(entry)
        matched = entry_tokens & query_tokens
        if not matched:
            continue
        matched_weight = sum(weights[t] for t in matched)
        entry_weight = sum(weights[t] for t in entry_tokens) or 1.0
        unconfirmed = [
            field for field in DIMENSION_FIELDS
            if _field_tokens(entry, field) and not (_field_tokens(entry, field) & query_tokens)
        ]
        scored.append(
            {
                **entry,
                "_matched": sorted(matched),
                "_confidence": round(matched_weight / entry_weight, 3),
                "_unconfirmed_dimensions": unconfirmed,
            }
        )

    scored.sort(key=lambda e: e["_confidence"], reverse=True)
    return scored[:top_n]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("description", help="Free-text analysis request, quoted")
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--json", action="store_true", help="Print raw JSON instead of a formatted report")
    args = parser.parse_args()

    results = match(args.description, top_n=args.top)

    if args.json:
        json.dump(results, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return

    if not results:
        print("No catalog matches. This is a candidate for the 'build' path,")
        print("or a sign the catalog needs a new entry -- not a silent failure.")
        return

    for rank, entry in enumerate(results, 1):
        print(f"{rank}. [confidence {entry['_confidence']:.2f}] {entry['name']}  ({entry['id']})")
        print(f"   matched on: {', '.join(entry['_matched'])}")
        print(f"   {entry['url']}")
        print()


if __name__ == "__main__":
    main()
