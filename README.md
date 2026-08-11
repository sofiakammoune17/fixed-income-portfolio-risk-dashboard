Fixed Income Portfolio Risk Dashboard

End-to-end fixed income portfolio project combining bond valuation, interest-rate and credit risk measurement, stress testing, futures hedging, collateral monitoring, and trade reconciliation using Python and Excel.

The project was developed by Sofia Kammoune as a practical demonstration of Fixed Income, Market Risk, and Middle Office skills.

Important: all instruments, yields, spreads, valuations, and transactions are illustrative. This project does not constitute investment advice or a source of live market prices.

Project objectives

The project aims to reproduce a simplified professional workflow for monitoring a EUR-denominated bond portfolio:

value a portfolio of eight sovereign and corporate bonds;

calculate yield, modified duration, convexity, and DV01;

analyse exposure by issuer type, rating, and maturity bucket;

estimate P&L under interest-rate and credit-spread shocks;

design an indicative DV01 hedge using bond futures;

simulate collateral calls on derivative positions;

identify trade and valuation discrepancies through reconciliation controls;

present the results in an auditable Excel dashboard.

Key results

Indicator

Result

Interpretation

Portfolio market value

EUR 10,227,860

Total value of the eight illustrative bond positions

Weighted yield

2.89%

Portfolio yield weighted by market value

Modified duration

3.79

Approximate sensitivity to a 100 bp parallel yield shift

Convexity

24.03

Second-order adjustment to the duration-based estimate

DV01

EUR 3,875 per bp

Approximate loss for a one-basis-point rise in yields

Worst scenario

EUR -462,851

Parallel rate rise of 100 bp combined with rating-based spread widening

Worst-scenario impact

-4.53%

Estimated decline relative to the initial portfolio value

Indicative futures hedge

-46 contracts

Short position designed to reduce the portfolio's positive DV01

Residual DV01

EUR -35 per bp

Small remaining exposure after the simplified hedge

Hedge effectiveness

99.10%

Reduction in absolute DV01 under the stated assumptions

The portfolio is therefore primarily exposed to rising interest rates. The proposed short futures position substantially reduces linear rate sensitivity, although basis risk, curve risk, spread risk, and contract specifications remain relevant in practice.

Methodology

1. Bond valuation and risk measures

Each bond is valued by discounting its annual coupon and principal cash flows at its yield to maturity. The Python engine then calculates:

clean price per EUR 100 of nominal value;

market value;

Macaulay and modified duration;

convexity;

DV01 at instrument and portfolio levels.

2. Stress testing

Four non-base scenarios are applied to the portfolio:

Parallel rate rise: +100 bp across the curve, with additional rating-based spread widening;

Rate rally: -75 bp across the curve;

Credit widening: larger spread shocks for lower-rated bonds;

Bear steepener: progressively larger shocks for medium- and long-dated bonds.

The estimated P&L uses a duration-convexity approximation:

Estimated P&L = Market Value × (-Modified Duration × Shock + 0.5 × Convexity × Shock²)

3. Futures hedge

The indicative number of futures contracts is derived from the ratio between portfolio DV01 and an assumed futures DV01 of EUR 85 per basis point:

Number of contracts = -Portfolio DV01 / Futures DV01

The calculation produces a short position of approximately 46 contracts. This is a simplified hedge and should not be interpreted as a transaction recommendation.

4. Collateral and reconciliation controls

The project also includes simplified Middle Office controls:

margin-call calculations based on mark-to-market, thresholds, and minimum transfer amounts;

comparison of internal and counterparty notionals, valuations, and collateral balances;

comparison of internal and custodian trade data;

automatic OK or EXCEPTION status based on predefined tolerances.

Excel dashboard

The Excel workbook contains 11 auditable worksheets:

Worksheet

Purpose

Dashboard

Executive view of portfolio value, risk indicators, scenarios, and allocation

Portefeuille

Bond characteristics, valuation, weights, duration, convexity, and DV01

Cashflows

Annual coupon and principal cash flows

Courbe Scenarios

Illustrative yield curve and shock assumptions

Stress Tests

Scenario-level and instrument-level P&L estimates

Couverture

Futures hedge calculation and residual DV01

Collateral

Margin calls and counterparty reconciliation controls

Reconciliation

Internal-versus-custodian trade matching

Checks

Formula consistency and audit controls

Sources

Methodological references

Guide

Workbook navigation and assumptions

Repository contents

fixed-income-portfolio-risk-dashboard/
├── README.md
├── projet_fixed_income_sanso.py
├── Dashboard_Fixed_Income_Sanso_Sofia_Kammoune.xlsx
└── Projet_Fixed_Income_Sanso_Sofia_Kammoune.pdf

Running the Python analysis

Requirements

Python 3.10 or later;

NumPy;

pandas;

Matplotlib.

Installation and execution

git clone https://github.com/sofiakammoune17/fixed-income-portfolio-risk-dashboard.git
cd fixed-income-portfolio-risk-dashboard
python -m pip install numpy pandas matplotlib
python projet_fixed_income_sanso.py --output-dir resultats_python

The script generates:

portfolio_metrics.csv;

yield_curve.csv;

stress_test_detail.csv;

stress_test_summary.csv;

collateral_reconciliation.csv;

trade_reconciliation.csv;

summary.json;

dashboard_python.png.

Technical scope and limitations

Coupons are annual and yields are compounded annually.

Market data and transactions are illustrative and dated 11 August 2026 for project consistency.

The stress-test engine uses a duration-convexity approximation rather than full repricing.

Credit spread and risk-free rate shocks are combined in a simplified framework.

The futures hedge assumes a constant contract DV01 and does not model cheapest-to-deliver dynamics, conversion factors, liquidity, or basis risk.

Collateral calculations are simplified and do not reproduce the full legal and operational terms of an actual CSA.

References

European Central Bank – Euro area yield curves

ISDA – Collateral Management Suggested Operational Practices

Bank for International Settlements – Interest rate risk shock scenarios

Author

Sofia KammouneMBA Trading & Finance de Marché – ESLSCA Business School ParisGitHub profile
