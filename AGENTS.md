# Agent instructions — Revenue Agentic repository

The primary product in this repository is the portable Agent Skill at:

`skills/revenue-mechanics/SKILL.md`

When a task involves acquisition economics, CRO, funnels, CRM, ecommerce, B2B pipeline, recurring revenue, LTV/payback, KPI decomposition, reverse planning, marginal efficiency, or metric consistency:

1. Read `skills/revenue-mechanics/SKILL.md`.
2. Follow its progressive-disclosure references only as needed.
3. Use the deterministic Python solver/engine for calculations; do not substitute LLM arithmetic for implemented formulas.
4. Keep mathematical identities separate from forecasts and causal claims.
5. Before modifying formulas, run:
   - `python skills/revenue-mechanics/scripts/validate_skill.py`
   - `python scripts/validate_production.py`

Repository-wide mathematical authority:

- `revenue_mechanics.py` — deterministic engine.
- `reliability_registry.py` — ICO/governance registry.
- `docs/MATHEMATICAL_SPEC.md` — full derivations.
- `docs/VALIDATION_REPORT.md` — empirical/synthetic validation.
- `docs/PRODUCTION_GATES.md` — release gates.
