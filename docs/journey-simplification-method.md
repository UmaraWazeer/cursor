# Simplifying a dense journey map without losing detail

## 1. Status of the source artefact

The board was supplied as a single downscaled screenshot. At that resolution the
sticky-note and card text is roughly two pixels tall, so **none of the wording on
the board is legible** — not the phase labels along the top, not the swimlane
labels down the left, not the content of any note.

Routes tried to reach the underlying board instead of the screenshot:

| Route | Result |
| --- | --- |
| Locate the image file on disk to read it at native resolution | Not present; only the downscaled copy exists |
| Miro `board_search_boards` | `Board search is temporarily unavailable` (retried) |
| Miro `space_list` → `space_list_boards` | Two spaces visible (`Agility Enablement Area`, `PI planning`), both `Access forbidden` |
| FigJam `get_figjam` on the squad's known board `mpDzwlze9tYwtzM0Q6FJcP` | Returns the *T1 PDC Rich Pictures* board — a different artefact |
| Confluence / Jira search for a matching journey map or board link | No page matches this board's shape |

So everything below in §2 and §3 is derived from **geometry only** — the position,
size, colour and connector pattern of objects, which are readable at this
resolution. Section §4 onward is the method and toolkit, which are independent of
the wording. To finish the content pass, see §8.

## 2. What the artefact is

It is a **service blueprint**, not a plain journey map. The tell is the dashed
horizontal rule immediately below the first swimlane: in blueprint grammar that is
the *line of interaction*, separating what the customer sees from backstage
process. Structure:

- **5 phases** across the top, marked by the dark navy header band split into five
  equal segments.
- **6 swimlanes** down the left, marked by the dark blue left rail.
- Each phase is subdivided into about four placeholder columns, giving a
  pre-drawn grid of roughly **20 columns × 14 rows** of empty cells.
- **A seventh band, detached below the main body**, holding an unconnected cluster
  of notes.
- Roughly **60–75 content objects** — cards plus yellow, pink and green stickies,
  each carrying an author avatar dot — joined by connectors.

## 3. Where the complexity actually sits

This is the part worth acting on. Content is very unevenly distributed:

| Lane | Occupancy |
| --- | --- |
| 1 (front stage, above the line of interaction) | Empty except for one cluster in the **final** phase |
| 2 | Concentrated in phase 1, small cluster in phase 2 |
| 3 | Short chain in phases 1–2 |
| **4** | **The spine — a near-continuous chain of ~12–15 cards from phase 1 to phase 4, carrying the heaviest yellow/pink annotation load** |
| 5 | Sparse, phases 1–2 only |
| 6 | Two disconnected clusters, one in phase 2 and one in phases 4–5 |
| Detached bottom band | ~6–8 notes, no connectors into the flow |

Five findings follow from that:

1. **The grid spends space where there is no content.** Around 70% of the objects
   sit in one lane of six and two phases of five, but the grid reserves equal area
   for every cell. The informative region is compressed while empty cells consume
   most of the canvas.
2. **Four kinds of information share one plane** — sequence on the x-axis,
   ownership on the y-axis, commentary in the sticky colour, and dependency in the
   connectors. Each is legible alone; together they multiply.
3. **A few long-distance connectors cost the most comprehension.** One runs the
   full height of the board, from mid-canvas down past every lane into the bottom
   band. The final-phase clusters in lanes 1 and 6 also reach back to the middle
   of the board. These long runs are what make the map feel unreadable.
4. **The detached bottom band is unanchored content** — notes that belong to the
   discussion but have no position in the flow, so they are invisible to anyone
   reading the journey.
5. **The front stage is nearly empty.** A blueprint whose customer lane is blank
   until the last phase is really a *process and systems* map in blueprint
   clothing. The lane structure is fighting the content it holds.

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

- **Object count** — the number of register rows must equal the
  `expected_counts.notes` you record from the original board.
- **No orphans** — every annotation must resolve to a declared step, or be
  explicitly marked `step: null` with a reason.
- **No dangling references** — every `phase`, `lane` and `step` referenced must be
  declared.
- **Connector accounting** — every connector on the original board must be either
  on the spine or a declared named branch, and the totals must reconcile.
- **Verbatim preservation** — the register carries the original wording in `text`;
  any shortening lives in a separate `summary` field, so the original is never
  overwritten.

Because these are assertions rather than good intentions, "we simplified it and
lost nothing" becomes a claim you can demonstrate.

## 8. Using the toolkit

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

## 9. To complete the content pass

Any one of these unblocks the actual reading of your board:

1. **The board URL** (Miro or FigJam). This is much the best option — it gives the
   text, colours, authors and connector endpoints directly, and the register in
   §5's Move 1 can then be populated automatically rather than by hand.
2. **A PDF export**, which keeps the text as text at any zoom.
3. **A set of cropped screenshots**, one per phase or per swimlane, at readable
   zoom.

With the source in hand the extraction is mechanical, and §5 Moves 2–5 become a
review conversation about the spine rather than a transcription exercise.
