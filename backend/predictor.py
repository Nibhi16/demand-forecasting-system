from __future__ import annotations

import logging
from typing import Any, Sequence

import pandas as pd

from .allocation import allocate

logger = logging.getLogger("demand_forecasting_api")


def build_model_input_frame(
    input_frame: pd.DataFrame, model_feature_names: Sequence[str] | None
) -> pd.DataFrame:
    """
    Align the request input with the model's expected feature columns.

    If the model expects additional columns not present in the API request,
    they are filled with 0.0 to keep prediction running.
    """

    if model_feature_names is None:
        return input_frame

    aligned = input_frame.copy()

    for feature in model_feature_names:
        if feature not in aligned.columns:
            aligned[feature] = 0.0

    # Ensure correct column order
    return aligned[list(model_feature_names)]


def predict_with_allocation(
    model: Any,
    model_feature_names: Sequence[str] | None,
    input_rows: Sequence[dict],
) -> list[dict]:
    """
    Predict demand and compute allocation decisions using adaptive logic.
    """

    # Convert input to DataFrame
    input_frame = pd.DataFrame(list(input_rows))

    # Align with model features
    model_input = build_model_input_frame(input_frame, model_feature_names)

    # Make predictions
    preds = model.predict(model_input)

    # Convert predictions to float list
    pred_list = [float(p) for p in preds]

    # 🧠 Compute dynamic average demand
    avg_demand = sum(pred_list) / len(pred_list)

    outputs: list[dict] = []

    for predicted_demand in pred_list:
        decision = allocate(predicted_demand, avg_demand)

        outputs.append(
            {
                "predicted_demand": predicted_demand,
                "allocation_decision": decision,
            }
        )

    logger.info(
        "Predictions generated for batch_size=%s | avg_demand=%.2f",
        len(outputs),
        avg_demand,
    )

    return outputs