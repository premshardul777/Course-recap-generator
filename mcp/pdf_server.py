#!/usr/bin/env python3
"""pdf-recap MCP server (stdio).

Two real capabilities that live OUTSIDE the agent harness:
  1. extract_pdf     - read a PDF from disk and return per-page text (PyMuPDF)
  2. render_diagram  - validate + render Mermaid source to PNG/SVG (mermaid-cli)

Run directly:  python mcp/pdf_server.py   (speaks MCP over stdio)
"""
import json
import os
import shutil
import subprocess
import tempfile
from glob import glob
from pathlib import Path

import pymupdf
try:  # mcp >= 2.0
    from mcp.server.mcpserver import MCPServer as _Server
except ImportError:  # mcp 1.x
    from mcp.server.fastmcp import FastMCP as _Server

mcp = _Server("pdf-recap")


@mcp.tool()
def extract_pdf(pdf_path: str, output_dir: str = "") -> str:
    """Extract text from a PDF, page by page.

    Returns JSON: {file, pages, chars, scanned_warning, content: [{page, text}]}.
    If output_dir is given, also writes extracted.md there so later steps
    (and the reviewer sub-agent) can read the exact source text.
    """
    p = Path(pdf_path).expanduser()
    if not p.is_file():
        return json.dumps({"error": f"file not found: {pdf_path}"})
    doc = pymupdf.open(p)
    pages = [{"page": i + 1, "text": pg.get_text("text").strip()} for i, pg in enumerate(doc)]
    chars = sum(len(x["text"]) for x in pages)
    result = {
        "file": p.name,
        "pages": len(pages),
        "chars": chars,
        "scanned_warning": chars < 40 * max(len(pages), 1),
        "content": pages,
    }
    if output_dir:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        md = [f"# Extracted text: {p.name}", ""]
        for x in pages:
            md += [f"## Page {x['page']}", "", x["text"] or "_(no extractable text)_", ""]
        (out / "extracted.md").write_text("\n".join(md), encoding="utf-8")
        result["written_to"] = str(out / "extracted.md")
    return json.dumps(result, ensure_ascii=False)


def _find_chrome() -> str | None:
    """mermaid-cli needs a Chrome. Honour env vars, else look in common places."""
    env = os.environ.get("PUPPETEER_EXECUTABLE_PATH") or os.environ.get("CHROME_PATH")
    if env and Path(env).exists():
        return env
    for pat in ("~/.cache/puppeteer/chrome/*/chrome-linux64/chrome",
                "~/.cache/puppeteer/chrome-headless-shell/*/*/chrome-headless-shell",
                "~/.cache/puppeteer/chrome/*/chrome-mac*/*/Contents/MacOS/Google Chrome for Testing",
                "/opt/pw-browsers/chromium-*/chrome-linux/chrome"):
        hits = sorted(glob(str(Path(pat).expanduser())))
        if hits:
            return hits[-1]
    return None


@mcp.tool()
def render_diagram(mermaid_path: str, output_basename: str = "") -> str:
    """Render a Mermaid (.mmd) file to PNG and SVG.

    Returns JSON {ok, png, svg} on success or {ok:false, error} with the Mermaid
    parser message, so the agent can fix its syntax and retry (max 2 tries).
    """
    src = Path(mermaid_path).expanduser()
    if not src.is_file():
        return json.dumps({"ok": False, "error": f"file not found: {mermaid_path}"})
    exe = shutil.which("mmdc")
    if not exe:
        return json.dumps({"ok": False, "error": "mmdc not installed: npm i -g @mermaid-js/mermaid-cli"})
    base = Path(output_basename) if output_basename else src.with_suffix("")
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        cfg = {"args": ["--no-sandbox", "--disable-setuid-sandbox"]}
        chrome = _find_chrome()
        if chrome:
            cfg["executablePath"] = chrome
        json.dump(cfg, f)
        pcfg = f.name
    outs, errs = {}, []
    for ext in ("png", "svg"):
        target = f"{base}.{ext}"
        args = [exe, "-i", str(src), "-o", target, "-p", pcfg, "-b", "white"]
        if ext == "png":
            args += ["-s", "2"]
        r = subprocess.run(args, capture_output=True, text=True, env=dict(os.environ), timeout=120)
        if r.returncode == 0 and Path(target).exists():
            outs[ext] = target
        else:
            errs.append((r.stderr or r.stdout).strip()[:600])
    os.unlink(pcfg)
    if errs:
        return json.dumps({"ok": False, "error": errs[0]})
    return json.dumps({"ok": True, **outs})


if __name__ == "__main__":
    mcp.run()
