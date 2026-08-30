import math
import random
import unittest

import revenue_mechanics as rm


class TestExactIdentitiesProperty(unittest.TestCase):
    """Round-trip tests: each algebraic variation is exercised repeatedly."""

    def test_media_roundtrips_500_random_cases(self):
        rnd = random.Random(42)
        for _ in range(500):
            budget = rnd.uniform(100, 1_000_000)
            cpm = rnd.uniform(1, 500)
            ctr = rnd.uniform(0.001, 0.25)
            imp = rm.impressions_from_budget_cpm(budget, cpm)
            self.assertAlmostEqual(rm.cpm_from_budget_impressions(budget, imp), cpm, places=10)
            clicks = rm.clicks_from_impressions_ctr(imp, ctr)
            cpc = rm.cpc(budget, clicks)
            self.assertAlmostEqual(cpc, rm.cpc_from_cpm_ctr(cpm, ctr), places=10)
            self.assertAlmostEqual(rm.cpm_from_cpc_ctr(cpc, ctr), cpm, places=10)
            self.assertAlmostEqual(rm.ctr_from_cpm_cpc(cpm, cpc), ctr, places=10)

    def test_funnel_cost_roundtrips_500_random_cases(self):
        rnd = random.Random(43)
        for _ in range(500):
            initial = rnd.uniform(10, 1_000_000)
            rates = [rnd.uniform(0.01, 0.9) for _ in range(rnd.randint(1, 6))]
            outcome = rm.funnel_outcome(initial, rates)
            self.assertAlmostEqual(rm.required_initial_volume(outcome, rates), initial, places=8)
            cost = rnd.uniform(0.01, 10_000)
            p = rnd.uniform(0.01, 0.99)
            next_cost = rm.next_stage_cost(cost, p)
            self.assertAlmostEqual(rm.conversion_from_stage_costs(cost, next_cost), p, places=10)

    def test_revenue_roas_roundtrips_500_random_cases(self):
        rnd = random.Random(44)
        for _ in range(500):
            customers = rnd.uniform(1, 100_000)
            aov = rnd.uniform(1, 100_000)
            cac = rnd.uniform(1, 100_000)
            spend = customers * cac
            rev = rm.transactional_revenue(customers, aov)
            self.assertAlmostEqual(rm.roas(rev, spend), rm.roas_from_aov_cac(aov, cac), places=10)

    def test_recurring_closed_form_matches_iteration_250_cases(self):
        rnd = random.Random(45)
        for _ in range(250):
            active0 = rnd.uniform(0, 10_000)
            churn = rnd.uniform(0.001, 0.40)
            new = rnd.uniform(0, 1_000)
            periods = rnd.randint(1, 48)
            iterative = active0
            for _ in range(periods):
                iterative = rm.active_customers_next(iterative, churn, new)
            closed = rm.active_customers_closed_form(active0, churn, new, periods)
            self.assertAlmostEqual(iterative, closed, places=8)


class TestSyntheticCases(unittest.TestCase):
    def test_media_funnel_neutral_case(self):
        budget, cpm, ctr, q, s2l, l2c = 12_000, 40, 0.02, 0.92, 0.07, 0.18
        impressions = rm.impressions_from_budget_cpm(budget, cpm)
        clicks = rm.clicks_from_impressions_ctr(impressions, ctr)
        sessions = rm.sessions_from_clicks(clicks, q)
        leads = rm.leads_from_sessions(sessions, s2l)
        customers = rm.next_stage(leads, l2c)
        self.assertAlmostEqual(impressions, 300_000)
        self.assertAlmostEqual(clicks, 6_000)
        self.assertAlmostEqual(sessions, 5_520)
        self.assertAlmostEqual(leads, 386.4)
        self.assertAlmostEqual(customers, 69.552)
        self.assertAlmostEqual(rm.cpl(budget, leads), rm.cpl_from_cpm(cpm, ctr, q, s2l))
        self.assertAlmostEqual(
            rm.media_cac(budget, customers),
            rm.media_cac_from_funnel(cpm, ctr, q, [s2l, l2c]),
        )

    def test_cro_solver_neutral_case(self):
        g = rm.multiplicative_growth(
            {"ctr": 1, "cvr": 1, "close": 1},
            {"ctr": 1.10, "cvr": 1.08, "close": 1.05},
        )
        self.assertAlmostEqual(g, 1.2474)
        self.assertAlmostEqual(rm.equal_lever_multiplier(1.30, 3) ** 3, 1.30)
        self.assertAlmostEqual(rm.residual_growth(1.40, 1.25), 1.12)
        with self.assertRaises(rm.RevenueMechanicsError):
            rm.required_single_lever(0.80, 1.50, upper_bound=1.0)

    def test_arc_elasticity_neutral_case(self):
        b1, b2, c1, c2 = 20_000, 30_000, 100, 130
        observed_mcac = rm.marginal_cost(b1, b2, c1, c2)
        from_arc = rm.marginal_cost_from_arc_elasticity(b1, b2, c1, c2)
        self.assertAlmostEqual(observed_mcac, 333.3333333333, places=6)
        self.assertAlmostEqual(from_arc, observed_mcac, places=10)

    def test_recurring_neutral_case(self):
        active12 = rm.active_customers_closed_form(500, 0.04, 60, 12)
        self.assertAlmostEqual(active12, 887.290242670233, places=6)
        self.assertAlmostEqual(rm.mrr(active12, 200), active12 * 200)
        self.assertAlmostEqual(rm.arr_from_mrr(1000), 12_000)


