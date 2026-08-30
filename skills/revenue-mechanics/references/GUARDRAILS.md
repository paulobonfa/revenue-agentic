# Revenue Mechanics — Data and Causality Guardrails

## Data compatibility checklist

Before deriving across metrics, check:

1. Same time window.
2. Same population/cohort.
3. Same channel/segment when material.
4. Same attribution model.
5. Same event definition.
6. Same currency and tax treatment.
7. Same CAC cost scope.
8. Same revenue concept: attributed revenue, bookings, billings, recognized revenue, or MRR.

If any mismatch is material, do not silently combine inputs.

## Consistency tiers

For observed `Y` and mathematically derived `Y_hat`:

`relative_error = |Y - Y_hat| / |Y|`

- `<1%`: A — excellent consistency.
- `1–3%`: B — likely rounding/minor measurement variation.
- `3–10%`: C — inspect definitions.
- `>=10%`: D — data integrity warning.

## Causal boundary

Algebra answers:

- where the mechanical result changed;
- how much a factor mathematically contributed;
- what target would be required ceteris paribus.

Algebra does **not** prove why a KPI changed.

Examples requiring empirical/causal evidence:

- creative → CTR;
- page speed → CVR;
- speed-to-lead → close rate;
- pricing → conversion;
- budget → CPM/CVR changes.

## Structural-intervention guard

Do not compute scale saturation from two points if any of the following changed materially:

- campaign architecture;
- channel mix;
- audience/targeting;
- offer/pricing;
- landing page/funnel;
- attribution/tracking;
- product;
- sales process.

Report the pair as an **intervention comparison**, not a marginal scale curve.

## Benchmark boundary

Benchmarks may be used to ask “is this plausible?” or “where do peers cluster?”. They must not overwrite first-party data in the deterministic equation without explicit scenario labeling.
