# Course Recap Generator

Give it a course PDF; get a source-grounded summary, key concepts, a rendered concept diagram, and an independent review.
Built with **OpenCode** (the required agent harness) for the "Day 6 - AI Coding Techniques" assignment.

## Problem
Revising from slides is slow. This tool turns a deck into a recap and concept map in one clean pass.

## Architecture
```
PDF -> MCP extract_pdf -> skill extract-key-concepts -> summary.md -> diagram.mmd
    -> MCP render_diagram -> sub-agent summary-reviewer -> fixes (once) -> recap.md
```
Details: `docs/architecture.md`, decisions: `PLAN.md`.

| Component | Where | Used how |
|---|---|---|
| Harness | OpenCode (`opencode.json`, `.opencode/`) | runs the `/recap` command |
| MCP server `pdf-recap` | `mcp/pdf_server.py` | `extract_pdf`, `render_diagram` (docs/mcp.md) |
| Sub-agent `summary-reviewer` | `.opencode/agents/` | read-only review via Task tool (docs/sub-agent.md) |
| Skill `extract-key-concepts` | `.opencode/skills/` | fixed-format concept extraction (docs/custom-skill.md) |
| CLI | `app/recap.py` | runs OpenCode headlessly, writes `run-log.md` evidence |

## Install
```
npm i -g opencode-ai @mermaid-js/mermaid-cli
pip install -r requirements.txt
opencode providers login        # configure any model provider (API key stays in OpenCode's own store, never in this repo)
```
mermaid-cli needs Chrome (`npx puppeteer browsers install chrome-headless-shell`); the server auto-detects it.
On Windows use `python` instead of `python3` in `opencode.json`.

## Run
```
python app/recap.py path/to/your_deck.pdf [--model provider/model]
```
or interactively: `opencode`, then `/recap path/to/deck.pdf`.
Output: `outputs/<deck>/` with `extracted.md concepts.md summary.md diagram.mmd diagram.png diagram.svg review.md recap.md run-log.md`.

## Example
`examples/reference-run/` shows the expected output format on a synthetic deck. **Read its README: only the MCP extraction
and diagram rendering there are real; the rest was hand-written to illustrate the format.** A genuine run on your real deck is
still required (see FINAL_CHECKLIST.md).

## Limitations
- The full AI pipeline was not run in the build sandbox (no model credentials). Harness config, MCP server and rendering were tested separately.
- Text-layer PDFs only; scanned decks are rejected (no OCR). Images/charts in slides are not read.
- Quality depends on the chosen model; the reviewer reduces but does not eliminate errors.
- No web UI: a CLI was chosen for reliability.

## Why this design
One small MCP server for the two things a model cannot do (read PDFs, render diagrams), a skill for consistency across decks,
a read-only reviewer in its own context for independent checking, and a single-pass command to keep AI usage low.

## Run it yourself (free)
See docs/run-it-yourself.md for setup, and docs/ui-and-deployment.md for the web UI and deployment.