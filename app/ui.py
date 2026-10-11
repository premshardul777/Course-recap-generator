"""Streamlit front-end for the Course Recap Generator.

    streamlit run app/ui.py

Generation is delegated to app/recap.py (which drives OpenCode: MCP + skill + sub-agent).
If OpenCode / mermaid-cli are not installed, or RECAP_DEMO_ONLY=1 is set (use this on public
deployments), the app runs in read-only demo mode and shows a saved example run instead.
"""
import io, os, re, subprocess, sys, tempfile, time, zipfile
from pathlib import Path

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parent
sys.path.insert(0, str(APP_DIR))
import doctor  # noqa: E402
import recap  # noqa: E402

STEPS = [  # (file that appears when the step finishes, label, component)
    ("extracted.md", "Extract PDF text", "MCP"),
    ("concepts.md", "Key concepts", "Skill"),
    ("summary.md", "Summary", "Agent"),
    ("diagram.png", "Concept diagram", "MCP"),
    ("review.md", "Independent review", "Sub-agent"),
    ("recap.md", "Final recap", "Agent"),
]
def _demo_flag() -> bool:
    """Demo mode via env var or (on Streamlit Cloud) a secret named RECAP_DEMO_ONLY."""
    if os.environ.get("RECAP_DEMO_ONLY") == "1":
        return True
    try:
        return str(st.secrets.get("RECAP_DEMO_ONLY", "")) == "1"
    except Exception:  # no secrets file
        return False


DEMO_ONLY = _demo_flag()

st.set_page_config(page_title="Course Recap Generator", page_icon="🎓", layout="wide")
st.markdown("""
<style>
.block-container {padding-top: 3.2rem; max-width: 1150px;}
.hero {background: linear-gradient(120deg,#4f46e5 0%,#0ea5a4 100%); color:#fff; padding:1.6rem 1.8rem;
       border-radius:18px; margin-bottom:1.2rem;}
.hero h1 {color:#fff; margin:0 0 .3rem 0; font-size:2rem;}
.hero p {margin:0; opacity:.92; font-size:1.02rem;}
.pipe {display:flex; gap:.5rem; flex-wrap:wrap; margin-top:.9rem;}
.pill {background:rgba(255,255,255,.18); border-radius:999px; padding:.18rem .75rem; font-size:.82rem;}
.step {display:flex; align-items:center; gap:.6rem; padding:.45rem .8rem; border-radius:10px; margin:.25rem 0;
       background:#f3f4fb; font-size:.95rem;}
.step.done {background:#e7f8ee;} .step.now {background:#fff4d6;}
.tag {margin-left:auto; font-size:.72rem; background:#e0e3f5; border-radius:6px; padding:.05rem .45rem;}
.chip {display:inline-block; padding:.15rem .6rem; border-radius:999px; font-size:.8rem; margin:.15rem .3rem .15rem 0;}
.ok {background:#e7f8ee; color:#12683a;} .bad {background:#fde8e8; color:#9b1c1c;}
.note {border-left:4px solid #4f46e5; background:#f3f4fb; padding:.7rem 1rem; border-radius:6px; margin:.6rem 0;}
</style>
<div class="hero">
  <h1>🎓 Course Recap Generator</h1>
  <p>Upload a course PDF and get a source-grounded summary, a concept diagram, and an independent review.</p>
  <div class="pipe"><span class="pill">PDF</span><span class="pill">MCP extraction</span><span class="pill">Skill: key concepts</span>
  <span class="pill">Summary</span><span class="pill">Mermaid diagram</span><span class="pill">Sub-agent review</span></div>
</div>
""", unsafe_allow_html=True)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""


