---
name: revenue-decision-science
description: Use statistical uncertainty, Poisson event models, confidence/significance thresholds, maturity checks and stop-loss logic to decide whether to scale, hold/optimize, wait, reduce or pause paid-growth campaigns. Use when the question is "do I scale this campaign?", "is this CPA trustworthy?", "how much evidence do I have?", "is zero conversion already meaningful?", or when campaign decisions need statistical support instead of point estimates alone.
license: CC-BY-SA-4.0
metadata:
  author: Paulo Bonfa
  product: Revenue Agentic
  version: "0.1.0"
  framework: Revenue Decision Science
  architecture: skill-first-deterministic-core
  compatibility: Python 3.10+
---

# Revenue Decision Science Skill

Use this skill when the business question is not only **what is the observed CPA/ROAS?**, but **how much confidence should we place in it, and what action is justified by the evidence?**

## Non-negotiable rule

**The language model interprets; the Python engine calculates.**

Do not invent confidence percentages or treat a point estimate as validated performance. Run `scripts/decision_solver.py` for every scale/hold/pause decision supported by this skill.

## Decision outputs

The solver returns one of five operational states:

- `WAIT_FOR_MATURITY` — lagged conversions are still too immature for a hard decision.
- `TEST_INCREMENT` — observed CPA is at/below target, but sample uncertainty is still high; allow only a controlled budget increase.
- `SCALE_GRADUALLY` — event volume and statistical evidence support performance better than target.
- `HOLD_AND_OPTIMIZE` — evidence is inconclusive; keep spend controlled while optimizing or accumulating data.
- `PAUSE_OR_REDUCE` — mature performance is statistically inconsistent with the target at the selected significance level.

## Core model

For campaign decisions where conversions can be treated as approximately independent rare events over spend exposure:

- Target event rate per currency unit: `lambda_0 = 1 / target_CPA`
- Expected conversions at target: `mu_0 = spend / target_CPA`
- Standard deviation of the target count under Poisson: `sigma_0 = sqrt(mu_0)`
- Observed CPA: `CPA_hat = spend / conversions`
- Relative standard error of a Poisson count when `conversions > 0`: `RSE ~= 1 / sqrt(conversions)`

The solver uses one-sided Poisson tail probabilities under the null `true CPA = target CPA`:

- underperformance: `P(N <= observed | mu_0)`
- outperformance: `P(N >= observed | mu_0)`

For zero conversions, the probability of seeing zero events at the target CPA is:

`P(N=0) = exp(-spend / target_CPA)`

At `alpha = 0.05`, zero conversions become statistically inconsistent with the target at approximately:

`spend / target_CPA >= -ln(0.05) ~= 3.0x`

This is the mathematical basis for a 3x-CPA zero-conversion stop-loss, provided the outcome data is mature and measurement is healthy.

## Workflow

1. **Check maturity first.** If approval/revenue/conversion lag is material, pass `maturity_ratio`. Do not pause a campaign because late outcomes have not arrived yet.
2. **Use the correct business event.** Prefer approved order / qualified sale / realized conversion over a shallow platform event when the business economics depend on downstream qualification.
3. **Run the solver** with spend, mature conversions, target CPA and optional policy parameters.
4. **Read uncertainty, not only CPA.** Use expected conversions at target, tail probabilities, event count and relative standard error together.
5. **Act according to the decision state.** Aggressive scale requires stronger evidence than a small test increment. Hard pause requires mature data and evidence of underperformance.
6. **Re-run after material budget or structural changes.** A large scale step, new audience, new offer, new landing page or attribution change creates a new state; historical evidence may no longer transfer cleanly.

## Default policy

Unless the user specifies another policy:

- significance level: `alpha = 0.05`;
- minimum maturity for hard decisions: `maturity_ratio >= 0.80`;
- minimum approved conversions for statistically supported scale: `10`;
- exploratory scale when CPA is good but evidence is weak: no more than `25%` in one step;
- zero-conversion stop-loss: approximately `3x target CPA` at 95% one-sided significance.

These are operational defaults, not universal laws. Change them when the business has different risk tolerance, conversion lag, budget scale or event density.

## Guardrails

- A p-value is **not** the probability that a campaign is good or bad.
- Statistical significance is **not** business significance. Always combine this skill with Revenue Mechanics when margin, LTV, payback or ROAS constraints matter.
- Do not use the Poisson model blindly when spend composition, audience, placement, offer, attribution or tracking changed materially inside the evaluated window.
- Do not treat `1/sqrt(n)` as a full confidence interval. It is a useful uncertainty heuristic for Poisson event counts.
- For small event counts, avoid normal confidence intervals; the solver intentionally withholds approximate CPA intervals until event volume is larger.
- Reach, CPM, CTR and CPC may explain delivery, but they do not override a mature downstream business outcome.

## Solver

```bash
python skills/revenue-decision-science/scripts/decision_solver.py \
  --json '{"spend":2200,"conversions":0,"target_cpa":500,"maturity_ratio":1.0}'
```

For the allu-style examples:

- `spend=800`, `conversions=2`, `target_cpa=500` → `TEST_INCREMENT`, not 5x scale.
- `spend=2200`, `conversions=0`, `target_cpa=500`, mature data → `PAUSE_OR_REDUCE`; `P(N=0 | target) ~= 1.23%`.

## Relationship with Revenue Mechanics

Use **Revenue Mechanics** to answer the economic question:

> What CPA, ROAS, conversion rate, margin, LTV or payback does the business require?

Use **Revenue Decision Science** to answer the evidence question:

> Given the sample observed so far, how confidently can we scale, hold, optimize or pause?

In production, the preferred sequence is:

`Revenue Mechanics target -> Revenue Decision Science evidence -> operational decision`
