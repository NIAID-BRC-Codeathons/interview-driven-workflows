#!/usr/bin/env bash
# Execute the workflow against real data via Planemo.
#
# Usage: scripts/run_workflow_tests.sh <path-to-workflow.ga>
#
# Planemo auto-discovers the test file by naming convention: a workflow at
# <dir>/<name>.ga is tested against <dir>/<name>-tests.yml if present (this
# is what fetch_iwc_workflow.py's output already matches: workflow.ga +
# workflow-tests.yml). There is no separate flag to point at a test file
# explicitly -- --test_data is for tool test-data directories, not this.
#
# Needs one of, checked in this order:
#   1. GALAXY_URL + GALAXY_USER_KEY env vars -- runs against an existing
#      Galaxy instance (e.g. usegalaxy.org, or your own). Fastest option if
#      you already have one.
#   2. GALAXY_ROOT env var -- a local Galaxy source checkout.
#   3. Neither set -- falls back to `--install_galaxy`, which downloads and
#      configures a disposable Galaxy. This works with no setup but is slow
#      (many minutes) and needs several GB of disk; expect it on first run.
#
# This mirrors exactly what IWC's own CI does to regression-test these
# workflows (see https://github.com/galaxyproject/iwc) -- it is the real
# test runner referenced in PROPOSAL.md, not a placeholder.

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

test_file="${WORKFLOW%.ga}-tests.yml"
if [[ ! -f "$test_file" ]]; then
  echo "warning: no ${test_file} found alongside the workflow -- planemo will" >&2
  echo "report 'no tests' rather than actually exercising the workflow." >&2
fi

args=(test)

if [[ -n "${GALAXY_URL:-}" && -n "${GALAXY_USER_KEY:-}" ]]; then
  echo "Testing against external Galaxy: ${GALAXY_URL}" >&2
  args+=(--engine external_galaxy --galaxy_url "$GALAXY_URL" --galaxy_user_key "$GALAXY_USER_KEY")
elif [[ -n "${GALAXY_ROOT:-}" ]]; then
  echo "Testing against local Galaxy checkout: ${GALAXY_ROOT}" >&2
  args+=(--galaxy_root "$GALAXY_ROOT")
else
  echo "No GALAXY_URL/GALAXY_USER_KEY or GALAXY_ROOT set -- falling back to" >&2
  echo "--install_galaxy (downloads a disposable Galaxy; slow on first run)." >&2
  args+=(--install_galaxy)
fi

args+=("$WORKFLOW")

planemo "${args[@]}"