def slug(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", Path(name).stem).strip("_")[:40] or "deck"


def env_problems() -> list[str]:
    if DEMO_ONLY:
        return ["Live generation is switched off on this deployment (demo mode)."]
    return recap.preflight(os.environ.get("OPENCODE_BIN", "opencode"))


def example_folder():
    for name in ("real-run", "reference-run"):
        p = ROOT / "examples" / name
        if (p / "recap.md").is_file():
            return p
    return None


def step_html(done: set, running: bool) -> str:
    first_open = next((i for i, s in enumerate(STEPS) if s[0] not in done), None)
    rows = []
    for i, (_, label, comp) in enumerate(STEPS):
        cls, icon = ("done", "✅") if STEPS[i][0] in done else (("now", "⏳") if running and i == first_open else ("", "⚪"))
        rows.append(f'<div class="step {cls}">{icon} {label}<span class="tag">{comp}</span></div>')
    return "".join(rows)


def run_pipeline(pdf: Path, model: str, timeout: int):
    out = ROOT / "outputs" / pdf.stem
    start = time.time()
    cmd = [sys.executable, str(APP_DIR / "recap.py"), str(pdf), "--timeout", str(timeout)]
    if model.strip():
        cmd += ["--model", model.strip()]
    bar, box = st.progress(0.0, text="Starting..."), st.empty()
    with tempfile.TemporaryFile("w+", encoding="utf-8") as buf:
        env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
        proc = subprocess.Popen(cmd, cwd=ROOT, stdout=buf, stderr=subprocess.STDOUT, text=True, env=env)
        while proc.poll() is None:
            done = {f for f, _, _ in STEPS if (out / f).is_file() and (out / f).stat().st_mtime >= start - 1}
            bar.progress(len(done) / len(STEPS), text=f"Working... {len(done)}/{len(STEPS)} steps ({int(time.time()-start)}s)")
            box.markdown(step_html(done, True), unsafe_allow_html=True)
            time.sleep(1.5)
        buf.seek(0)
        text = buf.read()
    done = {f for f, _, _ in STEPS if (out / f).is_file() and (out / f).stat().st_mtime >= start - 1}
    bar.progress(len(done) / len(STEPS), text="Finished" if proc.returncode == 0 else "Stopped")
    box.markdown(step_html(done, False), unsafe_allow_html=True)
    return proc.returncode, text, out


def zip_folder(folder: Path) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(folder.iterdir()):
            if f.is_file() and f.suffix != ".jsonl":
                z.write(f, f.name)
    return buf.getvalue()


def render_results(folder: Path, key: str):
    summary, review = read(folder / "summary.md"), read(folder / "review.md")
    recap_md, mmd, log = read(folder / "recap.md"), read(folder / "diagram.mmd"), read(folder / "run-log.md")
    png = folder / "diagram.png"
    nodes = len(set(re.findall(r"\b([A-Za-z_]\w*)\s*[\[\(\{]", mmd)))
    checks = re.findall(r"- \[(x| )\]", log)
    c1, c2, c3 = st.columns(3)
    c1.metric("Summary length", f"{len(summary.split())} words")
    c2.metric("Diagram nodes", nodes or "n/a")
    c3.metric("Pipeline checks", f"{checks.count('x')}/{len(checks)} passed" if checks else "no run log")
    if log:
        chips = "".join(f'<span class="chip {"ok" if m.group(1)=="x" else "bad"}">{"✔" if m.group(1)=="x" else "✘"} {m.group(2)}</span>'
                        for m in re.finditer(r"- \[(x| )\] ([^\n]+?) \(`", log))
        st.markdown(chips, unsafe_allow_html=True)
    t1, t2, t3, t4, t5 = st.tabs(["📝 Summary", "🗺️ Diagram", "🔍 Review", "📄 Full recap", "🧾 Pipeline log"])
    with t1:
        st.markdown(summary or "_No summary found._")
    with t2:
        if png.is_file():
            st.image(str(png), use_container_width=True)
        else:
            st.info("No rendered diagram found.")
        with st.expander("Mermaid source"):
            st.code(mmd, language="text")
    with t3:
        st.markdown(review or "_No review found._")
    with t4:
        st.markdown(re.sub(r"!\[[^\]]*\]\(diagram\.png\)", "", recap_md) or "_No recap found._")
    with t5:
        st.markdown(log or "_No run log in this folder._")
    d1, d2, d3 = st.columns(3)
    d1.download_button("⬇ recap.md", recap_md, "recap.md", key=f"dl1{key}", use_container_width=True)
    if png.is_file():
        d2.download_button("⬇ diagram.png", png.read_bytes(), "diagram.png", "image/png", key=f"dl2{key}", use_container_width=True)
    d3.download_button("⬇ everything (.zip)", zip_folder(folder), "course-recap.zip", key=f"dl3{key}", use_container_width=True)


with st.sidebar:
    st.header("Settings")
    model = st.text_input("Model", os.environ.get("RECAP_MODEL", "google/gemini-3.5-flash"),
                          help="provider/model as shown by `opencode models`. Leave empty for OpenCode's default.")
    timeout = st.slider("Timeout (minutes)", 5, 30, 15)
    try:
        cur_reviewer = doctor.get_reviewer_model()
    except (OSError, ValueError):
        cur_reviewer = ""
    reviewer = st.text_input("Reviewer model (optional)", cur_reviewer,
                             help="Model for the review sub-agent. Empty = same as the main model. Free opencode/* models cannot run "
                                  "sub-agents, so pair them with a Google model here, e.g. google/gemini-3.5-flash.")
    st.caption("Keys are stored by OpenCode (`opencode providers login`), never by this app.")
    problems = env_problems()
    if problems:
        st.warning("**Demo mode**\n\n" + "\n\n".join(f"- {p}" for p in problems))
    else:
        st.success("OpenCode, mermaid-cli and Python deps found.")

tab_gen, tab_ex = st.tabs(["✨ Generate", "📚 Example run"])

with tab_gen:
    up = st.file_uploader("Course PDF (text-based, not scanned)", type=["pdf"], disabled=bool(problems))
    go = st.button("Generate Course Recap", type="primary", disabled=bool(problems) or up is None)
    if problems:
        st.markdown('<div class="note">Live generation needs OpenCode and a model login on the machine running this app. '
                    'See the <b>Example run</b> tab for a saved result, or follow the README to run it locally.</div>',
                    unsafe_allow_html=True)
    if go and up is not None:
        try:
            if reviewer.strip() != cur_reviewer:
                doctor.set_reviewer_model(reviewer)
        except (OSError, ValueError) as e:
            st.error(f"Reviewer model not changed: {e}")
            st.stop()
        pdf = ROOT / "input" / f"{slug(up.name)}.pdf"
        pdf.parent.mkdir(exist_ok=True)
        pdf.write_bytes(up.getvalue())
        st.write(f"Processing **{up.name}** with `{model or 'default model'}`. This can take several minutes; keep this tab open.")
        code, text, out = run_pipeline(pdf, model, timeout * 60)
        st.session_state["last_out"] = str(out)
        if code != 0:
            st.error("The run did not finish cleanly. Partial results (if any) are shown below; see the Pipeline log tab.")
            with st.expander("Raw output"):
                st.code(text[-3000:] or "(empty)")
    last = st.session_state.get("last_out")
    if last and (Path(last) / "recap.md").is_file():
        st.subheader("Result")
        render_results(Path(last), "gen")

with tab_ex:
    ex = example_folder()
    if ex is None:
        st.info("No example run found in `examples/`.")
    else:
        if (ex / "run-log.md").is_file():
            st.markdown('<div class="note"><b>Saved run.</b> Produced by <code>app/recap.py</code> through OpenCode; '
                        'the Pipeline log tab shows which components ran.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="note"><b>Illustrative sample.</b> The text files here were written by hand to show the output '
                        'format on a small synthetic deck; only the PDF extraction and diagram rendering were produced by the tools. '
                        'It is not a real pipeline run.</div>', unsafe_allow_html=True)
        render_results(ex, "ex")
