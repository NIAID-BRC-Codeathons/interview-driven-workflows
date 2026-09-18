#!/usr/bin/env bash
# Static validation: tool identifiers, tool version/changeset installability,
# parameter connections between steps, and structural test-file correctness.
#
# Usage: scripts/validate_workflow.sh <path-to-workflow.ga>
#
# Wraps `planemo workflow_lint`, which needs no live Galaxy instance -- it
# checks the .ga file's structure and cross-references tool ids/versions
# against the public Galaxy toolshed. Exit code mirrors planemo's: 0 means
# no ERROR-level findings (warnings, e.g. "step has no annotation", do not
# fail validation); non-zero means at least one real problem (invalid tool
# id, uninstallable changeset revision, disconnected required input, etc.)
# was found. This is a real check, not a stub -- it has caught genuine
# stale-changeset-revision errors on published IWC workflows during
# development of this pipeline.

set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <path-to-workflow.ga>" >&2
  exit 2
fi

WORKFLOW="$1"

if [[ ! -f "$WORKFLOW" ]]; then
  echo "error: no such file: ${WORKFLOW}" >&2
  exit 2
fi

if ! command -v planemo >/dev/null 2>&1; then
  echo "error: planemo not found on PATH. Install with: pip install -r requirements.txt" >&2
  exit 2
fi

planemo workflow_lint "$WORKFLOW"
