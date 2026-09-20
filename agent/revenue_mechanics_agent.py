"""Optional OpenAI Agents SDK runner for Revenue Agentic.

The Agent is deliberately thin. Deterministic solvers remain the source of
truth for calculations. Install with:

    pip install "openai-agents>=0.14.0"

Set OPENAI_API_KEY, then run this module from repository root.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

try:
    from agents import Agent, Runner, function_tool
except ImportError as exc:  # pragma: no cover - optional dependency
    raise SystemExit(
        'Optional dependency missing. Install with: pip install "openai-agents>=0.14.0"'
    ) from exc

ROOT = Path(__file__).resolve().parents[1]

REVENUE_SKILL = (ROOT / "skills/revenue-mechanics/SKILL.md").read_text(encoding="utf-8")
DECISION_SKILL = (
    ROOT / "skills/revenue-decision-science/SKILL.md"
).read_text(encoding="utf-8")

REVENUE_SOLVER = ROOT / "skills/revenue-mechanics/scripts/revenue_solver.py"
DECISION_SOLVER = (
    ROOT / "skills/revenue-decision-science/scripts/decision_solver.py"
)


@function_tool
def run_revenue_mechanics(mode: str, payload_json: str) -> str:
    """Run a validated Revenue Mechanics workflow with a JSON payload."""
    if mode not in {
        "media-funnel", "reverse-funnel", "cro-target", "ecommerce",
        "b2b", "subscription", "scale", "consistency",
    }:
        return json.dumps({"ok": False, "error": f"unsupported mode: {mode}"})
    proc = subprocess.run(
        [sys.executable, str(REVENUE_SOLVER), mode, "--json", payload_json],
        cwd=str(ROOT), capture_output=True, text=True, timeout=30,
    )
    return proc.stdout.strip() or json.dumps(
        {"ok": False, "error": proc.stderr.strip()}
    )


@function_tool
def run_revenue_decision_science(payload_json: str) -> str:
    """Evaluate statistical evidence for scale/hold/optimize/pause decisions."""
    proc = subprocess.run(
        [sys.executable, str(DECISION_SOLVER), "--json", payload_json],
        cwd=str(ROOT), capture_output=True, text=True, timeout=30,
    )
    return proc.stdout.strip() or json.dumps(
        {"ok": False, "error": proc.stderr.strip()}
    )


agent = Agent(
    name="Revenue Agentic",
    instructions=(
        "You are the Revenue Agentic analyst. Revenue Mechanics defines the economic "
        "system and targets; Revenue Decision Science evaluates how much statistical "
        "evidence exists for scale, hold, optimize, reduce or pause decisions. "
        "For every calculation, call the appropriate deterministic solver instead of "
        "doing arithmetic yourself. When a decision depends on both economics and "
        "uncertainty, call both tools. Do not claim causality from metric decomposition "
        "or confuse p-values with the probability that a campaign is good or bad.\n\n"
        "=== REVENUE MECHANICS SKILL ===\n"
        + REVENUE_SKILL
        + "\n\n=== REVENUE DECISION SCIENCE SKILL ===\n"
        + DECISION_SKILL
    ),
    tools=[run_revenue_mechanics, run_revenue_decision_science],
)


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python agent/revenue_mechanics_agent.py "question"')
    result = Runner.run_sync(agent, " ".join(sys.argv[1:]))
    print(result.final_output)


if __name__ == "__main__":
    main()
