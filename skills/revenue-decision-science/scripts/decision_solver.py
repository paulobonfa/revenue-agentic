from __future__ import annotations

import argparse
import json
import math
from statistics import NormalDist
from typing import Any, Dict


def _poisson_cdf(k: int, mu: float) -> float:
    if k < 0:
        return 0.0
    if mu < 0:
        raise ValueError("mu must be non-negative")
    if mu == 0:
        return 1.0
    if mu > 700:
        z = (k + 0.5 - mu) / math.sqrt(mu)
        return NormalDist().cdf(z)
    p = math.exp(-mu)
    total = p
    for i in range(1, k + 1):
        p *= mu / i
        total += p
    return min(max(total, 0.0), 1.0)


def _poisson_sf(k: int, mu: float) -> float:
    return min(max(1.0 - _poisson_cdf(k, mu), 0.0), 1.0)


def _normal_rate_interval(k: int, exposure: float, z: float = 1.96):
    if k < 10:
        return None
    rate = k / exposure
    se = math.sqrt(k) / exposure
    lo = max(0.0, rate - z * se)
    hi = rate + z * se
    return {"rate_lower": lo, "rate_upper": hi, "method": "normal-approx-95"}


def analyze(payload: Dict[str, Any]) -> Dict[str, Any]:
    spend = float(payload["spend"])
    conversions = int(payload["conversions"])
    target_cpa = float(payload["target_cpa"])
    maturity_ratio = float(payload.get("maturity_ratio", 1.0))
    alpha = float(payload.get("alpha", 0.05))
    min_scale_events = int(payload.get("min_scale_events", 10))
    max_test_increment_pct = float(payload.get("max_test_increment_pct", 25.0))

    if spend <= 0 or target_cpa <= 0:
        raise ValueError("spend and target_cpa must be positive")
    if conversions < 0:
        raise ValueError("conversions must be non-negative")
    if not 0 <= maturity_ratio <= 1:
        raise ValueError("maturity_ratio must be between 0 and 1")
    if not 0 < alpha < 0.5:
        raise ValueError("alpha must be between 0 and 0.5")

    expected_at_target = spend / target_cpa
    sigma_at_target = math.sqrt(expected_at_target)
    observed_cpa = None if conversions == 0 else spend / conversions
    target_multiple = spend / target_cpa

    p_underperformance = _poisson_cdf(conversions, expected_at_target)
    p_outperformance = _poisson_sf(conversions - 1, expected_at_target)

    relative_se = None if conversions == 0 else 1.0 / math.sqrt(conversions)
    rate_interval = _normal_rate_interval(conversions, spend)
    cpa_interval = None
    if rate_interval and rate_interval["rate_lower"] > 0:
        cpa_interval = {
            "cpa_lower": 1.0 / rate_interval["rate_upper"],
            "cpa_upper": 1.0 / rate_interval["rate_lower"],
            "method": rate_interval["method"],
        }

    z_approx = None
    if expected_at_target >= 10:
        z_approx = (conversions - expected_at_target) / sigma_at_target

    warnings = []
    if maturity_ratio < 0.8:
        warnings.append("Outcome data is immature; wait for lagged conversions before a hard cut/scale decision.")
    if conversions < 10:
        warnings.append("Small event count: observed CPA has high sampling uncertainty.")
    warnings.append("Poisson decision logic assumes comparable traffic, stable measurement and approximately independent rare events per unit of spend.")

    if maturity_ratio < 0.8:
        decision = "WAIT_FOR_MATURITY"
        rationale = "Lagged outcomes are not mature enough for a hard decision."
    elif p_underperformance <= alpha and (observed_cpa is None or observed_cpa > target_cpa):
        decision = "PAUSE_OR_REDUCE"
        rationale = "Under the target-CPA null, performance this weak or weaker is statistically unlikely."
    elif conversions >= min_scale_events and observed_cpa is not None and observed_cpa < target_cpa and p_outperformance <= alpha:
        decision = "SCALE_GRADUALLY"
        rationale = "There is enough event volume and statistically significant evidence of performance better than target."
    elif observed_cpa is not None and observed_cpa <= target_cpa:
        decision = "TEST_INCREMENT"
        rationale = f"Observed CPA is at/below target, but evidence is not strong enough for aggressive scale; cap the next increment around {max_test_increment_pct:g}%."
    else:
        decision = "HOLD_AND_OPTIMIZE"
        rationale = "Performance is not yet statistically conclusive enough to justify either aggressive scale or a hard stop."

    zero_conv_stop_multiple = -math.log(alpha)

    return {
        "ok": True,
        "inputs": {
            "spend": spend,
            "conversions": conversions,
            "target_cpa": target_cpa,
            "maturity_ratio": maturity_ratio,
            "alpha": alpha,
        },
        "metrics": {
            "observed_cpa": observed_cpa,
            "spend_as_target_cpa_multiple": target_multiple,
            "expected_conversions_if_at_target": expected_at_target,
            "target_count_standard_deviation": sigma_at_target,
            "relative_standard_error": relative_se,
            "z_approx": z_approx,
            "approx_cpa_interval_95": cpa_interval,
        },
        "tests": {
            "p_underperformance_or_worse_given_target": p_underperformance,
            "p_outperformance_or_better_given_target": p_outperformance,
            "significance_level": alpha,
            "zero_conversion_stop_multiple_at_alpha": zero_conv_stop_multiple,
        },
        "decision": decision,
        "rationale": rationale,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Revenue Decision Science solver")
    parser.add_argument("--json", required=True, help="JSON payload")
    args = parser.parse_args()
    try:
        payload = json.loads(args.json)
        print(json.dumps(analyze(payload), ensure_ascii=False, indent=2))
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        raise SystemExit(2)


if __name__ == "__main__":
    main()
