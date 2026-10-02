---
name: gh-voice
description: House tone and structure for what gets written on GitHub and GitLab. Use when writing a pull request or merge request description, an issue, a review reply, or an issue comment, and when asked to tighten, trim, shorten, humanize, or clean up one that already exists.
---

# Voice for PRs, issues, and comments

One tone of voice for everything written on GitHub or GitLab: PR and MR descriptions, issues, review replies, and issue comments. Each tells the reader what is true and what to do. None is a record of how the work went.

A PR description tells a reviewer what the change is and why the code looks the way it does. An issue tells the next person what is broken and what to change. A comment answers or closes a thread.

A project's own template still wins. Check `.github/PULL_REQUEST_TEMPLATE.md`, `.github/PULL_REQUEST_TEMPLATE/`, `.github/ISSUE_TEMPLATE/`, `.gitlab/merge_request_templates/`, and `CONTRIBUTING.md` first. This skill governs tone everywhere, and structure only where the project states none.

## PR and MR descriptions

- **What**: the functional change in a few sentences. Not a file walkthrough; the diff shows that.
- **Why now**: what this unblocks, what it depends on, what constraint or decision drove it.
- **Notes for review**: only when the diff contains choices a reader would otherwise stop and question. Each note says what the code does and why, never what changed during development.

Drop any section with nothing real to say. Length follows the change. A description that runs long is usually narrating how the work went, so re-read it for process before trimming for length.

**Headings are labels, not theses.** A heading like "Why the retry limit is safe to raise" argues before the section starts. Use a flat noun (Notes, Risk, Rejected) or name the subject. A section carrying one fact is a sentence, not a section: if the heading is the longer half, delete it and keep the sentence.

**Sections are about the change, never about writing the change.** This is the test that catches the respectable-looking additions. "Rejected alternatives" and "What I could not verify" both read as structure and are both process narration under a heading. The decisions that mattered while working are mostly not the decisions that matter to someone reading the diff.

- An alternative earns a mention only when the diff looks wrong without it, when the obvious approach fails for a reason the code cannot show. Then it is a note explaining the code, and it belongs in Notes.
- An open risk is stated as system behavior, not as a caveat about the author. ✗ "I could not verify this before Monday." ✓ "The switch first runs Monday, and a failure there is logged rather than shown on the PR, so it looks like a quiet week." The second is checkable and tells the reader what to do.

## Issues

- **Problem**: what is observed, with evidence a reader can chase: exact error text, the run or PR link, the file and line. One paragraph.
- **Cause**: only when known. Say what the code does that produces the problem, not how it was found.
- **Required change**: numbered, each item checkable. A recommendation, not a menu of options.

Usually shorter than a PR description. When one runs long, the excess is almost always background the reader does not need in order to act.

## Comments

Review replies and issue comments lead with the outcome or the answer, then the reason, in one to three sentences. Link the commit or line instead of quoting the diff.

- ✗ "Thanks for the catch! You're right that..." (no thanks, no restating their comment)
- ✗ "Fixed in the latest push." (say what the code does now, and where)
- ✓ "`upload-database: false` now, since `upload: never` only covers SARIF. d3cd529."
- Declining a suggestion: one sentence on what the code does and why. No apology, no "happy to change it if you prefer".

## What comes out

Each of these costs the reader attention and tells them nothing about the change.

**Reader stage-direction.** Narrating the reader's job. Emphasis comes from what the words are spent on, not from instructions about where to look or how to feel. Give the risky thing three paragraphs and everything else a line, and the weight is obvious without being announced.

- ✗ "The version pin is the part to argue with." / "Look here first" as a heading.
- ✗ "Worth opening that log Monday." ✓ "Open that log Monday even if nothing shows up."

**Process narration.** The reviewer sees the diff against the base branch. A bug introduced and fixed inside the branch never existed for them.

- ✗ "Preflight against a real fork caught four defects."
- ✗ "Three share a root cause worth naming."
- ✗ "Addresses review feedback from round 2."
- ✓ State the resulting design: "`COPY .mvn*/` globs so a fork shipping no root `.mvn/` still builds."

**Backlog and follow-up sections.** They pull attention off the change under review. File an issue for the follow-up and leave it out of the PR.

**Test-plan checklists.** Left out by default. Verification belongs in the description only when how it was proven is itself the interesting part: a real-environment reproduction, a negative control.

**File-by-file enumeration.** Group by behavior, not by path.

**Restatement.** If the commit message or the diff already says it, it does not need saying again.

**Praise and hedging in comments.** "Great point", "you're absolutely right", "just to confirm my understanding". State the change or the reason.

## Words

No em dashes or en dashes. Rewrite the sentence. A comma, colon, period, or parentheses always works.

Plain engineering vocabulary. These swaps illustrate the direction; they are examples, not a list to match against:

| Inflated | Plain |
|---|---|
| four defects | four bugs |
| degraded to a clean skip | skipped silently |
| a destructive deletion path | that script deletes registry tags |
| accumulates a tag per push | adds a tag per push and never gets cleaned up |
| the contract this consumes | the contract this uses |
| grows a new mode | gets a new mode |
| by approved decision | as agreed |
| the honest fix is to X | X |
| which is the evidence that X | so X |
| a failure there is quiet | it logs the error instead of failing the check |

Three things read as machine-written even when the words are plain:

- **Grading the fix:** "honest", "principled", "proper", "clean". Say what the fix does.
- **Calling a test or check a "signal":** "keep the signal", "lose signal". Say what the check checks.
- **Stock filler:** "notably", "leverage", "robust", "seamless", "comprehensive". Each stands in for a specific claim; make the claim. Prefer "make sure" to "ensure".

Contractions are fine and usually better. Prose with none of them ("does not", "has not", "cannot") reads stiff. So does uniform rhythm: when every paragraph runs claim, then reason, then a concessive clause, it reads as generated no matter how plain the words are. Real writing is lumpier.

## Tightening an existing one

1. Delete process narration and follow-up sections first. That is usually most of the excess.
2. Replace every em dash and en dash.
3. Swap inflated vocabulary for plain.
4. Re-read **Notes for review**. Anything that reads as history gets restated as design or cut.
5. Read the result back from the host, since that is what the reader sees, and confirm no dash and no session history is left:

```bash
gh pr view NUMBER --json body --jq .body
gh issue view NUMBER --json body --jq .body
glab mr view NUMBER
```

Keep the load-bearing "why" while cutting. A note explaining why an odd-looking file exists is the reason a reviewer does not have to ask.

Editing a description, issue, or comment that is already posted changes what other people see. Show the rewritten text and post it when the person asks for it to be posted.
