from __future__ import annotations

import pandas as pd
import requests
import streamlit as st

from utils import now_time_str


API_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_HISTORY_COLUMNS = [
    "timestamp",
    "week",
    "center_id",
    "meal_label",
    "meal_id",
    "lag_1",
    "lag_2",
    "predicted_demand",
    "allocation_decision",
]

MEAL_OPTIONS = {
    "Lunch (Premium)": 1062,
    "Dinner (Standard)": 1248,
    "Breakfast (Express)": 1885,
    "Evening Snacks": 1993,
}


def init_state() -> None:
    if "running" not in st.session_state:
        st.session_state.running = False
    if "history_df" not in st.session_state:
        st.session_state.history_df = pd.DataFrame(columns=DEFAULT_HISTORY_COLUMNS)
    if "api_error" not in st.session_state:
        st.session_state.api_error = ""
    if "last_updated" not in st.session_state:
        st.session_state.last_updated = "--:--:--"


def build_payload(config: dict, history_df: pd.DataFrame) -> dict:
    next_week = 1 if history_df.empty else int(history_df["week"].iloc[-1]) + 1
    lag_1 = float(history_df["predicted_demand"].iloc[-1]) if len(history_df) >= 1 else 140.0
    lag_2 = float(history_df["predicted_demand"].iloc[-2]) if len(history_df) >= 2 else lag_1
    return {
        "week": next_week,
        "center_id": config["center_id"],
        "meal_id": config["meal_id"],
        "lag_1": round(lag_1, 3),
        "lag_2": round(lag_2, 3),
    }


def fetch_prediction(base_url: str, payload: dict) -> tuple[dict | None, str]:
    endpoint = f"{base_url}/predict"
    try:
        response = requests.post(endpoint, json=payload, timeout=5)
        response.raise_for_status()
        return response.json(), ""
    except requests.exceptions.RequestException as exc:
        return None, f"Unable to fetch prediction from `{endpoint}`. Details: {exc}"


def append_history(history_df: pd.DataFrame, config: dict, payload: dict, result: dict) -> pd.DataFrame:
    row = {
        "timestamp": now_time_str(),
        "week": payload["week"],
        "center_id": config["center_id"],
        "meal_label": config["meal_label"],
        "meal_id": config["meal_id"],
        "lag_1": payload["lag_1"],
        "lag_2": payload["lag_2"],
        "predicted_demand": float(result["predicted_demand"]),
        "allocation_decision": result["allocation_decision"],
    }
    return pd.concat([history_df, pd.DataFrame([row])], ignore_index=True)


def run_simulation_tick(config: dict) -> None:
    history_df = st.session_state.history_df
    payload = build_payload(config, history_df)
    with st.spinner("Fetching latest demand signal..."):
        result, error = fetch_prediction(config["api_base_url"], payload)
    if error:
        st.session_state.api_error = error
        st.session_state.running = False
        return

    st.session_state.api_error = ""
    st.session_state.history_df = append_history(history_df, config, payload, result)
    st.session_state.last_updated = now_time_str()


def get_api_status(base_url: str) -> bool:
    try:
        response = requests.get(f"{base_url}/", timeout=2.5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False
