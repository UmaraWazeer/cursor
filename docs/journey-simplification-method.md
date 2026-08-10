# Simplifying a dense journey map without losing detail

## 1. Status of the source artefact

The board first arrived as a single downscaled screenshot in which the note text
was about two pixels tall and completely illegible. It was then supplied as a
**PDF** (`Copy_of_PIM_Service_Blueprint_049c.pdf`), which turned out to be a single
flattened **5417 × 3738** image with no text layer. Extracting that embedded image
and tiling it into overlapping high-resolution crops makes every card and sticky
legible, so the board has now been **fully transcribed** into `journey/journey.yaml`
(85 objects) and the simplified views regenerated from it.

For the record, before the PDF arrived these routes to the live board were tried
and all failed: the image was not on disk at native resolution; Miro
`board_search_boards` returned `Board search is temporarily unavailable`; both
visible Miro spaces (`Agility Enablement Area`, `PI planning`) returned
`Access forbidden`; the squad's known FigJam board `mpDzwlze9tYwtzM0Q6FJcP` is the
*T1 PDC Rich Pictures* board, a different artefact; and Confluence/Jira search
surfaced no page matching this board's shape. The PDF was the unlock.

## 2. What the artefact is

It is a **PIM (Product Information Management) service blueprint** for Kmart — the
end-to-end path a product/SKU takes from Merch creation to being published and
discoverable online, illustrated by a customer persona ("Mary" buying an Easter
basket). It is a service blueprint, not a plain journey map: the dashed horizontal
rule below the first swimlane is the *line of interaction*, separating what the
customer sees from backstage process. Structure:

- **5 phases** across the top — but the headers are unlabelled `Phase` placeholders,
  so the phases carry no names on the board itself. In the model they are named for
  the process stage they contain: *Create & register → Capture imagery → Enrich &
  ingest → Copywrite → Categorise, publish & discover*.
- **6 swimlanes**: `User actions` (front stage), then backstage `Merch Team →
  Photography Studios → Online Team & Merkle → External Suppliers → Marketing &
  Website`.
- Each phase is subdivided into placeholder columns, giving a large pre-drawn grid
  that is mostly empty cells.
- **A seventh band, detached below the main body** (`Additional Notes`), holding an
  unconnected cluster of ~10 systemic observations.
- **85 content objects** — process cards plus yellow (fact), pink (pain) and green
  (follow-up question) stickies, each carrying an author avatar dot — joined by
  connectors that mostly run left-to-right along the `Online Team & Merkle` lane.

## 3. Where the complexity actually sits

This is the part worth acting on. Content is very unevenly distributed across the
85 objects:

| Lane | Objects | Occupancy |
| --- | --- | --- |
| User actions (front stage) | 5 | Customer "Mary" flow, **only in the final phase** |
| Merch Team | 11 | Concentrated in phase 1 (create & register) |
| Photography Studios | 11 | Phase 2, heavy fact/question annotation |
| **Online Team & Merkle** | **35** | **The backbone — a continuous chain end to end, carrying almost all the pain and risk notes** |
| External Suppliers | 4 | Phase 3 only |
| Marketing & Website | 8 | Final phase (channel feeds) |
| Additional Notes (detached) | 10 | No connectors into the flow |

Five findings follow from that:

1. **One lane carries the board.** The `Online Team & Merkle` lane holds 35 of 85
   objects — over 40% — in a single continuous chain, while the grid reserves equal
   area for every cell. The informative region is compressed while empty cells
   consume most of the canvas.
2. **Four kinds of information share one plane** — sequence on the x-axis,
   ownership on the y-axis, commentary in the sticky colour, and dependency in the
   connectors. Each is legible alone; together they multiply.
3. **The long connectors run the length of the Merkle lane.** The backbone threads
   left-to-right across all five phases, and the final-phase `Marketing & Website`
   and `User actions` clusters reach back to it. These long runs are what make the
   board feel unreadable.
