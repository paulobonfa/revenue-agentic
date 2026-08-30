#!/usr/bin/env python3
"""Deterministic workflow interface for the Revenue Mechanics Agent Skill.

JSON in, JSON out. The LLM chooses the workflow and interprets the output;
this script owns the arithmetic and production-tier metadata.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import revenue_mechanics as rm  # noqa: E402
from reliability_registry import FAMILIES  # noqa: E402


def reliability(family: str) -> dict[str, Any]:
    c = FAMILIES[family]
    return {"family": family, "ico": round(c.score(), 2), "tier": c.production_tier()}


def finite_or_none(x: float) -> float | None:
    return x if math.isfinite(x) else None


def nonnegative_number(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise rm.RevenueMechanicsError(f"{name} must be a finite number >= 0; got {value!r}")
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise rm.RevenueMechanicsError(f"{name} must be a finite number >= 0; got {value!r}")
    return value


def media_funnel(p: dict[str, Any]) -> dict[str, Any]:
    budget = p["budget"]
    cpm = p["cpm"]
    ctr_rate = p["ctr"]
    q = p.get("session_realization_rate", 1.0)
    rates = p.get("downstream_rates", [])
    avg = p.get("average_value")

    impressions = rm.impressions_from_budget_cpm(budget, cpm)
    clicks = rm.clicks_from_impressions_ctr(impressions, ctr_rate)
    sessions = rm.sessions_from_clicks(clicks, q)
    outcome = rm.funnel_outcome(sessions, rates)
    cpc = rm.cpc(budget, clicks)
    cps = rm.cost_per_session(budget, sessions)
    cost_per_outcome = rm.media_cac(budget, outcome) if outcome > 0 else math.inf

    out: dict[str, Any] = {
        "impressions": impressions,
        "clicks": clicks,
        "sessions": sessions,
        "outcomes": outcome,
        "cpc": cpc,
        "cps": cps,
        "cost_per_final_outcome": finite_or_none(cost_per_outcome),
        "identity_crosscheck_cpc": rm.cpc_from_cpm_ctr(cpm, ctr_rate),
        "reliability": reliability("funnel_and_cost_chain"),
        "interpretation": "cost_per_final_outcome is media-only and should be called CAC only if the final outcome is a new customer.",
    }
    if avg is not None:
        revenue = rm.transactional_revenue(outcome, avg)
        out.update({
            "revenue": revenue,
            "roas": rm.roas(revenue, budget),
            "revenue_reliability": reliability("transactional_revenue_ecommerce"),
        })
    return out


def reverse_funnel(p: dict[str, Any]) -> dict[str, Any]:
    if "target_outcome" in p:
        required = rm.required_initial_volume(p["target_outcome"], p["conversion_rates"])
        return {
            "required_initial_volume": required,
            "total_conversion": rm.total_conversion(p["conversion_rates"]),
            "reliability": reliability("funnel_and_cost_chain"),
        }
    required = rm.required_stage_conversion(p["target_total_conversion"], p["other_rates"])
    return {
        "required_stage_conversion": required,
        "reliability": reliability("cro_reverse_planning"),
        "assumption": "Other stage rates are held constant (ceteris paribus).",
    }


def cro_target(p: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {"reliability": reliability("cro_reverse_planning")}
    if "current_value" in p:
        required = rm.required_single_lever(
            p["current_value"], p["target_growth"], p.get("exponent", 1.0), upper_bound=p.get("upper_bound")
        )
        out.update({
            "required_value": required,
            "relative_change": required / p["current_value"] - 1.0,
            "assumption": "All other variables remain constant (ceteris paribus).",
        })
        return out

    current = p["current"]
    future = p["future"]
    exponents = p.get("exponents")
    achieved = rm.multiplicative_growth(current, future, exponents)
    out.update({
        "achieved_growth": achieved,
        "achieved_change": achieved - 1.0,
        "log_contributions": rm.log_change_decomposition(current, future, exponents),
        "assumption": "This is a mechanical scenario/decomposition, not a causal forecast.",
    })
    if "target_growth" in p:
        out["residual_growth"] = rm.residual_growth(p["target_growth"], achieved)
        out["residual_change"] = out["residual_growth"] - 1.0
    return out


def ecommerce(p: dict[str, Any]) -> dict[str, Any]:
    aov = rm.aov_from_units_asp(p["units_per_order"], p["average_selling_price"])
    orders = rm.next_stage(p["sessions"], p["conversion_rate"])
    revenue = rm.transactional_revenue(orders, aov)
    return {
        "orders": orders,
        "aov": aov,
        "revenue": revenue,
        "revenue_per_session": rm.revenue_per_session(p["conversion_rate"], aov),
        "reliability": reliability("transactional_revenue_ecommerce"),
    }


def b2b(p: dict[str, Any]) -> dict[str, Any]:
    target = p["bookings_target"]
    win = p["win_rate"]
    adv = p["average_deal_value"]
    opps = rm.required_opportunities(target, win, adv)
    return {
        "required_opportunities": opps,
        "required_pipeline_value": rm.required_pipeline_value(target, win),
        "required_wins": target / adv,
        "pipeline_coverage": 1.0 / win,
        "reliability": reliability("b2b_reverse_funnel"),
        "assumption": "Win rate and deal value are representative of the same segment/cohort and timing is handled separately.",
    }


def subscription(p: dict[str, Any]) -> dict[str, Any]:
    active = rm.active_customers_closed_form(
        p["active0"], p["churn_rate"], p["new_customers_per_period"], p["periods"]
    )
    mrr_value = rm.mrr(active, p["arpa"])
    out: dict[str, Any] = {
        "active_end": active,
        "mrr_end": mrr_value,
        "arr_run_rate": rm.arr_from_mrr(mrr_value),
        "state_reliability": reliability("recurring_stock_mrr"),
    }
    if "cac" in p and "contribution_margin" in p:
        ltv = rm.simple_contribution_ltv(p["arpa"], p["contribution_margin"], p["churn_rate"])
        out.update({
            "simple_contribution_ltv": finite_or_none(ltv),
            "simple_payback_periods": rm.simple_payback(p["cac"], p["arpa"], p["contribution_margin"]),
            "churn_adjusted_payback_periods": finite_or_none(
                rm.churn_adjusted_payback(p["cac"], p["arpa"], p["contribution_margin"], p["churn_rate"])
            ),
            "ltv_payback_reliability": reliability("contribution_ltv_payback"),
            "ltv_assumption": "Constant churn and stable ARPA/contribution margin. Use cohort analysis when heterogeneity is material.",
        })
    return out


def scale(p: dict[str, Any]) -> dict[str, Any]:
    structural = p.get("structural_change", False)
    if not isinstance(structural, bool):
        raise rm.RevenueMechanicsError("structural_change must be a JSON boolean")
    if structural:
        input1 = nonnegative_number(p["input1"], "input1")
        input2 = nonnegative_number(p["input2"], "input2")
        outcome1 = nonnegative_number(p["outcome1"], "outcome1")
        outcome2 = nonnegative_number(p["outcome2"], "outcome2")
        return {
            "mode": "intervention-comparison",
            "warning": "Structural change detected. Do not label the delta as scale marginal CAC/ROAS or saturation.",
            "delta_input": input2 - input1,
            "delta_outcome": outcome2 - outcome1,
            "reliability": reliability("marginal_scale_metrics"),
        }
    out = {
        "mode": "comparable-scale",
        "marginal_cost": finite_or_none(rm.marginal_cost(p["input1"], p["input2"], p["outcome1"], p["outcome2"])),
        "arc_elasticity": rm.arc_elasticity(p["input1"], p["input2"], p["outcome1"], p["outcome2"]),
        "midpoint_average_cost": rm.midpoint_average_cost(p["input1"], p["input2"], p["outcome1"], p["outcome2"]),
        "marginal_cost_from_arc": finite_or_none(
            rm.marginal_cost_from_arc_elasticity(p["input1"], p["input2"], p["outcome1"], p["outcome2"])
        ),
        "marginal_reliability": reliability("marginal_scale_metrics"),
        "elasticity_reliability": reliability("arc_elasticity"),
    }
    if "revenue1" in p and "revenue2" in p:
        out["marginal_roas"] = rm.marginal_roas(p["input1"], p["input2"], p["revenue1"], p["revenue2"])
    return out


def consistency(p: dict[str, Any]) -> dict[str, Any]:
    checks = p["checks"]
    if not isinstance(checks, list) or not checks:
        raise rm.RevenueMechanicsError("checks must be a non-empty JSON array")
    results = []
    worst = "A"
    order = {"A": 0, "B": 1, "C": 2, "D": 3}
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            raise rm.RevenueMechanicsError(f"checks[{index}] must be a JSON object")
        tier = rm.consistency_tier(check["observed"], check["derived"])
        worst = tier if order[tier] > order[worst] else worst
        results.append({
            "name": check.get("name", "metric"),
            "observed": check["observed"],
            "derived": check["derived"],
            "relative_error": rm.relative_error(check["observed"], check["derived"]),
            "consistency_score": rm.consistency_score(check["observed"], check["derived"]),
            "tier": tier,
        })
    return {
        "checks": results,
        "worst_tier": worst,
        "data_integrity_warning": worst == "D",
        "reliability": reliability("aggregation_consistency"),
    }


MODES = {
    "media-funnel": media_funnel,
    "reverse-funnel": reverse_funnel,
    "cro-target": cro_target,
    "ecommerce": ecommerce,
    "b2b": b2b,
    "subscription": subscription,
    "scale": scale,
    "consistency": consistency,
}


def load_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.json is not None:
        return json.loads(args.json)
    if args.input is not None:
        return json.loads(Path(args.input).read_text(encoding="utf-8"))
    return json.load(sys.stdin)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=sorted(MODES))
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--json", help="Inline JSON payload")
    group.add_argument("--input", help="Path to JSON input file")
    args = parser.parse_args()
    try:
        payload = load_payload(args)
        if not isinstance(payload, dict):
            raise rm.RevenueMechanicsError("payload must be a JSON object")
        result = MODES[args.mode](payload)
        print(json.dumps({"ok": True, "mode": args.mode, "result": result}, indent=2, ensure_ascii=False, allow_nan=False))
        return 0
    except (KeyError, TypeError, ValueError, rm.RevenueMechanicsError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "mode": args.mode, "error": str(exc)}, indent=2, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
