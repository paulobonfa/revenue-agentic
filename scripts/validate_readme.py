"""Validate README structure and GitHub math render safety."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"

FORBIDDEN_MATH = {
    r"\operatorname": "GitHub rejects this macro in repository math rendering",
    r"\newcommand": "custom macro definitions are not allowed",
    r"\renewcommand": "custom macro definitions are not allowed",
    r"\require": "runtime package loading is not allowed",
}

REQUIRED_SECTIONS = (
    "## Aula completa: Revenue Mechanics do zero",
    "### 3. A equação fundamental",
    "### 5. Planejamento reverso: partir da meta",
    "### 6. A cadeia de custos nasce da cadeia de fluxo",
    "## Exemplos práticos resolvidos",
    "## Confiabilidade",
)


def relative_links(markdown: str) -> set[str]:
    links: set[str] = set()
    for target in re.findall(r"\]\(([^)]+)\)", markdown):
        target = target.strip()
        if target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        path = target.split("#", 1)[0]
        if path:
            links.add(path)
    return links


def main() -> int:
    errors: list[str] = []
    text = README.read_text(encoding="utf-8")

    fence_count = sum(line.startswith("```") for line in text.splitlines())
    if fence_count % 2:
        errors.append(f"unbalanced fenced blocks: {fence_count}")

    math_blocks = re.findall(r"```math\s*\n(.*?)\n```", text, flags=re.DOTALL)
    if not math_blocks:
        errors.append("no GitHub-native math blocks found")

    for macro, reason in FORBIDDEN_MATH.items():
        if macro in text:
            errors.append(f"forbidden math macro {macro}: {reason}")

    if r"\[" in text or r"\]" in text:
        errors.append(r"legacy \[...\] math delimiter found; use ```math blocks")

    for section in REQUIRED_SECTIONS:
        if section not in text:
            errors.append(f"required section missing: {section}")

    links = relative_links(text)
    for link in sorted(links):
        if not (ROOT / link).exists():
            errors.append(f"broken relative link: {link}")

    if errors:
        for error in errors:
            print(f"FAIL: README: {error}")
        return 1

    print(
        "PASS: README render-safety "
        f"({len(math_blocks)} math blocks, {len(links)} relative links)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