4. **The detached `Additional Notes` band is unanchored content** — 10 systemic
   observations (e.g. *"Two systems so two truths"*, *"All systems are MS DOS from
   the 90's"*) that belong to the discussion but have no position in the flow, so
   they are invisible to anyone reading the journey.
5. **The front stage is nearly empty.** The customer lane is blank until the final
   phase, so this is really a *process and systems* map in blueprint clothing — the
   backstage machinery that has to complete before "Mary" can find the product. The
   lane structure is fighting the content it holds.

## 4. The principle

Simplify by **separating the dimensions, not by deleting content**. Every attempt
to simplify a blueprint by "removing the less important stickies" loses detail and
gets rejected by whoever wrote them. Instead, give each kind of information its
own artefact, and connect the artefacts with stable IDs. Nothing is discarded; the
reader chooses their depth. That is progressive disclosure, and it is the only
form of simplification that is genuinely lossless.

## 5. The method — five moves

### Move 1 — Extract to a register before you redraw

Turn the board into data first. Every object on the board becomes one row with a
stable ID, its lane, its phase, its colour, its author and its verbatim text.
Do not paraphrase at this stage.

This single step is what makes losslessness *checkable*: once you know the board
holds, say, 68 objects, any later artefact can be tested against that count.
Redrawing before extracting is how detail gets lost silently.

### Move 2 — Fix the spine

Choose one primary actor and one happy path, and express it as **5–9 steps**,
aligned to the existing phases. That is the whole simplified journey. Everything
else in the register *attaches to* a step rather than occupying canvas beside it.

Your lane 4 already is this spine — it is the only lane with a continuous chain.
Promote it and let the phases stay as they are.

### Move 3 — Collapse lanes into per-step roles

Six persistent swimlanes force every step to reserve vertical space in all six,
which is what produces the sea of empty cells. Replace them: annotate each spine
step with the actors and systems involved in *that* step.

No information is lost, because lane membership is still a field on every register
row — the lane view is recoverable at any time by filtering. You are removing the
*empty space*, not the data.

### Move 4 — Move commentary off the canvas into typed annotations

Retype every non-step note against a fixed vocabulary — `pain`, `risk`,
`assumption`, `question`, `opportunity`, `decision`, `system`, `info` — and attach
it to a step ID. The canvas keeps the flow; the register keeps the discussion.

Most of the visual noise leaves here, and the colour axis is freed up. It also
gives the bottom band a home: those unanchored notes become annotations on the
step they actually concern, or explicit `assumption`/`question` rows with no step,
which is itself a useful finding.

### Move 5 — Reroute exceptions as named branches

Long connectors are the highest-cost, lowest-value marks on the board. Give each
exception path a **name**, and draw it as a short local branch hanging off its
step, with a pointer to where it rejoins. A reader follows a named branch far more
easily than a two-metre diagonal line.

## 6. The three output layers

| Layer | Contents | Audience |
| --- | --- | --- |
| **L0 — one-pager** | The spine only: 5–9 steps under their phase bands | Leadership, stand-ups, PRD intro |
| **L1 — journey view** | Spine + per-step actors and systems + a count of attached annotations per step, so density is visible without reading it | The squad, refinement, planning |
| **L2 — detail register** | Every original object, typed, attributed and linked to a step | Whoever wrote the note; audit and hand-off |

L0 is what replaces the wall. L2 is what guarantees nobody's contribution was
thrown away. L1 is the working artefact that points from one to the other.

## 7. Losslessness guarantees

The generator in `journey/` enforces these mechanically and fails the build if any
are violated:

- **Object count** — the objects represented must equal the
  `expected_counts.objects` you record from the original board. When the spine is a
  consolidation of many cards rather than the literal cards themselves, set
  `synthetic_spine: true` and only the annotations (the literal cards and stickies)
  reconcile — the synthetic steps are excluded so the count stays honest.
- **No orphans** — every annotation must resolve to a declared step, or be
  explicitly marked `step: null` with an `unanchored_reason`.
- **No dangling references** — every `phase`, `lane` and `step` referenced must be
  declared, and no IDs may collide.
- **Connector accounting** — with a literal spine, connector totals must reconcile;
  with a `synthetic_spine` the connector total is advisory, since the drawn edges
  are themselves a simplification.
- **Verbatim preservation** — the register carries the original wording in `text`;
  any shortening lives in a separate `summary` field, so the original is never
  overwritten.

Because these are assertions rather than good intentions, "we simplified it and
lost nothing" becomes a claim you can demonstrate.

## 8. Using the toolkit

The real board has already been transcribed into `journey/journey.yaml` (85
objects, `synthetic_spine: true`). Regenerate the simplified views with:

```bash
python3 journey/build_journey.py journey/journey.yaml
```

To model a different board, start from the annotated template instead:

```bash
cp journey/journey.example.yaml journey/journey.yaml   # then fill in from the board
python3 journey/build_journey.py journey/journey.yaml
```

Outputs land in `journey/out/`:

- `L0-one-pager.md`
- `L1-journey.md`
- `L2-detail-register.md` and `L2-detail-register.csv`
- `journey.miro.dsl` — a layout in the same DSL convention the squad already uses,
  ready to render the simplified board back into Miro

The command exits non-zero and prints every violation if a completeness check
fails, so it can run in CI over the journey file.

`journey/journey.example.yaml` is a small synthetic journey that exercises every
field, including an unanchored note standing in for the board's detached bottom
band. The guarantees in §7 are themselves tested — each test deletes or corrupts
something that must not be lost silently and asserts the build rejects it:

```bash
cd journey && python3 test_build_journey.py
```

## 9. What is now done, and what to check

The content pass is complete: the PDF was the source that unblocked it, the board
is transcribed into `journey/journey.yaml`, and the L0/L1/L2 views plus the Miro
DSL are generated and reconcile against all 85 objects.

What remains is a **review of the model's judgement calls**, none of which lose
data (everything is verbatim in the L2 register regardless):

1. **Phase names.** The board's phases were blank `Phase` placeholders; the five
   stage names are the model's interpretation of the flow. Rename freely.
2. **Spine granularity.** The 8 spine steps consolidate ~44 process cards. If the
   squad wants a step split or merged, adjust `steps` — the attached cards move with
   their `step` reference.
3. **A few source-legibility calls.** The board is a flattened raster, so one or two
   long stickies and a couple of avatar/system labels were read as best as the pixels
   allowed (e.g. studio name "Melohd"/"Melodie", "MAM"/"MAM?"). These are flagged
   with `?` in the text and are worth a second eye. The live board URL would let
   these be confirmed exactly.
