# Architecture
```
user -> app/recap.py -> opencode run --command recap <pdf>
   OpenCode main agent (.opencode/commands/recap.md)
     1 MCP pdf-recap.extract_pdf -> extracted.md
     2 skill extract-key-concepts -> concepts.md
     3 summary.md   4 diagram.mmd
     5 MCP pdf-recap.render_diagram -> diagram.png/.svg
     6 sub-agent summary-reviewer -> review.md
     7 apply fixes once   8 recap.md
app/recap.py -> outputs/<deck>/run-log.md (evidence from event stream)
```
Single pass: one render retry, one review, one round of fixes.
