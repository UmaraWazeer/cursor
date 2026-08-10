#!/usr/bin/env python3
"""Build the L0/L1/L2 journey artefacts from a journey definition.

Reads a journey YAML file, verifies that nothing from the original board has been
dropped, and writes the simplified views plus a Miro layout. Exits non-zero if any
completeness check fails, so it can run in CI over the journey file.

Usage:
    python3 journey/build_journey.py journey/journey.yaml [--out DIR]
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ANNOTATION_TYPES = (
    "pain",
    "risk",
    "assumption",
    "question",
    "opportunity",
    "decision",
    "system",
    "info",
)

# Annotation type -> Miro sticky colour, so the rebuilt board reads consistently.
STICKY_COLOURS = {
    "pain": "light_pink",
    "risk": "red",
    "assumption": "violet",
    "question": "orange",
    "opportunity": "light_green",
    "decision": "cyan",
    "system": "light_blue",
    "info": "light_yellow",
}

SPINE_MIN, SPINE_MAX = 5, 9


@dataclass
class Report:
    """Collected check results. Errors fail the build; warnings are advisory."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    @property
    def ok(self) -> bool:
        return not self.errors


class Journey:
    def __init__(self, data: dict):
        self.title = data.get("title") or "Untitled journey"
        self.source = data.get("source") or ""
        self.primary_actor = data.get("primary_actor") or ""
        self.expected = data.get("expected_counts") or {}
        self.phases = data.get("phases") or []
        self.lanes = data.get("lanes") or []
        self.steps = data.get("steps") or []
        self.branches = data.get("branches") or []
        self.cross_links = data.get("cross_links") or []
        self.annotations = data.get("annotations") or []

    @property
    def phase_ids(self) -> list[str]:
        return [p["id"] for p in self.phases]

    @property
    def lane_ids(self) -> set[str]:
        return {lane["id"] for lane in self.lanes}

    @property
    def branch_steps(self) -> list[dict]:
        return [s for b in self.branches for s in (b.get("steps") or [])]

    @property
    def step_ids(self) -> set[str]:
        return {s["id"] for s in self.steps} | {s["id"] for s in self.branch_steps}

    def lane_name(self, lane_id: str) -> str:
        for lane in self.lanes:
            if lane["id"] == lane_id:
                return lane["name"]
        return lane_id

    def phase_name(self, phase_id: str) -> str:
        for phase in self.phases:
            if phase["id"] == phase_id:
                return phase["name"]
        return phase_id

    def steps_in_phase(self, phase_id: str) -> list[dict]:
        return [s for s in self.steps if s.get("phase") == phase_id]

    def annotations_for(self, step_id: str) -> list[dict]:
        return [a for a in self.annotations if a.get("step") == step_id]

    @property
    def unanchored(self) -> list[dict]:
        return [a for a in self.annotations if not a.get("step")]

    def object_count(self) -> int:
        return len(self.steps) + len(self.branch_steps) + len(self.annotations)

    def connector_count(self) -> int:
        """Spine transitions + branch edges + explicit cross-links."""
        spine = max(len(self.steps) - 1, 0)
        branch = 0
        for b in self.branches:
            inner = b.get("steps") or []
            if inner:
                branch += 1 + (len(inner) - 1)
            if b.get("rejoins"):
                branch += 1
        return spine + branch + len(self.cross_links)


def check(journey: Journey) -> Report:
    report = Report()

    _check_unique_ids(journey, report)
    _check_references(journey, report)
    _check_annotations(journey, report)
    _check_counts(journey, report)

    if not journey.steps:
        report.error("No steps defined — the spine is empty.")
    elif not SPINE_MIN <= len(journey.steps) <= SPINE_MAX:
        report.warn(
            f"Spine has {len(journey.steps)} steps; aim for {SPINE_MIN}-{SPINE_MAX} "
            "so the one-pager stays readable."
        )

    return report


def _check_unique_ids(journey: Journey, report: Report) -> None:
    groups = {
        "phase": [p.get("id") for p in journey.phases],
        "lane": [lane.get("id") for lane in journey.lanes],
        "step": [s.get("id") for s in journey.steps] + [s.get("id") for s in journey.branch_steps],
        "branch": [b.get("id") for b in journey.branches],
        "annotation": [a.get("id") for a in journey.annotations],
    }
    for kind, ids in groups.items():
        if None in ids:
            report.error(f"At least one {kind} is missing an `id`.")
        seen, dupes = set(), set()
        for value in ids:
            if value in seen:
                dupes.add(value)
            seen.add(value)
        for value in sorted(str(d) for d in dupes):
            report.error(f"Duplicate {kind} id: {value}")


