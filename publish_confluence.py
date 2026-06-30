#!/usr/bin/env python3
"""Build full Confluence page body with groups appended."""

import json
from html import escape
from pathlib import Path

# Existing page body fetched from Confluence API (version 10)
EXISTING_BODY_PATH = Path(__file__).parent / "confluence_existing_body.html"

with open(Path(__file__).parent / "squad_groups.json") as f:
    groups = json.load(f)

ungrouped = [
    {"name": "Oxana Alexandrova", "role": "Senior Engineer", "squad": 19, "squad_name": "Loyalty & Engagement"},
    {"name": "Darcy Vreeken", "role": "Engineer", "squad": 19, "squad_name": "Loyalty & Engagement"},
]

parts = [
    '<hr>',
    '<h2>Team Allocation — Groups of 6</h2>',
    '<div data-type="panel-info"><p><strong>Rules applied</strong></p><ul>',
    '<li>BLR members excluded from grouping</li>',
    '<li>Squad members kept together where possible</li>',
    '<li>Members borrowed from adjacent squads when needed to complete groups of 6</li>',
    '<li>PM/PD and BA/IM may be in separate groups</li>',
    '</ul></div>',
]

for g in groups:
    squads = ' + '.join(f'Squad {s}' for s in g['squads'])
    parts.append(f'<h3>Group {g["group_num"]} ({squads})</h3><ul>')
    for m in g['members']:
        text = (
            f'<strong>{escape(m["name"])}</strong> — {escape(m["role"])} '
            f'<em>(Squad {m["squad"]}: {escape(m["squad_name"])})</em>'
        )
        parts.append(f'<li><p>{text}</p></li>')
    parts.append('</ul>')

if ungrouped:
    parts.append('<h3>Not grouped (insufficient squad size)</h3><ul>')
    for m in ungrouped:
        text = (
            f'<strong>{escape(m["name"])}</strong> — {escape(m["role"])} '
            f'<em>(Squad {m["squad"]}: {escape(m["squad_name"])})</em>'
        )
        parts.append(f'<li><p>{text}</p></li>')
    parts.append('</ul>')

append_html = ''.join(parts)

if EXISTING_BODY_PATH.exists():
    existing = EXISTING_BODY_PATH.read_text()
    # Remove trailing empty paragraphs if groups section already exists (idempotent update)
    marker = '<h2>Team Allocation — Groups of 6</h2>'
    if marker in existing:
        existing = existing.split('<hr>')[0] if marker in existing else existing
        idx = existing.find(marker)
        if idx != -1:
            existing = existing[:existing.rfind('<hr>', 0, idx)]
    full_body = existing + append_html
else:
    full_body = append_html

Path(__file__).parent.joinpath('confluence_full_body.html').write_text(full_body)
print(len(full_body))
