# Findings reports

A findings report is the written result of an audit, review, assessment, or investigation: who has access to something, whether a skill or a codebase is fit for a job, what a release changes, why an incident happened. The reader wants to know what is true, how sure the author is, and what to do about it.

It follows the same reader's path and voice as a design. What differs is below.

## The opening box

Three short paragraphs:

1. **What was examined**, against what question, and as of when. Name the system and the source of evidence: "the directory role assignments and guest invitation policy of the tenant, read through Microsoft Graph on 2 March".
2. **What was found.** The answer to the question first, then the number of findings by severity. A reader who stops here has the result.
3. **What was not examined** or could not be verified, and why. An audit that could not read something says so here, because a reader otherwise assumes it was checked and clean.

## Three kinds of statement

Keep these apart in every section. Mixing them is the most common way a report misleads.

| Kind | Meaning | How it reads |
|---|---|---|
| Confirmed | Observed directly: a query result, a file's contents, a test that ran | Stated plainly, with its source |
| Inferred | Follows from confirmed facts but was not itself observed | "likely", "expected to", with the reasoning |
| Not checked | Out of reach or out of scope | Named as a gap, with what would close it |

A root cause is inferred until something reproduces it. A capability derived from a role definition is expected, not demonstrated, until the operation has been tried.

## Findings

Give the findings one table near the top, ordered most severe first. One row per finding.

| Column | Content |
|---|---|
| Severity | A word, not only a color |
| Finding | The claim, as a phrase a reader could repeat |
| Consequence | What happens, or can happen, because of it |
| Recommendation | The action, or "decision needed" with who decides |

Define the severity scale once, in the legend, in terms of consequence for this subject. A common scale:

- **High**: causes harm or blocks the purpose now, or can with no further step.
- **Medium**: causes harm under conditions that are plausible here.
- **Low**: worth fixing, with limited consequence.
- **Note**: true and relevant, with no action expected.

A report with no findings says so in the opening box and stops there. Do not manufacture low-severity findings to fill the table.

After the table, give a section only to the findings that need more than their row: the evidence, the mechanism, and the reason for the recommendation. A finding fully explained by its row does not get a section.

## Current state before judgment

When the audit maps something (who holds which access, which component owns which step), show the map before the findings, as a table or a diagram. The reader needs the facts in front of them to judge the findings. Describe the state without grading it; the findings carry the judgment.

## Recommendations

Each recommendation names the finding it answers, the action, and who has to take or approve it. Order them by what should happen first. Where two reasonable options exist, state the one recommended and its reason, and put the comparison in an appendix.

A recommendation is not an action already taken. If something was changed during the audit, report it separately as a change, with its before and after.

## Appendices

- **Method**: the queries, commands, or files read, so the audit can be repeated. This is where a later reader learns whether the audit could have seen what they are worried about.
- **Full inventories**: every assignment, every file, every row. The body carries the ones that matter.
- **Raw evidence**: trimmed output, with secrets and tokens removed.

## Real identifiers

An access audit that hides who has access is useless to its audience, so a findings report keeps the real names, groups, and IDs the reader needs. Treat the document as private to the people who asked for it. If it will be shared more widely, produce a second version with placeholders and say which one is which. Secrets, tokens, and credential values are left out of every version.

## Dates

Findings describe a moment. Put the date the evidence was gathered in the opening box and in the page's eyebrow line. Write absolute dates. "Recently" and "currently" lose their meaning as soon as the document is read later.
