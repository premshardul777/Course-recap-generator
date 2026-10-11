#!/usr/bin/env python3
"""Setup checker for the Course Recap Generator.

    python app/doctor.py                      # check everything (uses no model quota)
    python app/doctor.py --ping google/gemini-3.5-flash   # also send ONE tiny request to a model
    python app/doctor.py --reviewer-model google/gemini-3.5-flash   # set the sub-agent's model
    python app/doctor.py --reviewer-model ""  # remove it (reviewer inherits the main model)

Prints [OK] / [WARN] / [FAIL] with a fix hint. ASCII only so it works in any Windows console.
"""
import argparse, importlib.util, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENT = ROOT / ".opencode" / "agents" / "summary-reviewer.md"
MODEL_RE = re.compile(r"^[\w.\-]+/[\w.\-:]+$")
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def _frontmatter(text: str):
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        raise ValueError("agent file has no frontmatter")
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        raise ValueError("agent file frontmatter is not closed")
    return lines, end


def get_reviewer_model(path: Path = AGENT) -> str:
    """Model pinned for the summary-reviewer sub-agent ('' = inherits the main agent's model)."""
    lines, end = _frontmatter(path.read_text(encoding="utf-8"))
    for line in lines[1:end]:
        m = re.match(r"\s*model\s*:\s*(\S+)", line)
        if m:
            return m.group(1)
    return ""


def set_reviewer_model(model: str, path: Path = AGENT) -> bool:
    """Pin (or with '' remove) the reviewer's model. Returns True if the file changed."""
    model = model.strip()
    if model and not MODEL_RE.match(model):
        raise ValueError(f"'{model}' is not a valid provider/model name (example: google/gemini-3.5-flash)")
    lines, end = _frontmatter(path.read_text(encoding="utf-8"))
    idx = next((i for i in range(1, end) if re.match(r"\s*model\s*:", lines[i])), None)
    if idx is not None:
        if not model:
            del lines[idx]
        elif lines[idx] == f"model: {model}":
            return False
        else:
            lines[idx] = f"model: {model}"
    elif model:
        pos = next((i for i in range(1, end) if re.match(r"\s*mode\s*:", lines[i])), end - 1)
        lines.insert(pos + 1, f"model: {model}")
    else:
        return False
    path.write_text("\n".join(lines), encoding="utf-8")
    return True


def _run(cmd, timeout=60):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=timeout, cwd=ROOT)
        return r.returncode, ANSI.sub("", (r.stdout or "") + (r.stderr or ""))
    except subprocess.TimeoutExpired:
        return 124, "timed out"
    except OSError as e:
        return 999, str(e)


class Report:
    def __init__(self):
        self.fails = self.warns = 0

    def add(self, level: str, msg: str, hint: str = ""):
        self.fails += level == "FAIL"
        self.warns += level == "WARN"
        print(f"[{level}] {msg}")
        if hint and level != "OK":
            print(f"       -> {hint}")


