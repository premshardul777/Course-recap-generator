---
name: extract-key-concepts
description: Extract key concepts from course slides or lecture text into one fixed, structured format (topic, definition, concepts, points, examples, keywords, relationships). Use when summarising any slide deck, lecture PDF or study material.
---

# extract-key-concepts

Turn raw extracted course text into a consistent, source-grounded concept sheet.
Works on any subject; never assume the topic in advance.

## Rules
- Use ONLY what is in the provided text. If something is not stated, omit it. Do not add outside knowledge.
- Group slides into 3-8 topics by meaning, not one topic per slide.
- Cite slide/page numbers like `(p.3)` after each definition and relationship.
- Keywords are terms that literally appear in the source.
- Relationships use a fixed verb vocabulary so diagrams stay consistent:
  `is-a`, `part-of`, `uses`, `enables`, `produces`, `depends-on`, `example-of`, `contrasts-with`.
- If a field has nothing in the source, write `none stated`.

## Output format (write to `concepts.md`)
```
# Concepts: <deck title>

## Topic: <name>
Definition: <1-2 sentences from source> (p.N)
Key Concepts:
- <concept>: <short gloss>
Important Points:
- <point> (p.N)
Examples:
- <example from source>
Keywords: <comma separated>
Relationships:
- <Concept A> --<verb>--> <Concept B> (p.N)

(repeat per topic)

## Global Relationships
- <Topic/Concept> --<verb>--> <Topic/Concept> (p.N)
```

## Quality check before finishing
- Every Relationship names two concepts that appear above.
- No definition without a page reference.
- 12-25 distinct concepts total for a 5-30 slide deck (fewer for smaller decks).
