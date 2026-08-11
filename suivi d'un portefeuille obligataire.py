from __future__ import annotations

import argparse
import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "sanso_mpl_cache"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


AS_OF_DATE = "2026-08-11"


@dataclass(frozen=True)
class Bond:
    bond_id: str
    instrument: str
    sector: str
    rating: str
    maturity_years: int
    coupon_rate: float
    yield_to_maturity: float
    nominal_eur: float
    spread_bps: float


PORTFOLIO = [
    Bond("B01", "Souverain EUR 2027", "Souverain", "AAA", 1, 0.0000, 0.0210, 2_000_000, 5),
    Bond("B02", "Souverain EUR 2029", "Souverain", "AAA", 3, 0.0200, 0.0225, 1_800_000, 8),
    Bond("B03", "Souverain EUR 2032", "Souverain", "AA", 6, 0.0275, 0.0250, 1_500_000, 18),
    Bond("B04", "Corporate Utilities 2028", "Corporate", "A", 2, 0.0320, 0.0300, 1_200_000, 75),
    Bond("B05", "Banque Senior 2030", "Financier", "A", 4, 0.0375, 0.0340, 1_000_000, 95),
    Bond("B06", "Corporate Industrie 2031", "Corporate", "BBB", 5, 0.0410, 0.0390, 900_000, 145),
    Bond("B07", "Souverain EUR 2034", "Souverain", "BBB", 8, 0.0400, 0.0360, 1_100_000, 120),
    Bond("B08", "Green Bond Corporate 2036", "Corporate", "BBB", 10, 0.0430, 0.0420, 700_000, 175),
]


YIELD_CURVE = pd.DataFrame(
    {
        "Maturite_annees": [1, 2, 3, 5, 7, 10, 15, 30],
        "Taux_spot": [0.0200, 0.0210, 0.0218, 0.0235, 0.0250, 0.0265, 0.0282, 0.0305],
    }
)


SCENARIOS: dict[str, dict[str, Any]] = {
    "Base": {
        "rate_short": 0,
        "rate_mid": 0,
        "rate_long": 0,
        "spread": {"AAA": 0, "AA": 0, "A": 0, "BBB": 0},
    },
    "Hausse parallele +100 pb": {
        "rate_short": 100,
        "rate_mid": 100,
        "rate_long": 100,
        "spread": {"AAA": 10, "AA": 15, "A": 25, "BBB": 35},
    },
    "Rally taux -75 pb": {
        "rate_short": -75,
        "rate_mid": -75,
        "rate_long": -75,
        "spread": {"AAA": -5, "AA": -8, "A": -10, "BBB": -10},
    },
    "Ecartement credit": {
        "rate_short": 0,
        "rate_mid": 0,
        "rate_long": 0,
        "spread": {"AAA": 20, "AA": 35, "A": 75, "BBB": 150},
    },
    "Bear steepener": {
        "rate_short": 25,
        "rate_mid": 75,
        "rate_long": 125,
        "spread": {"AAA": 10, "AA": 15, "A": 25, "BBB": 50},
    },
}


COLLATERAL_TRADES = pd.DataFrame(
    [
        ["D01", "IRS EUR 5Y", 5_000_000, 5_000_000, 180_000, 177_000, 150_000, 150_000, 25_000, 10_000],
        ["D02", "IRS EUR 10Y", 8_000_000, 7_980_000, -260_000, -272_000, -220_000, -220_000, 25_000, 10_000],
        ["D03", "CDS iTraxx 5Y", 3_000_000, 3_000_000, 95_000, 92_500, 50_000, 45_000, 20_000, 5_000],
        ["D04", "Swaption EUR", 2_500_000, 2_500_000, 60_000, 58_000, 0, 0, 50_000, 10_000],
        ["D05", "Equity Swap", 1_500_000, 1_500_000, -140_000, -137_000, -110_000, -105_000, 25_000, 10_000],
        ["D06", "IRS EUR 2Y", 2_000_000, 2_000_000, 35_000, 34_000, 0, 0, 25_000, 5_000],
    ],
    columns=[
        "Trade_ID",
        "Instrument",
        "Notionnel_interne",
        "Notionnel_contrepartie",
        "MtM_interne",
        "MtM_contrepartie",
        "Collateral_interne",
        "Collateral_contrepartie",
        "Seuil",
        "MTA",
    ],
)


