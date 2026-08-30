# Revenue Mechanics — Solver Workflows

All rates are decimals: `0.05 = 5%`.

Run from the skill directory.

## media-funnel

Use for paid acquisition from CPM to downstream outcomes.

```bash
python scripts/revenue_solver.py media-funnel --json '{
  "budget": 12000,
  "cpm": 40,
  "ctr": 0.02,
  "session_realization_rate": 0.92,
  "downstream_rates": [0.07, 0.18],
  "average_value": 650
}'
```

`downstream_rates` starts after sessions. In this example it is session→lead and lead→customer.

## reverse-funnel

```bash
python scripts/revenue_solver.py reverse-funnel --json '{
  "target_outcome": 100,
  "conversion_rates": [0.08, 0.20]
}'
```

Returns required initial volume.

To solve a missing stage rate instead:

```bash
python scripts/revenue_solver.py reverse-funnel --json '{
  "target_total_conversion": 0.02,
  "other_rates": [0.5, 0.4, 0.25]
}'
```

## cro-target

One lever:

```bash
python scripts/revenue_solver.py cro-target --json '{
  "current_value": 0.08,
  "target_growth": 1.25,
  "exponent": 1,
  "upper_bound": 1
}'
```

Multiple observed/planned changes:

```bash
python scripts/revenue_solver.py cro-target --json '{
  "current": {"ctr": 0.02, "cvr": 0.08, "close": 0.15},
  "future": {"ctr": 0.022, "cvr": 0.0864, "close": 0.1575},
  "exponents": {"ctr": 1, "cvr": 1, "close": 1},
  "target_growth": 1.30
}'
```

## ecommerce

```bash
python scripts/revenue_solver.py ecommerce --json '{
  "sessions": 50000,
  "conversion_rate": 0.024,
  "units_per_order": 1.6,
  "average_selling_price": 112.5
}'
```

## b2b

```bash
python scripts/revenue_solver.py b2b --json '{
  "bookings_target": 1200000,
  "win_rate": 0.25,
  "average_deal_value": 25000
}'
```

## subscription

```bash
python scripts/revenue_solver.py subscription --json '{
  "active0": 500,
  "churn_rate": 0.04,
  "new_customers_per_period": 60,
  "periods": 12,
  "arpa": 200,
  "cac": 900,
  "contribution_margin": 0.75
}'
```

The LTV/payback fields are conditional constant-churn outputs; the response marks their lower reliability tier.

## scale

Only use when period 1 and period 2 are operationally comparable.

```bash
python scripts/revenue_solver.py scale --json '{
  "input1": 20000,
  "input2": 30000,
  "outcome1": 100,
  "outcome2": 130,
  "revenue1": 50000,
  "revenue2": 62000,
  "structural_change": false
}'
```

If `structural_change` is true, the solver refuses to label the delta as scale-marginal.

## consistency

```bash
python scripts/revenue_solver.py consistency --json '{
  "checks": [
    {"name": "revenue", "observed": 804.66, "derived": 1016.07},
    {"name": "conversion_rate", "observed": 0.0089, "derived": 0.01322}
  ]
}'
```

Use this before combining metrics from different systems.
