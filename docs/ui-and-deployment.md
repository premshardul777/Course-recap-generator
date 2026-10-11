# Web UI, GitHub and deployment

![UI](ui-screenshot.png)
_Screenshot of the UI in demo mode, showing the **illustrative** sample (hand-written text on a synthetic deck), not a real run._

## 1. Run the UI on your own computer (full features)
```
cd "<your project folder>"
pip install -r requirements.txt
python -m streamlit run app/ui.py
```
It opens at http://localhost:8501. Upload a text-based PDF, check the model name in the sidebar, click
**Generate Course Recap**. The UI calls `app/recap.py`, which runs OpenCode (MCP + skill + sub-agent). Progress ticks
off as each output file appears. Results show in tabs (Summary, Diagram, Review, Full recap, Pipeline log) with downloads.

Needs the same setup as the CLI: OpenCode, mermaid-cli, a model login (`opencode providers login`).
Note: `opencode.json` uses `python`; on macOS/Linux change it to `python3`.

The UI has no "summary style" option because the pipeline has no such feature; it would be fake.

## 2. Demo mode
If OpenCode or mermaid-cli is missing, or `RECAP_DEMO_ONLY=1` is set, the app disables generation and shows a saved
example (`examples/real-run`, else `examples/reference-run`). Use demo mode for any public deployment: a public live
generator would let strangers spend your model quota.

## 3. Put it on GitHub
Before the first commit, check privacy:
- `input/` must hold no PDFs (it is git-ignored) and `outputs/` is ignored too.
- `examples/real-run/run-log.md` contains the command with your Windows user path; edit it out if you care.
- Never commit `auth.json` or any API key (git-ignored, but check `git status`).
- Your Renewable Energy deck's title page showed your name and college; make sure no such file is in the repo.

Create an **empty** repo on github.com (no README), then in the project folder:
```
git init
git config user.name "Your Name"
git config user.email "you@example.com"
git add .
git status
git commit -m "Course Recap Generator with Streamlit UI"
git branch -M main
git remote add origin https://github.com/<your-username>/course-recap-generator.git
git push -u origin main
```
`git status` before committing should list no PDFs from `input/` and no `outputs/` files.
The workflow in `.github/workflows/ci.yml` runs the tests on every push (see the Actions tab; it has not been run on GitHub yet).

## 4. Deploy (Streamlit Community Cloud, free)
1. Make sure the repo is public (the free tier deploys from public repos).
2. Go to https://share.streamlit.io, sign in with GitHub, click **New app**.
3. Choose your repository, branch `main`, and main file path `app/ui.py`.
4. Under advanced settings choose a recent Python (3.10 or newer; the `mcp` package needs it) and, optionally, add the secret
   `RECAP_DEMO_ONLY = "1"`.
5. Click **Deploy**. Streamlit installs `requirements.txt` automatically.

On the cloud the app runs in demo mode (no OpenCode there) and shows your saved example run. Live generation stays a local feature.
The UI was tested locally in a headless browser; it has not been deployed to Streamlit Cloud yet.

## 5. Why not deploy live generation?
It needs OpenCode, Chrome, mermaid-cli and your private model key on the server, and every visitor would use your quota.
If you ever want it, a Docker image on a host you control is the way, with a login in front. That is outside this assignment.
