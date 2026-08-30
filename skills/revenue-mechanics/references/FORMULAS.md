# Revenue Mechanics — Formula Reference

This is the compact mathematical reference used by the skill. The full derivations live in `docs/MATHEMATICAL_SPEC.md` at repository root.

## 1. Universal funnel

For a stage volume `N_i` and conditional passage rate `p_i`:

\[
N_{i+1}=N_i p_i
\]

For a chain:

\[
N_n=N_0\prod_i p_i
\]

Reverse planning:

\[
N_0^*=\frac{N_n^*}{\prod_i p_i}
\]

A stage target, holding the others constant:

\[
p_k^*=\frac{p_{0,n}^*}{\prod_{i\neq k}p_i}
\]

## 2. Cost chain

If `c_i = Cost/N_i`:

\[
c_{i+1}=\frac{c_i}{p_i}
\]

and:

\[
p_i=\frac{c_i}{c_{i+1}}
\]

Examples:

\[
CPL=\frac{CPS}{CVR_{session\to lead}}
\]

\[
CAC_{media}=\frac{CPL}{CVR_{lead\to customer}}
\]

## 3. Paid media

\[
Impressions=\frac{1000\,Budget}{CPM}
\]

\[
Clicks=Impressions\times CTR
\]

\[
CPC=\frac{CPM}{1000\,CTR}
\]

With session-realization rate `q = Sessions/AdClicks`:

\[
CPS=\frac{CPC}{q}
\]

For downstream rates `p_i`:

\[
CAC_{media}=\frac{CPM}{1000\,CTR\,q\prod_i p_i}
\]

## 4. Transactional revenue / ecommerce

\[
Revenue=Outcomes\times AverageValue
\]

\[
Revenue=Traffic\times\left(\prod_i p_i\right)\times AverageValue
\]

Ecommerce:

\[
Revenue=Sessions\times CVR\times AOV
\]

\[
AOV=UnitsPerOrder\times ASP
\]

\[
RPS=CVR\times AOV
\]

## 5. ROAS and economics

\[
ROAS=\frac{Revenue}{Spend}
\]

For same attributed customers and one transaction:

\[
ROAS=\frac{AOV}{CAC_{media}}
\]

If `m` is pre-media contribution margin:

\[
ROAS_{break-even}=\frac1m
\]

For desired post-media margin `\mu`:

\[
ROAS_{min}=\frac1{m-\mu}
\]

## 6. CRO multiplicative mechanics

For a monomial model:

\[
Y=K\prod_i x_i^{a_i}
\]

Scenario change:

\[
\frac{Y_1}{Y_0}=\prod_i\left(\frac{x_{i1}}{x_{i0}}\right)^{a_i}
\]

Single-lever target:

\[
x_j^*=x_{j0}g^{1/a_j}
\]

Equal improvement across `n` unit-exponent levers:

\[
m=g^{1/n}
\]

Residual multiplier:

\[
g_{residual}=\frac{g_{target}}{g_{achieved}}
\]

Exact log decomposition:

\[
\ln(Y_1/Y_0)=\sum_i a_i\ln(x_{i1}/x_{i0})
\]

## 7. Scale / marginal mechanics

For comparable operating regimes only:

\[
mCost=\frac{\Delta Cost}{\Delta Outcome}
\]

\[
mROAS=\frac{\Delta Revenue}{\Delta Spend}
\]

For discrete intervals use arc elasticity:

\[
\varepsilon_{arc}=\frac{\Delta Y/\bar Y}{\Delta X/\bar X}
\]

Do not treat these as causal across structural interventions.

## 8. Recurring state

\[
Active_t=Active_{t-1}(1-h_t)+New_t
\]

Constant churn/new customer closed form:

\[
Active_t=Active_0(1-h)^t+New\frac{1-(1-h)^t}{h}
\]

\[
MRR_t=Active_t\times ARPA_t
\]

\[
ARR_t=12MRR_t
\]

MRR bridge:

\[
MRR_{end}=MRR_{start}+New+Expansion+Reactivation-Contraction-Churn
\]

## 9. Retention / simple LTV

Constant churn model:

\[
RC_H=\frac{1-(1-h)^H}{h}
\]

Infinite horizon (`h>0`):

\[
RC=\frac1h
\]

\[
SimpleRevenueLTV=ARPA\times RC
\]

\[
SimpleContributionLTV=ARPA\times ContributionMargin\times RC
\]

Simple payback:

\[
Payback\approx\frac{CAC}{ARPA\times ContributionMargin}
\]

These are CONDITIONAL when churn/ARPA are not stable.

## 10. Expected value chain

For final economic value `V_n`:

\[
V_i=V_n\prod_{j=i}^{n-1}p_j
\]

Break-even stage cost must satisfy:

\[
CostPerEvent_i\le V_i
\]

This allows customer economics to propagate backward into CAC/CPL/CPC/CPM limits.
