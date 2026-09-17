#!/usr/bin/env python3
"""Real MCP client for galaxyproject/galaxy-mcp -- Goal 1/2's "MCP-native"
requirement, done for real rather than reimplemented.

This spawns the actual `galaxy-mcp` server (github.com/galaxyproject/galaxy-mcp)
as a subprocess over stdio and calls its tools via the standard MCP protocol
(through the `fastmcp` client, since that's what galaxy-mcp is built on).
It is a genuine MCP integration, not a re-implementation of what galaxy-mcp
does -- see PROPOSAL.md and docs/ for why this matters: galaxy-mcp searches
the full, live IWC registry (via BM25) rather than our curated ~20-workflow
catalog, and its `import_workflow_from_iwc`/`invoke_workflow` tools talk to
a real Galaxy instance.

Requires: `pip install galaxy-mcp fastmcp` (see requirements.txt) and the
`galaxy-mcp` console script on PATH (installed by the galaxy-mcp package).
No credentials needed for search/recommend -- only `import_workflow` and
`invoke_workflow` need GALAXY_URL + a Galaxy API key (same credentials
already used by run_workflow_tests.sh).
"""

import asyncio
import json
import os
from typing import Any

from fastmcp import Client
from fastmcp.client.transports import StdioTransport


def _make_transport() -> StdioTransport:
    env = {}
    if os.environ.get("GALAXY_URL"):
        env["GALAXY_URL"] = os.environ["GALAXY_URL"]
    if os.environ.get("GALAXY_API_KEY"):
        env["GALAXY_API_KEY"] = os.environ["GALAXY_API_KEY"]
    return StdioTransport(command="galaxy-mcp", args=[], env=env or None)


async def _call_tool(name: str, arguments: dict[str, Any]) -> dict:
    """Connect to galaxy-mcp, call one tool, disconnect. Returns parsed JSON."""
    client = Client(_make_transport())
    async with client:
        result = await client.call_tool(name, arguments)
        text = "".join(getattr(block, "text", "") for block in result.content)
        return json.loads(text)


def recommend_workflows(intent: str, limit: int = 5) -> list[dict]:
    """Real BM25 search against the full, live IWC registry manifest.

    No Galaxy credentials required -- this only reads the public
    iwc.galaxyproject.org manifest. Returns the "data" list from
    galaxy-mcp's recommend_iwc_workflows tool: each entry has trsID, name,
    description, tags, categories, tools_used, step_count, authors, and
    match_score (higher = more relevant).
    """
    result = asyncio.run(_call_tool("recommend_iwc_workflows", {"intent": intent, "limit": limit}))
    return result.get("data", [])


def search_workflows(query: str) -> list[dict]:
    """Substring search (name/description/tags/readme) against the live IWC manifest."""
    result = asyncio.run(_call_tool("search_iwc_workflows", {"query": query}))
    return result.get("data", [])


def get_workflow_details(trs_id: str) -> dict:
    """Full details (including readme) for one live-registry workflow by trsID."""
    result = asyncio.run(_call_tool("get_iwc_workflow_details", {"trs_id": trs_id}))
    return result.get("data", {})


def import_workflow(trs_id: str) -> dict:
    """Import a live-registry workflow directly into a real Galaxy instance.

    Requires GALAXY_URL + GALAXY_API_KEY env vars -- an actual Galaxy
    account, same credential as run_workflow_tests.sh's GALAXY_USER_KEY.
    """
    result = asyncio.run(_call_tool("import_workflow_from_iwc", {"trs_id": trs_id}))
    return result.get("data", {})


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_rec = sub.add_parser("recommend", help="BM25 search the live IWC registry by intent")
    p_rec.add_argument("intent")
    p_rec.add_argument("--limit", type=int, default=5)

    p_search = sub.add_parser("search", help="Substring search the live IWC registry")
    p_search.add_argument("query")

    p_details = sub.add_parser("details", help="Get full details for a trsID")
    p_details.add_argument("trs_id")

    args = parser.parse_args()

    if args.command == "recommend":
        results = recommend_workflows(args.intent, limit=args.limit)
    elif args.command == "search":
        results = search_workflows(args.query)
    elif args.command == "details":
        results = get_workflow_details(args.trs_id)

    json.dump(results, __import__("sys").stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
