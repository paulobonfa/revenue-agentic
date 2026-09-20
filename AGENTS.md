# Agent instructions — Revenue Agentic repository

This repository exposes two portable Agent Skills:

- `skills/revenue-mechanics/SKILL.md` — acquisition economics, KPI decomposition, reverse planning, unit economics and metric consistency.
- `skills/revenue-decision-science/SKILL.md` — statistical evidence for scale / hold / optimize / reduce / pause decisions.

## Routing

When a task involves acquisition economics, CRO, funnels, CRM, ecommerce, B2B pipeline, recurring revenue, LTV/payback, KPI decomposition, reverse planning, marginal efficiency, or metric consistency:

1. Read `skills/revenue-mechanics/SKILL.md`.
2. Follow its progressive-disclosure references only as needed.
3. Use the deterministic Revenue Mechanics solver/engine for calculations; do not substitute LLM arithmetic for implemented formulas.
4. Keep mathematical identities separate from forecasts and causal claims.

When a task asks whether to scale, maintain, optimize, reduce or pause a campaign/creative — or asks about sample size, confidence, significance, probability of observed outcomes, standard error, variance, standard deviation or zero-conversion stop rules:

1. Read `skills/revenue-decision-science/SKILL.md`.
2. Check conversion/revenue maturity before taking a hard decision.
3. Use `skills/revenue-decision-science/scripts/decision_solver.py` for the statistical calculation.
4. Keep statistical evidence separate from business economics: a statistically strong campaign can still be economically bad, and an economically attractive point estimate can still have weak evidence.
5. When both questions exist, use the sequence:
   - Revenue Mechanics defines the economic target/constraint.
   - Revenue Decision Science evaluates the evidence around the observed result.
   - The agent translates both into an operational decision.

## Validation

Before modifying Revenue Mechanics formulas or governance, run:

- `python skills/revenue-mechanics/scripts/validate_skill.py`
- `python scripts/validate_production.py`

For Revenue Decision Science changes, run:

- `python -m pytest tests/test_revenue_decision_science.py`

Repository-wide mathematical authority:

- `revenue_mechanics.py` — deterministic Revenue Mechanics engine.
- `reliability_registry.py` — ICO/governance registry.
- `docs/MATHEMATICAL_SPEC.md` — Revenue Mechanics derivations.
- `docs/VALIDATION_REPORT.md` — empirical/synthetic validation.
- `docs/PRODUCTION_GATES.md` — release gates.
- `skills/revenue-decision-science/references/STATISTICAL_RULES.md` — statistical decision rules.
