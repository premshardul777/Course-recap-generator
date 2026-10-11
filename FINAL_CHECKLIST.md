# Final checklist (honest audit)
Status meanings: PASS = verified here; PARTIAL = built and config-validated but needs your run; FAIL = not met.

| Requirement | Implementation | Evidence | Status |
|---|---|---|---|
| Harness Codex/OpenCode | OpenCode; Claude Code is not used as the harness | `opencode.json`, `.opencode/`; CLI v1.18.34 loaded the config | PASS (config) |
| Planning phase / plan mode | `PLAN.md` written before code, but by Claude in chat; OpenCode plan agent was run afterwards | `PLAN.md`, `docs/planning-output.md` | **PARTIAL** - OpenCode plan-agent output is now recorded in `docs/planning-output.md`, but it was run after the build, so "planning before building" rests on `PLAN.md` (written before code) |
| ≥1 real MCP server | `pdf-recap` (2 tools) | `opencode mcp list` = connected; stdio tests in `examples/run-log.md` | PASS |
| MCP used by project | `/recap` steps 1 and 5 | `app/recap.py` checks event stream | PARTIAL - tools tested directly; not yet invoked by an LLM run |
| ≥1 harness sub-agent defined | `summary-reviewer` | `opencode agent list` | PASS |
| Sub-agent actually used | `/recap` step 6 | needs real run | **PARTIAL** |
| ≥1 custom skill defined | `extract-key-concepts` | `opencode debug skill` | PASS |
| Skill actually used | `/recap` step 2 | needs real run | **PARTIAL** |
| Summary generated | `summary.md` | only hand-written reference exists | **PARTIAL** |
| Diagram from course content, rendered | Mermaid via `render_diagram` | `examples/reference-run/diagram.png` (rendering real, content hand-written, synthetic deck) | PARTIAL |
| Reviewer checks summary + diagram | agent instructions | needs real run | PARTIAL |
| End-to-end run on a real course deck | `python app/recap.py deck.pdf` | **not done**: no real deck, no model access in sandbox | **FAIL (for you to run)** |
| Single pass, no loop | one retry/review/fix round | `recap.md` command | PASS |
| README + docs | present | `README.md`, `docs/` | PASS |
| No fake claims | reference outputs labelled | `examples/reference-run/README.md` | PASS |
| No secrets in repo | none; keys stay in OpenCode auth store | `.gitignore` | PASS |

## To finish (about 15 minutes)
1. Install per README; log in to a provider.
2. Run plan mode (docs/plan-mode-prompt.md), paste output.
3. `python app/recap.py <real course deck>.pdf`; confirm `outputs/<deck>/run-log.md` is all checked.
4. Copy that output to `examples/` and tick the PARTIAL rows.
