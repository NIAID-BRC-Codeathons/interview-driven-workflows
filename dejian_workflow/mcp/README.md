# MCP Servers

Configuration for the MCP servers the interview grounds against (Goals 2
and 3).

- `servers.yaml` — connection details for the BRC Analytics MCP server and,
  once a partner is confirmed, a second resource center's MCP server for
  the portability run. Do not commit credentials/tokens here — use
  environment variable references and keep actual secrets in a local,
  gitignored `.env`.

The portability run (Goal 3) is just this same config with a second entry
pointed at a different center — the interview and runtime code should not
need to change to support it. If it does, that's exactly the "integration
friction" the portability report is supposed to capture.
