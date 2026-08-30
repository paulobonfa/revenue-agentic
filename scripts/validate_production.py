import os
import random
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import revenue_mechanics as rm
from reliability_registry import CORE_A, CORE_B, average_score


def stress(rounds=20_000):
    rnd = random.Random(20260829)
    max_err = 0.0
    for _ in range(rounds):
        budget = rnd.uniform(10, 10_000_000)
        cpm = rnd.uniform(0.5, 1000)
        ctr = rnd.uniform(0.0001, 0.50)
        q = rnd.uniform(0.25, 1.25)  # measurement ratio may exceed 1
        rates = [rnd.uniform(0.001, 0.95) for _ in range(rnd.randint(1, 5))]
        aov = rnd.uniform(1, 100_000)

        imp = rm.impressions_from_budget_cpm(budget, cpm)
        clicks = rm.clicks_from_impressions_ctr(imp, ctr)
        sessions = rm.sessions_from_clicks(clicks, q)
        outcomes = rm.funnel_outcome(sessions, rates)

        if outcomes > 0:
            cac_direct = budget / outcomes
            cac_derived = rm.media_cac_from_funnel(cpm, ctr, q, rates)
            err = rm.relative_error(cac_direct, cac_derived)
            max_err = max(max_err, err)

        revenue_direct = outcomes * aov
        revenue_derived = rm.paid_transactional_revenue(budget, cpm, ctr, q, rates, aov)
        max_err = max(max_err, rm.relative_error(revenue_direct, revenue_derived))

        cpc_direct = budget / clicks
        max_err = max(max_err, rm.relative_error(cpc_direct, rm.cpc_from_cpm_ctr(cpm, ctr)))

    return max_err


def main():
    skill_validation = subprocess.run(
        [sys.executable, os.path.join(ROOT, "skills/revenue-mechanics/scripts/validate_skill.py")],
        cwd=ROOT,
    )
    if skill_validation.returncode != 0:
        print("PRODUCTION GATE: FAIL (Agent Skill structure)")
        return 1

    test = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", os.path.join(ROOT, "tests"), "-v"],
        cwd=ROOT,
    )
    if test.returncode != 0:
        print("PRODUCTION GATE: FAIL (unit/external fixture tests)")
        return 1

    max_err = stress()
    core_a = average_score(CORE_A)
    core_ab = average_score({**CORE_A, **CORE_B})
    print(f"Stress-test max relative identity error: {max_err:.3e}")
    print(f"CORE_A governance ICO: {core_a:.2f}")
    print(f"Production CORE (A+B) governance ICO: {core_ab:.2f}")

    # Gate: exact identity drift < 1e-10; Core A >=95; Production Core >=94.
    passed = max_err < 1e-10 and core_a >= 95 and core_ab >= 94
    print("PRODUCTION GATE:", "PASS" if passed else "FAIL")
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
