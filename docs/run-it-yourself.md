# Run it yourself (free)

Anyone can run the whole project on their own computer at no cost. Nothing is hosted, so there is no shared key or quota.
You need about 20 minutes the first time.

## What you need (all free)
- **Node.js LTS** (nodejs.org) and **Python 3.10 or newer**
- A free **Google AI Studio key** (no credit card): https://aistudio.google.com/apikey -> Create API key
- This repository (download the ZIP or `git clone`)

## 1. Install
Open a terminal **inside the project folder** (the one containing `opencode.json`).
```
npm i -g opencode-ai@1.18.34 @mermaid-js/mermaid-cli
npx -y puppeteer browsers install chrome-headless-shell
pip install -r requirements.txt
```
- Version 1.18.34 is the one this project was tested with. OpenCode 2.x did not load this config in testing.
- Windows: if npm prints `EPERM`, close other terminals and retry in an Administrator PowerShell.
- macOS/Linux: open `opencode.json` and change `"python"` to `"python3"`.

## 2. Connect a model
```
opencode providers login
```
Choose **Google** and paste your AI Studio key. The key is stored by OpenCode on your machine, never in this repo.
List available model names with `opencode models`.

## 3. Check your setup (uses no model quota)
```
python app/doctor.py
```
Every line should say `[OK]`. Each `[FAIL]` prints the command that fixes it.
Add `--ping google/gemini-3.5-flash` to also send one tiny request and confirm the key and model work.

## 4. Free model recipe
Google's free tier allows only about **20 requests per model per day**, and a full run needs more than that on one model.
The split that worked on the author's machine (Windows, October 2026):

| Part | Model | Why |
|---|---|---|
| Main agent | `opencode/big-pickle` (a free OpenCode model) | Does not use your Google quota |
| Reviewer sub-agent | `google/gemini-3.5-flash` | Free OpenCode models cannot run sub-agents |

```
python app/doctor.py --reviewer-model google/gemini-3.5-flash
python app/recap.py path/to/deck.pdf --model opencode/big-pickle
```
(Or set both in the web UI's sidebar.) Model names change over time: check `opencode models` and pick current ones.
Observed on that machine: `google/gemini-3.5-flash` alone reached the diagram step and then hit the 20-request cap;
`google/gemini-3.6-flash` and `3.7-flash` failed on this command with a 400 error. These are single-machine observations, not guarantees.

## 5. Run
Web interface: `python -m streamlit run app/ui.py` (opens at http://localhost:8501).
Command line: `python app/recap.py path/to/deck.pdf --model opencode/big-pickle`.
Results are written to `outputs/<deck name>/` (`recap.md`, `diagram.png`, `review.md`, `run-log.md`, ...).
Open `run-log.md` to see which components really ran. Use a text-based PDF (you can select its text), not a scan.

## Free-tier limits and privacy
- Run it once, on a short deck (10-20 slides). If a run stops with a quota message, wait for the reset time it shows.
- Google may use free-tier requests to improve its products. Do not upload confidential material.

## Troubleshooting
| What you see | Likely cause | Fix |
|---|---|---|
| `streamlit` is not recognized (Windows) | pip's Scripts folder is not on PATH | Run it as `python -m streamlit run app/ui.py` |
| `can't open file '...\app\recap.py'` or `No MCP servers configured` | Terminal is not in the project folder | `cd` into the folder containing `opencode.json` |
| `opencode` says `v2.x`, or `agent list` is not a command | Wrong OpenCode version | `npm i -g opencode-ai@1.18.34 --force`, then open a new terminal |
| `Database is not empty and has no session table` | Switched OpenCode versions | Rename OpenCode's data folder (`~/.local/share/opencode`) after closing all OpenCode windows; you will log in again |
| `EPERM` while installing mermaid-cli | Windows locking files | Close other terminals; run an Administrator PowerShell |
| `You exceeded your current quota` / 429 | Free daily limit for that model | Wait for the reset, or use a different model |
| `Requests ending with a model turn are not supported` (400) | That model rejects this command | Use `google/gemini-3.5-flash` |
| `free tier can only be used from within OpenCode` on the review step | Reviewer is using a free `opencode/*` model | `python app/doctor.py --reviewer-model google/gemini-3.5-flash` |
| `Cannot connect to API` | Network or VPN hiccup | Retry; test with `python app/doctor.py --ping <model>` |
| Windows prints `UnicodeDecodeError` | Old copy of `recap.py` | Use the current `app/recap.py` |
| Commands pasted twice run together and fail | Copy-paste glitch | Paste one command per line |
| Google rejects the key | Key type or restriction | Create a fresh key in AI Studio |

## Not included
A Docker image or hosted live version is not provided. Live hosting would need OpenCode, Chrome and a private model key on a
server, and free hosts do not offer that. Self-running keeps it free and keeps your key private.
