# Sub-agent: `summary-reviewer`
- **Declared in:** `.opencode/agents/summary-reviewer.md` (`mode: subagent`); verified by `opencode agent list`.
- **Role:** independent, read-only reviewer (edit, bash, webfetch denied).
- **Inputs:** paths to `extracted.md`, `concepts.md`, `summary.md`, `diagram.mmd`.
- **Checks:** missing concepts, unsupported claims, inaccuracies, diagram faithfulness.
- **Output:** fixed-format REVIEW REPORT ending in a verdict (APPROVED / APPROVED WITH CORRECTIONS / REJECTED), saved to `review.md`.
- **Invoked:** step 6 of `/recap` via OpenCode's Task tool; called once. `app/recap.py` checks the event stream for `summary-reviewer`.
