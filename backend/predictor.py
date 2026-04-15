from __future__ import annotations

import logging
from typing import Any, Sequence

import pandas as pd

from .allocation import allocate

logger = logging.getLogger("demand_forecasting_api")


def build_model_input_frame(
    input_frame: pd.DataFrame,
    model_feature_names: Sequence[str] | None,
) -> pd.DataFrame:
    """
    Align input data with model's expected feature columns.
    """

    if model_feature_names is None:
        return input_frame

    aligned = input_frame.copy()

    # Add missing features
    for feature in model_feature_names:
        if feature not in aligned.columns:
            aligned[feature] = 0.0

    # Ensure correct order
    return aligned[list(model_feature_names)]


def predict_with_allocation(
    model: Any,
    model_feature_names: Sequence[str] | None,
    input_rows: Sequence[dict],
) -> list[dict]:
    """
    Predict demand using trained model and apply allocation logic.
    """

    # Convert input to DataFrame
    input_frame = pd.DataFrame(list(input_rows))

    # Align features
    model_input = build_model_input_frame(input_frame, model_feature_names)

    # Predict
    preds = model.predict(model_input)

    # Convert to float list
    pred_list = [float(p) for p in preds]

    # Compute dynamic average
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
        "📊 Predictions generated | batch_size=%s | avg_demand=%.2f",
        len(outputs),
        avg_demand,
    )

    return outputs