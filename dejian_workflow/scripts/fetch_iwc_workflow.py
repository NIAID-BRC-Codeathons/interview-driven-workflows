#!/usr/bin/env python3
"""Fetch a real workflow (.ga), its Planemo test file, and its README from the
IWC registry on GitHub, given a catalog entry id or an iwc_path.

This is what turns a routing decision ("use" or "adapt" this workflow) into
an actual file on disk to validate/test/modify -- not a placeholder.
"""

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from search_pipeline_catalog import load_catalog  # noqa: E402

RAW_BASE = "https://raw.githubusercontent.com/galaxyproject/iwc/main"
API_BASE = "https://api.github.com/repos/galaxyproject/iwc/contents"


def _entry_by_id(entry_id: str) -> dict:
    for entry in load_catalog():
        if entry["id"] == entry_id:
            return entry
    raise KeyError(f"no catalog entry with id {entry_id!r}")


def _list_dir(iwc_path: str) -> list[dict]:
    """List a directory in the IWC repo via the GitHub contents API.

    Subject to GitHub's unauthenticated rate limit (60 req/hour/IP) -- fine
    for occasional interview-driven fetches, not for bulk catalog refreshes.
    Set GITHUB_TOKEN to raise that limit if needed.
    """
    req = urllib.request.Request(f"{API_BASE}/{iwc_path}")
    import os

    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def _download(url: str, dest: Path) -> None:
    with urllib.request.urlopen(url, timeout=30) as resp:
        dest.write_bytes(resp.read())


def fetch(entry_id: str, output_dir: Path) -> Path:
    """Download the workflow's .ga file, its Planemo test file, and README.

    IWC workflow directories do not follow one consistent filename
    convention (directory name, underscored, hyphenated, or unrelated all
    occur), so this lists the directory and finds files by extension/name
    pattern rather than guessing a filename from the directory name.

    Returns the path to the downloaded workflow (.ga) file.
    """
    entry = _entry_by_id(entry_id)
    iwc_path = entry["iwc_path"]
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        listing = _list_dir(iwc_path)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"could not list {iwc_path} on GitHub ({e}); check the catalog entry's url") from e

    files = {item["name"]: item["download_url"] for item in listing if item["type"] == "file"}

    ga_files = [n for n in files if n.endswith(".ga")]
    if not ga_files:
        raise RuntimeError(f"no .ga file found under {iwc_path} -- listing was: {sorted(files)}")
    if len(ga_files) > 1:
        # Prefer a name containing the directory's own slug if there's ambiguity.
        slug = iwc_path.rsplit("/", 1)[-1]
        ga_files.sort(key=lambda n: (slug not in n, n))

    workflow_path = output_dir / "workflow.ga"
    _download(files[ga_files[0]], workflow_path)

    test_files = [n for n in files if "test" in n.lower() and n.endswith((".yml", ".yaml"))]
    if test_files:
        _download(files[test_files[0]], output_dir / "workflow-tests.yml")

    if "README.md" in files:
        _download(files["README.md"], output_dir / "SOURCE_README.md")

    (output_dir / "SOURCE.txt").write_text(
        f"Fetched from {entry['url']}\ncatalog id: {entry_id}\nsource file: {ga_files[0]}\n"
    )

    return workflow_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog_id", help="id field from galaxy_pipeline_catalog.yaml")
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    workflow_path = fetch(args.catalog_id, args.output_dir)
    print(f"wrote {workflow_path}")


if __name__ == "__main__":
    main()
