# Planning evidence

## Honest status
`PLAN.md` was written by Claude in a chat session before implementation (no model credentials were available
in the build sandbox). The student later ran OpenCode's **plan** agent on the finished project using
`docs/plan-mode-prompt.md`; its output is recorded below. That run happened after the build, so it is a plan-mode
review of the project, not the plan that guided the first implementation.

## Findings from environment probing that changed the plan
- The assignment PDF has only a watermark text layer; its content is raster, so I read it visually. This confirmed the
  required components (harness, plan, MCP, sub-agent, skill, single pass, real deck).
- No course deck was provided, so a synthetic 5-slide test deck was generated (`examples/sample-input.pdf`).
- OpenCode (npm `opencode-ai` 1.18.34) installs and loads project config, so the harness files could be validated.
- MCP Python SDK 2.x renamed `FastMCP`; the server supports both 1.x and 2.x (tested).
- mermaid-cli could not find Chrome through the stdio subprocess; the server now auto-detects Chrome.
- UI: Streamlit dropped in favour of a CLI to reduce untested moving parts.

## OpenCode plan-mode output
Captured from the OpenCode **plan** agent (read-only; it cannot edit files). The model's reply began with a long
stretch of garbled, unreadable text before the proposal; that stretch is omitted here. The proposal below is
reproduced as received, starting from the line "Based on my review...".

```
+ Thought: 28.0s
Based on my review of the project structure, here's a proposal for improving the Course Recap Generator for real course decks:
Key Improvement Areas
1. Enhanced Topic Grouping
- Problem: Current grouping is arbitrary (3-8 topics by meaning)
- Improvement: Implement hierarchical topic clustering based on slide headings, subheadings, and semantic similarity. Real courses often have 10-20+ meaningful topics that shouldn't be collapsed into too few groups.
2. Multi-Format Content Handling
- Problem: Skill only handles plain text; struggles with code, math, tables
- Improvement: Add specialized parsers for:
- Code blocks: Detect and extract with syntax highlighting info
- Mathematical notation: Preserve LaTeX math expressions with proper rendering
- Tables: Extract structured data rather than flowing as text
- Figures/Captions: Associate images with descriptive captions
3. Advanced Diagram Layout
- Problem: Simple graph TD may produce cluttered diagrams for complex courses
- Improvement:
- Use graph LR (left-to-right) for linear courses
- Use graph TB (top-to-bottom) for hierarchical content
- Implement cluster/subgraphs for related concepts
- Add automatic node sizing based on content density
- Support edge labels beyond the fixed verb set (arrows, requires, includes)
4. Bibliography & Reference Extraction
- Problem: References/bibliography sections often lost
- Improvement: Detect and extract reference lists, with optional citation linking in the summary
5. Multi-Pass Review Loop
- Problem: Single-pass with one retry is fragile for real decks
- Improvement: Allow 2-3 review iterations with progressive tightening:
- Pass 1: Coverage & factual accuracy
- Pass 2: Relationship faithfulness & diagram structure
- Pass 3: Formatting & citation completeness
6. Output Flexibility
- Problem: Fixed recap.md format may not suit all use cases
- Improvement: Support multiple output formats:
- Markdown (current)
- HTML with embedded diagrams
- LaTeX for academic publishing
- JSON for tool integration
7. Scanned PDF Recovery
- Problem: Currently stops entirely on scanned PDFs
- Improvement: Integrate OCR (tesseract) as fallback, with user confirmation before proceeding
8. CLI Enhancements
- Problem: Basic /recap command
- Improvement: Add options for:
- --topics N to control topic count
- --diagram-style (td/bt/tb)
- --output-format (markdown/html/latex)
- --include-original-pages for slide-per-page view
9. Quality Metrics
- Problem: No quantitative quality measures
- Improvement: Add automated checks:
- Concept coverage % (concepts found / concepts in slides)
- Citation completeness %
- Diagram connectivity score
- Relationship verb distribution
10. MCP Server Expansion
- Problem: Only PDF extraction + rendering
- Improvement: Add tools for:
- Text translation
- Summarization via external LLM
- Diagram alternative text generation
- Slide index generation
These improvements would make the generator suitable for real academic courses (50+ slides, multiple content types, rigorous review requirements) while maintaining the source-grounded, reviewable principles of the current design.
```

### How this output was used
None of these suggestions have been implemented in this submission. Nothing in the code or config changed as a result
of this review. The assignment asks for one clean pass and a focused tool, so the items were left as possible future work:

- **Item 5 (multi-pass review loop)** conflicts with the assignment's single-pass constraint, so it is deliberately not adopted.
- **Items 6, 8 and 10** (extra output formats, more CLI options, more MCP tools) add scope beyond what the assignment asks for.
- **Items 1-4, 7 and 9** (topic clustering, table/math handling, diagram layout, OCR for scanned PDFs, quality metrics) are
  reasonable next steps. OCR for scanned decks is already listed as a limitation in `README.md`.
