# Revenue Mechanics — Reliability Policy

ICO is a production-governance score, not a probability and not forecast accuracy.

## Formula

`ICO = 0.30 M + 0.25 D + 0.20 V + 0.15 E + 0.10 U`

- `M`: mathematical validity.
- `D`: data robustness in normal operating environments.
- `V`: external validation / confrontation with synthetic, community and public cases.
- `E`: stability of assumptions.
- `U`: utility for the target ICP.

## Tiers

- `CORE_A >= 95`: identities/diagnostic mechanics.
- `CORE_B 90–94.99`: production planning with explicit assumptions.
- `CONDITIONAL 80–89.99`: only when model assumptions are visibly accepted.
- `EXPERIMENTAL < 80`: exclude from production decisions.

## Current registry

The authoritative scores are in repository-root `reliability_registry.py`.

Representative families:

- aggregation/consistency: CORE_A.
- media identities: CORE_A.
- funnel/cost chain: CORE_A.
- ecommerce/transactional revenue: CORE_A.
- recurring stock/MRR: CORE_A.
- MRR bridge/retention identities: CORE_A.
- break-even ROAS: CORE_B.
- CRO reverse planning: CORE_B/upper conditional depending on data assumptions.
- B2B reverse funnel: CONDITIONAL to CORE_B depending on segmentation/timing.
- marginal scale metrics: CONDITIONAL.
- arc elasticity: CONDITIONAL.
- constant-churn LTV/payback: CONDITIONAL.

## Interpretation rule

A low-tier family must never lower confidence in an upstream exact identity.

Example:

- `CPC = Spend/Clicks`: exact with compatible measurements.
- `Next-month CVR = current CVR`: forecast assumption.

Do not blend these into one undifferentiated “confidence”.
