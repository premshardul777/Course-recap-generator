# What was actually run in the build sandbox (2026-10-06)
| Test | Result |
|---|---|
| MCP stdio client -> `extract_pdf` on synthetic deck (mcp 1.x and 2.x) | PASS |
| MCP `render_diagram` valid Mermaid -> PNG+SVG | PASS |
| MCP `render_diagram` invalid Mermaid -> parser error returned | PASS |
| `opencode agent list` shows `summary-reviewer (subagent)` | PASS |
| `opencode debug skill` lists `extract-key-concepts` | PASS |
| `opencode debug config` shows command `recap` | PASS |
| `opencode mcp list` -> `pdf-recap connected` | PASS |
| `app/recap.py` headless run through OpenCode | **NOT COMPLETED**: no model credentials/network; wrapper reported INCOMPLETE correctly |
| Full LLM pipeline (skill, sub-agent invocation, summary) | **NOT RUN** here. Run on your machine. |
