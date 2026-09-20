# Statistical rules — Revenue Decision Science

## 1. Spend as exposure

For a target CPA `C*`, the target event rate per unit of spend is:

`lambda_0 = 1 / C*`

At spend `S`, the expected event count is:

`mu_0 = S / C*`

Under a Poisson approximation:

`Var(N) = mu_0` and `SD(N) = sqrt(mu_0)`.

## 2. One-sided decision tests

For observed conversions `k`:

- Evidence of underperformance uses `P(N <= k | mu_0)`.
- Evidence of outperformance uses `P(N >= k | mu_0)`.

The default significance threshold is 5%.

## 3. Zero-conversion stop rule

When `k = 0`:

`P(N=0 | mu_0) = exp(-mu_0)`.

Solving `exp(-mu_0) <= alpha` gives:

`mu_0 >= -ln(alpha)`.

At 5%, `-ln(0.05) = 2.9957`, hence the practical ~3x target-CPA rule.

## 4. Sampling uncertainty

For a Poisson count `k > 0`, a useful first-order uncertainty measure is:

`RSE ~= 1 / sqrt(k)`.

Examples:

- 2 events: ~70.7% relative standard error;
- 10 events: ~31.6%;
- 25 events: 20%;
- 100 events: 10%.

This is why a CPA based on 2 sales should not be treated like a CPA based on 100 sales.

## 5. What the model does not prove

This model does not prove causality and does not guarantee stationarity. A creative can change audience composition as spend grows. Budget expansion can move the campaign into more expensive inventory. Conversion lag can make the latest cohort look artificially weak. Tracking changes can invalidate the series.

Always check measurement health, maturity and structural comparability before applying a hard decision.
