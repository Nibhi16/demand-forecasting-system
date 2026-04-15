from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import DECISION_COLORS, compute_dynamic_insights, decision_pill, metric_card


def inject_custom_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg-main: #0f172a;
            --bg-secondary: #111827;
            --panel: #1f2937;
            --panel-soft: #243244;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --border: #334155;
            --accent: #38bdf8;
        }
        .stApp {
            background: radial-gradient(circle at top, #0b1220 0%, var(--bg-main) 55%);
            color: var(--text-main);
        }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #101827 0%, #0e1626 100%);
            border-right: 1px solid var(--border);
        }
        section[data-testid="stSidebar"] * {
            color: var(--text-main);
        }
        .hd-header {
            padding: 0.3rem 0 0.6rem 0;
        }
        .header-wrap {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 1rem;
        }
        .hd-title {
            font-size: 1.85rem;
            font-weight: 700;
            margin: 0;
            letter-spacing: 0.2px;
        }
        .hd-subtitle {
            color: var(--text-muted);
            font-size: 0.98rem;
            margin-top: 0.2rem;
        }
        .live-status {
            margin-top: 0.2rem;
            border: 1px solid var(--border);
            border-radius: 999px;
            padding: 0.35rem 0.75rem;
            font-size: 0.82rem;
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            background: rgba(31, 41, 55, 0.7);
            white-space: nowrap;
        }
        .status-dot {
            width: 9px;
            height: 9px;
            border-radius: 50%;
            display: inline-block;
            animation: pulse 1.2s infinite;
        }
        .dot-live { background: #22c55e; box-shadow: 0 0 8px rgba(34, 197, 94, 0.7); }
        .dot-stop { background: #ef4444; box-shadow: 0 0 8px rgba(239, 68, 68, 0.7); }
        @keyframes pulse {
            0% { transform: scale(0.9); opacity: 0.9; }
            50% { transform: scale(1.15); opacity: 0.45; }
            100% { transform: scale(0.9); opacity: 0.9; }
        }
        .card {
            background: linear-gradient(165deg, var(--panel) 0%, var(--panel-soft) 100%);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1rem 1rem 1rem 1rem;
            min-height: 122px;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.28);
        }
        .card-title {
            color: var(--text-muted);
            font-size: 0.84rem;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            margin-bottom: 0.4rem;
        }
        .card-value {
            font-size: 1.6rem;
            font-weight: 700;
            line-height: 1.1;
        }
        .value-unit {
            color: var(--text-muted);
            font-size: 0.76rem;
            margin-left: 0.25rem;
            font-weight: 500;
        }
        .decision-pill {
            display: inline-block;
            margin-top: 0.45rem;
            padding: 0.3rem 0.7rem;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 650;
            color: #0b1220;
            background: var(--accent);
        }
        .section-heading {
            margin: 0.2rem 0 0.75rem 0;
            font-size: 1.08rem;
            font-weight: 650;
        }
        .helper-note {
            color: var(--text-muted);
            font-size: 0.86rem;
            margin-top: 0.35rem;
        }
        .alert-box {
            border-radius: 12px;
            padding: 0.78rem 0.9rem;
            margin: 0.45rem 0 0.7rem 0;
            border: 1px solid transparent;
            font-size: 0.92rem;
        }
        .alert-high {
            background: rgba(249, 115, 22, 0.14);
            border-color: rgba(249, 115, 22, 0.5);
            color: #fdba74;
        }
        .alert-low {
            background: rgba(56, 189, 248, 0.14);
            border-color: rgba(56, 189, 248, 0.52);
            color: #93c5fd;
        }
        .health-card {
            background: rgba(31, 41, 55, 0.6);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 0.8rem 0.9rem;
            margin-bottom: 0.8rem;
        }
        .footer-note {
            color: var(--text-muted);
            text-align: center;
            font-size: 0.84rem;
            margin-top: 1.1rem;
            margin-bottom: 0.2rem;
            line-height: 1.4;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid var(--border);
            border-radius: 10px;
            overflow: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_top_metrics(history_df: pd.DataFrame) -> None:
    latest = history_df.iloc[-1] if not history_df.empty else None
    latest_demand = f"{latest['predicted_demand']:.1f}" if latest is not None else "--"
    latest_decision = latest["allocation_decision"] if latest is not None else "No data"
    avg_demand = f"{history_df['predicted_demand'].mean():.1f}" if not history_df.empty else "--"
    peak_demand = f"{history_df['predicted_demand'].max():.1f}" if not history_df.empty else "--"

    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1:
        st.markdown(
            metric_card(
                "Current Demand Signal",
                f"{latest_demand}<span class='value-unit'>orders/slot</span>",
            ),
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            metric_card("Allocation Decision", latest_decision, decision_pill(latest_decision)),
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            metric_card("Average Demand", f"{avg_demand}<span class='value-unit'>orders/slot</span>"),
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            metric_card("Peak Demand", f"{peak_demand}<span class='value-unit'>orders/slot</span>"),
            unsafe_allow_html=True,
        )


def render_alerts(history_df: pd.DataFrame) -> None:
    if history_df.empty:
        return
    latest = float(history_df["predicted_demand"].iloc[-1])
    if latest > 300:
        st.markdown(
            (
                "<div class='alert-box alert-high'>"
                "Demand surge detected (>300). Consider immediate rider ramp-up for SLA stability."
                "</div>"
            ),
            unsafe_allow_html=True,
        )
    elif latest < 80:
        st.markdown(
            (
                "<div class='alert-box alert-low'>"
                "Demand has dropped below 80. Capacity can be rebalanced to optimize utilization."
                "</div>"
            ),
            unsafe_allow_html=True,
        )


def render_charts(history_df: pd.DataFrame) -> None:
    st.markdown("<div class='section-heading'>Demand Trend</div>", unsafe_allow_html=True)
    if history_df.empty:
        st.caption("Start simulation to view demand trend.")
    else:
        trend_df = history_df.tail(30).copy()
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=trend_df["week"],
                y=trend_df["predicted_demand"],
                mode="lines",
                line={"color": "#38bdf8", "width": 3, "shape": "spline", "smoothing": 0.85},
                name="Demand",
            )
        )
        peak_idx = trend_df["predicted_demand"].idxmax()
        peak_row = trend_df.loc[peak_idx]
        fig.add_trace(
            go.Scatter(
                x=[peak_row["week"]],
                y=[peak_row["predicted_demand"]],
                mode="markers+text",
                marker={"size": 10, "color": "#f97316", "line": {"color": "#fdba74", "width": 1}},
                text=["Peak"],
                textposition="top center",
                name="Peak",
            )
        )
        fig.update_layout(
            template="plotly_dark",
            height=300,
            margin={"l": 8, "r": 8, "t": 8, "b": 8},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(17,24,39,0.65)",
            xaxis={"title": "Week Index", "gridcolor": "rgba(148,163,184,0.15)"},
            yaxis={"title": "Predicted Demand (orders/slot)", "gridcolor": "rgba(148,163,184,0.15)"},
            legend={"orientation": "h", "y": 1.08, "x": 0.0},
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("<div class='section-heading'>Decision Distribution</div>", unsafe_allow_html=True)
    if history_df.empty:
        st.caption("Decision frequency chart will appear after first prediction.")
        return
    ordered_decisions = ["Increase riders", "Maintain", "Reduce riders"]
    decision_counts = history_df["allocation_decision"].value_counts().reindex(ordered_decisions, fill_value=0)
    colors = [DECISION_COLORS[d] for d in ordered_decisions]
    bar_fig = go.Figure(
        data=[
            go.Bar(
                x=ordered_decisions,
                y=decision_counts.values,
                marker={"color": colors},
                text=decision_counts.values,
                textposition="outside",
                textfont={"size": 13},
            )
        ]
    )
    bar_fig.update_layout(
        template="plotly_dark",
        height=280,
        margin={"l": 8, "r": 8, "t": 8, "b": 8},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.65)",
        xaxis={"title": "Allocation Category", "tickfont": {"size": 12}},
        yaxis={"title": "Count", "gridcolor": "rgba(148,163,184,0.15)"},
        showlegend=False,
    )
    st.plotly_chart(bar_fig, use_container_width=True)


