from __future__ import annotations

import time

import streamlit as st

from components import (
    inject_custom_style,
    render_alerts,
    render_charts,
    render_data_tools,
    render_footer,
    render_header,
    render_insights,
    render_system_health,
    render_top_metrics,
)
from data_handler import API_BASE_URL, MEAL_OPTIONS, get_api_status, init_state, run_simulation_tick
from utils import now_time_str


def sidebar_controls() -> dict:
    st.sidebar.markdown("### Controls")
    st.sidebar.markdown("---")

    center_id = st.sidebar.selectbox(
        "Center selector",
        [11, 13, 34, 67, 77],
        index=0,
        help="Choose the fulfillment center for current demand simulation.",
    )
    meal_label = st.sidebar.selectbox(
        "Meal selector",
        list(MEAL_OPTIONS.keys()),
        index=0,
        help="Pick meal category tied to incoming orders.",
    )
    st.sidebar.markdown("### Simulation Settings")
    simulation_speed = st.sidebar.slider(
        "Simulation speed (seconds/tick)",
        min_value=1.0,
        max_value=10.0,
        value=2.0,
        step=0.5,
        help="Lower value means faster refresh and denser streaming points.",
    )
    api_base_url = st.sidebar.text_input(
        "FastAPI base URL",
        value=API_BASE_URL,
        help="Backend endpoint used for real-time prediction calls.",
    )

    st.sidebar.markdown("---")
    button_label = "Stop Simulation" if st.session_state.running else "Start Simulation"
    if st.sidebar.button(button_label, use_container_width=True):
        st.session_state.running = not st.session_state.running
        if st.session_state.running:
            st.session_state.api_error = ""

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Tip: run backend with `uvicorn backend.app:app --reload` before starting."
    )

    return {
        "center_id": center_id,
        "meal_label": meal_label,
        "meal_id": MEAL_OPTIONS[meal_label],
        "simulation_speed": simulation_speed,
        "api_base_url": api_base_url.rstrip("/"),
    }


def main() -> None:
    st.set_page_config(
        page_title="HybridDemand AI - Demand Intelligence Console",
        page_icon=":bar_chart:",
        layout="wide",
    )
    inject_custom_style()
    init_state()

    config = sidebar_controls()
    if st.session_state.last_updated == "--:--:--":
        st.session_state.last_updated = now_time_str()
    api_online = get_api_status(config["api_base_url"])

    render_header(st.session_state.running)
    st.markdown("---")

    if st.session_state.api_error:
        st.error(st.session_state.api_error)

    render_top_metrics(st.session_state.history_df)
    st.markdown("---")
    render_alerts(st.session_state.history_df)

    chart_col, insights_col = st.columns([1.5, 1], gap="large")
    with chart_col:
        render_charts(st.session_state.history_df)
    with insights_col:
        render_system_health(
            api_online=api_online,
            last_updated=st.session_state.last_updated,
            running=st.session_state.running,
        )
        render_insights(st.session_state.history_df)

    render_data_tools(st.session_state.history_df)
    render_footer()

    if st.session_state.running:
        run_simulation_tick(config)
        time.sleep(float(config["simulation_speed"]))
        st.rerun()


if __name__ == "__main__":
    main()
