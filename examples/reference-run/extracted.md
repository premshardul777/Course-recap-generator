# Extracted text: sample-input.pdf

## Page 1

SYNTHETIC TEST DECK: AI Coding Agents
- Agent harness = the tool that runs the model with files, shell and tools
- Examples: Codex, OpenCode, Claude Code
- This deck exists only to test the recap pipeline
Slide 1

## Page 2

Plan Mode
- Agent reads and proposes, but does not edit files
- Output: a plan reviewed before any code is written
- Reduces rework on larger tasks
Slide 2

## Page 3

MCP Servers
- MCP = Model Context Protocol
- A server exposes tools the harness cannot do itself
- Example: PDF reader, diagram renderer
- Harness calls them as tools by name
Slide 3

## Page 4

Sub-agents
- A named agent with its own role and instructions
- Runs in a separate context from the main agent
- Example: a reviewer that checks a summary against the source
- Declared in harness config, not just a second prompt
Slide 4

## Page 5

Skills
- A reusable instruction folder (SKILL.md)
- Loaded on demand by the agent
- Gives consistent output across different inputs
- Example: extract key concepts in a fixed format
Slide 5