class TestCommunityCases(unittest.TestCase):
    """Community-reported numbers; used for mechanical consistency, not causality."""

    def test_google_ads_reported_case(self):
        # Community fixture: spend $5,000; 39,200 impressions; 941 clicks; 26 conversions.
        spend, impressions, clicks, conv = 5_000, 39_200, 941, 26
        cpm = rm.cpm_from_budget_impressions(spend, impressions)
        click_rate = rm.ctr(clicks, impressions)
        direct_cpc = rm.cpc(spend, clicks)
        derived_cpc = rm.cpc_from_cpm_ctr(cpm, click_rate)
        self.assertAlmostEqual(direct_cpc, derived_cpc, places=10)
        direct_cpa = spend / conv
        derived_cpa = rm.next_stage_cost(direct_cpc, conv / clicks)
        self.assertAlmostEqual(direct_cpa, derived_cpa, places=10)

    def test_shopify_inconsistent_fixture_is_flagged(self):
        # Community fixture previously reported: 2,496 sessions, 0.89% CVR, 33 sales,
        # AOV $30.79, revenue $804.66. The numbers do not share a consistent definition.
        sessions, reported_cvr, orders, reported_aov, revenue = 2496, 0.0089, 33, 30.79, 804.66
        derived_orders = sessions * reported_cvr
        derived_revenue_from_reported = orders * reported_aov
        self.assertEqual(rm.consistency_tier(orders, derived_orders), "D")
        self.assertEqual(rm.consistency_tier(revenue, derived_revenue_from_reported), "D")

    def test_saas_high_churn_fixture(self):
        # Community fixture: 340 customers at $12/mo, ~29% monthly churn, CAC ~$45.
        customers, arpa, churn, cac = 340, 12, 0.29, 45
        self.assertAlmostEqual(rm.mrr(customers, arpa), 4_080)
        revenue_ltv = rm.simple_revenue_ltv(arpa, churn)
        self.assertLess(revenue_ltv, cac)  # unprofitable even before margin adjustment


class TestPublicCases(unittest.TestCase):
    def test_dental_google_ads_case(self):
        # The Dental Marketing Firm public case: spend $6,256; 26,196 impressions;
        # 1,677 clicks; 317 leads; reported CTR 6.4%, CVR 18.9%, CPL $19.74.
        spend, impressions, clicks, leads = 6256, 26196, 1677, 317
        self.assertAlmostEqual(rm.ctr(clicks, impressions), 0.0640174, places=6)
        self.assertAlmostEqual(rm.cpl(spend, leads), 19.7350, places=3)
        self.assertAlmostEqual(
            rm.next_stage_cost(rm.cpc(spend, clicks), leads / clicks),
            rm.cpl(spend, leads),
            places=10,
        )

    def test_coach2reach_google_ads_case(self):
        # Public case: ₹53,210 spend; 35,998 impressions; 1,073 clicks; 25 leads;
        # reported CPL ₹2,128.
        spend, impressions, clicks, leads = 53210, 35998, 1073, 25
        cpc = rm.cpc(spend, clicks)
        cv = leads / clicks
        self.assertAlmostEqual(rm.cpl(spend, leads), 2128.4, places=1)
        self.assertAlmostEqual(rm.next_stage_cost(cpc, cv), rm.cpl(spend, leads), places=10)

    def test_searchbloom_ecommerce_decomposition(self):
        # Public case: sessions +37.2%, CVR +39.1%, AOV +10.9%, revenue +111.7%.
        predicted = 1.372 * 1.391 * 1.109
        reported = 2.117
        self.assertLess(rm.relative_error(reported, predicted), 0.001)
        # Revenue/session should be CVR*AOV: +54.3% reported.
        predicted_rps = 1.391 * 1.109
        self.assertLess(rm.relative_error(1.543, predicted_rps), 0.001)

    def test_baremetrics_mrr_bridge_case(self):
        # Public Baremetrics case: new 4140, expansion 2619, reactivation 473,
        # contraction 158, churn 4622 -> net new MRR +2452.
        end_minus_start = rm.mrr_bridge(0, 4140, 2619, 473, 158, 4622)
        self.assertEqual(end_minus_start, 2452)

    def test_breakeven_roas_case(self):
        self.assertAlmostEqual(rm.breakeven_roas(0.12), 8.3333333333, places=8)
        self.assertAlmostEqual(rm.breakeven_roas(0.58), 1.7241379310, places=8)


