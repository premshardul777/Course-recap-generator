# PLAN: Course Recap Generator

> Authored before implementation by Claude (in a chat session) after reading the assignment PDF and probing the
> build environment (see docs/planning-output.md). It was NOT produced in OpenCode's Plan agent; see
> docs/plan-mode-prompt.md to produce that evidence on your own machine.

| Decision | Choice | Reason |
|---|---|---|
| Harness | **OpenCode** | Free/open, supports project-level agents, skills, commands and MCP via plain files; installable via npm and verifiable with `opencode agent list`, `opencode debug skill`, `opencode mcp list` |
| PDF reading | MCP tool `extract_pdf` (PyMuPDF), per-page text, saved to `extracted.md` | Deterministic, keeps page numbers for citations; warns if the PDF is scanned |
| Content structure | Per-**topic** (3-8 groups of slides), with page refs | Per-slide is too long; whole-deck too vague |
| Summary | Main agent writes from `concepts.md` + extracted text only | Source-grounded, reviewable |
| Diagram | Mermaid `graph TD` concept map (10-25 nodes), edges labelled with a fixed verb set | Concepts and relationships are what a recap needs; Mermaid is text, so it is reviewable |
| Diagram generation | Agent writes `.mmd`; MCP tool `render_diagram` (mermaid-cli) renders PNG+SVG and returns parser errors | Rendering is a real outside capability; one retry allowed |
| Review | Sub-agent `summary-reviewer` (read-only) checks coverage, unsupported claims, accuracy, diagram faithfulness | Independent context from the writer |
| MCP server | One local server `pdf-recap` (2 tools) | Simplest reliable option |
| Skill | `extract-key-concepts` (fixed output format, page citations, fixed relationship verbs) | Reusable on any deck |
| Interface | CLI (`app/recap.py`) wrapping `opencode run --command recap` | Most reliable to demo; avoids UI/harness integration risk |
| Loop policy | Single pass; one render retry; reviewer called once; fixes applied once | Assignment: no open-ended loop |

## Workflow
PDF -> MCP `extract_pdf` -> skill `extract-key-concepts` -> `summary.md` -> `diagram.mmd` -> MCP `render_diagram`
-> sub-agent `summary-reviewer` -> apply corrections once -> `recap.md`

## Implementation order (followed)
1. MCP server + tests  2. Skill, sub-agent, `/recap` command in `.opencode/`  3. Validate harness config
4. CLI wrapper with evidence log  5. Docs, README, checklist
