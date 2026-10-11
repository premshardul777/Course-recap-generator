#!/usr/bin/env python3
"""Course Recap Generator - CLI entry point (single pass, no loops).

    python app/recap.py path/to/deck.pdf [--model provider/model] [--timeout 900]

It runs OpenCode's `/recap` command headlessly (the harness does all the work:
MCP extraction -> skill -> summary -> diagram -> sub-agent review -> final recap),
saves the raw event stream, and writes outputs/<deck>/run-log.md with evidence of
which required components were really invoked.
"""
import argparse, datetime, os, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = {  # substring in OpenCode's JSON event stream -> what it proves
    "pdf-recap_extract_pdf": "MCP tool extract_pdf was called",
    "extract-key-concepts": "custom skill was loaded",
    "summary-reviewer": "sub-agent summary-reviewer was invoked",
    "pdf-recap_render_diagram": "MCP tool render_diagram was called",
}
EXPECTED = ["extracted.md", "concepts.md", "summary.md", "diagram.mmd", "diagram.png", "review.md", "recap.md"]


def preflight(opencode: str) -> list[str]:
    problems = []
    if not shutil.which(opencode):
        problems.append("OpenCode not found. Install: npm i -g opencode-ai  (or set OPENCODE_BIN)")
    if not shutil.which("mmdc"):
        problems.append("mermaid-cli not found. Install: npm i -g @mermaid-js/mermaid-cli")
    try:
        import pymupdf, mcp  # noqa: F401
    except ImportError as e:
        problems.append(f"Python deps missing ({e.name}). Run: pip install -r requirements.txt")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--model", help="provider/model, e.g. anthropic/claude-sonnet-4-5 (else OpenCode default)")
    ap.add_argument("--timeout", type=int, default=900)
    a = ap.parse_args()

    pdf = Path(a.pdf).expanduser().resolve()
    if not pdf.is_file() or pdf.suffix.lower() != ".pdf":
        print(f"ERROR: not a PDF file: {pdf}"); return 2
    opencode = os.environ.get("OPENCODE_BIN", "opencode")
    problems = preflight(opencode)
    if problems:
        print("Preflight failed:\n  - " + "\n  - ".join(problems)); return 2

    out = ROOT / "outputs" / pdf.stem
    out.mkdir(parents=True, exist_ok=True)
    cmd = [shutil.which(opencode) or opencode, "run", "--format", "json", "--command", "recap"]
    if a.model:
        cmd += ["--model", a.model]
    cmd += [str(pdf)]
    print("Running:", " ".join(cmd)); started = datetime.datetime.now()
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=a.timeout)
        events, code, note = r.stdout, r.returncode, r.stderr[-800:]
    except subprocess.TimeoutExpired as e:
        events, code, note = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or ""), 124, f"timed out after {a.timeout}s"
    (out / "opencode-events.jsonl").write_text(events, encoding="utf-8")

    seen = {k: False for k in EVIDENCE}
    import json
    for ln in events.splitlines():
        try:
            part = json.loads(ln).get("part", {})
        except ValueError:
            continue
        st = part.get("state") or {}
        if part.get("type") != "tool" or st.get("status") != "completed":
            continue
        tool, inp = part.get("tool", ""), st.get("input") or {}
        if tool in ("pdf-recap_extract_pdf", "pdf-recap_render_diagram"):
            seen[tool] = True
        if "extract-key-concepts" in json.dumps(inp):
            seen["extract-key-concepts"] = True
        if tool == "task" and inp.get("subagent_type") == "summary-reviewer":
            seen["summary-reviewer"] = True
    present = {f: (out / f).is_file() for f in EXPECTED}
    ok = code == 0 and all(seen.values()) and all(present.values())
    log = [f"# Run log: {pdf.name}", "", f"- Started: {started:%Y-%m-%d %H:%M:%S}",
           f"- Command: `{' '.join(cmd)}`", f"- Exit code: {code}", f"- Notes: {note or 'none'}", "",
           "## Component evidence (string found in OpenCode event stream)"]
    log += [f"- [{'x' if seen[k] else ' '}] {v} (`{k}`)" for k, v in EVIDENCE.items()]
    log += ["", "## Output files"] + [f"- [{'x' if present[f] else ' '}] {f}" for f in EXPECTED]
    log += ["", f"## Result: {'PASS' if ok else 'INCOMPLETE - see unchecked items'}"]
    (out / "run-log.md").write_text("\n".join(log) + "\n", encoding="utf-8")
    print("\n".join(log[-(len(EXPECTED) + len(EVIDENCE) + 6):]))
    print(f"\nOutputs: {out}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
