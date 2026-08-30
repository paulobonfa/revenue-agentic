"""Revenue Mechanics / Equações Bonfarianas 2.0.

Dependency-free mathematical core for decomposing acquisition, funnel,
revenue, retention and unit-economics metrics.

Design principles
-----------------
1. Exact identities are kept separate from empirical/forecast assumptions.
2. All rates are decimals (e.g. 0.05 = 5%).
3. Functions validate domains and fail loudly on impossible inputs.
4. Marginal metrics must not be interpreted across structural interventions.
5. LTV/payback helpers are explicitly named as simplified constant-churn models.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable, Mapping, Sequence

EPS = 1e-12


class RevenueMechanicsError(ValueError):
    """Raised when an input violates the mathematical domain or model scope."""


def _finite_number(x: float, name: str) -> float:
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise RevenueMechanicsError(f"{name} must be a finite number; got {x!r}")
    value = float(x)
    if not math.isfinite(value):
        raise RevenueMechanicsError(f"{name} must be a finite number; got {x!r}")
    return value


def _positive(x: float, name: str, *, allow_zero: bool = False) -> float:
    value = _finite_number(x, name)
    ok = value >= 0 if allow_zero else value > 0
    if not ok:
        op = ">= 0" if allow_zero else "> 0"
        raise RevenueMechanicsError(f"{name} must be finite and {op}; got {x!r}")
    return value


def _rate(x: float, name: str, *, allow_zero: bool = True, allow_one: bool = True) -> float:
    value = _finite_number(x, name)
    lo = 0.0 if allow_zero else EPS
    hi = 1.0 if allow_one else 1.0 - EPS
    if value < lo or value > hi:
        raise RevenueMechanicsError(f"{name} must be in [{lo}, {hi}]; got {x!r}")
    return value


def _integer(x: int, name: str, *, minimum: int = 0) -> int:
    value = _finite_number(x, name)
    if not value.is_integer() or value < minimum:
        raise RevenueMechanicsError(f"{name} must be an integer >= {minimum}; got {x!r}")
    return int(value)


def product(values: Iterable[float]) -> float:
    out = 1.0
    for v in values:
        out *= v
    return out


# ---------------------------------------------------------------------------
# Flow mechanics
# ---------------------------------------------------------------------------

def next_stage(volume: float, conversion_rate: float) -> float:
    _positive(volume, "volume", allow_zero=True)
    _rate(conversion_rate, "conversion_rate")
    return volume * conversion_rate


def funnel_outcome(initial_volume: float, conversion_rates: Sequence[float]) -> float:
    _positive(initial_volume, "initial_volume", allow_zero=True)
    for i, r in enumerate(conversion_rates):
        _rate(r, f"conversion_rates[{i}]")
    return initial_volume * product(conversion_rates)


def total_conversion(conversion_rates: Sequence[float]) -> float:
    for i, r in enumerate(conversion_rates):
        _rate(r, f"conversion_rates[{i}]")
    return product(conversion_rates)


def required_initial_volume(target_outcome: float, conversion_rates: Sequence[float]) -> float:
    _positive(target_outcome, "target_outcome", allow_zero=True)
    p = total_conversion(conversion_rates)
    if p <= 0:
        if target_outcome == 0:
            return 0.0
        raise RevenueMechanicsError("required volume is infinite because total conversion is zero")
    return target_outcome / p


def required_stage_conversion(target_total_conversion: float, other_rates: Sequence[float]) -> float:
    _rate(target_total_conversion, "target_total_conversion")
    p = total_conversion(other_rates)
    if p <= 0:
        raise RevenueMechanicsError("cannot isolate a stage when another required rate is zero")
    required = target_total_conversion / p
    if required > 1 + EPS:
        raise RevenueMechanicsError(
            f"required stage conversion is impossible (>100%): {required:.6f}"
        )
    return min(required, 1.0)


def dropoff(volume: float, conversion_rate: float) -> float:
    _positive(volume, "volume", allow_zero=True)
    _rate(conversion_rate, "conversion_rate")
    return volume * (1.0 - conversion_rate)


# ---------------------------------------------------------------------------
# Paid-media mechanics
# ---------------------------------------------------------------------------

def impressions_from_budget_cpm(budget: float, cpm: float) -> float:
    _positive(budget, "budget", allow_zero=True)
    _positive(cpm, "cpm")
    return 1000.0 * budget / cpm


def cpm_from_budget_impressions(budget: float, impressions: float) -> float:
    _positive(budget, "budget", allow_zero=True)
    _positive(impressions, "impressions")
    return 1000.0 * budget / impressions


def ctr(clicks: float, impressions: float) -> float:
    _positive(clicks, "clicks", allow_zero=True)
    _positive(impressions, "impressions")
    value = clicks / impressions
    if value > 1 + EPS:
        raise RevenueMechanicsError("clicks cannot exceed impressions for this CTR definition")
    return min(value, 1.0)


def clicks_from_impressions_ctr(impressions: float, ctr_rate: float) -> float:
    _positive(impressions, "impressions", allow_zero=True)
    _rate(ctr_rate, "ctr_rate")
    return impressions * ctr_rate


def cpc(spend: float, clicks: float) -> float:
    _positive(spend, "spend", allow_zero=True)
    _positive(clicks, "clicks")
    return spend / clicks


def cpc_from_cpm_ctr(cpm: float, ctr_rate: float) -> float:
    _positive(cpm, "cpm")
    _rate(ctr_rate, "ctr_rate", allow_zero=False)
    return cpm / (1000.0 * ctr_rate)


def cpm_from_cpc_ctr(cpc_value: float, ctr_rate: float) -> float:
    _positive(cpc_value, "cpc_value", allow_zero=True)
    _rate(ctr_rate, "ctr_rate")
    return 1000.0 * cpc_value * ctr_rate


def ctr_from_cpm_cpc(cpm: float, cpc_value: float) -> float:
    _positive(cpm, "cpm", allow_zero=True)
    _positive(cpc_value, "cpc_value")
    value = cpm / (1000.0 * cpc_value)
    if value > 1 + EPS:
        raise RevenueMechanicsError(f"derived CTR is impossible (>100%): {value:.6f}")
    return min(value, 1.0)


def session_realization_rate(sessions: float, ad_clicks: float) -> float:
    _positive(sessions, "sessions", allow_zero=True)
    _positive(ad_clicks, "ad_clicks")
    value = sessions / ad_clicks
    # >1 can happen due measurement/session definitions, so do not reject it.
    return value


def sessions_from_clicks(clicks: float, realization_rate: float) -> float:
    _positive(clicks, "clicks", allow_zero=True)
    _positive(realization_rate, "realization_rate", allow_zero=True)
    return clicks * realization_rate


def cost_per_session(spend: float, sessions: float) -> float:
    _positive(spend, "spend", allow_zero=True)
    _positive(sessions, "sessions")
    return spend / sessions


def cps_from_cpc(cpc_value: float, realization_rate: float) -> float:
    _positive(cpc_value, "cpc_value", allow_zero=True)
    _positive(realization_rate, "realization_rate")
    return cpc_value / realization_rate


def leads_from_sessions(sessions: float, session_to_lead: float) -> float:
    return next_stage(sessions, session_to_lead)


def cpl(spend: float, leads: float) -> float:
    _positive(spend, "spend", allow_zero=True)
    _positive(leads, "leads")
    return spend / leads


def cpl_from_cps(cps: float, session_to_lead: float) -> float:
    _positive(cps, "cps", allow_zero=True)
    _rate(session_to_lead, "session_to_lead", allow_zero=False)
    return cps / session_to_lead


def cpl_from_cpc(cpc_value: float, realization_rate: float, session_to_lead: float) -> float:
    _positive(cpc_value, "cpc_value", allow_zero=True)
    _positive(realization_rate, "realization_rate")
    _rate(session_to_lead, "session_to_lead", allow_zero=False)
    return cpc_value / (realization_rate * session_to_lead)


def cpl_from_cpm(cpm: float, ctr_rate: float, realization_rate: float, session_to_lead: float) -> float:
    return cpl_from_cpc(cpc_from_cpm_ctr(cpm, ctr_rate), realization_rate, session_to_lead)


def paid_funnel_outcome(
    budget: float,
    cpm: float,
    ctr_rate: float,
    realization_rate: float,
    downstream_rates: Sequence[float],
) -> float:
    impressions = impressions_from_budget_cpm(budget, cpm)
    clicks = clicks_from_impressions_ctr(impressions, ctr_rate)
    sessions = sessions_from_clicks(clicks, realization_rate)
    return funnel_outcome(sessions, downstream_rates)


def media_cac(spend: float, new_customers: float) -> float:
    _positive(spend, "spend", allow_zero=True)
    _positive(new_customers, "new_customers")
    return spend / new_customers


def media_cac_from_funnel(
    cpm: float,
    ctr_rate: float,
    realization_rate: float,
    downstream_rates: Sequence[float],
) -> float:
    _positive(cpm, "cpm")
    _rate(ctr_rate, "ctr_rate", allow_zero=False)
    _positive(realization_rate, "realization_rate")
    p = total_conversion(downstream_rates)
    if p <= 0:
        return math.inf
    return cpm / (1000.0 * ctr_rate * realization_rate * p)


def fully_loaded_cac(
    media_spend: float,
    marketing_acquisition_cost: float,
    sales_acquisition_cost: float,
    new_customers: float,
) -> float:
    for name, x in {
        "media_spend": media_spend,
        "marketing_acquisition_cost": marketing_acquisition_cost,
        "sales_acquisition_cost": sales_acquisition_cost,
    }.items():
        _positive(x, name, allow_zero=True)
    _positive(new_customers, "new_customers")
    return (media_spend + marketing_acquisition_cost + sales_acquisition_cost) / new_customers


# ---------------------------------------------------------------------------
# General cost/value mechanics
# ---------------------------------------------------------------------------

def next_stage_cost(current_cost: float, conversion_rate: float) -> float:
    _positive(current_cost, "current_cost", allow_zero=True)
    _rate(conversion_rate, "conversion_rate", allow_zero=False)
    return current_cost / conversion_rate


def conversion_from_stage_costs(current_cost: float, next_cost: float) -> float:
    _positive(current_cost, "current_cost", allow_zero=True)
    _positive(next_cost, "next_cost")
    value = current_cost / next_cost
    if value > 1 + EPS:
        raise RevenueMechanicsError(
            "derived conversion >100%; costs likely use incompatible populations/scopes"
        )
    return min(value, 1.0)


def previous_stage_expected_value(next_stage_value: float, conversion_rate: float) -> float:
    _positive(next_stage_value, "next_stage_value", allow_zero=True)
    _rate(conversion_rate, "conversion_rate")
    return next_stage_value * conversion_rate


def expected_value_at_stage(final_value: float, downstream_rates: Sequence[float]) -> float:
    _positive(final_value, "final_value", allow_zero=True)
    return final_value * total_conversion(downstream_rates)


def max_stage_cost_from_final_value(final_value: float, downstream_rates: Sequence[float]) -> float:
    return expected_value_at_stage(final_value, downstream_rates)


# ---------------------------------------------------------------------------
# Transactional revenue / ecommerce
# ---------------------------------------------------------------------------

def transactional_revenue(outcomes: float, average_value: float) -> float:
    _positive(outcomes, "outcomes", allow_zero=True)
    _positive(average_value, "average_value", allow_zero=True)
    return outcomes * average_value


def revenue_from_traffic(traffic: float, conversion_rates: Sequence[float], average_value: float) -> float:
    outcomes = funnel_outcome(traffic, conversion_rates)
    return transactional_revenue(outcomes, average_value)


def paid_transactional_revenue(
    budget: float,
    cpm: float,
    ctr_rate: float,
    realization_rate: float,
    downstream_rates: Sequence[float],
    average_value: float,
) -> float:
    outcomes = paid_funnel_outcome(budget, cpm, ctr_rate, realization_rate, downstream_rates)
    return transactional_revenue(outcomes, average_value)


def roas(revenue: float, spend: float) -> float:
    _positive(revenue, "revenue", allow_zero=True)
    _positive(spend, "spend")
    return revenue / spend


def roas_from_aov_cac(aov: float, cac_value: float) -> float:
    _positive(aov, "aov", allow_zero=True)
    _positive(cac_value, "cac_value")
    return aov / cac_value


def revenue_per_session(conversion_rate: float, aov: float) -> float:
    _rate(conversion_rate, "conversion_rate")
    _positive(aov, "aov", allow_zero=True)
    return conversion_rate * aov


def aov_from_units_asp(units_per_order: float, average_selling_price: float) -> float:
    _positive(units_per_order, "units_per_order", allow_zero=True)
    _positive(average_selling_price, "average_selling_price", allow_zero=True)
    return units_per_order * average_selling_price


def ecommerce_revenue(
    sessions: float,
    conversion_rate: float,
    units_per_order: float,
    average_selling_price: float,
) -> float:
    aov = aov_from_units_asp(units_per_order, average_selling_price)
    return revenue_from_traffic(sessions, [conversion_rate], aov)


# ---------------------------------------------------------------------------
# CRO mechanics / reverse planning
# ---------------------------------------------------------------------------

def multiplicative_growth(current: Mapping[str, float], future: Mapping[str, float], exponents: Mapping[str, float] | None = None) -> float:
    if set(current) != set(future):
        raise RevenueMechanicsError("current and future must contain the same variables")
    exponents = exponents or {k: 1.0 for k in current}
    if set(exponents) != set(current):
        raise RevenueMechanicsError("exponents must contain the same variables")
    g = 1.0
    for k in current:
        c = _positive(current[k], f"current[{k}]")
        f = _positive(future[k], f"future[{k}]")
        exponent = _finite_number(exponents[k], f"exponents[{k}]")
        try:
            g *= (f / c) ** exponent
        except OverflowError as exc:
            raise RevenueMechanicsError("multiplicative growth overflowed") from exc
    if not math.isfinite(g):
        raise RevenueMechanicsError("multiplicative growth must be finite")
    return g


def required_single_lever(current_value: float, target_growth: float, exponent: float = 1.0, *, upper_bound: float | None = None) -> float:
    _positive(current_value, "current_value")
    _positive(target_growth, "target_growth")
    exponent = _finite_number(exponent, "exponent")
    if abs(exponent) <= EPS:
        raise RevenueMechanicsError("cannot solve a lever with exponent 0")
    try:
        required = current_value * target_growth ** (1.0 / exponent)
    except OverflowError as exc:
        raise RevenueMechanicsError("required lever overflowed") from exc
    if not math.isfinite(required):
        raise RevenueMechanicsError("required lever must be finite")
    if upper_bound is not None:
        upper_bound = _positive(upper_bound, "upper_bound", allow_zero=True)
    if upper_bound is not None and required > upper_bound + EPS:
        raise RevenueMechanicsError(
            f"required lever {required:.6f} exceeds upper bound {upper_bound:.6f}"
        )
    return required


def equal_lever_multiplier(target_growth: float, number_of_levers: int) -> float:
    _positive(target_growth, "target_growth")
    number_of_levers = _integer(number_of_levers, "number_of_levers", minimum=1)
    return target_growth ** (1.0 / number_of_levers)


def residual_growth(target_growth: float, achieved_growth: float) -> float:
    _positive(target_growth, "target_growth")
    _positive(achieved_growth, "achieved_growth")
    return target_growth / achieved_growth


def max_growth_from_probability(current_probability: float) -> float:
    _rate(current_probability, "current_probability", allow_zero=False)
    return 1.0 / current_probability


def log_change_decomposition(current: Mapping[str, float], future: Mapping[str, float], exponents: Mapping[str, float] | None = None) -> dict[str, float]:
    if set(current) != set(future):
        raise RevenueMechanicsError("current and future must contain the same variables")
    exponents = exponents or {k: 1.0 for k in current}
    if set(exponents) != set(current):
        raise RevenueMechanicsError("exponents must contain the same variables")
    out: dict[str, float] = {}
    for k in current:
        c = _positive(current[k], f"current[{k}]")
        f = _positive(future[k], f"future[{k}]")
        exponent = _finite_number(exponents[k], f"exponents[{k}]")
        out[k] = exponent * math.log(f / c)
    return out


# ---------------------------------------------------------------------------
# Marginal & scale mechanics
# ---------------------------------------------------------------------------

def marginal_cost(input1: float, input2: float, outcome1: float, outcome2: float, *, structural_change: bool = False) -> float:
    input1 = _positive(input1, "input1", allow_zero=True)
    input2 = _positive(input2, "input2", allow_zero=True)
    outcome1 = _positive(outcome1, "outcome1", allow_zero=True)
    outcome2 = _positive(outcome2, "outcome2", allow_zero=True)
    if structural_change:
        raise RevenueMechanicsError(
            "marginal_cost cannot be interpreted as scale marginal cost across a structural intervention"
        )
    delta_input = input2 - input1
    delta_outcome = outcome2 - outcome1
    if abs(delta_outcome) <= EPS:
        return math.copysign(math.inf, delta_input if delta_input else 1.0)
    return delta_input / delta_outcome


def marginal_roas(spend1: float, spend2: float, revenue1: float, revenue2: float, *, structural_change: bool = False) -> float:
    spend1 = _positive(spend1, "spend1", allow_zero=True)
    spend2 = _positive(spend2, "spend2", allow_zero=True)
    revenue1 = _positive(revenue1, "revenue1", allow_zero=True)
    revenue2 = _positive(revenue2, "revenue2", allow_zero=True)
    if structural_change:
        raise RevenueMechanicsError(
            "marginal_roas cannot be interpreted as scale marginal ROAS across a structural intervention"
        )
    delta_spend = spend2 - spend1
    if abs(delta_spend) <= EPS:
        raise RevenueMechanicsError("spend delta cannot be zero")
    return (revenue2 - revenue1) / delta_spend


def arc_elasticity(input1: float, input2: float, outcome1: float, outcome2: float) -> float:
    for name, x in {"input1": input1, "input2": input2, "outcome1": outcome1, "outcome2": outcome2}.items():
        _positive(x, name)
    avg_input = (input1 + input2) / 2.0
    avg_outcome = (outcome1 + outcome2) / 2.0
    pct_input = (input2 - input1) / avg_input
    pct_outcome = (outcome2 - outcome1) / avg_outcome
    if abs(pct_input) <= EPS:
        raise RevenueMechanicsError("input change cannot be zero")
    return pct_outcome / pct_input


def midpoint_average_cost(input1: float, input2: float, outcome1: float, outcome2: float) -> float:
    avg_input = (_positive(input1, "input1") + _positive(input2, "input2")) / 2.0
    avg_outcome = (_positive(outcome1, "outcome1") + _positive(outcome2, "outcome2")) / 2.0
    return avg_input / avg_outcome


def marginal_cost_from_arc_elasticity(input1: float, input2: float, outcome1: float, outcome2: float) -> float:
    e = arc_elasticity(input1, input2, outcome1, outcome2)
    if abs(e) <= EPS:
        return math.inf
    return midpoint_average_cost(input1, input2, outcome1, outcome2) / e


# ---------------------------------------------------------------------------
# B2B / sales
# ---------------------------------------------------------------------------

def bookings_from_opportunities(opportunities: float, win_rate: float, average_deal_value: float) -> float:
    _positive(opportunities, "opportunities", allow_zero=True)
    _rate(win_rate, "win_rate")
    _positive(average_deal_value, "average_deal_value", allow_zero=True)
    return opportunities * win_rate * average_deal_value


def required_opportunities(bookings_target: float, win_rate: float, average_deal_value: float) -> float:
    _positive(bookings_target, "bookings_target", allow_zero=True)
    _rate(win_rate, "win_rate", allow_zero=False)
    _positive(average_deal_value, "average_deal_value")
    return bookings_target / (win_rate * average_deal_value)


def required_pipeline_value(bookings_target: float, win_rate: float) -> float:
    _positive(bookings_target, "bookings_target", allow_zero=True)
    _rate(win_rate, "win_rate", allow_zero=False)
    return bookings_target / win_rate


def revenue_throughput_rate(opportunities: float, average_deal_value: float, win_rate: float, sales_cycle_days: float) -> float:
    _positive(sales_cycle_days, "sales_cycle_days")
    return bookings_from_opportunities(opportunities, win_rate, average_deal_value) / sales_cycle_days


# ---------------------------------------------------------------------------
# Recurring revenue / retention
# ---------------------------------------------------------------------------

def active_customers_next(active_previous: float, churn_rate: float, new_customers: float) -> float:
    _positive(active_previous, "active_previous", allow_zero=True)
    _rate(churn_rate, "churn_rate")
    _positive(new_customers, "new_customers", allow_zero=True)
    return active_previous * (1.0 - churn_rate) + new_customers


def active_customers_closed_form(active0: float, churn_rate: float, new_customers_per_period: float, periods: int) -> float:
    _positive(active0, "active0", allow_zero=True)
    _rate(churn_rate, "churn_rate")
    _positive(new_customers_per_period, "new_customers_per_period", allow_zero=True)
    periods = _integer(periods, "periods")
    if periods == 0:
        return active0
    if churn_rate <= EPS:
        return active0 + new_customers_per_period * periods
    r = 1.0 - churn_rate
    return active0 * r ** periods + new_customers_per_period * (1.0 - r ** periods) / churn_rate


def mrr(active_customers: float, arpa: float) -> float:
    _positive(active_customers, "active_customers", allow_zero=True)
    _positive(arpa, "arpa", allow_zero=True)
    return active_customers * arpa


def arr_from_mrr(mrr_value: float) -> float:
    _positive(mrr_value, "mrr_value", allow_zero=True)
    return 12.0 * mrr_value


def mrr_bridge(
    mrr_start: float,
    new_mrr: float,
    expansion_mrr: float,
    reactivation_mrr: float,
    contraction_mrr: float,
    churned_mrr: float,
) -> float:
    for name, x in locals().items():
        _positive(x, name, allow_zero=True)
    ending_mrr = mrr_start + new_mrr + expansion_mrr + reactivation_mrr - contraction_mrr - churned_mrr
    if ending_mrr < -EPS:
        raise RevenueMechanicsError("MRR bridge inputs are inconsistent: ending MRR would be negative")
    return max(0.0, ending_mrr)


def grr(mrr_start: float, churned_mrr: float, contraction_mrr: float) -> float:
    _positive(mrr_start, "mrr_start")
    _positive(churned_mrr, "churned_mrr", allow_zero=True)
    _positive(contraction_mrr, "contraction_mrr", allow_zero=True)
    retained = mrr_start - churned_mrr - contraction_mrr
    if retained < -EPS:
        raise RevenueMechanicsError("GRR inputs are inconsistent: churn + contraction exceed starting MRR")
    return max(0.0, retained / mrr_start)


def nrr(mrr_start: float, expansion_mrr: float, churned_mrr: float, contraction_mrr: float) -> float:
    _positive(mrr_start, "mrr_start")
    _positive(expansion_mrr, "expansion_mrr", allow_zero=True)
    _positive(churned_mrr, "churned_mrr", allow_zero=True)
    _positive(contraction_mrr, "contraction_mrr", allow_zero=True)
    ending_cohort_mrr = mrr_start + expansion_mrr - churned_mrr - contraction_mrr
    if ending_cohort_mrr < -EPS:
        raise RevenueMechanicsError("NRR inputs are inconsistent: ending cohort MRR would be negative")
    return max(0.0, ending_cohort_mrr / mrr_start)


def expected_recurring_cycles_constant_churn(churn_rate: float, horizon: int | None = None) -> float:
    _rate(churn_rate, "churn_rate")
    if horizon is not None:
        horizon = _integer(horizon, "horizon", minimum=1)
    if churn_rate <= EPS:
        return math.inf if horizon is None else float(horizon)
    if horizon is None:
        return 1.0 / churn_rate
    return (1.0 - (1.0 - churn_rate) ** horizon) / churn_rate


def simple_revenue_ltv(arpa: float, churn_rate: float, horizon: int | None = None) -> float:
    _positive(arpa, "arpa", allow_zero=True)
    return arpa * expected_recurring_cycles_constant_churn(churn_rate, horizon)


def simple_contribution_ltv(arpa: float, contribution_margin: float, churn_rate: float, horizon: int | None = None) -> float:
    _positive(arpa, "arpa", allow_zero=True)
    _rate(contribution_margin, "contribution_margin")
    return arpa * contribution_margin * expected_recurring_cycles_constant_churn(churn_rate, horizon)


def simple_payback(cac_value: float, arpa: float, contribution_margin: float) -> float:
    _positive(cac_value, "cac_value", allow_zero=True)
    _positive(arpa, "arpa")
    _rate(contribution_margin, "contribution_margin", allow_zero=False)
    return cac_value / (arpa * contribution_margin)


def churn_adjusted_payback(cac_value: float, arpa: float, contribution_margin: float, churn_rate: float) -> float:
    _positive(cac_value, "cac_value", allow_zero=True)
    _positive(arpa, "arpa")
    _rate(contribution_margin, "contribution_margin", allow_zero=False)
    _rate(churn_rate, "churn_rate")
    if cac_value == 0:
        return 0.0
    period_contribution = arpa * contribution_margin
    if churn_rate <= EPS:
        return cac_value / period_contribution
    if churn_rate >= 1.0 - EPS:
        return 1.0 if cac_value <= period_contribution + EPS else math.inf
    max_value = period_contribution / churn_rate
    if cac_value >= max_value - EPS:
        return math.inf
    inside = 1.0 - cac_value * churn_rate / period_contribution
    return math.log(inside) / math.log(1.0 - churn_rate)


# ---------------------------------------------------------------------------
# Unit economics
# ---------------------------------------------------------------------------

def breakeven_roas(contribution_margin: float) -> float:
    _rate(contribution_margin, "contribution_margin", allow_zero=False)
    return 1.0 / contribution_margin


def minimum_roas_for_post_media_margin(contribution_margin: float, target_post_media_margin: float) -> float:
    _rate(contribution_margin, "contribution_margin", allow_zero=False)
    _rate(target_post_media_margin, "target_post_media_margin")
    spread = contribution_margin - target_post_media_margin
    if spread <= 0:
        raise RevenueMechanicsError("target post-media margin must be below pre-media contribution margin")
    return 1.0 / spread


def contribution_roas(roas_value: float, contribution_margin: float) -> float:
    _positive(roas_value, "roas_value", allow_zero=True)
    _rate(contribution_margin, "contribution_margin")
    return roas_value * contribution_margin


def max_cac_from_contribution_ltv(contribution_ltv: float, acquisition_share: float = 1.0) -> float:
    _positive(contribution_ltv, "contribution_ltv", allow_zero=True)
    _rate(acquisition_share, "acquisition_share")
    return contribution_ltv * acquisition_share


# ---------------------------------------------------------------------------
# Aggregation & consistency
# ---------------------------------------------------------------------------

def aggregate_ratio(numerators: Sequence[float], denominators: Sequence[float]) -> float:
    if len(numerators) != len(denominators) or not numerators:
        raise RevenueMechanicsError("numerators and denominators must have the same non-zero length")
    num = sum(_positive(x, f"numerator[{i}]", allow_zero=True) for i, x in enumerate(numerators))
    den = sum(_positive(x, f"denominator[{i}]", allow_zero=True) for i, x in enumerate(denominators))
    if den <= 0:
        raise RevenueMechanicsError("aggregate denominator must be > 0")
    return num / den


def relative_error(observed: float, derived: float) -> float:
    if not math.isfinite(observed) or not math.isfinite(derived):
        raise RevenueMechanicsError("observed and derived must be finite")
    if abs(observed) <= EPS:
        return 0.0 if abs(derived) <= EPS else math.inf
    return abs(observed - derived) / abs(observed)


def consistency_score(observed: float, derived: float) -> float:
    err = relative_error(observed, derived)
    if math.isinf(err):
        return 0.0
    return max(0.0, 100.0 * (1.0 - err))


def consistency_tier(observed: float, derived: float) -> str:
    err = relative_error(observed, derived)
    if err < 0.01:
        return "A"
    if err < 0.03:
        return "B"
    if err < 0.10:
        return "C"
    return "D"


# ---------------------------------------------------------------------------
# Reliability rubric (governance, not a statistical probability)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ReliabilityComponents:
    mathematical_validity: float
    data_robustness: float
    external_validation: float
    assumption_stability: float
    icp_utility: float

    def score(self) -> float:
        vals = [
            _finite_number(self.mathematical_validity, "mathematical_validity"),
            _finite_number(self.data_robustness, "data_robustness"),
            _finite_number(self.external_validation, "external_validation"),
            _finite_number(self.assumption_stability, "assumption_stability"),
            _finite_number(self.icp_utility, "icp_utility"),
        ]
        if any(v < 0 or v > 100 for v in vals):
            raise RevenueMechanicsError("reliability components must be in [0,100]")
        return (
            0.30 * self.mathematical_validity
            + 0.25 * self.data_robustness
            + 0.20 * self.external_validation
            + 0.15 * self.assumption_stability
            + 0.10 * self.icp_utility
        )

    def production_tier(self) -> str:
        s = self.score()
        if s >= 95:
            return "CORE_A"
        if s >= 90:
            return "CORE_B"
        if s >= 80:
            return "CONDITIONAL"
        return "EXPERIMENTAL"
