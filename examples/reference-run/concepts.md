# Concepts: AI Coding Agents (synthetic test deck)

## Topic: Agent Harness
Definition: The tool that runs the model with files, shell and tools. (p.1)
Key Concepts:
- Agent harness: runs the model with files, shell and tools
Important Points:
- Examples are Codex, OpenCode, Claude Code (p.1)
Examples:
- Codex, OpenCode, Claude Code
Keywords: agent harness, Codex, OpenCode, Claude Code
Relationships:
- Agent Harness --uses--> MCP Servers (p.3)

## Topic: Plan Mode
Definition: The agent reads and proposes but does not edit files. (p.2)
Key Concepts:
- Plan: reviewed before any code is written
Important Points:
- Reduces rework on larger tasks (p.2)
Examples: none stated
Keywords: plan mode, plan, rework
Relationships:
- Plan Mode --produces--> Plan (p.2)

## Topic: MCP Servers
Definition: MCP (Model Context Protocol) servers expose tools the harness cannot do itself. (p.3)
Key Concepts:
- MCP server: exposes tools; harness calls them by name
Important Points:
- Harness calls them as tools by name (p.3)
Examples:
- PDF reader, diagram renderer
Keywords: MCP, Model Context Protocol, tools
Relationships:
- MCP Servers --enables--> PDF Reader (p.3)
- MCP Servers --enables--> Diagram Renderer (p.3)

## Topic: Sub-agents
Definition: A named agent with its own role and instructions, run in a separate context. (p.4)
Key Concepts:
- Sub-agent: declared in harness config, not just a second prompt
Important Points:
- Separate context from the main agent (p.4)
Examples:
- A reviewer that checks a summary against the source
Keywords: sub-agent, role, instructions
Relationships:
- Sub-agents --part-of--> Agent Harness (p.4)

## Topic: Skills
Definition: A reusable instruction folder (SKILL.md) loaded on demand. (p.5)
Key Concepts:
- Skill: gives consistent output across different inputs
Important Points:
- Loaded on demand by the agent (p.5)
Examples:
- Extract key concepts in a fixed format
Keywords: skill, SKILL.md
Relationships:
- Skills --enables--> Consistent Output (p.5)

## Global Relationships
- none stated beyond the per-topic relationships above
