from __future__ import annotations

from datetime import datetime

import pandas as pd


DECISION_COLORS: dict[str, str] = {
    "Increase riders": "#2ecc71",
    "Maintain": "#f1c40f",
    "Reduce riders": "#e74c3c",
}


def decision_pill(decision: str) -> str:
    color = DECISION_COLORS.get(decision, "#38bdf8")
    return f"<span class='decision-pill' style='background:{color};'>{decision}</span>"


def metric_card(title: str, value: str, extra: str = "") -> str:
    return (
        "<div class='card'>"
        f"<div class='card-title'>{title}</div>"
        f"<div class='card-value'>{value}</div>"
        f"{extra}"
        "</div>"
    )


def compute_dynamic_insights(history_df: pd.DataFrame) -> list[str]:
    insights: list[str] = []
    if history_df.empty:
        return insights

    latest = float(history_df["predicted_demand"].iloc[-1])
    avg_demand = float(history_df["predicted_demand"].mean())
    if avg_demand > 0:
        delta_pct = ((latest - avg_demand) / avg_demand) * 100
        if delta_pct >= 0:
            insights.append(f"Demand is above average by {delta_pct:.1f}% in the latest interval.")
        else:
            insights.append(f"Demand is below average by {abs(delta_pct):.1f}% in the latest interval.")

    if len(history_df) >= 5:
        recent5 = history_df["predicted_demand"].tail(5).reset_index(drop=True)
        if recent5.is_monotonic_increasing:
            insights.append("Demand is trending upward over the last 5 intervals.")
        elif recent5.is_monotonic_decreasing:
            insights.append("Demand is trending downward over the last 5 intervals.")
        else:
            start_val = float(recent5.iloc[0])
            end_val = float(recent5.iloc[-1])
            trend_delta = end_val - start_val
            trend_word = "upward" if trend_delta >= 0 else "downward"
            insights.append(
                f"Recent movement shows a mild {trend_word} shift ({abs(trend_delta):.1f} orders across 5 intervals)."
            )

    latest_decision = history_df["allocation_decision"].iloc[-1]
    insights.append(f"Current allocation signal is '{latest_decision}', aligned to latest demand intensity.")
    return insights


def now_time_str() -> str:
    return datetime.now().strftime("%H:%M:%S")
