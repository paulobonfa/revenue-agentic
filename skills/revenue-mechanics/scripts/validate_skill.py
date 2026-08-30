#!/usr/bin/env python3
"""Dependency-free validation for the Revenue Mechanics SKILL.md package."""
from __future__ import annotations

import re
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL = SKILL_ROOT / "SKILL.md"
ALLOWED_FRONTMATTER_KEYS = {
    "allowed-tools",
    "description",
    "license",
    "metadata",
    "name",
}


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def parse_top_level_frontmatter(frontmatter: str) -> dict[str, str]:
    """Parse the controlled top-level scalar keys without a YAML dependency.

    The validator only needs the top-level schema and the scalar name/description.
    Nested metadata remains YAML-compatible but is deliberately not reimplemented.
    """
    parsed: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if not line or line[0].isspace() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z0-9_-]+):(?:\s*(.*))?", line)
        if not match:
            fail(f"malformed top-level frontmatter line: {line!r}")
        key, value = match.groups()
        parsed[key] = (value or "").strip().strip("\"'")
    return parsed


def main() -> int:
    text = SKILL.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail("SKILL.md must start with YAML frontmatter")
    try:
        _, front, body = text.split("---", 2)
    except ValueError:
        fail("SKILL.md frontmatter delimiters are malformed")
    data = parse_top_level_frontmatter(front)
    unexpected = sorted(set(data) - ALLOWED_FRONTMATTER_KEYS)
    if unexpected:
        fail(f"unsupported frontmatter key(s): {unexpected}")
    for field in ("name", "description"):
        if not data.get(field):
            fail(f"missing required field: {field}")
    name = data["name"]
    if len(name) > 64 or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        fail("name violates Agent Skills naming constraints")
    if len(data["description"]) > 1024:
        fail("description exceeds 1024 characters")
    if len(body.splitlines()) > 500:
        fail("SKILL.md body exceeds recommended 500 lines")

    refs = re.findall(r"`((?:scripts|references|assets)/[^`]+)`", body)
    missing = [r for r in refs if not (SKILL_ROOT / r).exists()]
    if missing:
        fail(f"referenced files missing: {missing}")

    print("PASS: Agent Skill structure")
    print(f"name={name}")
    print(f"body_lines={len(body.splitlines())}")
    print(f"bundled_refs={len(set(refs))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