class TestModelGuards(unittest.TestCase):
    def test_structural_change_blocks_marginal_interpretation(self):
        with self.assertRaises(rm.RevenueMechanicsError):
            rm.marginal_cost(100, 90, 10, 12, structural_change=True)

    def test_ltv_is_explicit_constant_churn_model(self):
        self.assertAlmostEqual(rm.simple_revenue_ltv(100, 0.05), 2000)
        self.assertAlmostEqual(rm.simple_revenue_ltv(100, 0.05, 12), 919.2798246747266, places=9)

    def test_payback_domain(self):
        # contribution LTV = 200*0.75/0.04 = 3750; CAC >= LTV never pays back.
        self.assertTrue(math.isinf(rm.churn_adjusted_payback(4000, 200, 0.75, 0.04)))
        self.assertGreater(rm.churn_adjusted_payback(900, 200, 0.75, 0.04), rm.simple_payback(900, 200, 0.75))


    def test_zero_and_full_churn_boundaries(self):
        self.assertTrue(math.isinf(rm.expected_recurring_cycles_constant_churn(0.0)))
        self.assertEqual(rm.expected_recurring_cycles_constant_churn(0.0, 12), 12.0)
        self.assertEqual(rm.expected_recurring_cycles_constant_churn(1.0), 1.0)
        self.assertAlmostEqual(rm.churn_adjusted_payback(300, 100, 0.50, 0.0), 6.0)
        self.assertEqual(rm.churn_adjusted_payback(40, 100, 0.50, 1.0), 1.0)
        self.assertTrue(math.isinf(rm.churn_adjusted_payback(60, 100, 0.50, 1.0)))

    def test_retention_inputs_fail_loudly(self):
        with self.assertRaises(rm.RevenueMechanicsError):
            rm.grr(100, 80, 30)
        with self.assertRaises(rm.RevenueMechanicsError):
            rm.nrr(100, 0, 80, 30)
        with self.assertRaises(rm.RevenueMechanicsError):
            rm.mrr_bridge(100, 0, 0, 0, 20, 90)

    def test_full_churn_stock_boundaries(self):
        self.assertEqual(rm.active_customers_next(500, 1.0, 60), 60)
        self.assertEqual(rm.active_customers_closed_form(500, 1.0, 60, 12), 60)

    def test_discrete_horizons_reject_fractional_values(self):
        with self.assertRaises(rm.RevenueMechanicsError):
            rm.active_customers_closed_form(500, 0.04, 60, 12.5)
        with self.assertRaises(rm.RevenueMechanicsError):
            rm.expected_recurring_cycles_constant_churn(0.04, 12.5)

    def test_non_numeric_and_non_finite_inputs_fail_loudly(self):
        with self.assertRaises(rm.RevenueMechanicsError):
            rm.impressions_from_budget_cpm(True, 40)
        with self.assertRaises(rm.RevenueMechanicsError):
            rm.impressions_from_budget_cpm(float("nan"), 40)
        with self.assertRaises(rm.RevenueMechanicsError):
            rm.multiplicative_growth({"cvr": 0.1}, {"cvr": 0.2}, {"cvr": float("inf")})

    def test_consistency_tiers(self):
        self.assertEqual(rm.consistency_tier(100, 100.5), "A")
        self.assertEqual(rm.consistency_tier(100, 102), "B")
        self.assertEqual(rm.consistency_tier(100, 107), "C")
        self.assertEqual(rm.consistency_tier(100, 120), "D")


if __name__ == "__main__":
    unittest.main(verbosity=2)
