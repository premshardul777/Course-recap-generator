# MCP server: `pdf-recap`
- **File:** `mcp/pdf_server.py` (stdio, Python, PyMuPDF + mermaid-cli)
- **Config:** `opencode.json` -> `mcp.pdf-recap` (`python3 mcp/pdf_server.py`)
- **Why needed:** the model cannot read PDFs or render diagrams by itself; both are real external capabilities.
- **Tools:** `extract_pdf(pdf_path, output_dir)` and `render_diagram(mermaid_path, output_basename)`.
- **How the agent calls it:** OpenCode exposes them as `pdf-recap_extract_pdf` and `pdf-recap_render_diagram`; steps 1 and 5 of `.opencode/commands/recap.md` call them.
- **Tested example** (`python examples/test_mcp_client.py examples/sample-input.pdf out/ diagram.mmd`):
  `extract_pdf -> {'file': 'sample-input.pdf', 'pages': 5, 'chars': 974, 'scanned_warning': False}` and
  `render_diagram -> {"ok": true, "png": "...png", "svg": "...svg"}`; invalid Mermaid returns `{"ok": false, "error": "Parse error on line 3 ..."}`.
- Verified: `opencode mcp list` shows `pdf-recap connected`.
