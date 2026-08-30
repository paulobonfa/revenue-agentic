---
name: revenue-mechanics
description: Decompose acquisition, CRO, CRM, sales, ecommerce, recurring revenue and unit-economics metrics with the deterministic Revenue Mechanics engine. Use for KPI diagnosis, reverse planning, target setting, metric consistency checks, economic limits, funnel decomposition, scale/marginal analysis, and prioritization of revenue levers. Always use the bundled scripts for arithmetic and keep identities separate from forecasts or causal hypotheses.
license: CC-BY-SA-4.0
metadata:
  author: Paulo Bonfa
  product: Revenue Agentic
  version: "2.1.0-rc1"
  framework: Revenue Mechanics / Equacoes Bonfarianas
  architecture: skill-first-deterministic-core
  production-gate: "CORE_A+B >= 95"
  compatibility: Python 3.10+; optional agent runner requires openai-agents>=0.14.0
---

# Revenue Mechanics Skill

Use this skill to turn business metrics into a mathematical system that can be decomposed, audited, reverse-solved, and translated into operational targets.

The deterministic workflows require Python 3.10+ and the Revenue Mechanics repository. They do not require network access. The optional OpenAI agent runner additionally requires `openai-agents>=0.14.0`.

## Non-negotiable rule

**The language model interprets; the Python engine calculates.**

Never rely on mental arithmetic for a result that the bundled solver can compute. Never invent a formula when an implemented and validated identity exists.

## Core model

Revenue Mechanics treats business outcomes as combinations of:

- **Volume** — impressions, clicks, sessions, leads, opportunities, customers, orders.
- **Probabilities** — CTR, stage conversion rates, retention/churn.
- **Value** — AOV, ARPA, deal value, contribution value.
- **State** — active customers/MRR carried from one period to another.
- **Cost** — media cost, stage cost, CAC, marginal cost.

The canonical abstraction is:

`Result = Volume × Probabilities × Value`

Use the smallest model that answers the user's decision.

## Workflow

1. **Classify the question** into one or more modes:
   - `media-funnel`: CPM → CTR → clicks → sessions → conversions → CAC/ROAS.
   - `reverse-funnel`: target outcome → required top-of-funnel volume or stage conversion.
   - `cro-target`: required improvement in one or multiple multiplicative levers.
   - `ecommerce`: sessions × CVR × AOV; optional units/order × ASP decomposition.
   - `b2b`: opportunities × win rate × average deal; reverse pipeline planning.
   - `subscription`: active base, churn, new customers, MRR/ARR, simple LTV/payback.
   - `scale`: marginal CAC/ROAS and arc elasticity between comparable states.
   - `consistency`: verify whether reported metrics close mathematically.

2. **Validate scope before calculating.** Confirm internally that inputs use compatible:
   - time windows;
   - populations/cohorts;
   - attribution rules;
   - event definitions;
   - cost scope (`media CAC` vs `fully loaded CAC`).
   If incompatible, flag the mismatch instead of combining the numbers.

3. **Choose the minimum sufficient equation.** Do not introduce MMM, Bayesian models, survival analysis, or causal inference unless the user's decision genuinely requires them.

4. **Run the deterministic solver.** Use `scripts/revenue_solver.py`. See `references/WORKFLOWS.md` for payloads.

5. **Check reliability.** Read the returned `family`, `ico`, and `tier`. `ICO` is production-governance fitness, not probability or forecast accuracy.

6. **Return an operational answer** in this order:
   - current state;
   - mathematical decomposition;
   - bottleneck/gap;
   - numerical target(s);
   - economic constraint(s);
   - assumptions and data warnings;
   - what to test next if causality is unknown.

## Hard boundaries

### Identity vs forecast

If an equation is an identity, you may state it deterministically for compatible data.

If a future result assumes unchanged surrounding variables, label it **ceteris paribus scenario**, not prediction.

### Correlation vs causality

Do not claim that a change in creative, page speed, speed-to-lead, price, offer, or any other operational factor *caused* a KPI change unless causal evidence is provided.

Use algebra to locate **where** the result changed. Use experiments/analysis to determine **why**.

### Benchmarks

Benchmarks are plausibility checks, not coefficients. Never substitute an industry benchmark for the company's own observed conversion, churn, margin, or CAC unless the user explicitly asks for a benchmark scenario.

### Marginal metrics

Do not interpret `ΔSpend / ΔCustomers` as scale marginal CAC if a structural intervention occurred between periods (new campaign structure, new offer, creative reset, landing-page redesign, pricing change, attribution change, etc.). In that case report it as an intervention comparison, not a saturation measure.

### LTV

`ARPA / churn` is **Simple Constant-Churn Revenue LTV**. It requires approximately stable churn and ARPA. Do not call it “true LTV”. For heterogeneous cohorts, recommend cohort analysis when material.

### CAC

Always name the scope: `media CAC`, `marketing CAC`, or `sales & marketing / fully loaded CAC`.

## Production tiers

- `CORE_A` (ICO ≥ 95): identities and diagnostic mechanics. Safe default when data definitions are consistent.
- `CORE_B` (90 ≤ ICO < 95): conditioned planning. Show assumptions.
- `CONDITIONAL` (80 ≤ ICO < 90): use only with explicit model limitations.
- `EXPERIMENTAL` (<80): do not use for production recommendations.

See `references/RELIABILITY.md` for the registry and policy.

## Available scripts

- `scripts/revenue_solver.py` — deterministic JSON-in/JSON-out workflow solver.
- `scripts/validate_skill.py` — validates SKILL.md structure and bundled file references.

Example:

```bash
python scripts/revenue_solver.py media-funnel --json '{"budget":12000,"cpm":40,"ctr":0.02,"session_realization_rate":0.92,"downstream_rates":[0.07,0.18],"average_value":650}'
```

Do not manually recompute the output if the script succeeds.

## References to load only when needed

- For formulas and domain conditions: `references/FORMULAS.md`.
- For workflow payloads and examples: `references/WORKFLOWS.md`.
- For confidence and production governance: `references/RELIABILITY.md`.
- For data integrity and causality boundaries: `references/GUARDRAILS.md`.

## When modifying the framework

Any change to formulas, guards, reliability scores, or skill instructions must pass both:

```bash
python scripts/validate_skill.py
python ../../../scripts/validate_production.py
```

A formula does not enter the production core because it sounds useful. It enters only after analysis → test → external confrontation → production gate.