RECONCILIATION_TRADES = pd.DataFrame(
    [
        ["T01", "Achat", "B01", "2026-08-07", 750_000, 750_000, 97.94, 97.94],
        ["T02", "Achat", "B04", "2026-08-07", 500_000, 500_000, 100.39, 100.39],
        ["T03", "Vente", "B02", "2026-08-08", 300_000, 300_000, 99.28, 99.30],
        ["T04", "Achat", "B06", "2026-08-08", 250_000, 240_000, 100.91, 100.91],
        ["T05", "Achat", "B03", "2026-08-09", 400_000, 400_000, 101.39, 101.15],
        ["T06", "Vente", "B07", "2026-08-09", 350_000, 350_000, 102.75, 102.75],
        ["T07", "Achat", "B05", "2026-08-10", 200_000, 200_000, 101.29, 101.29],
        ["T08", "Achat", "B08", "2026-08-10", 150_000, 150_000, 100.81, 100.79],
    ],
    columns=[
        "Trade_ID",
        "Sens",
        "Bond_ID",
        "Date_trade",
        "Nominal_interne",
        "Nominal_depositaire",
        "Prix_interne",
        "Prix_depositaire",
    ],
)


def bond_analytics(bond: Bond) -> dict[str, float | str]:
    """Calcule prix, durations, convexite et DV01 avec coupons annuels."""
    times = np.arange(1, bond.maturity_years + 1, dtype=float)
    cash_flows = np.full_like(times, bond.coupon_rate * 100.0)
    cash_flows[-1] += 100.0
    discount_factors = (1.0 + bond.yield_to_maturity) ** times
    present_values = cash_flows / discount_factors
    price = float(present_values.sum())
    macaulay = float((times * present_values).sum() / price)
    modified = macaulay / (1.0 + bond.yield_to_maturity)
    convexity = float(
        (times * (times + 1.0) * present_values).sum()
        / (price * (1.0 + bond.yield_to_maturity) ** 2)
    )
    market_value = bond.nominal_eur * price / 100.0
    dv01 = modified * market_value * 0.0001
    return {
        **asdict(bond),
        "price_per_100": price,
        "market_value_eur": market_value,
        "macaulay_duration": macaulay,
        "modified_duration": modified,
        "convexity": convexity,
        "dv01_eur_per_bp": dv01,
    }


def build_portfolio() -> pd.DataFrame:
    portfolio = pd.DataFrame([bond_analytics(bond) for bond in PORTFOLIO])
    portfolio["weight"] = portfolio["market_value_eur"] / portfolio["market_value_eur"].sum()
    portfolio["maturity_bucket"] = pd.cut(
        portfolio["maturity_years"],
        bins=[0, 3, 7, np.inf],
        labels=["Court <= 3 ans", "Moyen 4-7 ans", "Long > 7 ans"],
        right=True,
    )
    return portfolio


def rate_shock_for_maturity(scenario: dict[str, Any], maturity_years: int) -> float:
    if maturity_years <= 3:
        return float(scenario["rate_short"])
    if maturity_years <= 7:
        return float(scenario["rate_mid"])
    return float(scenario["rate_long"])


