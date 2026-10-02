# Saving, previewing, and handing over

The saved document is the source of truth. A canvas or published page is its review surface, not a substitute for persistence.

## Choose the work surface

- In an authorized repository session, follow its documentation location and naming conventions.
- In a standalone chat, use the session's persistent artifact directory exposed by the host. Do not assume a repository exists.
- If the host exposes neither, use a user-approved output directory or ask where to save.
- For revisions, read the existing document and use its path. Do not generate `final-v2` files or change artifact identity without a reason.

Read-only access to a configured repository does not permit writing into its primary checkout. Where the host requires a separate project session for changes to a repository, use one. A standalone document can still be saved as a session artifact.

## HTML first

Start from `assets/page-kit.html`. It is a complete standalone document: doctype, HTML, head, and body. Replace placeholders, remove irrelevant blocks, and save as `<subject>.html`. It has no external fonts, scripts, stylesheets, or images.

Keep the file self-contained. Escape text inserted into HTML or SVG. Include a descriptive title, logical headings, table headers, and accessible diagram descriptions. Do not make color the only way to identify an actor or outcome.

The kit has four starter owner colors and a severity set for findings reports. Add or change owner tokens if the subject requires it, updating both themes and the legend. Do not force unrelated owners into one color to fit the kit. Recheck contrast and color distinguishability.

The page honors `data-theme="light"` and `data-theme="dark"` on the HTML element. Without an explicit value, it follows the operating-system color preference. Both explicit themes must work independently of that preference.

## Copilot app

Discover available canvases and inspect their input schemas before use. Do not invent canvas types, actions, or browser page handles.

With the built-in Browser canvas available, open the saved HTML file using a `file://` URL when supported, or a local HTTP URL if necessary. Keep a stable caller-chosen instance handle and reuse it for revisions. Reopening the panel updates the review surface; a local preview URL is not a public, durable publishing URL.

Browser opening and browser automation are separate capabilities. If screenshot actions require a page handle from a tool that is not available, do not fabricate that handle. Use an available local renderer instead, or disclose that visual inspection is blocked.

If local HTTP serving is necessary, bind to loopback and serve only the artifact directory, not a home directory or repository containing private files. Verify readiness before opening. Stop a server used only for validation. A server needed after the turn must use the host's approved persistent-process mechanism; do not leave a session-bound helper running and claim a durable preview.

The Editor canvas is appropriate for a requested Markdown artifact, not for rendering HTML. Explicitly choose repository scope for repository files or workspace scope for session artifacts according to the discovered schema. What a Markdown preview renders varies by host, and inline SVG is the usual gap. Check what the preview actually shows before relying on it.

## Copilot CLI and other hosts

Save the same self-contained HTML and return its path. Preview it using available browser tools or an installed headless renderer. A missing renderer is a limitation to report, not a reason to install a browser or leave a server running.

For Chrome rendering, discover its executable instead of assuming a macOS path. Use an isolated temporary browser profile and a bounded render. Take screenshots at desktop and narrow widths for both themes. Explicit theme snapshots may be generated as temporary copies; do not alter the delivered document's theme preference just for verification.

Two things to know about headless Chrome: it can keep running after it has written the screenshot, so wait for the file and then stop the process instead of waiting for it to exit; and it has a minimum window width of roughly 500px, so a narrower size crops the page instead of reflowing it. Use about 520px for the narrow check.

Inspect the images, not just the renderer's exit code. A nonempty screenshot does not prove labels fit. DOM or geometry checks help identify overflowing text but cannot prove the arrows or color hierarchy make sense.

If no renderer is available, complete editorial and structural checks and say visual inspection was not performed. Do not claim publication or validation that did not happen.

## Optional publication

Use an external artifact publisher only when the user requests publication and its tool is available. Respect the destination's privacy and approval rules. A design request is not permission to post to GitHub or send a document to an external service.

Read the publisher's contract before adapting markup. Some accept body fragments rather than a full HTML shell; some require dark-default tokens, system fonts, or declared palettes. Extract or adapt the saved page for that contract without replacing the canonical file with an incompatible fragment.

Reuse the publisher's documented stable artifact key on revision. If stable URLs are not supported, say so. Never claim a local canvas URL is publicly accessible.

## Markdown by request or convention

Preserve the same reader's path, evidence, and boundaries. Use a heading and three opening paragraphs in place of the problem box. Use Mermaid only if the target renderer supports it; otherwise use a linked SVG asset or prose/table. Do not leave a broken diagram as a quality fallback.

HTML and Markdown need not both be generated. If both are requested, keep one content source or verify that behavior, counts, boundaries, and status match after every revision.

## Final handoff

Lead with the artifact link or path and the outcome: the design's direction, or the report's answer and its most severe finding. Mention real unresolved decisions or verification limitations. Do not repeat the whole document in chat, invent a public URL, or automatically create an issue, commit, or pull request.
