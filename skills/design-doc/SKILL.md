---
name: design-doc
description: Write and revise engineering documents a colleague can act on, as a self-contained HTML review page with a consistent voice and diagram style. Use for design docs, architecture proposals, RFCs, ownership maps, and explanations of how a system or change works. Also use to write up the results of an audit, review, assessment, or investigation as a findings report, and when asked to put something "in the design document format" or to tighten or humanize one of these documents. Writes Markdown instead when requested or when the repository requires it. Not for PR descriptions, issue text, slide decks, or infographics.
---

# Documents people can read and act on

A document from this skill lets a colleague understand a subject, judge its boundaries, and act without the author's conversation history. That holds whether the subject is a change being designed or the findings of an audit.

Paths below are relative to this skill's directory, not the repository being written about.

| When | Read |
|---|---|
| Before drafting anything | `references/exemplars.md` for finished examples of the voice |
| The document reports findings (audit, review, assessment, investigation) | `references/audit-reports.md` |
| Drawing a diagram | `references/diagram-patterns.md` |
| Saving, previewing, or handing over | `references/delivery.md` |
| Before every delivery and revision | `references/review-checklist.md` |

For HTML, start from `assets/page-kit.html`. `assets/ownership-example.html` and `assets/audit-example.html` are complete rendered examples.

## Evidence comes first

Before writing:

1. Read the request and any existing document. A revision keeps the scope, settled decisions, and file path it already has unless the person changes them.
2. Read the repository's own instructions, contribution rules, and documentation conventions. They take precedence over the structure described here.
3. Establish what exists today, what is proposed or recommended, and what is unknown. Support each consequential claim about the current state with a source: a link, a repository path and symbol, or the output of a command that was run. Use line numbers and URLs only when they were observed.
4. Take terminal mockups from real output: a supplied sample, a test, documentation, or a safe read-only run. When no sample exists, describe the behavior in prose, because a fabricated mockup reads as evidence. Mark behavior that does not exist yet as proposed.
5. Find the decisions that materially shape the document. When one is missing and drafting cannot proceed without it, ask one focused question. When drafting can proceed, record the uncertainty in the document so the choice is visible instead of made silently.

Gathering evidence is reading. Being able to read a repository or a tenant is not permission to change it, deploy, send messages, or publish. Credentials and secrets stay out of the document and out of the conversation.

## The reader's path

This is a pattern. Drop any part that has nothing real to say.

1. **An opening box of three short paragraphs.** For a design: today's behavior and its problem, what the change does, and what it does not do or guarantee. For a findings report: what was examined and as of when, what was found, and what was not examined. Link the relevant issue inline when there is one.
2. **A legend**, only when diagrams or tables are colored by owner or severity. One color per actor, defined once and used the same way throughout.
3. **Sections that answer the reader's next questions** in the order they would ask them. One heading each, normally a flat noun phrase.
4. **Lettered appendices** for reference material: full lists, schemas, syntax, method, detailed diagrams, and alternatives not chosen.

The body supports understanding and judgment. Appendices support building and verification. A consequential tradeoff, risk, or open decision belongs in the body even when that makes it longer.

## Maturity

An **exploratory proposal** separates current behavior from the proposal, states the recommended direction with its main reason, and keeps real open questions visible with their consequence and who decides. Detailed comparisons of alternatives go in an appendix unless choosing between them is the point of the document.

A **settled design** describes the behavior directly: "This change adds...", not "We propose...". Approval framing and resolved questions come out; the reason for each choice stays beside it.

A **findings report** separates what was confirmed from what is inferred, and both from what was not checked. `references/audit-reports.md` covers its shape.

An unresolved dependency is not a non-goal. "We do not know yet" stays an open question; writing it as "not in this change" makes a document look more settled than it is.

## Say each thing once, in the form that shows it best

- **Diagrams show shape:** branches, ownership lanes, layers, a decision tree. Inline SVG, with the real component names on the elements. Every recipient, owner, and outcome is labeled on its own element so the reader never has to match it to a caption. Draw only when the shape says more than a sentence or a table would.
- **Tables compare:** today against the design, options, responsibilities, findings, parallel cases. Cells are phrases.
- **Terminal mockups show experience:** real borders, column order, and summary lines, with example identifiers.
- **Prose states behavior, boundaries, and reasons:** a consequential choice gets its reason beside it, usually in one or two sentences.

A diagram's outcomes are not repeated in a table and again in prose. A table under a decision flow can say when each check runs instead of restating the branches.

## Boundaries beside behavior

State each limit where its mechanism appears:

- What a check establishes and what it does not evaluate.
- Exactly what authority a grant confers: to whom, on what, across which scope.
- What each failure path does and why.
- What is outside the change, or outside what was examined.
- Compatibility, rollout, rollback, performance, or operational constraints when they matter.

Give the real reason for a boundary, not one that explains a single case. Cover the concerns the subject actually raises; there is no fixed list of sections to fill.

## House voice

Short declarative sentences, plain engineering vocabulary, precise terms. Contractions are fine. Counts match the diagrams and name their units: roles versus assignments, components versus instances.

These come out, because each one costs the reader attention without telling them anything:

- Generalizations about people or organizations that have no evidence behind them.
- Praise and grading words such as "clean", "proper", and "robust".
- Arguments that define no behavior, rhetorical closing lines, and narration of how the document was produced.
- Em dashes and en dashes. Use a period, a comma, or parentheses.
- Raw syntax in the body where a sentence would explain it. The full expression goes in an appendix.
- File-by-file inventories. Describe behavior and how it is verified. A targeted source citation is not an inventory.
- Numbered lists for things that are not a sequence.

**Identifiers.** A design uses synthetic placeholders for private identifiers: user and object IDs, subscription and tenant IDs, email addresses, personal names. A findings report is often about exactly those things, so it keeps the real ones its audience needs and is treated as private to that audience; produce a version with placeholders when the person asks for one to share more widely. Public technical identifiers, such as published role-definition IDs and API names, stay in both. Secrets never appear in either.

Repository requirements take precedence over this voice. It covers the document itself; a pull request or issue body requested alongside follows that repository's own conventions.

## Method and completion

1. Gather evidence, decide the maturity, and write the opening box. If the box cannot state the mechanism or the finding yet, surface the missing decision or evidence before drawing anything.
2. Choose actors and colors when needed. Write the sections and appendices, drawing only where shape matters.
3. Save the document somewhere persistent. HTML is the default; Markdown when requested or required. A revision edits the same file.
4. Run `references/review-checklist.md`. Keep completed verification separate from a validation plan: a test result is claimed only when the result was observed.
5. For HTML, render it and look at it at a desktop width and a narrow width, in light and dark themes. Check clipping, arrows, contrast, and reading order, fix what is visibly wrong, and recheck the affected views. After two rounds of fixes, report any remaining defect instead of calling the page verified.
6. Hand over the saved file. If nothing was available to render it, say that visual inspection was not performed. HTML that could not be previewed is still delivered as HTML.

Done means the file is saved, its consequential claims are traceable or clearly marked as proposed or inferred, open decisions are stated honestly, and the editorial and visual checks were either performed or their gaps disclosed. Publishing the document anywhere external, or opening an issue from it, happens only on a separate request.