def check_all(rep: Report, ping: str = ""):
    py = sys.version_info
    rep.add("OK" if py >= (3, 10) else "FAIL", f"Python {py.major}.{py.minor}.{py.micro}", "Python 3.10 or newer is required (the mcp package needs it).")
    for mod, pipname in (("pymupdf", "pymupdf"), ("mcp", "mcp"), ("streamlit", "streamlit")):
        ok = importlib.util.find_spec(mod) is not None
        rep.add("OK" if ok else "FAIL", f"Python package {pipname}", "Run: pip install -r requirements.txt")

    node = shutil.which("node")
    rep.add("OK" if node else "FAIL", "Node.js found" if node else "Node.js not found", "Install Node.js LTS from nodejs.org (needed for OpenCode and mermaid-cli).")

    oc = shutil.which(os.environ.get("OPENCODE_BIN", "opencode"))
    if not oc:
        rep.add("FAIL", "OpenCode not found", "Run: npm i -g opencode-ai@1.18.34   (or set OPENCODE_BIN to its full path)")
        return
    _, out = _run([oc, "--version"])
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", out)
    ver = m.group(0) if m else out.strip()[:40]
    if m and int(m.group(1)) == 1:
        rep.add("OK", f"OpenCode {ver}")
    else:
        rep.add("WARN", f"OpenCode {ver}: this project was tested with 1.18.x",
                "OpenCode 2.x changed its commands and did not load this config in testing. Run: npm i -g opencode-ai@1.18.34 --force")

    mmdc = shutil.which("mmdc")
    if not mmdc:
        rep.add("FAIL", "mermaid-cli (mmdc) not found", "Run: npm i -g @mermaid-js/mermaid-cli  (Windows: use an Administrator PowerShell if you get EPERM)")
    else:
        sys.path.insert(0, str(ROOT / "mcp"))
        import pdf_server
        with tempfile.TemporaryDirectory() as d:
            src = Path(d) / "t.mmd"
            src.write_text("graph TD\n  A[Test] --> B[Render]\n", encoding="utf-8")
            res = json.loads(pdf_server.render_diagram(str(src)))
        if res.get("ok"):
            rep.add("OK", "Diagram rendering works (mermaid-cli + Chrome)")
        else:
            rep.add("FAIL", "Diagram rendering failed: " + str(res.get("error", ""))[:160],
                    "Install a browser for it: npx -y puppeteer browsers install chrome-headless-shell")

    sample = ROOT / "examples" / "sample-input.pdf"
    try:
        sys.path.insert(0, str(ROOT / "mcp"))
        import pdf_server
        res = json.loads(pdf_server.extract_pdf(str(sample)))
        ok = res.get("pages") == 5 and not res.get("scanned_warning")
        rep.add("OK" if ok else "FAIL", "PDF extraction works" if ok else f"PDF extraction gave: {str(res)[:120]}")
    except Exception as e:  # noqa: BLE001
        rep.add("FAIL", f"PDF extraction crashed: {e}", "Run: pip install -r requirements.txt")

    cfg = ROOT / "opencode.json"
    try:
        exe = json.loads(cfg.read_text(encoding="utf-8"))["mcp"]["pdf-recap"]["command"][0]
        if not shutil.which(exe):
            alt = next((a for a in ("python", "python3", "py") if shutil.which(a)), None)
            rep.add("FAIL", f"opencode.json starts the MCP server with '{exe}', which is not on this computer",
                    f"Edit opencode.json and change \"{exe}\" to \"{alt}\"." if alt else "Install Python and put it on PATH.")
    except (OSError, KeyError, ValueError, IndexError) as e:
        rep.add("FAIL", f"Cannot read the MCP entry in opencode.json: {e}")

    code, out = _run([oc, "mcp", "list"])
    if "pdf-recap" in out and "connected" in out and "disconnected" not in out:
        rep.add("OK", "OpenCode sees the pdf-recap MCP server and it is connected")
    elif "No MCP servers" in out:
        rep.add("FAIL", "OpenCode found no MCP servers", "Run this from the project folder (the one containing opencode.json). OpenCode 2.x may also ignore the config; use 1.18.34.")
    else:
        rep.add("FAIL", "pdf-recap MCP server is not connected: " + out.strip()[-200:], "Check the 'command' line in opencode.json (python vs python3).")

    code, out = _run([oc, "providers", "list"])
    m = re.search(r"(\d+)\s+credentials?", out)
    if m and int(m.group(1)) > 0:
        rep.add("OK", f"{m.group(1)} model login(s) saved in OpenCode")
    else:
        rep.add("WARN", "No model login found in OpenCode", "Run: opencode providers login   (a free Google AI Studio key works; see docs/run-it-yourself.md)")

    rev = get_reviewer_model()
    rep.add("OK", f"Reviewer sub-agent model: {rev}" if rev else "Reviewer sub-agent model: (inherits the main model)")
    if rev == "":
        rep.add("WARN", "Reviewer inherits the main model",
                "If you use a free opencode/* model as the main model, the reviewer fails. Fix: python app/doctor.py --reviewer-model google/gemini-3.5-flash")

    if ping:
        code, out = _run([oc, "run", "--model", ping, "Reply with the single word: ready"], timeout=120)
        low = out.lower()
        if "ready" in low and "error" not in low[:200]:
            rep.add("OK", f"Model {ping} replied (used 1 request)")
        elif "quota" in low or "429" in low:
            rep.add("FAIL", f"Model {ping}: daily free quota used up", "Wait for the reset time shown in the message, or try another model from: opencode models")
        elif "model turn" in low:
            rep.add("FAIL", f"Model {ping} rejects this request style", "Try google/gemini-3.5-flash instead.")
        else:
            rep.add("FAIL", f"Model {ping} did not answer: {out.strip()[-250:]}", "Check the name with: opencode models, and your login with: opencode providers login")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ping", metavar="MODEL", default="", help="send one tiny request to this model")
    ap.add_argument("--reviewer-model", metavar="MODEL", default=None, help="set (or '' to clear) the reviewer sub-agent's model")
    a = ap.parse_args()
    if a.reviewer_model is not None:
        try:
            changed = set_reviewer_model(a.reviewer_model)
        except ValueError as e:
            print(f"[FAIL] {e}"); return 2
        print(f"[OK] reviewer model {'set to ' + a.reviewer_model if a.reviewer_model else 'cleared'}" + ("" if changed else " (no change needed)"))
    rep = Report()
    check_all(rep, a.ping)
    print(f"\n{rep.fails} problem(s), {rep.warns} warning(s).")
    return 1 if rep.fails else 0


if __name__ == "__main__":
    sys.exit(main())