def build_stress_tests(portfolio: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    details: list[dict[str, Any]] = []
    for scenario_name, scenario in SCENARIOS.items():
        for row in portfolio.itertuples(index=False):
            rate_bps = rate_shock_for_maturity(scenario, int(row.maturity_years))
            spread_bps = float(scenario["spread"].get(row.rating, scenario["spread"]["BBB"]))
            shock = (rate_bps + spread_bps) / 10_000.0
            pnl = row.market_value_eur * (
                -row.modified_duration * shock + 0.5 * row.convexity * shock**2
            )
            details.append(
                {
                    "Scenario": scenario_name,
                    "Bond_ID": row.bond_id,
                    "Rating": row.rating,
                    "Maturite_annees": row.maturity_years,
                    "Choc_taux_pb": rate_bps,
                    "Choc_spread_pb": spread_bps,
                    "Choc_total_pb": rate_bps + spread_bps,
                    "PnL_EUR": pnl,
                    "Valeur_stressee_EUR": row.market_value_eur + pnl,
                }
            )
    detail_df = pd.DataFrame(details)
    summary = (
        detail_df.groupby("Scenario", sort=False)
        .agg(PnL_EUR=("PnL_EUR", "sum"), Valeur_stressee_EUR=("Valeur_stressee_EUR", "sum"))
        .reset_index()
    )
    base_mv = float(portfolio["market_value_eur"].sum())
    summary["Impact_pct"] = summary["PnL_EUR"] / base_mv
    return detail_df, summary


def build_collateral() -> pd.DataFrame:
    trades = COLLATERAL_TRADES.copy()
    sign = np.sign(trades["MtM_interne"])
    trades["Collateral_requis"] = sign * np.maximum(np.abs(trades["MtM_interne"]) - trades["Seuil"], 0)
    raw_call = trades["Collateral_requis"] - trades["Collateral_interne"]
    trades["Appel_de_marge"] = np.where(np.abs(raw_call) >= trades["MTA"], raw_call, 0.0)
    trades["Ecart_notionnel"] = trades["Notionnel_interne"] - trades["Notionnel_contrepartie"]
    trades["Ecart_MtM"] = trades["MtM_interne"] - trades["MtM_contrepartie"]
    trades["Ecart_collateral"] = trades["Collateral_interne"] - trades["Collateral_contrepartie"]
    trades["Statut"] = np.where(
        (np.abs(trades["Ecart_notionnel"]) > 1_000)
        | (np.abs(trades["Ecart_MtM"]) > 5_000)
        | (np.abs(trades["Ecart_collateral"]) > 5_000),
        "EXCEPTION",
        "OK",
    )
    return trades


def build_reconciliation() -> pd.DataFrame:
    trades = RECONCILIATION_TRADES.copy()
    trades["Ecart_nominal"] = trades["Nominal_interne"] - trades["Nominal_depositaire"]
    trades["Ecart_prix"] = trades["Prix_interne"] - trades["Prix_depositaire"]
    trades["Statut"] = np.where(
        (np.abs(trades["Ecart_nominal"]) > 1_000) | (np.abs(trades["Ecart_prix"]) > 0.05),
        "EXCEPTION",
        "OK",
    )
    return trades


def portfolio_summary(portfolio: pd.DataFrame, stress_summary: pd.DataFrame) -> dict[str, Any]:
    total_mv = float(portfolio["market_value_eur"].sum())
    weighted_yield = float((portfolio["yield_to_maturity"] * portfolio["weight"]).sum())
    weighted_duration = float((portfolio["modified_duration"] * portfolio["weight"]).sum())
    weighted_convexity = float((portfolio["convexity"] * portfolio["weight"]).sum())
    total_dv01 = float(portfolio["dv01_eur_per_bp"].sum())
    future_dv01 = 85.0
    hedge_contracts = int(round(-total_dv01 / future_dv01))
    residual_dv01 = total_dv01 + hedge_contracts * future_dv01
    worst = stress_summary.loc[stress_summary["PnL_EUR"].idxmin()]
    return {
        "as_of_date": AS_OF_DATE,
        "total_market_value_eur": total_mv,
        "weighted_yield": weighted_yield,
        "weighted_modified_duration": weighted_duration,
        "weighted_convexity": weighted_convexity,
        "total_dv01_eur_per_bp": total_dv01,
        "future_dv01_eur_per_bp": future_dv01,
        "hedge_contracts": hedge_contracts,
        "residual_dv01_eur_per_bp": residual_dv01,
        "hedge_effectiveness": 1.0 - abs(residual_dv01) / abs(total_dv01),
        "worst_scenario": str(worst["Scenario"]),
        "worst_scenario_pnl_eur": float(worst["PnL_EUR"]),
        "worst_scenario_impact_pct": float(worst["Impact_pct"]),
    }


def save_dashboard_chart(portfolio: pd.DataFrame, stress_summary: pd.DataFrame, output_path: Path) -> None:
    colors = {
        "navy": "#17365D",
        "teal": "#2F809B",
        "mint": "#56B59A",
        "red": "#C94C4C",
        "gold": "#D6A94E",
        "grey": "#DDE5EC",
    }
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 4.6), gridspec_kw={"width_ratios": [1.25, 1]})
    fig.patch.set_facecolor("white")

    stress_plot = stress_summary[stress_summary["Scenario"] != "Base"].copy()
    bar_colors = [colors["red"] if value < 0 else colors["mint"] for value in stress_plot["PnL_EUR"]]
    axes[0].barh(stress_plot["Scenario"], stress_plot["PnL_EUR"] / 1_000, color=bar_colors)
    axes[0].axvline(0, color="#6B7280", linewidth=0.8)
    axes[0].set_title("PnL par scenario (kEUR)", loc="left", color=colors["navy"], weight="bold")
    axes[0].set_xlabel("kEUR")
    axes[0].grid(axis="x", color=colors["grey"], linewidth=0.6)
    axes[0].set_axisbelow(True)

    rating = portfolio.groupby("rating", sort=False)["market_value_eur"].sum()
    axes[1].pie(
        rating.values,
        labels=rating.index,
        autopct="%1.0f%%",
        startangle=90,
        colors=[colors["teal"], colors["mint"], colors["gold"], "#8AA2B8"],
        wedgeprops={"width": 0.42, "edgecolor": "white"},
    )
    axes[1].set_title("Allocation par rating", color=colors["navy"], weight="bold")
    plt.tight_layout()
    fig.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def run(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    portfolio = build_portfolio()
    stress_detail, stress_summary = build_stress_tests(portfolio)
    collateral = build_collateral()
    reconciliation = build_reconciliation()
    summary = portfolio_summary(portfolio, stress_summary)

    portfolio.to_csv(output_dir / "portfolio_metrics.csv", index=False, encoding="utf-8-sig")
    YIELD_CURVE.to_csv(output_dir / "yield_curve.csv", index=False, encoding="utf-8-sig")
    stress_detail.to_csv(output_dir / "stress_test_detail.csv", index=False, encoding="utf-8-sig")
    stress_summary.to_csv(output_dir / "stress_test_summary.csv", index=False, encoding="utf-8-sig")
    collateral.to_csv(output_dir / "collateral_reconciliation.csv", index=False, encoding="utf-8-sig")
    reconciliation.to_csv(output_dir / "trade_reconciliation.csv", index=False, encoding="utf-8-sig")
    save_dashboard_chart(portfolio, stress_summary, output_dir / "dashboard_python.png")

    with (output_dir / "summary.json").open("w", encoding="utf-8") as stream:
        json.dump(summary, stream, ensure_ascii=False, indent=2)

    print("Projet calcule avec succes")
    print(f"Valeur de marche : {summary['total_market_value_eur']:,.0f} EUR")
    print(f"Duration modifiee : {summary['weighted_modified_duration']:.2f}")
    print(f"DV01 : {summary['total_dv01_eur_per_bp']:,.0f} EUR/pb")
    print(
        f"Pire scenario : {summary['worst_scenario']} "
        f"({summary['worst_scenario_pnl_eur']:,.0f} EUR)"
    )
    print(f"Couverture indicative : {summary['hedge_contracts']} contrats futures")
    print(f"Fichiers generes dans : {output_dir.resolve()}")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyse obligataire et middle-office illustrative")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("resultats_python"),
        help="Dossier de sortie des CSV, JSON et du graphique",
    )
    return parser.parse_args()


if __name__ == "__main__":
    cli_args = parse_args()
    run(output_dir=cli_args.output_dir)