"""Builds a SMALL, CLEARLY SYNTHETIC test deck (not a real course deck)."""
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas

SLIDES = [
    ("SYNTHETIC TEST DECK: AI Coding Agents", ["Agent harness = the tool that runs the model with files, shell and tools",
        "Examples: Codex, OpenCode, Claude Code", "This deck exists only to test the recap pipeline"]),
    ("Plan Mode", ["Agent reads and proposes, but does not edit files", "Output: a plan reviewed before any code is written",
        "Reduces rework on larger tasks"]),
    ("MCP Servers", ["MCP = Model Context Protocol", "A server exposes tools the harness cannot do itself",
        "Example: PDF reader, diagram renderer", "Harness calls them as tools by name"]),
    ("Sub-agents", ["A named agent with its own role and instructions", "Runs in a separate context from the main agent",
        "Example: a reviewer that checks a summary against the source", "Declared in harness config, not just a second prompt"]),
    ("Skills", ["A reusable instruction folder (SKILL.md)", "Loaded on demand by the agent",
        "Gives consistent output across different inputs", "Example: extract key concepts in a fixed format"]),
]
c = canvas.Canvas("examples/sample-input.pdf", pagesize=landscape(letter))
for i, (title, bullets) in enumerate(SLIDES, 1):
    c.setFont("Helvetica-Bold", 28); c.drawString(60, 520, title)
    c.setFont("Helvetica", 18)
    for j, b in enumerate(bullets): c.drawString(80, 460 - 40 * j, "- " + b)
    c.setFont("Helvetica", 10); c.drawString(60, 30, f"Slide {i}")
    c.showPage()
c.save()