def render_insights(history_df: pd.DataFrame) -> None:
    st.markdown("<div class='section-heading'>Recent Predictions</div>", unsafe_allow_html=True)
    if history_df.empty:
        st.caption("No predictions yet.")
        return

    recent_cols = ["timestamp", "week", "predicted_demand", "allocation_decision", "center_id", "meal_label"]
    recent = history_df[recent_cols].tail(5).iloc[::-1].copy()
    recent = recent.rename(
        columns={
            "timestamp": "Timestamp",
            "week": "Week",
            "predicted_demand": "Predicted Demand",
            "allocation_decision": "Decision",
            "center_id": "Center",
            "meal_label": "Meal",
        }
    )

    def highlight_rows(row: pd.Series) -> list[str]:
        demand = float(row["Predicted Demand"])
        decision = row["Decision"]
        if demand > 200 or decision == "Increase riders":
            return ["background-color: rgba(34, 197, 94, 0.16); color: #e5e7eb;"] * len(row)
        return [""] * len(row)

    styled = recent.style.format({"Predicted Demand": "{:.1f}"}).apply(highlight_rows, axis=1)
    st.dataframe(styled, width="stretch", hide_index=True)

    st.markdown("**Smart Insights**")
    for insight in compute_dynamic_insights(history_df):
        st.markdown(f"- {insight}")


