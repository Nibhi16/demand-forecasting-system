from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import joblib

logger = logging.getLogger("demand_forecasting_api")


@dataclass(frozen=True)
class ModelState:
    model: Optional[Any]
    model_error: Optional[str]
    feature_names_in: Optional[list[str]]


def load_model(model_path: Path) -> ModelState:
    """
    Load a trained sklearn model from disk using joblib.

    If the file is missing or loading fails, returns a ModelState with `model=None`.
    """

    try:
        model = joblib.load(model_path)
        feature_names = getattr(model, "feature_names_in_", None)
        feature_names_in = list(feature_names) if feature_names is not None else None
        logger.info("Model loaded successfully: %s", model_path)
        return ModelState(model=model, model_error=None, feature_names_in=feature_names_in)
    except FileNotFoundError as e:
        logger.exception("Model file not found: %s", model_path)
        return ModelState(model=None, model_error=str(e), feature_names_in=None)
    except Exception as e:
        logger.exception("Failed to load model from: %s", model_path)
        return ModelState(model=None, model_error=str(e), feature_names_in=None)

