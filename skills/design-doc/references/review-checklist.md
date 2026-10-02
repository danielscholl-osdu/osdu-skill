# Review checklist

Run before initial delivery and before every revision is presented. Fix defects rather than putting a checklist in the document.

## Evidence and maturity

- Current-state claims are grounded in inspected sources or supplied evidence.
- Proposed behavior is not presented as implemented behavior.
- Consequential claims have usable source references; counts and identifiers are not invented.
- Open questions remain visible and are not disguised as exclusions.
- Settled designs describe behavior directly, without approval framing or resolved decision lists.
- Test results describe observed runs; unexecuted verification is labeled as a plan.
- Repository documentation and contribution requirements are respected.

## Findings reports

- The opening states what was examined, as of what date, what was found, and what was not examined.
- Confirmed, inferred, and not-checked statements are distinguishable wherever they appear.
- Findings are ordered by severity, and the severity words are defined once in terms of consequence.
- Each recommendation names its finding and who acts or decides. Nothing recommended is described as already done.
- The method appendix would let someone repeat the audit.
- Real identifiers are present only where the audience needs them; no secrets or tokens appear.

## Framing

- The opening has three short paragraphs: for a design, today's problem, the change, and its limits.
- The reader can understand the whole change from that opening.
- Sections use one heading each, normally a flat noun phrase.
- A legend appears only when needed and maps colors to actual owners or actors.
- Detail needed to judge the design is in the body; build-only detail is in appendices.

## Counts and terms

- Every count agrees with its diagram and table.
- Different counts have named units: roles versus assignments, images versus deployments.
- Scope, recipients, permissions, inputs, and outcomes are precise.
- Generalizations about people or organizations have evidence or are removed.

## Boundaries

- Mechanisms state their limits beside the behavior.
- Every material failure path names its result and reason.
- Grant descriptions specify authority, recipient, target, and scope.
- Boundaries give the real reason, not an explanation for only one case.
- Compatibility, rollout, rollback, and operational constraints are addressed when material.
- Anything easily mistaken as included is explicitly included or excluded.

## Repetition and voice

- Each visible form has its own job; prose does not retell a diagram or table.
- Rationale sits beside the choice; detailed alternatives normally live in an appendix.
- No file inventory, process narration, grading words, rhetorical closer, or unsupported pitch.
- No em dashes or en dashes in authored prose.
- Reference syntax is in an appendix unless exact syntax is essential to the reader's decision.

## Diagrams and tables

- Actors retain the same colors across the document.
- Every box, chip, and leaf names its real component, recipient, owner, or outcome.
- Dashed elements have an explained meaning.
- Semantic colors describe outcomes, not arbitrary objects.
- Marker and accessibility IDs are unique; diagrams do not depend on other diagrams' definitions.
- Table columns and rows are parallel; headers identify their data.
- Accessible diagram descriptions convey the mechanism without relying on color.

## Mockups and privacy

- Terminal shape comes from a real sample or no mockup is used.
- New terminal behavior is labeled as proposed.
- In a design, private identifiers and people are replaced with synthetic values throughout.
- Public technical identifiers needed for precision remain intact.
- No credentials, private source content sent to external services, or unrequested publication.

## Presentation and delivery

- HTML is self-contained and includes a title, document shell, and meaningful heading order.
- No authoring placeholders remain in the finished artifact.
- Light and dark themes both work, including explicit theme overrides.
- Normal text has at least 4.5:1 contrast; large text at least 3:1. Meaningful graphic boundaries have at least 3:1 contrast where needed to understand them.
- Actor identity and outcomes remain understandable without color.
- Desktop and narrow renders have been inspected for clipping, overlap, arrows, and reading order.
- Wide diagrams scroll inside their container; the entire page does not overflow.
- Visible defects were corrected and affected views rechecked, or remaining limitations are disclosed.
- The source file exists on a persistent authorized surface.
- Revisions retain the file and review surface unless the user requested a change.
- The final handoff links the saved artifact and accurately states unresolved decisions or unavailable verification.
