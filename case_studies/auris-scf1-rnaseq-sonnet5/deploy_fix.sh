#!/bin/bash
set -euo pipefail
curl -s -X PUT "https://usegalaxy.org/api/workflows/575e9ee747b2031f" \
  -H "x-api-key: $(cat /Users/scottcain/git/dms/draft-manuscript-galaxy/galaxy.key)" \
  -H "Content-Type: application/json" \
  --data @/private/tmp/claude-502/-Users-scottcain-git-dms/852e3f3f-024b-408f-81ff-cf3e995da91f/scratchpad/update_workflow_payload_fixed.json
echo
