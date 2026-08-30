from revenue_mechanics import ReliabilityComponents

# Governance scores are not statistical confidence probabilities. They rate
# production fitness: mathematical validity, data robustness, external
# validation, assumption stability and usefulness to the target user.
FAMILIES = {
    "media_identities": ReliabilityComponents(100, 98, 99, 100, 100),
    "funnel_and_cost_chain": ReliabilityComponents(100, 96, 99, 99, 100),
    "transactional_revenue_ecommerce": ReliabilityComponents(100, 94, 99, 98, 100),
    "recurring_stock_mrr": ReliabilityComponents(100, 96, 99, 97, 100),
    "mrr_bridge_retention": ReliabilityComponents(100, 95, 99, 96, 98),
    "aggregation_consistency": ReliabilityComponents(100, 97, 99, 100, 100),
    "breakeven_roas": ReliabilityComponents(100, 92, 97, 93, 98),
    "cro_reverse_planning": ReliabilityComponents(100, 89, 97, 88, 100),
    "b2b_reverse_funnel": ReliabilityComponents(100, 86, 92, 84, 97),
    "expected_value_chain": ReliabilityComponents(100, 84, 92, 82, 96),
    "marginal_scale_metrics": ReliabilityComponents(100, 82, 91, 78, 96),
    "arc_elasticity": ReliabilityComponents(100, 82, 91, 78, 90),
    "simple_constant_churn_ltv": ReliabilityComponents(100, 81, 92, 74, 92),
    "contribution_ltv_payback": ReliabilityComponents(100, 78, 92, 74, 93),
    "revenue_throughput_rate": ReliabilityComponents(100, 82, 88, 74, 88),
}

CORE_A = {k: v for k, v in FAMILIES.items() if v.score() >= 95}
CORE_B = {k: v for k, v in FAMILIES.items() if 90 <= v.score() < 95}
CONDITIONAL = {k: v for k, v in FAMILIES.items() if 80 <= v.score() < 90}
EXPERIMENTAL = {k: v for k, v in FAMILIES.items() if v.score() < 80}


def average_score(items):
    vals = [v.score() for v in items.values()]
    return sum(vals) / len(vals) if vals else float('nan')


if __name__ == "__main__":
    for name, components in sorted(FAMILIES.items(), key=lambda kv: kv[1].score(), reverse=True):
        print(f"{name:36s} {components.score():6.2f} {components.production_tier()}")
    print(f"\nCORE_A average: {average_score(CORE_A):.2f}")
    print(f"CORE_A+B average: {average_score({**CORE_A, **CORE_B}):.2f}")
