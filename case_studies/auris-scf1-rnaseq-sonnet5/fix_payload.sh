#!/bin/bash
set -euo pipefail
jq '. + {"exact_tools": false, "allow_missing_tools": true}' \
  /private/tmp/claude-502/-Users-scottcain-git-dms/852e3f3f-024b-408f-81ff-cf3e995da91f/scratchpad/update_workflow_payload.json \
  > /private/tmp/claude-502/-Users-scottcain-git-dms/852e3f3f-024b-408f-81ff-cf3e995da91f/scratchpad/update_workflow_payload_fixed.json
echo "wrote update_workflow_payload_fixed.json"
