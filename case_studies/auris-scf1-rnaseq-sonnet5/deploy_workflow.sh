#!/bin/bash
# Deploy galaxy-workflow.gxwf.yml to usegalaxy.org workflow 575e9ee747b2031f.
#
# Two things this handles that a naive download/edit/upload round trip does not:
#
#   1. Tool Shed step `tool_id`s must be VERSIONED at deploy time. `download?style=ga`
#      emits them unversioned with `tool_version` alongside; re-importing that saves
#      cleanly and reports no step errors, but the workflow then CANNOT be invoked
#      ("required tools are not installed", naming tools that are installed). See
#      foundry-feedback.ledger.yml entry
#      `ga-download-normalizes-tool-id-producing-workflows-that-save-but-cannot-invoke`.
#   2. GalaxyUserTool steps resolve by `tool_uuid`, which gxformat2 does not model
#      (ledger `gxformat2-step-schema-does-not-model-tool-uuid-for-dynamic-tool-resolution`),
#      so the uuids are injected here. Update LEXICMAP_STREAMER_UUID after deploying a
#      new version of the UDT via POST /api/unprivileged_tools.
set -euo pipefail
cd "$(dirname "$0")"
KEY=$(cat galaxy.key)
WF_ID=575e9ee747b2031f
LEXICMAP_STREAMER_UUID=4c60cafe-59c7-4397-903a-66dc2b6ae739   # v1.0.2
DEDUP_UUID=c840abb7-d012-48ac-91eb-3f85f71444cf               # kmindex_hit_dedup_max_score v1.0.0
FLATTEN_UUID=2450bd91-b7fd-41f5-b982-ce9906c039dd             # flatten_gene_summary_json_to_row v1.0.0
PY=${PLANEMO_PYTHON:-$HOME/.local/share/uv/tools/planemo/bin/python}
OUT=$(mktemp -t wf_payload).json
"$PY" - "$OUT" <<PYEOF
import json,sys,yaml
from gxformat2 import python_to_workflow
ga=python_to_workflow(yaml.safe_load(open('galaxy-workflow.gxwf.yml')))
uu={'lexicmap_streamer':'$LEXICMAP_STREAMER_UUID',
    'kmindex_hit_dedup_max_score':'$DEDUP_UUID',
    'flatten_gene_summary_json_to_row':'$FLATTEN_UUID'}
for s in ga['steps'].values():
    tid=s.get('tool_id')
    if not tid: continue
    if tid in uu: s['tool_uuid']=uu[tid]
    v=s.get('tool_version')
    if 'toolshed' in tid and v and not tid.endswith(v):
        s['tool_id']=f"{tid}/{v}"          # see note 1 above
ga['name']='ΦX174 SRA Landscape & Spike-In Sieve (Workflow A)'
json.dump({'workflow':ga},open(sys.argv[1],'w'))
print('steps:',len(ga['steps']))
PYEOF
curl -s -X PUT "https://usegalaxy.org/api/workflows/$WF_ID" \
  -H "x-api-key: $KEY" -H "Content-Type: application/json" --data @"$OUT" \
  | "$PY" -c "import json,sys;d=json.load(sys.stdin);print('deployed version',d.get('version'),'|',len(d.get('steps',{})),'steps')"
rm -f "$OUT"
