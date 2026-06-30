#!/usr/bin/env python3
"""Build combined Confluence HTML body for update."""
from pathlib import Path

# Existing page body from Confluence API v10 (fetched via getConfluencePage)
existing_path = Path(__file__).parent / "confluence_existing_body.html"
append_path = Path(__file__).parent / "confluence_append.html"
output_path = Path(__file__).parent / "confluence_full_body.html"

if not existing_path.exists():
    raise SystemExit(f"Missing {existing_path}")

existing = existing_path.read_text()
append_html = append_path.read_text()

# Idempotent: strip prior groups section if re-running
marker = "<h2>Team Allocation — Groups of 6</h2>"
if marker in existing:
    idx = existing.find(marker)
    hr_idx = existing.rfind("<hr", 0, idx)
    if hr_idx != -1:
        existing = existing[:hr_idx]

full_body = existing + append_html
output_path.write_text(full_body)
print(f"Wrote {len(full_body)} bytes to {output_path}")
