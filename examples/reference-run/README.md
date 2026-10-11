# READ THIS FIRST - what is and is not real in this folder

| File | Produced by | Real run of the pipeline? |
|---|---|---|
| `extracted.md` | **MCP server** `extract_pdf`, called through a real MCP stdio client | YES |
| `diagram.png` / `diagram.svg` | **MCP server** `render_diagram` (mermaid-cli) | YES (rendering is real) |
| `concepts.md`, `summary.md`, `diagram.mmd`, `review.md`, `recap.md` | **Written by hand by Claude in a chat session** to show the expected format | **NO - NOT produced by OpenCode, its skill or its sub-agent** |

Why: the sandbox where this project was built had no model credentials, so OpenCode could not
call an LLM. The input is a **synthetic 5-slide test deck**, not a real course deck.

To get the genuine evidence your assignment needs, run `python app/recap.py <your real deck>.pdf`
on your own machine. It writes real output plus `run-log.md` under `outputs/<deck>/`.
Do not submit this folder as your example run.
