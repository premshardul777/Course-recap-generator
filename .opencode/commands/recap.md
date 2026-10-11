---
description: Generate a course recap (summary + concept diagram + review) from a PDF. Usage - /recap path/to/deck.pdf
---

Create a course recap for the PDF at: $ARGUMENTS

Do exactly one clean pass. No loops beyond the single allowed fix-up noted below.

Set `OUT=outputs/<pdf-file-name-without-extension>/` and follow these steps in order:

1. **Extract (MCP).** Call the `pdf-recap_extract_pdf` tool with `pdf_path` = the PDF and `output_dir` = OUT. If `scanned_warning` is true, stop and tell the user the PDF has no text layer.
2. **Key concepts (skill).** Load the `extract-key-concepts` skill and follow it exactly on the extracted text. Write `OUT/concepts.md`.
3. **Summary.** Write `OUT/summary.md` using ONLY `concepts.md` and the extracted text, with these sections: `## 1. Overview`, `## 2. Main Topics` (per topic: Definition, Key concepts, Important points, Examples), `## 3. Key Takeaways`, `## 4. Important Relationships`.
4. **Diagram source.** Write `OUT/diagram.mmd` as Mermaid `graph TD`, built from the concept sheet's Topics, Key Concepts and Relationships (edge labels = the relationship verbs). 10-25 nodes, short labels, no invented nodes. Do not reuse any example topic names.
5. **Render (MCP).** Call `pdf-recap_render_diagram` with `mermaid_path` = `OUT/diagram.mmd`. If it returns an error, fix the Mermaid syntax once and call it once more.
6. **Review (sub-agent).** Invoke the `summary-reviewer` sub-agent via the Task tool, passing the four file paths (`extracted.md`, `concepts.md`, `summary.md`, `diagram.mmd`). Save its reply verbatim to `OUT/review.md`.
7. **Apply corrections.** Make the reviewer's concrete corrections to `summary.md` / `diagram.mmd` once; if `diagram.mmd` changed, re-render it. Do NOT call the reviewer again.
8. **Final output.** Write `OUT/recap.md` containing: `# Course Recap: <title>`, the summary sections, `## 5. Concept Diagram` (embed `![Concept diagram](diagram.png)` plus the Mermaid source in a code block), and `## 6. Review Report` (Missing concepts, Corrections applied, Diagram verification, Final status from the reviewer's verdict).

Finish by listing the files written under OUT.
