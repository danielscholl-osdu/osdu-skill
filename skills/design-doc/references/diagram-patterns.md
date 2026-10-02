# Diagram grammar

Use inline SVG inside `<div class="flow">` for HTML. Draw against a fixed viewBox and scale with CSS. A generator can place repetitive elements, but the author owns the geometry and labels.

## The box

Use a title, one or two detail lines, and an optional caveat. The page kit defines the classes.

```svg
<rect x="24" y="58" width="216" height="100" class="box b-o1"/>
<text x="36" y="82" class="t">Payload repository</text>
<text x="36" y="104" class="sub">Publishes a versioned image</text>
<text x="36" y="126" class="sub">Owns schema contents</text>
<text x="36" y="146" class="tiny">Release tag is the input</text>
```

Text starts 12px from the left edge. Use around 80px of height for a title, one detail line, and a caveat; around 100px for two detail lines. Leave at least 12px below the final baseline.

Approximate width budgets are useful, not proof: at 12px, budget roughly 7px per character. Font, case, and glyphs change that estimate. Measure rendered bounds and inspect the page. Shorten or wrap a label before shrinking it; diagram text must stay at least 11px, with titles normally 14px.

Explicit `<tspan>` lines are more portable than relying on SVG text wrapping.

## Color and identity

`b-o1` through `b-o4` represent owners or actors defined in the page legend. Add tokens if more owners are needed. `b-mute` means an unused, excluded, or out-of-band element; define the specific dashed meaning in the legend.

`b-ok`, `b-warn`, and `b-bad` describe outcomes or severity, never owners. A role assignment is not intrinsically a failure: use a neutral or owner-colored chip unless the chip actually depicts a denied or dangerous outcome.

Labels must identify owners and outcomes even without color. Check light and dark theme contrast. Recipient-pill foregrounds come from theme tokens; do not assume white is legible on a pale dark-theme owner color. A pass, warning, and denial must have explicit text, not just green, grey, and red.

## Lanes

Use lanes for stages or ownership boundaries. Boxes read left to right, and cross-lane arrows show transitions.

```svg
<rect x="8" y="8" width="984" height="156" class="lanebg"/>
<text x="22" y="30" class="lanelbl">Payload repository CI</text>
```

For today versus the design, use the same left-to-right geometry where possible so the changed mechanism is the thing that moves. Do not add empty lanes simply to fill the page.

## Arrows

Draw connections before boxes when their paths run beneath nodes. Do not place arrow labels where a box will cover them.

```svg
<path d="M240 106 L280 106" class="arrow" marker-end="url(#ownership-arrow)"/>
```

Define markers inside each SVG with a document-unique prefix, such as `ownership-arrow` or `permission-denied-arrow`. Each diagram should remain valid if extracted on its own. Avoid repeated IDs and cross-diagram marker dependencies.

Label an edge only when its endpoints do not already communicate the relationship. Branch labels should name the condition, such as "present", "absent", or "API unavailable".

## Decision trees

The decision names the actual input or predicate. Each leaf names the outcome and the actor or case that reaches it.

```svg
<polygon points="500,70 640,118 500,166 360,118" class="decision"/>
<text x="500" y="111" text-anchor="middle" class="t">Payload directory present?</text>
<text x="500" y="133" text-anchor="middle" class="sub mono">schemas/</text>
```

An error leaf states whether the mechanism stops, warns, retries, or skips. Do not merge "no payload" and "failed to inspect payload" into the same successful skip unless that is the actual design.

## Chips and recipients

One chip represents one thing on one recipient. Two recipients require two chips. Put the recipient on the chip, not in a caption that the reader has to match by inference. The pill takes its owner's color: `p-o1` through `p-o4`.

```svg
<rect x="24" y="114" width="340" height="28" class="chip"/>
<text x="34" y="133" class="chipt">Artifact Reader</text>
<rect x="208" y="118" width="144" height="20" class="pill p-o4"/>
<text x="216" y="132" class="pillt">runtime identity</text>
```

Dashed chips (`chip chip-dashed`) represent an explicitly explained exception or out-of-band operation. A dashed shape is not a general decoration.

## Layers

Draw an assembled image or artifact as stacked parts inside its owner's outer box, each labeled with its contributor. Arrows from contributors show what enters the assembly. State the execution or layering order; do not assume that "top" means "runs first" for every artifact.

## Accessibility and sizing

- Use `role="img"` with a concise accessible name and, for complex diagrams, a `<desc>` linked with `aria-describedby`.
- Accessible descriptions may repeat the mechanism for readers who cannot see the diagram. The no-repetition rule concerns visible editorial duplication, not accessibility.
- Start with a viewBox width around 1000 to 1124 and a content-sized height. Keep at least 12px of outer margin.
- The kit uses a 1000px minimum SVG width for a 1000-unit viewBox. If the viewBox is wider, raise that diagram's minimum width to match so scaling does not reduce 11px labels below 11 rendered pixels. Diagrams scroll internally on narrow screens; horizontal scrolling of the whole document is not.
- Verify arrowheads, text bounds, labels, and captions in both themes. Static coordinate estimates do not replace image inspection.

## When not to draw

A list of facts is a table. A single unbranched path is often a sentence. A two-option comparison is a table unless the topology itself differs. If a drawing only decorates a paragraph, remove it.
