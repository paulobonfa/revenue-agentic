import importlib.util
from pathlib import Path

SOLVER = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "revenue-decision-science"
    / "scripts"
    / "decision_solver.py"
)
spec = importlib.util.spec_from_file_location("decision_solver", SOLVER)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
analyze = module.analyze


def test_allu_creative_a_is_test_increment_not_aggressive_scale():
    r = analyze({"spend": 800, "conversions": 2, "target_cpa": 500})
    assert r["decision"] == "TEST_INCREMENT"
    assert abs(r["tests"]["p_outperformance_or_better_given_target"] - 0.4750690532) < 1e-9
    assert abs(r["metrics"]["relative_standard_error"] - 2 ** -0.5) < 1e-12


def test_allu_creative_b_is_pause_when_mature():
    r = analyze({"spend": 2200, "conversions": 0, "target_cpa": 500, "maturity_ratio": 1.0})
    assert r["decision"] == "PAUSE_OR_REDUCE"
    assert abs(r["tests"]["p_underperformance_or_worse_given_target"] - 0.0122773399) < 1e-9


def test_three_x_target_zero_conversion_matches_5pct_rule():
    r = analyze({"spend": 1500, "conversions": 0, "target_cpa": 500})
    assert r["tests"]["p_underperformance_or_worse_given_target"] < 0.05
    assert r["decision"] == "PAUSE_OR_REDUCE"


def test_immature_data_blocks_hard_pause():
    r = analyze({"spend": 2200, "conversions": 0, "target_cpa": 500, "maturity_ratio": 0.5})
    assert r["decision"] == "WAIT_FOR_MATURITY"


def test_strong_positive_sample_scales_gradually():
    r = analyze({"spend": 5000, "conversions": 18, "target_cpa": 500})
    assert r["decision"] == "SCALE_GRADUALLY"
    assert r["tests"]["p_outperformance_or_better_given_target"] < 0.05