def _check_references(journey: Journey, report: Report) -> None:
    phase_ids, lane_ids, step_ids = set(journey.phase_ids), journey.lane_ids, journey.step_ids

    for step in journey.steps:
        if step.get("phase") not in phase_ids:
            report.error(f"Step {step.get('id')} references undeclared phase {step.get('phase')!r}.")
        for lane_id in step.get("lanes") or []:
            if lane_id not in lane_ids:
                report.error(f"Step {step.get('id')} references undeclared lane {lane_id!r}.")

    for branch in journey.branches:
        if branch.get("from_step") not in step_ids:
            report.error(
                f"Branch {branch.get('id')} leaves from undeclared step "
                f"{branch.get('from_step')!r}."
            )
        rejoins = branch.get("rejoins")
        if rejoins and rejoins not in step_ids:
            report.error(f"Branch {branch.get('id')} rejoins undeclared step {rejoins!r}.")
        if not branch.get("steps"):
            report.error(f"Branch {branch.get('id')} has no steps.")

    for link in journey.cross_links:
        for end in ("from", "to"):
            if link.get(end) not in step_ids:
                report.error(f"Cross-link {end} references undeclared step {link.get(end)!r}.")


def _check_annotations(journey: Journey, report: Report) -> None:
    step_ids, lane_ids, phase_ids = journey.step_ids, journey.lane_ids, set(journey.phase_ids)

    for note in journey.annotations:
        note_id = note.get("id")

        if not (note.get("text") or "").strip():
            report.error(f"Annotation {note_id} has no `text` — the verbatim wording is required.")

        if note.get("type") not in ANNOTATION_TYPES:
            report.error(
                f"Annotation {note_id} has type {note.get('type')!r}; "
                f"expected one of {', '.join(ANNOTATION_TYPES)}."
            )

        step_id = note.get("step")
        if step_id:
            if step_id not in step_ids:
                report.error(f"Annotation {note_id} attaches to undeclared step {step_id!r}.")
        elif not (note.get("unanchored_reason") or "").strip():
            report.error(
                f"Annotation {note_id} has no step and no `unanchored_reason` — "
                "unplaced objects must say why so they are not lost silently."
            )

        lane_id = note.get("lane")
        if lane_id and lane_id not in lane_ids:
            report.error(f"Annotation {note_id} references undeclared lane {lane_id!r}.")

        phase_id = note.get("phase")
        if phase_id and phase_id not in phase_ids:
            report.error(f"Annotation {note_id} references undeclared phase {phase_id!r}.")


def _check_counts(journey: Journey, report: Report) -> None:
    expected_objects = journey.expected.get("objects")
    if expected_objects is None:
        report.warn(
            "`expected_counts.objects` is not set, so object-level losslessness "
            "cannot be verified. Count the cards and stickies on the original board."
        )
    elif journey.object_count() != expected_objects:
        report.error(
            f"Object count mismatch: the original board has {expected_objects} objects "
            f"but this file accounts for {journey.object_count()} "
            f"({len(journey.steps)} steps + {len(journey.branch_steps)} branch steps + "
            f"{len(journey.annotations)} annotations)."
        )

    expected_connectors = journey.expected.get("connectors")
    if expected_connectors is None:
        report.warn("`expected_counts.connectors` is not set, so connectors are not reconciled.")
    elif journey.connector_count() != expected_connectors:
        report.error(
            f"Connector count mismatch: the original board has {expected_connectors} "
            f"connectors but this file accounts for {journey.connector_count()}."
        )


def render_l0(journey: Journey) -> str:
    lines = [f"# {journey.title} — one-pager", ""]
    if journey.primary_actor:
        lines += [f"**Primary actor:** {journey.primary_actor}", ""]
    if journey.source:
        lines += [f"**Source board:** {journey.source}", ""]

    lines += ["The happy path, and nothing else. Detail lives in the L2 register.", ""]

    counter = 0
    for phase_id in journey.phase_ids:
        phase_steps = journey.steps_in_phase(phase_id)
        if not phase_steps:
            continue
        lines += [f"## {journey.phase_name(phase_id)}", ""]
        for step in phase_steps:
            counter += 1
            lines.append(f"{counter}. **{step['name']}**")
        lines.append("")

    if journey.branches:
        lines += ["## Exception paths", ""]
        for branch in journey.branches:
            rejoins = branch.get("rejoins")
            tail = f", rejoins at {rejoins}" if rejoins else ""
            lines.append(f"- **{branch['name']}** — from {branch['from_step']}{tail}")
        lines.append("")

    return "\n".join(lines)


