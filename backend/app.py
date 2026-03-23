from __future__ import annotations

import logging
import time
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .model_loader import ModelState, load_model
from .predictor import predict_with_allocation
from .schemas import PredictInput, PredictResponse

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "ml" / "model.pkl"


def _configure_logging() -> None:
    # Keep this simple but production-friendly: structured-ish log lines.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


_configure_logging()
logger = logging.getLogger("demand_forecasting_api")


app = FastAPI(
    title="Demand Forecasting API",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup() -> None:
    """
    Load the trained sklearn model once at startup.
    """

    state = load_model(MODEL_PATH)
    # Store state on app for fast access in request handlers.
    app.state.model_state = state


@app.middleware("http")
async def add_response_time_header(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
    finally:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        # Even if downstream raises, we still want timing for observability.
        if "response" in locals():
            response.headers["X-Response-Time-ms"] = f"{elapsed_ms:.3f}"
        logger.info(
            "request method=%s path=%s elapsed_ms=%.3f",
            request.method,
            request.url.path,
            elapsed_ms,
        )
    return response


def _get_model_or_raise(model_state: ModelState):
    if model_state.model is None:
        raise HTTPException(
            status_code=503,
            detail=f"Model not loaded. {model_state.model_error or 'Unknown error.'}",
        )
    return model_state.model


@app.get("/", summary="Health Check")
def health_check():
    """
    Health check endpoint.
    """

    return {"status": "API running"}


@app.post("/predict", response_model=PredictResponse, summary="Single Prediction")
def predict(payload: PredictInput):
    """
    Predict demand for a single (week, center_id, meal_id, lag_1, lag_2) input.
    """

    model_state: ModelState = app.state.model_state
    model = _get_model_or_raise(model_state)

    # Convert validated input to pandas DataFrame (required by spec).
    input_frame = pd.DataFrame([payload.model_dump()])

    # Align input to model feature columns, then predict.
    try:
        aligned_outputs = predict_with_allocation(
            model=model,
            model_feature_names=model_state.feature_names_in,
            input_rows=input_frame.to_dict(orient="records"),
        )
        output = aligned_outputs[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Prediction failed for request=%s", payload.model_dump())
        raise HTTPException(status_code=500, detail="Prediction failed.") from e

    logger.info(
        "prediction input=%s predicted_demand=%.6f decision=%s",
        payload.model_dump(),
        output["predicted_demand"],
        output["allocation_decision"],
    )

    return PredictResponse(**output)


@app.post(
    "/predict_batch",
    summary="Batch Prediction",
    response_model=list[PredictResponse],
)
def predict_batch(payload: list[PredictInput]):
    """
    Predict demand for a batch of inputs.
    """

    if not payload:
        raise HTTPException(status_code=400, detail="Payload list must not be empty.")

    model_state: ModelState = app.state.model_state
    model = _get_model_or_raise(model_state)

    input_frame = pd.DataFrame([row.model_dump() for row in payload])

    try:
        outputs = predict_with_allocation(
            model=model,
            model_feature_names=model_state.feature_names_in,
            input_rows=input_frame.to_dict(orient="records"),
        )
    except Exception as e:
        logger.exception("Batch prediction failed batch_size=%s", len(payload))
        raise HTTPException(status_code=500, detail="Batch prediction failed.") from e

    logger.info("prediction_batch size=%s", len(outputs))
    if outputs:
        preview = outputs[:25]
        logger.info(
            "prediction_batch_preview=%s",
            [
                {
                    "predicted_demand": o["predicted_demand"],
                    "allocation_decision": o["allocation_decision"],
                }
                for o in preview
            ],
        )
    return [PredictResponse(**o).model_dump() for o in outputs]


@app.exception_handler(ValidationError)
def validation_exception_handler(request: Request, exc: ValidationError):
    logger.warning("validation error path=%s err=%s", request.url.path, exc)
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

