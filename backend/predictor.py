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

    If the model expects additional columns not present in the API request, they
    are filled with 0.0 to keep prediction running.
    """

    # `feature_names_in_` can be a NumPy array; don't rely on truthiness.
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
    Predict demand and compute allocation decisions for a batch of input rows.
    """

    input_frame = pd.DataFrame(list(input_rows))
    model_input = build_model_input_frame(input_frame, model_feature_names)

    preds = model.predict(model_input)

    outputs: list[dict] = []
    for pred in preds:
        predicted_demand = float(pred)
        outputs.append(
            {
                "predicted_demand": predicted_demand,
                "allocation_decision": allocate(predicted_demand),
            }
        )

    logger.info("Predictions generated for batch_size=%s", len(outputs))
    return outputs