def render_l1(journey: Journey) -> str:
    lines = [f"# {journey.title} — journey view", ""]
    if journey.source:
        lines += [f"**Source board:** {journey.source}", ""]
    lines += [
        "Each step carries the actors and systems that were previously spread across "
        "swimlanes, plus how much attached detail sits behind it in the L2 register.",
        "",
        "| # | Phase | Step | Actors | Systems | Original lanes | Attached detail |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    for index, step in enumerate(journey.steps, start=1):
        notes = journey.annotations_for(step["id"])
        counts: dict[str, int] = {}
        for note in notes:
            counts[note["type"]] = counts.get(note["type"], 0) + 1
        detail = ", ".join(f"{count} {name}" for name, count in sorted(counts.items())) or "—"
        lanes = ", ".join(journey.lane_name(l) for l in step.get("lanes") or []) or "—"
        lines.append(
            f"| {index} | {journey.phase_name(step.get('phase', ''))} | {step['name']} "
            f"| {', '.join(step.get('actors') or []) or '—'} "
            f"| {', '.join(step.get('systems') or []) or '—'} | {lanes} | {detail} |"
        )

    lines.append("")

    for branch in journey.branches:
        rejoins = branch.get("rejoins")
        tail = f" and rejoins at {rejoins}" if rejoins else ""
        lines += [
            f"## Branch — {branch['name']}",
            "",
            f"Leaves {branch['from_step']}{tail}.",
            "",
        ]
        for step in branch.get("steps") or []:
            lines.append(f"- **{step['name']}** ({', '.join(step.get('actors') or []) or '—'})")
        lines.append("")

    if journey.cross_links:
        lines += ["## Cross-links", ""]
        for link in journey.cross_links:
            lines.append(f"- {link['from']} → {link['to']}: {link.get('label', '')}".rstrip(": "))
        lines.append("")

    if journey.unanchored:
        lines += [
            "## Unplaced objects",
            "",
            f"{len(journey.unanchored)} object(s) from the original board have no step. "
            "They are listed in full in the L2 register.",
            "",
        ]

    return "\n".join(lines)


def render_l2(journey: Journey) -> str:
    lines = [
        f"# {journey.title} — detail register",
        "",
        f"Every object from the original board: {journey.object_count()} in total "
        f"({len(journey.steps)} steps, {len(journey.branch_steps)} branch steps, "
        f"{len(journey.annotations)} annotations). Wording is verbatim.",
        "",
    ]

    step_lookup = {s["id"]: s for s in journey.steps}
    step_lookup.update({s["id"]: s for s in journey.branch_steps})

    for step_id, step in step_lookup.items():
        notes = journey.annotations_for(step_id)
        if not notes:
            continue
        lines += [
            f"## {step_id} — {step['name']}",
            "",
            "| ID | Type | Detail | Lane | Author |",
            "| --- | --- | --- | --- | --- |",
        ]
        for note in notes:
            lane = journey.lane_name(note["lane"]) if note.get("lane") else "—"
            text = note["text"].strip().replace("\n", " ").replace("|", "\\|")
            lines.append(
                f"| {note['id']} | {note['type']} | {text} | {lane} "
                f"| {note.get('author', '—')} |"
            )
        lines.append("")

    if journey.unanchored:
        lines += [
            "## Unplaced objects",
            "",
            "Objects with no position in the flow, kept with the reason they could not "
            "be placed.",
            "",
            "| ID | Type | Detail | Why unplaced | Author |",
            "| --- | --- | --- | --- | --- |",
        ]
        for note in journey.unanchored:
            text = note["text"].strip().replace("\n", " ").replace("|", "\\|")
            reason = (note.get("unanchored_reason") or "").strip().replace("\n", " ")
            lines.append(
                f"| {note['id']} | {note['type']} | {text} | {reason} "
                f"| {note.get('author', '—')} |"
            )
        lines.append("")

    return "\n".join(lines)


def render_csv(journey: Journey, path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["id", "step", "step_name", "type", "text", "summary", "lane", "phase",
             "colour", "author", "unanchored_reason"]
        )
        names = {s["id"]: s["name"] for s in journey.steps}
        names.update({s["id"]: s["name"] for s in journey.branch_steps})
        for note in journey.annotations:
            step_id = note.get("step") or ""
            writer.writerow(
                [
                    note.get("id", ""),
                    step_id,
                    names.get(step_id, ""),
                    note.get("type", ""),
                    (note.get("text") or "").strip(),
                    (note.get("summary") or "").strip(),
                    journey.lane_name(note["lane"]) if note.get("lane") else "",
                    note.get("phase", ""),
                    note.get("colour", ""),
                    note.get("author", ""),
                    (note.get("unanchored_reason") or "").strip(),
                ]
            )


def render_miro_dsl(journey: Journey) -> str:
    """Emit the simplified board in the layout DSL the squad already uses."""

    def quote(text: str) -> str:
        return text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")

    phase_width, phase_gap = 1100, 60
    card_width, card_height = 300, 120

    lines = [
        f'title TEXT x=0 y=-400 w=3000 size=48 align=center font=open_sans "{quote(journey.title)}"'
    ]
    if journey.primary_actor:
        lines.append(
            f'subtitle TEXT x=0 y=-300 w=2800 size=16 align=center color=#666666 '
            f'"{quote(journey.primary_actor)}"'
        )

    occupied = [p for p in journey.phase_ids if journey.steps_in_phase(p)]
    for index, phase_id in enumerate(occupied):
        phase_steps = journey.steps_in_phase(phase_id)
        frame_x = index * (phase_width + phase_gap)
        frame_height = 200 + len(phase_steps) * (card_height + 40)
        lines.append(
            f'{phase_id} FRAME x={frame_x} y=0 w={phase_width} h={frame_height} '
            f'fill=#EEF6FF "{quote(journey.phase_name(phase_id))}"'
        )
        lines.append(
            f'{phase_id}t TEXT parent={phase_id} x={phase_width // 2} y=45 '
            f'w={phase_width - 40} size=24 align=center font=open_sans '
            f'"{quote(journey.phase_name(phase_id))}"'
        )
        for position, step in enumerate(phase_steps):
            card_y = 140 + position * (card_height + 40)
            lines.append(
                f'{step["id"]} STICKY parent={phase_id} x={phase_width // 2} y={card_y} '
                f'w={card_width} color=light_blue "{quote(step["name"])}"'
            )

    # Annotations sit below the spine, one column per step, so density is visible
    # without the notes competing with the flow.
    annotation_top = 900
    for index, step in enumerate(journey.steps):
        notes = journey.annotations_for(step["id"])
        if not notes:
            continue
        column_x = index * (card_width + 60)
        lines.append(
            f'{step["id"]}_ann FRAME x={column_x} y={annotation_top} w={card_width + 40} '
            f'h={120 + len(notes) * 180} fill=#FAFAFA "{quote(step["name"])}"'
        )
        for position, note in enumerate(notes):
            colour = STICKY_COLOURS.get(note["type"], "light_yellow")
            body = f'{note["type"].upper()}: {note.get("summary") or note["text"]}'
            lines.append(
                f'{note["id"]} STICKY parent={step["id"]}_ann x={(card_width + 40) // 2} '
                f'y={90 + position * 180} w={card_width - 40} color={colour} "{quote(body)}"'
            )

    for index, branch in enumerate(journey.branches):
        branch_steps = branch.get("steps") or []
        frame_x = index * (phase_width + phase_gap)
        lines.append(
            f'{branch["id"]} FRAME x={frame_x} y=600 w={phase_width} '
            f'h={160 + len(branch_steps) * (card_height + 40)} fill=#FFF6E5 '
            f'"{quote(branch["name"])}"'
        )
        for position, step in enumerate(branch_steps):
            lines.append(
                f'{step["id"]} STICKY parent={branch["id"]} x={phase_width // 2} '
                f'y={120 + position * (card_height + 40)} w={card_width} color=orange '
                f'"{quote(step["name"])}"'
            )

    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("journey", type=Path, help="Path to the journey YAML file")
    parser.add_argument("--out", type=Path, default=None, help="Output directory")
    args = parser.parse_args(argv)

    if not args.journey.exists():
        print(f"error: {args.journey} not found", file=sys.stderr)
        return 2

    data = yaml.safe_load(args.journey.read_text(encoding="utf-8")) or {}
    journey = Journey(data)
    report = check(journey)

    for warning in report.warnings:
        print(f"warning: {warning}")
    for error in report.errors:
        print(f"error: {error}", file=sys.stderr)

    if not report.ok:
        print(
            f"\n{len(report.errors)} completeness check(s) failed — no output written.",
            file=sys.stderr,
        )
        return 1

    out_dir = args.out or args.journey.parent / "out"
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "L0-one-pager.md").write_text(render_l0(journey), encoding="utf-8")
    (out_dir / "L1-journey.md").write_text(render_l1(journey), encoding="utf-8")
    (out_dir / "L2-detail-register.md").write_text(render_l2(journey), encoding="utf-8")
    render_csv(journey, out_dir / "L2-detail-register.csv")
    (out_dir / "journey.miro.dsl").write_text(render_miro_dsl(journey), encoding="utf-8")

    print(
        f"\nAll checks passed: {journey.object_count()} objects and "
        f"{journey.connector_count()} connectors accounted for."
    )
    print(f"Wrote 5 artefacts to {out_dir}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