def render_data_tools(history_df: pd.DataFrame) -> None:
    st.markdown("---")
    st.markdown("<div class='section-heading'>Data Export & Audit</div>", unsafe_allow_html=True)
    if history_df.empty:
        st.caption("Simulation history is empty.")
        return

    csv_bytes = history_df.to_csv(index=False).encode("utf-8")
    col_left, col_right = st.columns([1, 1])
    with col_left:
        st.download_button(
            "Download history CSV",
            data=csv_bytes,
            file_name="hybriddemand_history.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with col_right:
        show_raw = st.toggle("Show raw data")
    if show_raw:
        st.dataframe(history_df, width="stretch", hide_index=True)


def render_system_health(api_online: bool, last_updated: str, running: bool) -> None:
    st.markdown("<div class='section-heading'>System Health</div>", unsafe_allow_html=True)
    api_state = "Online" if api_online else "Offline"
    stream_state = "Active" if running else "Stopped"
    api_color = "#22c55e" if api_online else "#ef4444"
    stream_color = "#22c55e" if running else "#ef4444"
    st.markdown(
        (
            "<div class='health-card'>"
            f"<div>API Status: <span style='color:{api_color}; font-weight:650;'>{api_state}</span></div>"
            f"<div style='margin-top:0.35rem;'>Streaming Status: <span style='color:{stream_color}; font-weight:650;'>{stream_state}</span></div>"
            f"<div class='helper-note' style='margin-top:0.5rem;'>Last Updated: {last_updated}</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_header(running: bool) -> None:
    live_text = "Live Streaming" if running else "Stopped"
    dot_class = "dot-live" if running else "dot-stop"
    icon = "🟢" if running else "🔴"
    st.markdown(
        f"""
        <div class='hd-header'>
            <div class='header-wrap'>
                <div>
                    <p class='hd-title'>HybridDemand AI - Demand Intelligence Console</p>
                    <p class='hd-subtitle'>Real-time forecasting and allocation insights</p>
                </div>
                <div class='live-status'>
                    <span class='status-dot {dot_class}'></span>
                    {icon} {live_text}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown(
        """
        <div class='footer-note'>
            HybridDemand AI © 2026<br/>
            Real-time Demand Intelligence System
        </div>
        """,
        unsafe_allow_html=True,
    )
